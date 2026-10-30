
from pathlib import Path
import math

SOURCE = Path("extracted/disk_a_sectors")
OUTPUT = Path("notes/file_cluster_map.txt")

def read_sector(lba):
    track = lba // 8
    sector = lba % 8 + 1
    cylinder = track // 2
    head = track % 2

    filename = (
        f"track_{track:03d}_C{cylinder:02d}_"
        f"H{head}_R{sector:02d}.bin"
    )

    return (SOURCE / filename).read_bytes()

boot = read_sector(0)

bps = int.from_bytes(boot[0x0B:0x0D], "little")
spc = boot[0x0D]
reserved = int.from_bytes(boot[0x0E:0x10], "little")
fat_count = boot[0x10]
root_entries = int.from_bytes(boot[0x11:0x13], "little")
spf = int.from_bytes(boot[0x16:0x18], "little")

root_sectors = math.ceil(root_entries * 32 / bps)
root_start = reserved + fat_count * spf
data_start = root_start + root_sectors

fat = b"".join(read_sector(reserved + i) for i in range(spf))

def next_cluster(cluster):
    offset = cluster + cluster // 2
    value = fat[offset] | (fat[offset + 1] << 8)
    return (value >> 4) & 0xFFF if cluster & 1 else value & 0xFFF

root = b"".join(read_sector(root_start + i) for i in range(root_sectors))

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT.open("w", encoding="utf-8") as report:
    for offset in range(0, len(root), 32):
        entry = root[offset:offset + 32]

        if entry[0] == 0:
            break
        if entry[0] == 0xE5 or entry[11] == 0x0F or entry[11] & 0x18:
            continue

        name = entry[:8].decode("ascii", errors="replace").rstrip()
        ext = entry[8:11].decode("ascii", errors="replace").rstrip()
        filename = f"{name}.{ext}" if ext else name

        cluster = int.from_bytes(entry[26:28], "little")
        size = int.from_bytes(entry[28:32], "little")

        clusters = []
        visited = set()

        while cluster >= 2 and cluster < 0xFF0 and cluster not in visited:
            visited.add(cluster)
            clusters.append(cluster)

            if len(clusters) * spc * bps >= size:
                break

            cluster = next_cluster(cluster)

        report.write(f"{filename} | {size} bytes\n")

        for current in clusters:
            first_lba = data_start + (current - 2) * spc
            report.write(
                f"  Cluster {current} -> LBA {first_lba}"
                f" hasta {first_lba + spc - 1}\n"
            )

        report.write("\n")

print(f"Mapa creado: {OUTPUT}")
