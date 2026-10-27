
from pathlib import Path
import struct
import json

# Archivo binario de entrada
source = Path("samples/dialogues.bin")

# Archivo JSON de salida
output = Path("extracted/dialogues.json")

data = source.read_bytes()
count = 3

# Leer la tabla de offsets
offsets = []

for i in range(count):
    offset = struct.unpack_from("<I", data, i * 4)[0]
    offsets.append(offset)

# Extraer los diálogos
dialogues = []

for i, offset in enumerate(offsets):
    end = data.index(b"\x00", offset)
    raw_text = data[offset:end]
    text = raw_text.decode("utf-8")

    dialogues.append({
        "id": i,
        "offset": offset,
        "text": text
    })

# Crear la carpeta de salida si no existe
output.parent.mkdir(parents=True, exist_ok=True)

# Guardar como JSON
output.write_text(
    json.dumps(dialogues, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print(f"Se extrajeron {len(dialogues)} diálogos.")
print(f"Archivo creado: {output}")
