
from pathlib import Path
import struct

IMAGE = Path("samples/rusty/rusty.hdi")

data = IMAGE.read_bytes()

data_offset = struct.unpack_from("<I", data, 0x08)[0]
disk_size = struct.unpack_from("<I", data, 0x0C)[0]
cylinders = struct.unpack_from("<I", data, 0x10)[0]
heads = struct.unpack_from("<I", data, 0x14)[0]
sectors = struct.unpack_from("<I", data, 0x18)[0]
sector_size = struct.unpack_from("<I", data, 0x1C)[0]

calculated_size = cylinders * heads * sectors * sector_size

print("=== HDI INSPECTOR ===")
print(f"Archivo: {IMAGE}")
print(f"Tamaño real: {len(data):,}")
print(f"Offset de datos: {data_offset}")
print(f"Tamaño declarado: {disk_size:,}")

print("\n=== GEOMETRÍA ===")
print(f"Cilindros: {cylinders}")
print(f"Cabezas: {heads}")
print(f"Sectores: {sectors}")
print(f"Bytes por sector: {sector_size}")
print(f"Tamaño calculado: {calculated_size:,}")

print("\n=== VALIDACIÓN ===")
print("Tamaño de datos correcto:",
      len(data) - data_offset == disk_size)
print("Geometría coherente:",
      calculated_size == disk_size)

print("\n=== PRIMER BLOQUE ===")
block = data[data_offset:data_offset + sector_size]
print("Bytes:", len(block))
print("Hex:", block.hex(" "))

print("\nFirma en offset 0xFE:",
      block[0xFE:0x100].hex(" ") if len(block) >= 256 else "No disponible")
