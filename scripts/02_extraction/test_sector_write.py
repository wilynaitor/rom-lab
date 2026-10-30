
from pathlib import Path
import struct
import hashlib

SOURCE = Path("samples/dark/disk_a.d88")
OUTPUT = Path("rebuilt/disk_a_write_test.d88")

HEADER_SIZE = 0x2B0
TRACK_COUNT = 164
SECTOR_HEADER_SIZE = 16

# Elegimos el primer sector de la primera pista.
TARGET_TRACK = 0
TARGET_SECTOR = 1

data = bytearray(SOURCE.read_bytes())

# Localizar la pista.
track_offset = struct.unpack_from(
    "<I", data, 0x20 + TARGET_TRACK * 4
)[0]

if track_offset == 0:
    raise ValueError("La pista seleccionada no existe")

# Leer la cabecera del sector.
c, h, r, n, count = struct.unpack_from(
    "<BBBBH", data, track_offset
)
size = struct.unpack_from("<H", data, track_offset + 14)[0]

if r != TARGET_SECTOR:
    raise ValueError("No se encontró el sector esperado")

payload_start = track_offset + SECTOR_HEADER_SIZE
payload_end = payload_start + size

if payload_end > len(data):
    raise ValueError("Los datos del sector exceden el archivo")

# Copiar los datos y escribir exactamente los mismos bytes.
original_payload = bytes(data[payload_start:payload_end])
data[payload_start:payload_end] = original_payload

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_bytes(data)

original_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
test_hash = hashlib.sha256(data).hexdigest()

print(f"Pista: {TARGET_TRACK}")
print(f"Sector: {TARGET_SECTOR}")
print(f"Tamaño: {size} bytes")
print("Cabecera conservada:", data[track_offset:payload_start].hex(" "))
print("Contenido conservado:", original_payload == data[payload_start:payload_end])
print("Archivos idénticos:", original_hash == test_hash)
print(f"Resultado: {OUTPUT}")
