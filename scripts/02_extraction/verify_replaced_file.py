
from pathlib import Path
import struct
import hashlib

SOURCE = Path("rebuilt/disk_a_replaced.d88")
EXPECTED = Path("rebuilt/SERIFU1.DAT")

data = SOURCE.read_bytes()

tracks = []

for i in range(164):
    offset = struct.unpack_from("<I", data, 0x20 + i * 4)[0]
    if offset:
        tracks.append((i, offset))

tracks.sort(key=lambda item: item[1])

sectors = []

for index, (track, start) in enumerate(tracks):
    end = tracks[index + 1][1] if index + 1 < len(tracks) else len(data)
    pos = start

    while pos < end:
        size = struct.unpack_from("<H", data, pos + 14)[0]
        payload = pos + 16

        if size == 0 or payload + size > end:
            raise ValueError(f"Sector inválido en pista {track}")

        sectors.append(data[payload:payload + size])
        pos = payload + size

boot = sectors[0]
bps = int.from_bytes(boot[0x0B:0x0D], "little")
spc = boot[0x0D]
reserved = int.from_bytes(boot[0x0E:0x10], "little")
fat_count = boot[0x10]
root_entries = int.from_bytes(boot[0x11:0x13], "little")
spf = int.from_bytes(boot[0x16:0x18], "little")

root_sectors = (root_entries * 32 + bps - 1) // bps
root_start = reserved + fat_count * spf
data_start = root_start + root_sectors

fat = b"".join(sectors[reserved:reserved + spf])

def next_cluster(cluster):
    offset = cluster + cluster // 2
    value = fat[offset] | (fat[offset + 1] << 8)
    return (value >> 4) & 0xFFF if cluster & 1 else value & 0xFFF

root = b"".join(sectors[root_start:root_start + root_sectors])

for offset in range(0, len(root), 32):
    entry = root[offset:offset + 32]

    if entry[0] == 0:
        break
    if entry[0] == 0xE5 or entry[11] == 0x0F:
        continue

    name = entry[:8].decode("ascii").rstrip()
    ext = entry[8:11].decode("ascii").rstrip()

    if name == "SERIFU1" and ext == "DAT":
        cluster = int.from_bytes(entry[26:28], "little")
        size = int.from_bytes(entry[28:32], "little")
        break
else:
    raise ValueError("SERIFU1.DAT no encontrado")

result = bytearray()
visited = set()

while len(result) < size:
    if cluster < 2 or cluster >= 0xFF0 or cluster in visited:
        raise ValueError("Cadena FAT12 inválida")

    visited.add(cluster)
    first_lba = data_start + (cluster - 2) * spc

    for i in range(spc):
        result.extend(sectors[first_lba + i])

    if len(result) >= size:
        break

    cluster = next_cluster(cluster)

result = bytes(result[:size])
expected = EXPECTED.read_bytes()

print("Tamaño recuperado:", len(result))
print("Tamaño esperado:", len(expected))
print("Contenido idéntico:", result == expected)
print("SHA-256 recuperado:", hashlib.sha256(result).hexdigest())
print("SHA-256 esperado:", hashlib.sha256(expected).hexdigest())
