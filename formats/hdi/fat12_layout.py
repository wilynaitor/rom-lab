from pathlib import Path
import struct

IMAGE = Path("samples/rusty/rusty.hdi")
data = IMAGE.read_bytes()

BPB_OFFSET = 0x9400

bytes_per_sector = struct.unpack_from("<H", data, BPB_OFFSET + 11)[0]
sectors_per_cluster = data[BPB_OFFSET + 13]
reserved_sectors = struct.unpack_from("<H", data, BPB_OFFSET + 14)[0]
fat_count = data[BPB_OFFSET + 16]
root_entries = struct.unpack_from("<H", data, BPB_OFFSET + 17)[0]
total_sectors = struct.unpack_from("<H", data, BPB_OFFSET + 19)[0]
sectors_per_fat = struct.unpack_from("<H", data, BPB_OFFSET + 22)[0]

root_sectors = (
    root_entries * 32 + bytes_per_sector - 1
) // bytes_per_sector

fat_start = reserved_sectors
root_start = reserved_sectors + fat_count * sectors_per_fat
data_start = root_start + root_sectors

print("=== FAT12 LAYOUT ===")
print("FAT 1:", fat_start)
print("FAT 2:", fat_start + sectors_per_fat)
print("Directorio raíz:", root_start)
print("Sectores del directorio:", root_sectors)
print("Datos:", data_start)
print("Sectores totales:", total_sectors)
print("Tamaño calculado:", total_sectors * bytes_per_sector)

print("\n=== OFFSETS ABSOLUTOS ===")
for name, sector in [
    ("FAT 1", fat_start),
    ("FAT 2", fat_start + sectors_per_fat),
    ("Directorio raíz", root_start),
    ("Datos", data_start),
]:
    print(f"{name}: 0x{BPB_OFFSET + sector * bytes_per_sector:X}")