
from pathlib import Path
import hashlib

IMAGE = Path("samples/rusty/rusty.hdi")

DATA_OFFSET = 0x1000
BLOCK_SIZE = 310
BLOCK_COUNT = 12

data = IMAGE.read_bytes()

print("=== HDI BLOCK INSPECTOR ===")

for index in range(BLOCK_COUNT):
    start = DATA_OFFSET + index * BLOCK_SIZE
    block = data[start:start + BLOCK_SIZE]

    if len(block) != BLOCK_SIZE:
        print(f"Bloque {index}: incompleto")
        continue

    digest = hashlib.sha256(block).hexdigest()

    print(f"\nBloque: {index}")
    print(f"Offset: 0x{start:X}")
    print(f"Tamaño: {len(block)}")
    print(f"SHA-256: {digest}")
    print(f"Primeros 32 bytes: {block[:32].hex(' ')}")
