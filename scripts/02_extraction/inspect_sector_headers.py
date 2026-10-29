
from pathlib import Path
import struct

SOURCE = Path("samples/dark/disk_a.d88")
OUTPUT = Path("notes/sector_headers.txt")

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
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

total = 0

with OUTPUT.open("w", encoding="utf-8") as report:
    for index, (track_id, start) in enumerate(tracks):
        end = (
            tracks[index + 1][1]
            if index + 1 < len(tracks)
            else len(data)
        )

        pos = start

        while pos < end:
            if pos + SECTOR_HEADER_SIZE > end:
                raise ValueError(
                    f"Cabecera incompleta en pista {track_id}"
                )

            c, h, r, n, count = struct.unpack_from(
                "<BBBBH", data, pos
            )
            size = struct.unpack_from("<H", data, pos + 14)[0]
            payload_end = pos + SECTOR_HEADER_SIZE + size

            if size == 0 or payload_end > end:
                raise ValueError(
                    f"Sector inválido en pista {track_id}, "
                    f"offset 0x{pos:X}"
                )

            report.write(
                f"Pista={track_id} Offset=0x{pos:X} "
                f"C={c} H={h} R={r} N={n} "
                f"Count={count} Tamaño={size} "
                f"Cabecera={data[pos:pos+16].hex(' ')}\n"
            )

            total += 1
            pos = payload_end

    report.write(f"\nTotal de sectores: {total}\n")

print(f"Informe creado: {OUTPUT}")
print(f"Sectores analizados: {total}")
