
from pathlib import Path
import struct

# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------

IMAGE_PATH = Path("samples/rusty/rusty.hdi")
VOLUME_OFFSET = 0x9400

OUTPUT_DIR = Path("extracted/hdi_recursive")
REPORT_PATH = Path("notes/hdi_recursive_extraction_report.txt")

# --------------------------------------------------
# FUNCIONES BÁSICAS
# --------------------------------------------------

def u16(data, offset):
    return struct.unpack_from("<H", data, offset)[0]


def u32(data, offset):
    return struct.unpack_from("<I", data, offset)[0]


def decode_name(entry):
    name = entry[0:8].decode("ascii", errors="replace").rstrip()
    ext = entry[8:11].decode("ascii", errors="replace").rstrip()
    return f"{name}.{ext}" if ext else name


def fat12_entry(fat, cluster):
    offset = cluster + cluster // 2

    if offset + 1 >= len(fat):
        raise ValueError(f"Entrada FAT fuera de rango: cluster {cluster}")

    value = fat[offset] | (fat[offset + 1] << 8)

    if cluster & 1:
        return value >> 4

    return value & 0x0FFF


# --------------------------------------------------
# LECTURA DE CADENAS FAT12
# --------------------------------------------------

def get_chain(fat, start_cluster, max_cluster):
    if start_cluster < 2 or start_cluster > max_cluster:
        raise ValueError(f"Cluster inicial inválido: {start_cluster}")

    chain = []
    seen = set()
    cluster = start_cluster

    while True:
        if cluster < 2 or cluster > max_cluster:
            raise ValueError(f"Cluster fuera de rango: {cluster}")

        if cluster in seen:
            raise ValueError(f"Ciclo detectado en cluster {cluster}")

        seen.add(cluster)
        chain.append(cluster)

        next_cluster = fat12_entry(fat, cluster)

        if 0xFF8 <= next_cluster <= 0xFFF:
            return chain

        if next_cluster == 0:
            raise ValueError(f"Cluster libre en cadena: {cluster}")

        if next_cluster == 0xFF7:
            raise ValueError(f"Cluster defectuoso: {cluster}")

        if 0xFF0 <= next_cluster <= 0xFF6:
            raise ValueError(f"Cluster reservado: {next_cluster:03X}")

        cluster = next_cluster


# --------------------------------------------------
# LECTURA DE DIRECTORIOS
# --------------------------------------------------

def parse_directory(data):
    entries = []

    for offset in range(0, len(data), 32):
        entry = data[offset:offset + 32]

        if len(entry) < 32:
            break

        if entry[0] == 0x00:
            break

        if entry[0] == 0xE5:
            continue

        attr = entry[11]

        # Entradas de nombre largo
        if (attr & 0x0F) == 0x0F:
            continue

        # Etiquetas de volumen
        if attr & 0x08:
            continue

        name = decode_name(entry)

        if name in (".", ".."):
            continue

        entries.append({
            "name": name,
            "attr": attr,
            "cluster": u16(entry, 26),
            "size": u32(entry, 28),
            "is_dir": bool(attr & 0x10),
        })

    return entries


# --------------------------------------------------
# EXTRACTOR
# --------------------------------------------------

class HDIExtractor:
    def __init__(self, image):
        self.image = image
        self.errors = []
        self.extracted_files = 0
        self.extracted_dirs = 0
        self.skipped = 0
        self.used_clusters = {}

        self.bytes_per_sector = u16(image, VOLUME_OFFSET + 0x0B)
        self.sectors_per_cluster = image[VOLUME_OFFSET + 0x0D]
        self.reserved_sectors = u16(image, VOLUME_OFFSET + 0x0E)
        self.fat_count = image[VOLUME_OFFSET + 0x10]
        self.root_entries = u16(image, VOLUME_OFFSET + 0x11)
        self.total_sectors = u16(image, VOLUME_OFFSET + 0x13)
        self.sectors_per_fat = u16(image, VOLUME_OFFSET + 0x16)

        if self.bytes_per_sector == 0 or self.sectors_per_cluster == 0:
            raise ValueError("BPB inválido: tamaño de sector o cluster igual a cero")

        if self.fat_count != 2:
            raise ValueError(f"Se esperaban 2 FAT; se encontraron {self.fat_count}")

        self.cluster_size = (
            self.bytes_per_sector * self.sectors_per_cluster
        )

        self.root_sectors = (
            self.root_entries * 32 + self.bytes_per_sector - 1
        ) // self.bytes_per_sector

        self.fat_start = (
            VOLUME_OFFSET + self.reserved_sectors * self.bytes_per_sector
        )

        self.fat_size = self.sectors_per_fat * self.bytes_per_sector

        fat1 = image[
            self.fat_start:self.fat_start + self.fat_size
        ]

        fat2_start = self.fat_start + self.fat_size
        fat2 = image[fat2_start:fat2_start + self.fat_size]

        if len(fat1) != self.fat_size or len(fat2) != self.fat_size:
            raise ValueError("Una de las FAT está incompleta")

        if fat1 != fat2:
            raise ValueError("Las dos copias FAT12 no coinciden")

        self.fat = fat1

        self.root_start = (
            self.fat_start + self.fat_count * self.fat_size
        )

        self.data_start = (
            self.root_start + self.root_sectors * self.bytes_per_sector
        )

        self.data_clusters = (
            self.total_sectors
            - self.reserved_sectors
            - self.fat_count * self.sectors_per_fat
            - self.root_sectors
        ) // self.sectors_per_cluster

        self.max_cluster = self.data_clusters + 1

        self.volume_end = (
            VOLUME_OFFSET + self.total_sectors * self.bytes_per_sector
        )

        if self.volume_end > len(image):
            raise ValueError("El volumen declarado supera el tamaño de la imagen")

        if self.data_start > self.volume_end:
            raise ValueError("Inicio de datos fuera del volumen")

    def read_cluster(self, cluster):
        offset = self.data_start + (cluster - 2) * self.cluster_size
        end = offset + self.cluster_size

        if offset < self.data_start or end > self.volume_end:
            raise ValueError(f"Cluster fuera del volumen: {cluster}")

        return self.image[offset:end]

    def read_directory(self, entry):
        if entry["cluster"] < 2:
            raise ValueError(
                f"Directorio sin cluster inicial: {entry['name']}"
            )

        chain = get_chain(
            self.fat,
            entry["cluster"],
            self.max_cluster
        )

        content = b"".join(
            self.read_cluster(cluster) for cluster in chain
        )

        return content, chain

    def register_clusters(self, chain, path):
        for cluster in chain:
            previous = self.used_clusters.get(cluster)

            if previous is not None:
                self.errors.append(
                    f"Cluster compartido {cluster}: {previous} y {path}"
                )
            else:
                self.used_clusters[cluster] = str(path)

    def extract_file(self, entry, destination):
        name = entry["name"]
        size = entry["size"]
        start = entry["cluster"]

        output_path = destination / name

        if output_path.exists():
            raise FileExistsError(
                f"El archivo ya existe; no se sobrescribe: {output_path}"
            )

        if size == 0:
            if start not in (0, 1):
                raise ValueError(
                    f"Archivo vacío con cluster inesperado: {start}"
                )

            output_path.write_bytes(b"")
            self.extracted_files += 1
            return

        if start < 2:
            raise ValueError(
                f"Archivo con tamaño pero sin cluster válido: {name}"
            )

        chain = get_chain(self.fat, start, self.max_cluster)

        required_clusters = (
            size + self.cluster_size - 1
        ) // self.cluster_size

        if len(chain) != required_clusters:
            raise ValueError(
                f"Cadena de {name}: {len(chain)} clusters; "
                f"se esperaban {required_clusters}"
            )

        self.register_clusters(chain, output_path)

        content = b"".join(
            self.read_cluster(cluster) for cluster in chain
        )

        content = content[:size]

        if len(content) != size:
            raise ValueError(f"Tamaño incompleto: {name}")

        output_path.write_bytes(content)
        self.extracted_files += 1

    def walk_directory(self, entries, destination, depth=0):
        if depth > 32:
            self.errors.append(
                f"Profundidad máxima de directorios superada: {destination}"
            )
            return

        for entry in entries:
            name = entry["name"]
            output_path = destination / name

            try:
                if entry["is_dir"]:
                    if output_path.exists():
                        raise FileExistsError(
                            f"La carpeta ya existe: {output_path}"
                        )

                    output_path.mkdir(parents=True)
                    self.extracted_dirs += 1

                    content, chain = self.read_directory(entry)
                    self.register_clusters(chain, output_path)

                    child_entries = parse_directory(content)

                    self.walk_directory(
                        child_entries,
                        output_path,
                        depth + 1
                    )

                else:
                    self.extract_file(entry, destination)

            except (ValueError, OSError) as error:
                message = f"{output_path}: {error}"
                self.errors.append(message)

    def run(self):
        root_size = self.root_entries * 32
        root_data = self.image[
            self.root_start:self.root_start + root_size
        ]

        root_entries = parse_directory(root_data)

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        self.walk_directory(root_entries, OUTPUT_DIR)


# --------------------------------------------------
# EJECUCIÓN Y REPORTE
# --------------------------------------------------

def main():
    if not IMAGE_PATH.exists():
        raise FileNotFoundError(f"No existe la imagen: {IMAGE_PATH}")

    image = IMAGE_PATH.read_bytes()

    extractor = HDIExtractor(image)

    try:
        extractor.run()
    except Exception as error:
        extractor.errors.append(f"Error general: {error}")

    lines = [
        "INFORME DE EXTRACCIÓN RECURSIVA HDI",
        f"Imagen: {IMAGE_PATH}",
        f"Tamaño de imagen: {len(image)} bytes",
        f"Volumen: 0x{VOLUME_OFFSET:X}",
        f"Tamaño de sector: {extractor.bytes_per_sector}",
        f"Sectores por cluster: {extractor.sectors_per_cluster}",
        f"Tamaño de cluster: {extractor.cluster_size}",
        f"Clusters de datos: {extractor.data_clusters}",
        f"Cluster máximo: {extractor.max_cluster}",
        f"FAT1 y FAT2 idénticas: Sí",
        f"Directorio de salida: {OUTPUT_DIR}",
        "",
        f"Archivos extraídos: {extractor.extracted_files}",
        f"Directorios creados: {extractor.extracted_dirs}",
        f"Clusters registrados: {len(extractor.used_clusters)}",
        f"Errores: {len(extractor.errors)}",
        "",
        "DETALLE DE ERRORES"
    ]

    if extractor.errors:
        lines.extend(
            f"- {error}" for error in extractor.errors
        )
    else:
        lines.append("Sin errores.")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(f"Extracción finalizada.")
    print(f"Informe: {REPORT_PATH}")
    print(f"Archivos: {extractor.extracted_files}")
    print(f"Directorios: {extractor.extracted_dirs}")
    print(f"Errores: {len(extractor.errors)}")


if __name__ == "__main__":
    main()
