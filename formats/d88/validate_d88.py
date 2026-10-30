
from pathlib import Path
import struct

SOURCE = Path("samples/dark/disk_a.d88")
HEADER_SIZE = 0x2B0
TRACK_COUNT = 164
SECTOR_HEADER_SIZE = 16

data = SOURCE.read_bytes()
tracks = []

for i in range(TRACK_COUNT):
    offset = struct.unpack_from("<I", data, 0x20 + i * 4)[0]
    if offset:
        if offset < HEADER_SIZE or offset >= len(data):
            raise ValueError(f"Offset inválido en pista {i}: 0x{offset:X}")
        tracks.append((i, offset))

tracks.sort(key=lambda item: item[1])
total = 0
errors = []

for index, (track_id, start) in enumerate(tracks):
    end = tracks[index + 1][1] if index + 1 < len(tracks) else len(data)
    pos = start
    track_count = 0

    while pos < end:
        if pos + SECTOR_HEADER_SIZE > end:
            errors.append(f"Pista {track_id}: cabecera incompleta en 0x{pos:X}")
            break

        c, h, r, n, count = struct.unpack_from("<BBBBH", data, pos)
        size = struct.unpack_from("<H", data, pos + 14)[0]
        payload_end = pos + SECTOR_HEADER_SIZE + size

        if size == 0 or payload_end > end:
            errors.append(f"Pista {track_id}: sector inválido en 0x{pos:X}")
            break

        # El tamaño indicado por N debería coincidir con el tamaño del sector.
        expected_size = 128 * (2 ** n)
        if size != expected_size:
            errors.append(
                f"Pista {track_id}, R={r}: tamaño {size}, "
                f"esperado según N={n}: {expected_size}"
            )

        total += 1
        track_count += 1
        pos = payload_end

    if pos != end and not errors:
        errors.append(f"Pista {track_id}: no termina en el límite esperado")

    print(f"Pista {track_id:3}: {track_count} sectores")

print(f"\nTotal de sectores: {total}")
print(f"Errores encontrados: {len(errors)}")

for error in errors:
    print("ERROR:", error)

if not errors:
    print("Validación estructural básica: OK")
