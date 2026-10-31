from pathlib import Path

IMAGE = Path("samples/rusty/rusty.hdi")
DATA_OFFSET = 0x1000

data = IMAGE.read_bytes()

targets = {
    "FAT12": 0x9436,
    "FAT": 0x80294,
    "CD001": 0xABA6C,
}

for name, pos in targets.items():
    start = max(0, pos - 64)
    end = min(len(data), pos + 96)

    print(f"\n=== {name} en 0x{pos:X} ===")
    print(data[start:end].hex(" "))