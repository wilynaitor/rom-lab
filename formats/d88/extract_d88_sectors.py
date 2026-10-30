
from pathlib import Path
import struct

SOURCE = Path("samples/dark/disk_a.d88")
OUTPUT = Path("extracted/disk_a_sectors")

HEADER_SIZE = 0x2B0
TRACK_COUNT = 164
SECTOR_HEADER_SIZE = 16

data = SOURCE.read_bytes()
OUTPUT.mkdir(parents=True, exist_ok=True)

tracks = []

for i in range(TRACK_COUNT):
    offset = struct.unpack_from("<I", data, 0x20 + i * 4)[0]

    if offset:
        if not HEADER_SIZE <= offset < len(data):
            raise ValueError(
                f"Offset de pista {i} fuera de rango: 0x{offset:X}"
            )
        tracks.append((i, offset))

tracks.sort(key=lambda item: item[1])

total_sectors = 0

for index, (track_id, start) in enumerate(tracks):
    end = (
        tracks[index + 1][1]
        if index + 1 < len(tracks)
        else len(data)
    )

    pos = start
    sector_index = 0

    while pos < end:
        if pos + SECTOR_HEADER_SIZE > end:
            raise ValueError(
                f"Cabecera incompleta en pista {track_id}, "
                f"offset 0x{pos:X}"
            )

        c, h, r, n, count = struct.unpack_from(
            "<BBBBH", data, pos
        )
        sector_size = struct.unpack_from("<H", data, pos + 14)[0]

        payload_start = pos + SECTOR_HEADER_SIZE
        payload_end = payload_start + sector_size

        if sector_size == 0 or payload_end > end:
            raise ValueError(
                f"Sector inválido en pista {track_id}, "
                f"offset 0x{pos:X}"
            )

        payload = data[payload_start:payload_end]

        filename = (
            f"track_{track_id:03}_"
            f"C{c:02}_H{h}_R{r:02}.bin"
        )
        (OUTPUT / filename).write_bytes(payload)

        sector_index += 1
        total_sectors += 1
        pos = payload_end

print(f"Sectores extraídos: {total_sectors}")
print(f"Directorio de salida: {OUTPUT}")
