from pathlib import Path

IMAGE = Path("samples/rusty/rusty.hdi")
DATA_OFFSET = 0x1000

data = IMAGE.read_bytes()[DATA_OFFSET:]

signatures = {
    "FAT": b"FAT",
    "FAT12": b"FAT12",
    "FAT16": b"FAT16",
    "FAT32": b"FAT32",
    "NTFS": b"NTFS",
    "EXFAT": b"EXFAT",
    "ISO9660": b"CD001",
}

print("=== BUSCADOR DE FIRMAS ===")

for name, signature in signatures.items():
    positions = []
    start = 0

    while True:
        pos = data.find(signature, start)
        if pos == -1:
            break

        positions.append(pos)
        start = pos + 1

    print(f"{name}: {len(positions)} coincidencias")
    for pos in positions[:5]:
        print(f"  Offset absoluto: 0x{DATA_OFFSET + pos:X}")