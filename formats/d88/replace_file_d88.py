
from pathlib import Path
import struct
import hashlib

SOURCE = Path("samples/dark/disk_a.d88")
NEW_FILE = Path("rebuilt/SERIFU1.DAT")
OUTPUT = Path("rebuilt/disk_a_replaced.d88")

TARGET_NAME = "SERIFU1"
TARGET_EXT = "DAT"

HEADER_SIZE = 0x2B0
SECTOR_SIZE = 1024
SECTOR_HEADER_SIZE = 16

data = bytearray(SOURCE.read_bytes())

if not NEW_FILE.exists():
    raise FileNotFoundError(
        f"Crea primero el archivo: {NEW_FILE}"
    )

replacement = NEW_FILE.read_bytes()

# Leer parámetros FAT12 del sector de arranque.
boot = None
tracks = []

for i in range(164):
    offset = struct.unpack_from("<I", data, 0x20 + i * 4)[0]
    if offset:
        tracks.append((i, offset))

tracks.sort(key=lambda item: item[1])

# Extraer sectores en orden LBA.
sectors = []
for index, (track_id, start) in enumerate(tracks):
    end = tracks[index + 1][1] if index + 1 < len(tracks) else len(data)
    pos = start

    while pos < end:
        size = struct.unpack_from("<H", data, pos + 14)[0]
        payload = pos + SECTOR_HEADER_SIZE

        if size != SECTOR_SIZE or payload + size > end:
            raise ValueError("Estructura de sector inesperada")

        sectors.append((pos, payload, size))
        pos = payload + size

boot = bytes(data[sectors[0][1]:sectors[0][1] + SECTOR_SIZE])

bps = int.from_bytes(boot[0x0B:0x0D], "little")
spc = boot[0x0D]
reserved = int.from_bytes(boot[0x0E:0x10], "little")
fat_count = boot[0x10]
root_entries = int.from_bytes(boot[0x11:0x13], "little")
spf = int.from_bytes(boot[0x16:0x18], "little")

if bps != SECTOR_SIZE or spc != 1:
    raise ValueError("Geometría FAT12 inesperada")

root_sectors = (root_entries * 32 + bps - 1) // bps
root_start = reserved + fat_count * spf
data_start = root_start + root_sectors

# Leer directorio raíz.
root = b"".join(
    data[sectors[root_start + i][1]:
         sectors[root_start + i][1] + SECTOR_SIZE]
    for i in range(root_sectors)
)

target_entry = None

for offset in range(0, len(root), 32):
    entry = root[offset:offset + 32]

    if entry[0] == 0:
        break
    if entry[0] == 0xE5 or entry[11] == 0x0F:
        continue

    name = entry[:8].decode("ascii").rstrip()
    ext = entry[8:11].decode("ascii").rstrip()

    if name == TARGET_NAME and ext == TARGET_EXT:
        target_entry = entry
        break

if target_entry is None:
    raise ValueError("Archivo no encontrado en el directorio raíz")

first_cluster = int.from_bytes(target_entry[26:28], "little")
original_size = int.from_bytes(target_entry[28:32], "little")

if len(replacement) != original_size:
    raise ValueError(
        f"El archivo nuevo mide {len(replacement)} bytes; "
        f"debe medir exactamente {original_size}"
    )

# Leer la primera FAT.
fat = b"".join(
    data[sectors[reserved + i][1]:
         sectors[reserved + i][1] + SECTOR_SIZE]
    for i in range(spf)
)

def next_cluster(cluster):
    offset = cluster + cluster // 2
    value = fat[offset] | (fat[offset + 1] << 8)
    return (value >> 4) & 0xFFF if cluster & 1 else value & 0xFFF

# Seguir cadena de clústeres.
clusters = []
visited = set()
cluster = first_cluster

while cluster >= 2 and cluster < 0xFF0:
    if cluster in visited:
        raise ValueError("Bucle en cadena FAT12")

    visited.add(cluster)
    clusters.append(cluster)

    if len(clusters) * bps * spc >= original_size:
        break

    cluster = next_cluster(cluster)

if len(clusters) * bps * spc < original_size:
    raise ValueError("Cadena FAT12 demasiado corta")

# Escribir datos en los sectores correspondientes.
position = 0

for cluster in clusters:
    first_lba = data_start + (cluster - 2) * spc

    for i in range(spc):
        lba = first_lba + i
        sector_data = replacement[position:position + bps]

        if not sector_data:
            break

        sector_data = sector_data.ljust(bps, b"\x00")
        sector_pos = sectors[lba][1]

        data[sector_pos:sector_pos + bps] = sector_data
        position += min(bps, len(replacement) - position)

# Guardar copia.
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_bytes(data)

print("Archivo reemplazado:", TARGET_NAME + "." + TARGET_EXT)
print("Clústeres utilizados:", clusters)
print("Tamaño:", len(replacement))
print("Original SHA-256:", hashlib.sha256(SOURCE.read_bytes()).hexdigest())
print("Copia SHA-256:", hashlib.sha256(data).hexdigest())
print("Resultado:", OUTPUT)
