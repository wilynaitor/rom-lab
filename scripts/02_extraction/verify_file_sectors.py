
from pathlib import Path
import hashlib

SOURCE = Path("samples/dark/disk_a.d88")
EXTRACTED = Path("extracted/disk_a_files/SERIFU1.DAT")

HEADER_SIZE = 0x2B0
SECTOR_SIZE = 1024
SECTOR_HEADER_SIZE = 16

FIRST_LBA = 896
SECTOR_COUNT = 8

data = SOURCE.read_bytes()
result = bytearray()

# Obtener offsets de las pistas.
import struct

tracks = []

for i in range(164):
    offset = struct.unpack_from("<I", data, 0x20 + i * 4)[0]
    if offset:
        tracks.append((i, offset))

tracks.sort(key=lambda item: item[1])

# Crear índice LBA -> datos del sector.
lba = 0

for index, (track_id, start) in enumerate(tracks):
    end = tracks[index + 1][1] if index + 1 < len(tracks) else len(data)
    pos = start

    while pos < end:
        size = struct.unpack_from("<H", data, pos + 14)[0]
        payload_start = pos + SECTOR_HEADER_SIZE
        payload_end = payload_start + size

        if size != SECTOR_SIZE or payload_end > end:
            raise ValueError(f"Sector inesperado en pista {track_id}")

        if FIRST_LBA <= lba < FIRST_LBA + SECTOR_COUNT:
            result.extend(data[payload_start:payload_end])

        lba += 1
        pos = payload_end

original_file = EXTRACTED.read_bytes()

print("Bytes extraídos:", len(result))
print("Bytes del archivo:", len(original_file))
print("Coinciden:", bytes(result[:len(original_file)]) == original_file)
print("SHA-256 archivo:", hashlib.sha256(original_file).hexdigest())
print("SHA-256 sectores:", hashlib.sha256(result[:len(original_file)]).hexdigest())
