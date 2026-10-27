
from pathlib import Path

folder = Path("extracted/disk_a_sectors")

for filename in [
    "track_000_C00_H0_R01.bin",
    "track_000_C00_H0_R06.bin",
    "track_000_C00_H0_R07.bin",
    "track_000_C00_H0_R08.bin",
]:
    path = folder / filename

    if not path.exists():
        print(f"No encontrado: {filename}")
        continue

    data = path.read_bytes()
    print(f"\n--- {filename} ---")

    for offset in range(0, len(data), 32):
        chunk = data[offset:offset + 32]
        printable = "".join(
            chr(b) if 32 <= b <= 126 else "."
            for b in chunk
        )
        print(f"{offset:04X}: {printable}")
