from pathlib import Path
from collections import Counter

IMAGE = Path("samples/rusty/rusty.hdi")
DATA_OFFSET = 0x1000

data = IMAGE.read_bytes()[DATA_OFFSET:]

print("=== ESCANEO HDI ===")
print("Tamaño de datos:", len(data))

# Buscar regiones consecutivas de ceros
zero_runs = []
start = None

for i, byte in enumerate(data):
    if byte == 0 and start is None:
        start = i
    elif byte != 0 and start is not None:
        if i - start >= 64:
            zero_runs.append((start, i - start))
        start = None

if start is not None and len(data) - start >= 64:
    zero_runs.append((start, len(data) - start))

print("\nRegiones de ceros (primeras 20):")
for offset, length in zero_runs[:20]:
    print(f"Offset 0x{offset:X} | {length} bytes")

# Frecuencia de bytes
counts = Counter(data)
print("\nBytes más frecuentes:")
for byte, count in counts.most_common(10):
    print(f"0x{byte:02X}: {count}")