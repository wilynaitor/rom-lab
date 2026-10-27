
from pathlib import Path

path = Path(
    "extracted/disk_a_sectors/track_000_C00_H0_R01.bin"
)

data = path.read_bytes()

print(f"Tamaño del sector: {len(data)} bytes")
print(f"Primeros 64 bytes: {data[:64].hex(' ').upper()}")
print(f"Bytes por sector (offset 0x0B): {int.from_bytes(data[0x0B:0x0D], 'little')}")
print(f"Sectores por clúster (offset 0x0D): {data[0x0D]}")
print(f"Sectores reservados: {int.from_bytes(data[0x0E:0x10], 'little')}")
print(f"Número de FAT: {data[0x10]}")
print(f"Entradas raíz: {int.from_bytes(data[0x11:0x13], 'little')}")
print(f"Firma en 0x1FE: {data[0x1FE:0x200].hex(' ').upper()}")


for offset in range(0, 128, 16):
    chunk = data[offset:offset + 16]
    print(f"{offset:04X}: {chunk.hex(' ').upper()}")
