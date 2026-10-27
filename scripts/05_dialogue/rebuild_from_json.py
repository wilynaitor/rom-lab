
from pathlib import Path
import json
import struct

# Archivos de entrada y salida
source = Path("extracted/dialogues.json")
output = Path("rebuilt/dialogues_rebuilt.bin")

# Leer el JSON
dialogues = json.loads(source.read_text(encoding="utf-8"))

# Comprobar que el JSON tenga la estructura esperada
if not isinstance(dialogues, list):
    raise ValueError("El JSON debe contener una lista de diálogos.")

# Convertir cada texto a bytes UTF-8 y añadir un byte nulo
encoded_texts = []

for dialogue in dialogues:
    if "text" not in dialogue:
        raise ValueError("Hay una entrada sin el campo 'text'.")

    text = dialogue["text"]

    if "\x00" in text:
        raise ValueError(
            "Un diálogo contiene un carácter nulo, "
            "que no está permitido en este formato."
        )

    encoded_texts.append(text.encode("utf-8") + b"\x00")

# En este formato de ejemplo, cada offset ocupa 4 bytes
table_size = len(encoded_texts) * 4
current_offset = table_size
offsets = []
string_data = bytearray()

# Calcular los offsets y construir la zona de textos
for encoded_text in encoded_texts:
    offsets.append(current_offset)
    string_data.extend(encoded_text)
    current_offset += len(encoded_text)

# Escribir la tabla de offsets en little-endian
binary = bytearray()

for offset in offsets:
    binary.extend(struct.pack("<I", offset))

# Añadir todos los textos después de la tabla
binary.extend(string_data)

# Guardar el archivo
output.parent.mkdir(parents=True, exist_ok=True)
output.write_bytes(binary)

print(f"Diálogos reconstruidos: {len(encoded_texts)}")
print(f"Offsets: {[hex(offset) for offset in offsets]}")
print(f"Tamaño: {len(binary)} bytes")
print(f"Archivo creado: {output}")
