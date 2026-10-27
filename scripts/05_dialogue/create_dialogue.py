
from pathlib import Path
import struct

dialogues = [
    "Bienvenido, viajero.",
    "La puerta está cerrada.",
    "Nos vemos mañana."
]

# Tabla de offsets: un entero de 4 bytes por diálogo.
header_size = len(dialogues) * 4
offsets = []
text_data = bytearray()

for dialogue in dialogues:
    offsets.append(header_size + len(text_data))
    text_data.extend(dialogue.encode("utf-8") + b"\x00")

# Guardamos los offsets como enteros little-endian.
header = b"".join(
    struct.pack("<I", offset)
    for offset in offsets
)

Path("samples/dialogues.bin").write_bytes(
    header + text_data
)

print("Archivo de diálogos creado.")
print("Offsets:", [hex(x) for x in offsets])