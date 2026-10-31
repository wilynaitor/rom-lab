
from pathlib import Path
import struct

IMAGE_PATH = Path("samples/rusty/rusty.hdi")
VOLUME_OFFSET = 0x9400
REPORT_PATH = Path("notes/hdi_directories_report.txt")

def read_u16(data, offset):
    return struct.unpack_from("<H", data, offset)[0]

def read_u32(data, offset):
    return struct.unpack_from("<I", data, offset)[0]

def fat12_entry(fat, cluster):
    offset = cluster + cluster // 2
    value = fat[offset] | (fat[offset + 1] << 8)

    if cluster & 1:
        return value >> 4
    return value & 0x0FFF

def get_chain(fat, start, max_cluster):
    chain = []
    seen = set()
    cluster = start

    while 2 <= cluster <= max_cluster:
        if cluster in seen:
            raise ValueError(f"Ciclo detectado en cluster {cluster}")

        seen.add(cluster)
        chain.append(cluster)
        next_cluster = fat12_entry(fat, cluster)

        if next_cluster >= 0xFF8:
            return chain

        if next_cluster == 0:
            raise ValueError(f"Cluster libre dentro de cadena: {cluster}")

        if next_cluster == 0xFF7:
            raise ValueError(f"Cluster marcado como defectuoso: {cluster}")

        if next_cluster >= 0xFF0:
            raise ValueError(f"Valor reservado en FAT: {next_cluster:03X}")

        cluster = next_cluster

    raise ValueError("Cadena fuera del rango válido")

def decode_name(entry):
    name = entry[0:8].decode("ascii", errors="replace").rstrip()
    ext = entry[8:11].decode("ascii", errors="replace").rstrip()
    return f"{name}.{ext}" if ext else name

def main():
    image = IMAGE_PATH.read_bytes()

    bytes_per_sector = read_u16(image, VOLUME_OFFSET + 0x0B)
    sectors_per_cluster = image[VOLUME_OFFSET + 0x0D]
    reserved_sectors = read_u16(image, VOLUME_OFFSET + 0x0E)
    fat_count = image[VOLUME_OFFSET + 0x10]
    root_entries = read_u16(image, VOLUME_OFFSET + 0x11)
    total_sectors = read_u16(image, VOLUME_OFFSET + 0x13)
    sectors_per_fat = read_u16(image, VOLUME_OFFSET + 0x16)

    cluster_size = bytes_per_sector * sectors_per_cluster
    root_sectors = (
        root_entries * 32 + bytes_per_sector - 1
    ) // bytes_per_sector

    fat_start = VOLUME_OFFSET + reserved_sectors * bytes_per_sector
    fat_size = sectors_per_fat * bytes_per_sector
    fat = image[fat_start:fat_start + fat_size]

    root_start = fat_start + fat_count * fat_size
    data_start = root_start + root_sectors * bytes_per_sector

    data_clusters = (
        total_sectors - reserved_sectors
        - fat_count * sectors_per_fat - root_sectors
    ) // sectors_per_cluster
    max_cluster = data_clusters + 1

    directories = []

    for offset in range(root_start, root_start + root_entries * 32, 32):
        entry = image[offset:offset + 32]

        if entry[0] == 0x00:
            break
        if entry[0] == 0xE5:
            continue

        attr = entry[11]
        if attr & 0x0F == 0x0F:
            continue
        if not (attr & 0x10):
            continue

        name = decode_name(entry)
        start_cluster = read_u16(entry, 26)

        if name in (".", "..") or start_cluster < 2:
            continue

        directories.append((name, start_cluster, attr))

    lines = [
        "INSPECCIÓN DE DIRECTORIOS HDI",
        f"Imagen: {IMAGE_PATH}",
        f"Volumen: 0x{VOLUME_OFFSET:X}",
        f"Tamaño de cluster: {cluster_size}",
        f"Cluster máximo: {max_cluster}",
        ""
    ]

    for name, start_cluster, attr in directories:
        lines.append(f"CARPETA: {name}")
        lines.append(f"Cluster inicial: {start_cluster}")
        lines.append(f"Atributos: 0x{attr:02X}")

        try:
            chain = get_chain(fat, start_cluster, max_cluster)
            lines.append(f"Cadena: {chain}")
            lines.append(f"Clusters: {len(chain)}")

            entries_found = 0
            ended = False

            for cluster in chain:
                cluster_offset = data_start + (cluster - 2) * cluster_size

                if cluster_offset + cluster_size > len(image):
                    raise ValueError("Directorio fuera de los límites de la imagen")

                block = image[cluster_offset:cluster_offset + cluster_size]

                for pos in range(0, len(block), 32):
                    entry = block[pos:pos + 32]

                    if entry[0] == 0x00:
                        ended = True
                        break
                    if entry[0] == 0xE5:
                        continue

                    attr_entry = entry[11]

                    if attr_entry & 0x0F == 0x0F:
                        continue
                    if attr_entry & 0x08:
                        continue

                    child_name = decode_name(entry)
                    if child_name in (".", ".."):
                        continue

                    child_cluster = read_u16(entry, 26)
                    child_size = read_u32(entry, 28)
                    is_dir = bool(attr_entry & 0x10)

                    kind = "DIRECTORIO" if is_dir else "ARCHIVO"
                    lines.append(
                        f"  {kind}: {child_name} | "
                        f"cluster={child_cluster} | "
                        f"tamaño={child_size} | "
                        f"atributos=0x{attr_entry:02X}"
                    )
                    entries_found += 1

                if ended:
                    break

            lines.append(f"Entradas encontradas: {entries_found}")

        except (ValueError, IndexError) as error:
            lines.append(f"ERROR: {error}")

        lines.append("")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Informe guardado en: {REPORT_PATH}")

if __name__ == "__main__":
    main()
