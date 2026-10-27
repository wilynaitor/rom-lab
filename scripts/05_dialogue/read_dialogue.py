
from pathlib import Path
import struct

data = Path("rebuilt/dialogues_rebuilt.bin").read_bytes()

# Número de diálogos que esperamos encontrar.
count = 3

# Leer la tabla de offsets.
offsets = []

for i in range(count):
    position = i * 4
    offset = struct.unpack_from("<I", data, position)[0]
    offsets.append(offset)

print("Offsets:", [hex(x) for x in offsets])

# Leer cada diálogo desde su offset.
for i, offset in enumerate(offsets, start=1):
    end = data.index(b"\x00", offset)
    raw_text = data[offset:end]
    dialogue = raw_text.decode("utf-8")

    print(f"Diálogo {i}: {dialogue}")
