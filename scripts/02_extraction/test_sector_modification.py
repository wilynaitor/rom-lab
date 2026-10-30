
from pathlib import Path
import hashlib
import struct

SOURCE = Path("samples/dark/disk_a.d88")
OUTPUT = Path("rebuilt/disk_a_modified_test.d88")

TRACK = 0
SECTOR = 1
BYTE_IN_SECTOR = 0

original = SOURCE.read_bytes()
data = bytearray(original)

track_offset = struct.unpack_from(
    "<I", data, 0x20 + TRACK * 4
)[0]

if not track_offset:
    raise ValueError("Pista inexistente")

header = bytes(data[track_offset:track_offset + 16])
size = struct.unpack_from("<H", data, track_offset + 14)[0]

payload_start = track_offset + 16
payload_end = payload_start + size

if size == 0 or payload_end > len(data):
    raise ValueError("Sector inválido")

if BYTE_IN_SECTOR >= size:
    raise ValueError("Posición fuera del sector")

old_value = data[payload_start + BYTE_IN_SECTOR]

# Cambiamos un byte por otro valor, sin alterar el tamaño.
new_value = old_value ^ 0xFF
data[payload_start + BYTE_IN_SECTOR] = new_value

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_bytes(data)

check = OUTPUT.read_bytes()

print(f"Byte original: {old_value:02X}")
print(f"Byte nuevo: {check[payload_start + BYTE_IN_SECTOR]:02X}")
print("Cabecera intacta:", check[track_offset:track_offset + 16] == header)
print("Tamaño intacto:", len(check) == len(original))
print("Original intacto:", SOURCE.read_bytes() == original)
print("Copia diferente:", hashlib.sha256(check).digest() != hashlib.sha256(original).digest())
print(f"Archivo creado: {OUTPUT}")
