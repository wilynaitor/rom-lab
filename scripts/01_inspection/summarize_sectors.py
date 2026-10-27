
from pathlib import Path
from collections import Counter

SOURCE = Path("extracted/disk_a_sectors")
files = sorted(SOURCE.glob("*.bin"))

print(f"Cantidad de sectores: {len(files)}")

sizes = Counter(path.stat().st_size for path in files)

print("\n=== Tamaños ===")
for size, count in sorted(sizes.items()):
    print(f"{size} bytes: {count} sectores")

print("\n=== Primeros 16 sectores ===")

for path in files[:16]:
    data = path.read_bytes()

    print(f"\n--- {path.name} ---")
    print("Hex:", data[:32].hex(" "))
    print("ASCII:", "".join(
        chr(b) if 32 <= b <= 126 else "."
        for b in data[:32]
    ))
