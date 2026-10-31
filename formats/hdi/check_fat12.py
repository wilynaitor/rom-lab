from pathlib import Path
import struct

IMAGE = Path("samples/rusty/rusty.hdi")
data = IMAGE.read_bytes()

offset = 0x9400

print("=== POSIBLE BPB FAT12 ===")

fields = {
    "Bytes por sector": struct.unpack_from("<H", data, offset + 11)[0],
    "Sectores por cluster": data[offset + 13],
    "Sectores reservados": struct.unpack_from("<H", data, offset + 14)[0],
    "Número de FAT": data[offset + 16],
    "Entradas raíz": struct.unpack_from("<H", data, offset + 17)[0],
    "Sectores totales": struct.unpack_from("<H", data, offset + 19)[0],
    "Sectores por FAT": struct.unpack_from("<H", data, offset + 22)[0],
}

for name, value in fields.items():
    print(f"{name}: {value}")

print("\nEtiqueta:", data[offset + 54:offset + 62])
print("Bytes finales del sector:",
      data[offset + 510:offset + 512].hex(" "))