
from pathlib import Path
import struct
import sys
import math

IMAGE_PATH = Path("samples/rusty/rusty.hdi")
VOLUME_OFFSET = 0x9400
OUTPUT_DIR = Path("extracted/hdi")
REPORT_PATH = Path("notes/hdi_extraction_report.txt")


def read_u16(data, offset):
    return struct.unpack_from("<H", data, offset)[0]


def read_u32(data, offset):
    return struct.unpack_from("<I", data, offset)[0]


def fat12_entry(fat, cluster):
    offset = cluster + cluster // 2

    if offset + 1 >= len(fat):
        raise ValueError(f"Entrada FAT fuera de rango: {cluster}")

    value = fat[offset] | (fat[offset + 1] << 8)

    if cluster & 1:
        return value >> 4

    return value & 0x0FFF


def get_file_chain(fat, first_cluster, max_cluster):
    chain = []
    visited = set()
    current = first_cluster

    while True:
        if current < 2 or current > max_cluster:
            raise ValueError(
                f"Clúster fuera de rango: {current}"
            )

        if current in visited:
            raise ValueError(
                f"Ciclo detectado en clúster {current}"
            )

        visited.add(current)
        chain.append(current)

        next_cluster = fat12_entry(fat, current)

        if next_cluster >= 0xFF8:
            break

        if next_cluster == 0:
            raise ValueError("La cadena termina en un clúster libre")

        if next_cluster == 1:
            raise ValueError("Referencia al clúster reservado 1")

        if next_cluster == 0xFF7:
            raise ValueError("La cadena contiene un clúster dañado")

        if 0xFF0 <= next_cluster <= 0xFF6:
            raise ValueError(
                f"Referencia a clúster reservado: {next_cluster:#x}"
            )

        current = next_cluster

        if len(chain) > max_cluster - 1:
            raise ValueError("Cadena FAT demasiado larga")

    return chain


def save_report(lines):
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8"
    )
    print(f"Reporte guardado en: {REPORT_PATH}")


def main():
    report = []

    if not IMAGE_PATH.exists():
        raise FileNotFoundError(
            f"No existe la imagen: {IMAGE_PATH}"
        )

    image = IMAGE_PATH.read_bytes()
    b = VOLUME_OFFSET

    if b + 512 > len(image):
        raise ValueError("No hay espacio suficiente para leer el BPB.")

    bpb = image[b:b + 512]

    bytes_per_sector = read_u16(bpb, 11)
    sectors_per_cluster = bpb[13]
    reserved_sectors = read_u16(bpb, 14)
    fat_count = bpb[16]
    root_entries = read_u16(bpb, 17)
    total_sectors = read_u16(bpb, 19) or read_u32(bpb, 32)
    sectors_per_fat = read_u16(bpb, 22)

    if bytes_per_sector not in (512, 1024, 2048, 4096):
        raise ValueError("Tamaño de sector no reconocido.")

    if not sectors_per_cluster or not fat_count or not sectors_per_fat:
        raise ValueError("Parámetros FAT inválidos.")

    if fat_count != 2:
        raise ValueError("Se esperaban dos copias FAT.")

    if not total_sectors:
        raise ValueError("El volumen no declara sectores totales.")

    root_dir_sectors = math.ceil(
        root_entries * 32 / bytes_per_sector
    )

    fat_size = sectors_per_fat * bytes_per_sector
    fat_start = b + reserved_sectors * bytes_per_sector
    root_start = fat_start + fat_count * fat_size
    data_start = root_start + root_dir_sectors * bytes_per_sector
    volume_end = b + total_sectors * bytes_per_sector

    cluster_size = bytes_per_sector * sectors_per_cluster

    data_sectors = (
        total_sectors
        - reserved_sectors
        - fat_count * sectors_per_fat
        - root_dir_sectors
    )

    if data_sectors <= 0:
        raise ValueError("No hay sectores de datos válidos.")

    cluster_count = data_sectors // sectors_per_cluster
    max_cluster = cluster_count + 1

    if volume_end > len(image) or data_start > volume_end:
        raise ValueError("Las estructuras exceden los límites del volumen.")

    fat1 = image[fat_start:fat_start + fat_size]
    fat2_start = fat_start + fat_size
    fat2 = image[fat2_start:fat2_start + fat_size]

    if len(fat1) != fat_size or len(fat2) != fat_size:
        raise ValueError("No se pudieron leer las FAT completas.")

    if fat1 != fat2:
        raise ValueError(
            "Las dos copias FAT son diferentes. Extracción cancelada."
        )

    root_size = root_dir_sectors * bytes_per_sector
    root = image[root_start:root_start + root_size]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    report.extend([
        "EXTRACCIÓN FAT12 - HDI",
        "=" * 40,
        f"Imagen: {IMAGE_PATH}",
        f"Tamaño de imagen: {len(image)} bytes",
        f"Inicio del volumen: {b:#x}",
        f"Bytes por sector: {bytes_per_sector}",
        f"Sectores por clúster: {sectors_per_cluster}",
        f"Tamaño de clúster: {cluster_size}",
        f"Clústeres de datos: {cluster_count}",
        f"Rango válido: 2 - {max_cluster}",
        f"Copias FAT idénticas: {fat1 == fat2}",
        f"Directorio de salida: {OUTPUT_DIR}",
        "",
        "ARCHIVOS",
        "-" * 40,
    ])

    extracted = 0
    skipped = 0
    errors = 0
    directories = 0

    for offset in range(0, len(root), 32):
        entry = root[offset:offset + 32]

        if len(entry) < 32 or entry[0] == 0x00:
            break

        if entry[0] == 0xE5:
            continue

        attributes = entry[11]

        # Entradas LFN y etiquetas de volumen.
        if attributes == 0x0F or attributes & 0x08:
            continue

        raw_name = entry[:8].decode(
            "ascii", errors="replace"
        ).strip()

        raw_ext = entry[8:11].decode(
            "ascii", errors="replace"
        ).strip()

        filename = (
            f"{raw_name}.{raw_ext}" if raw_ext else raw_name
        )

        first_cluster = read_u16(entry, 26)
        file_size = read_u32(entry, 28)

        if attributes & 0x10:
            directories += 1
            report.append(f"OMITIDO DIR  {filename}")
            continue

        if file_size == 0:
            output_path = OUTPUT_DIR / filename
            output_path.write_bytes(b"")
            extracted += 1
            report.append(f"OK VACÍO    {filename}")
            continue

        try:
            chain = get_file_chain(
                fat1, first_cluster, max_cluster
            )

            required_clusters = math.ceil(
                file_size / cluster_size
            )

            if len(chain) < required_clusters:
                raise ValueError(
                    f"Cadena corta: necesita {required_clusters}, "
                    f"tiene {len(chain)}"
                )

            file_data = bytearray()

            for cluster in chain:
                cluster_offset = (
                    data_start
                    + (cluster - 2) * cluster_size
                )

                cluster_end = cluster_offset + cluster_size

                if cluster_offset < data_start or cluster_end > volume_end:
                    raise ValueError(
                        f"Clúster {cluster} fuera del volumen"
                    )

                file_data.extend(
                    image[cluster_offset:cluster_end]
                )

            file_data = file_data[:file_size]

            if len(file_data) != file_size:
                raise ValueError("Tamaño extraído incorrecto")

            output_path = OUTPUT_DIR / filename

            if output_path.exists():
                raise FileExistsError(
                    f"El archivo ya existe: {output_path}"
                )

            output_path.write_bytes(file_data)

            extracted += 1
            report.append(
                f"OK          {filename} | "
                f"{file_size} bytes | "
                f"{len(chain)} clústeres"
            )

        except Exception as error:
            errors += 1
            report.append(
                f"ERROR       {filename}: {error}"
            )

    report.extend([
        "",
        "RESUMEN",
        "-" * 40,
        f"Archivos extraídos: {extracted}",
        f"Directorios omitidos: {directories}",
        f"Errores: {errors}",
        f"Archivos vacíos o normales omitidos: {skipped}",
        "",
        "Extracción de directorio raíz finalizada.",
    ])

    save_report(report)

    print(f"Archivos extraídos: {extracted}")
    print(f"Errores: {errors}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"ERROR: {error}")
        sys.exit(1)
