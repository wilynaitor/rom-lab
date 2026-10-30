
from pathlib import Path
import struct

source = Path("samples/dark/disk_a.d88")
data = source.read_bytes()

HEADER_SIZE = 0x2B0
TRACK_COUNT = 164
SECTOR_HEADER_SIZE = 16

if len(data) < HEADER_SIZE:
    raise ValueError("La imagen no contiene una cabecera D88 completa.")

declared_size = struct.unpack_from("<I", data, 0x1C)[0]

if declared_size != len(data):
    print(
        f"AVISO: tamaño declarado {declared_size}, "
        f"tamaño real {len(data)}"
    )

tracks = []

for i in range(TRACK_COUNT):
    offset = struct.unpack_from("<I", data, 0x20 + i * 4)[0]

    if offset:
        if not HEADER_SIZE <= offset < len(data):
            print(f"Offset de pista {i} fuera de rango: 0x{offset:X}")
            continue
        tracks.append((i, offset))

# Ordenar por posición física dentro del archivo.
tracks.sort(key=lambda item: item[1])

for index, (track_id, start) in enumerate(tracks):
    end = (
        tracks[index + 1][1]
        if index + 1 < len(tracks)
        else len(data)
    )

    pos = start
    sector_count = 0

    print(f"\nPista {track_id}: 0x{start:08X}–0x{end:08X}")

    while pos < end:
        if pos + SECTOR_HEADER_SIZE > end:
            print(f"  Cabecera incompleta en 0x{pos:X}")
            break

        c, h, r, n, count = struct.unpack_from(
            "<BBBBH", data, pos
        )

        # Bytes 6–13: información de estado/reservada.
        # Bytes 14–15: tamaño de datos del sector.
        sector_size = struct.unpack_from("<H", data, pos + 14)[0]
        sector_data_start = pos + SECTOR_HEADER_SIZE
        sector_data_end = sector_data_start + sector_size

        if sector_size == 0 or sector_data_end > end:
            print(
                f"  Sector sospechoso en 0x{pos:X}: "
                f"tamaño={sector_size}"
            )
            break

        print(
            f"  C={c} H={h} R={r} N={n} "
            f"sectores={count} tamaño={sector_size}"
        )

        sector_count += 1
        pos = sector_data_end

    print(f"  Sectores examinados: {sector_count}")
