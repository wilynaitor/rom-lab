
from pathlib import Path
import hashlib
import struct

SOURCE = Path("samples/dark/disk_a.d88")
OUTPUT = Path("rebuilt/disk_a_rebuilt.d88")

HEADER_SIZE = 0x2B0
TRACK_COUNT = 164
SECTOR_HEADER_SIZE = 16

data = SOURCE.read_bytes()
tracks = []

for i in range(TRACK_COUNT):
    offset = struct.unpack_from("<I", data, 0x20 + i * 4)[0]
    if offset:
        tracks.append((i, offset))

tracks.sort(key=lambda item: item[1])

# Conservamos intacta la cabecera original del disco.
rebuilt = bytearray(data[:HEADER_SIZE])

for index, (track_id, start) in enumerate(tracks):
    end = tracks[index + 1][1] if index + 1 < len(tracks) else len(data)
    track_data = data[start:end]

    # Actualizamos la tabla de offsets de pistas.
    new_offset = len(rebuilt)
    struct.pack_into("<I", rebuilt, 0x20 + track_id * 4, new_offset)

    # Copiamos todos los bytes de la pista, incluidas las cabeceras
    # de sectores, los datos y cualquier espacio entre ellos.
    rebuilt.extend(track_data)

# Actualizamos el tamaño total del archivo en la cabecera D88.
struct.pack_into("<I", rebuilt, 0x1C, len(rebuilt))

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_bytes(rebuilt)

original_hash = hashlib.sha256(data).hexdigest()
rebuilt_hash = hashlib.sha256(rebuilt).hexdigest()

print(f"Original: {len(data):,} bytes")
print(f"Reconstruido: {len(rebuilt):,} bytes")
print(f"SHA-256 original:      {original_hash}")
print(f"SHA-256 reconstruido:  {rebuilt_hash}")
print("Idénticos:", original_hash == rebuilt_hash)
print(f"Archivo creado: {OUTPUT}")
