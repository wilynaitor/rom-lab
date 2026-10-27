
from pathlib import Path
import math

SOURCE = Path("extracted/disk_a_sectors")
SECTOR_SIZE = 1024

def read_sector(lba):
    track = lba // 8
    sector = lba % 8 + 1
    cylinder = track // 2
    head = track % 2

    filename = (
        f"track_{track:03d}_C{cylinder:02d}_H{head}_R{sector:02d}.bin"
    )
    path = SOURCE / filename

    if not path.exists():
        raise FileNotFoundError(f"No encuentro el sector: {path}")

    data = path.read_bytes()
    if len(data) != SECTOR_SIZE:
        raise ValueError(f"Tamaño inesperado en {path}: {len(data)} bytes")

    return data


boot = read_sector(0)

bytes_per_sector = int.from_bytes(boot[0x0B:0x0D], "little")
sectors_per_cluster = boot[0x0D]
reserved_sectors = int.from_bytes(boot[0x0E:0x10], "little")
fat_count = boot[0x10]
root_entries = int.from_bytes(boot[0x11:0x13], "little")
total_sectors = int.from_bytes(boot[0x13:0x15], "little")
sectors_per_fat = int.from_bytes(boot[0x16:0x18], "little")

root_sectors = math.ceil(root_entries * 32 / bytes_per_sector)
root_start = reserved_sectors + fat_count * sectors_per_fat
data_start = root_start + root_sectors

print("=== Parámetros detectados ===")
print(f"Bytes por sector:       {bytes_per_sector}")
print(f"Sectores por clúster:   {sectors_per_cluster}")
print(f"Sectores reservados:    {reserved_sectors}")
print(f"Número de FATs:         {fat_count}")
print(f"Entradas raíz:          {root_entries}")
print(f"Sectores por FAT:       {sectors_per_fat}")
print(f"Total de sectores:      {total_sectors}")
print(f"Inicio directorio raíz: {root_start}")
print(f"Sectores del directorio:{root_sectors}")
print(f"Inicio de datos:        {data_start}")

root = b"".join(
    read_sector(root_start + i)
    for i in range(root_sectors)
)

print("\n=== Archivos del directorio raíz ===")

for offset in range(0, len(root), 32):
    entry = root[offset:offset + 32]

    if len(entry) < 32 or entry[0] == 0x00:
        break

    if entry[0] == 0xE5:
        continue

    attr = entry[11]

    # Saltar entradas de nombre largo y etiquetas de volumen.
    if attr == 0x0F or attr & 0x08:
        continue

    name = entry[0:8].decode("ascii", errors="replace").rstrip()
    ext = entry[8:11].decode("ascii", errors="replace").rstrip()
    filename = f"{name}.{ext}" if ext else name

    first_cluster = int.from_bytes(entry[26:28], "little")
    size = int.from_bytes(entry[28:32], "little")

    if attr & 0x10:
        kind = "DIR"
    else:
        kind = "FILE"

    print(
        f"{kind:4} {filename:15} "
        f"clúster={first_cluster:4} tamaño={size:8}"
    )
