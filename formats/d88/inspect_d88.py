
from pathlib import Path
import struct

source = Path("samples/dark/disk_a.d88")
data = source.read_bytes()

if len(data) < 0x2B0:
    raise ValueError("El archivo es demasiado pequeño para una cabecera D88.")

# Cabecera D88:
# 0x00–0x1A: nombre del disco
# 0x1B: protección contra escritura
# 0x1C: tipo de disco
# 0x1D–0x20: tamaño total declarado
# 0x20 en adelante: tabla de offsets de pistas

name = data[:0x1A].split(b"\x00", 1)[0]
write_protect = data[0x1A]
disk_type = data[0x1B]
declared_size = struct.unpack_from("<I", data, 0x1C)[0]

print(f"Archivo: {source}")
print(f"Tamaño real: {len(data):,} bytes")
print(f"Nombre en cabecera: {name!r}")
print(f"Protección contra escritura: {write_protect}")
print(f"Tipo de disco: 0x{disk_type:02X}")
print(f"Tamaño declarado: {declared_size:,} bytes")

if declared_size != len(data):
    print("AVISO: el tamaño declarado no coincide con el real.")

track_offsets = []

for i in range(164):
    offset = struct.unpack_from("<I", data, 0x20 + i * 4)[0]

    if offset:
        track_offsets.append((i, offset))

print(f"\nPistas con offset no nulo: {len(track_offsets)}")

for track_index, offset in track_offsets:
    status = "válido" if 0x2B0 <= offset < len(data) else "FUERA DE RANGO"
    print(f"Pista {track_index:3}: offset 0x{offset:08X} ({status})")
