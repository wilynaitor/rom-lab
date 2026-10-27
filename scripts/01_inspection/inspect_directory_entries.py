
from pathlib import Path

folder = Path("extracted/disk_a_sectors")

for filename in [
    "track_000_C00_H0_R06.bin",
    "track_000_C00_H0_R07.bin",
]:
    path = folder / filename
    data = path.read_bytes()

    print(f"\n--- {filename} ---")

    for offset in range(0, min(len(data), 128), 32):
        entry = data[offset:offset + 32]

        name = entry[:8].decode("ascii", errors="replace").rstrip()
        ext = entry[8:11].decode("ascii", errors="replace").rstrip()

        print(
            f"Offset 0x{offset:04X} | "
            f"{name}.{ext} | "
            f"{entry[11:].hex(' ').upper()}"
        )
