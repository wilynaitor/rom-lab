from pathlib import Path

IMAGE = Path("samples/rusty/rusty.hdi")
data = IMAGE.read_bytes()

BPB = 0x9400
BPS = 1024

fat1 = BPB + 1 * BPS
fat2 = BPB + 5 * BPS
root = BPB + 9 * BPS

fat_size = 4 * BPS
root_size = 24 * BPS

print("=== COMPARACIÓN DE FAT ===")
print("FAT 1:", data[fat1:fat1 + fat_size].hex(" "))
print("FAT 2:", data[fat2:fat2 + fat_size].hex(" "))
print("¿Son iguales?",
      data[fat1:fat1 + fat_size] ==
      data[fat2:fat2 + fat_size])

print("\n=== DIRECTORIO RAÍZ ===")

for pos in range(root, root + root_size, 32):
    entry = data[pos:pos + 32]

    if entry[0] == 0:
        break

    if entry[0] == 0xE5:
        continue

    name = entry[:8].decode("ascii", errors="replace").rstrip()
    ext = entry[8:11].decode("ascii", errors="replace").rstrip()
    attributes = entry[11]
    first_cluster = int.from_bytes(entry[26:28], "little")
    size = int.from_bytes(entry[28:32], "little")

    filename = f"{name}.{ext}" if ext else name

    print(
        f"{filename:15} "
        f"Atributos: 0x{attributes:02X} "
        f"Clúster: {first_cluster:5} "
        f"Tamaño: {size:8}"
    )