
from pathlib import Path
import struct

source = Path("samples/dialogues.bin")
output = Path("rebuilt/dialogues_translated.bin")

data = source.read_bytes()
count = 3

# Leer los offsets originales.
offsets = [
    struct.unpack_from("<I", data, i * 4)[0]
    for i in range(count)
]

# Extraer los diálogos.
dialogues = []

for offset in offsets:
    end = data.index(b"\x00", offset)
    dialogues.append(data[offset:end].decode("utf-8"))

# Modificar una traducción.
dialogues[1] = "¡La puerta está abierta de par en par!"

# Reconstruir la tabla y el bloque de texto.
header_size = count * 4
new_offsets = []
text_data = bytearray()

for dialogue in dialogues:
    new_offsets.append(header_size + len(text_data))
    text_data.extend(dialogue.encode("utf-8") + b"\x00")

header = b"".join(
    struct.pack("<I", offset)
    for offset in new_offsets
)

output.parent.mkdir(parents=True, exist_ok=True)
output.write_bytes(header + text_data)

print("Archivo reconstruido:", output)
print("Nuevos offsets:", [hex(x) for x in new_offsets])
print("Tamaño original:", len(data), "bytes")
print("Tamaño nuevo:", len(header + text_data), "bytes")
