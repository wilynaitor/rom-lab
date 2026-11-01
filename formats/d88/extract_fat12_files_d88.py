
from pathlib import Path
import math

# ============================================================
# Configuración
# Ejecutar desde la raíz del proyecto rom-lab.
# ============================================================

SOURCE = Path("extracted/disk_a_sectors")
DEST = Path("extracted/disk_a_files")

DEST.mkdir(parents=True, exist_ok=True)


# ============================================================
# Lectura de sectores
# El disco tiene 8 sectores por pista y 2 caras.
# ============================================================

def read_sector(lba):
    """Lee un sector usando su número lógico (LBA)."""
    track = lba // 8
    sector = lba % 8 + 1
    cylinder = track // 2
    head = track % 2

    filename = (
        f"track_{track:03d}_C{cylinder:02d}_"
        f"H{head}_R{sector:02d}.bin"
    )
    path = SOURCE / filename

    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró el sector LBA {lba}: {path}"
        )

    data = path.read_bytes()

    if len(data) != 1024:
        raise ValueError(
            f"El sector {path} mide {len(data)} bytes, no 1024."
        )

    return data


# ============================================================
# Lectura de parámetros del sistema de archivos
# ============================================================

boot = read_sector(0)

bytes_per_sector = int.from_bytes(boot[0x0B:0x0D], "little")
sectors_per_cluster = boot[0x0D]
reserved_sectors = int.from_bytes(boot[0x0E:0x10], "little")
fat_count = boot[0x10]
root_entries = int.from_bytes(boot[0x11:0x13], "little")
total_sectors = int.from_bytes(boot[0x13:0x15], "little")
sectors_per_fat = int.from_bytes(boot[0x16:0x18], "little")

if bytes_per_sector != 1024:
    raise ValueError(
        f"Tamaño de sector inesperado: {bytes_per_sector}"
    )

if sectors_per_cluster == 0:
    raise ValueError("Sectores por clúster no puede ser cero.")

root_sectors = math.ceil(
    root_entries * 32 / bytes_per_sector
)

root_start = reserved_sectors + fat_count * sectors_per_fat
data_start = root_start + root_sectors

if total_sectors and data_start >= total_sectors:
    raise ValueError("Los parámetros del sistema de archivos no cuadran.")


# ============================================================
# Carga de la primera FAT
# ============================================================

fat_start = reserved_sectors

fat = b"".join(
    read_sector(fat_start + i)
    for i in range(sectors_per_fat)
)


def next_cluster(cluster):
    """Obtiene la siguiente entrada de una tabla FAT12."""
    offset = cluster + cluster // 2

    if offset + 1 >= len(fat):
        raise ValueError(
            f"Entrada FAT12 fuera de rango para el clúster {cluster}."
        )

    value = fat[offset] | (fat[offset + 1] << 8)

    if cluster & 1:
        return value >> 4

    return value & 0x0FFF


# ============================================================
# Conversión de clúster a datos
# ============================================================

def read_cluster(cluster):
    """Lee todos los sectores de un clúster."""
    if cluster < 2:
        raise ValueError(f"Clúster de datos inválido: {cluster}")

    lba = data_start + (cluster - 2) * sectors_per_cluster

    return b"".join(
        read_sector(lba + i)
        for i in range(sectors_per_cluster)
    )


def extract_file(first_cluster, file_size):
    """Reconstruye un archivo siguiendo su cadena FAT12."""
    if file_size == 0:
        return b""

    if first_cluster < 2:
        raise ValueError(
            f"Clúster inicial inválido: {first_cluster}"
        )

    result = bytearray()
    visited = set()
    cluster = first_cluster

    while len(result) < file_size:
        if cluster in visited:
            raise ValueError(
                f"Bucle detectado en el clúster {cluster}."
            )

        if cluster < 2 or cluster >= 0xFF0:
            raise ValueError(
                f"Clúster inesperado en la cadena: {cluster:#05x}"
            )

        visited.add(cluster)
        result.extend(read_cluster(cluster))

        if len(result) >= file_size:
            break

        cluster = next_cluster(cluster)

        if cluster >= 0xFF8:
            raise ValueError(
                "La cadena terminó antes de alcanzar el tamaño esperado."
            )

        if cluster == 0xFF7:
            raise ValueError("La cadena contiene un clúster defectuoso.")

        if cluster >= 0xFF0:
            raise ValueError(
                f"Marcador FAT inesperado: {cluster:#05x}"
            )

    return bytes(result[:file_size])


# ============================================================
# Lectura del directorio raíz
# ============================================================

root = b"".join(
    read_sector(root_start + i)
    for i in range(root_sectors)
)

print("=== Extracción FAT12 de D'ark ===")
print(f"Fuente: {SOURCE}")
print(f"Destino: {DEST}")
print(f"Total de sectores: {total_sectors}")
print(f"Inicio de datos: {data_start}")
print()

success = 0
errors = 0

for offset in range(0, len(root), 32):
    entry = root[offset:offset + 32]

    if len(entry) < 32 or entry[0] == 0x00:
        break

    # Entrada eliminada.
    if entry[0] == 0xE5:
        continue

    attributes = entry[11]

    # Saltar nombres largos, etiquetas de volumen y directorios.
    if attributes == 0x0F or attributes & 0x18:
        continue

    name = entry[0:8].decode(
        "ascii", errors="replace"
    ).rstrip()

    extension = entry[8:11].decode(
        "ascii", errors="replace"
    ).rstrip()

    filename = f"{name}.{extension}" if extension else name

    first_cluster = int.from_bytes(entry[26:28], "little")
    file_size = int.from_bytes(entry[28:32], "little")

    try:
        content = extract_file(first_cluster, file_size)

        output_path = DEST / filename
        output_path.write_bytes(content)

        print(f"OK    {filename:15} {file_size:8} bytes")
        success += 1

    except (ValueError, FileNotFoundError) as error:
        print(f"ERROR {filename:15} {error}")
        errors += 1

print()
print("=== Resumen ===")
print(f"Archivos extraídos: {success}")
print(f"Archivos con errores: {errors}")
print(f"Carpeta de salida: {DEST.resolve()}")
