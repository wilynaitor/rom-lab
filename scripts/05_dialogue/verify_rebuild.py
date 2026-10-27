
from pathlib import Path
import json
import struct

JSON_PATH = Path("extracted/dialogues.json")
BIN_PATH = Path("rebuilt/dialogues_rebuilt.bin")

json_dialogues = json.loads(
    JSON_PATH.read_text(encoding="utf-8")
)
data = BIN_PATH.read_bytes()

# La tabla tiene un offset de 4 bytes por diálogo.
count = len(json_dialogues)
table_size = count * 4

if len(data) < table_size:
    raise ValueError("El binario es demasiado pequeño para la tabla.")

# Leer los offsets y extraer los textos.
binary_dialogues = []

for i in range(count):
    offset = struct.unpack_from("<I", data, i * 4)[0]

    if offset < table_size or offset >= len(data):
        raise ValueError(f"Offset inválido en diálogo {i}: {offset}")

    end = data.find(b"\x00", offset)

    if end == -1:
        raise ValueError(f"El diálogo {i} no termina en byte nulo.")

    text = data[offset:end].decode("utf-8")
    binary_dialogues.append(text)

# Comparar los textos originales del JSON con los del binario.
errors = 0

for i, (expected, actual) in enumerate(
    zip(json_dialogues, binary_dialogues)
):
    expected_text = expected["text"]

    if expected_text == actual:
        print(f"OK  Diálogo {i}: {actual}")
    else:
        print(f"ERROR Diálogo {i}")
        print(f"  JSON:    {expected_text}")
        print(f"  Binario: {actual}")
        errors += 1

if len(json_dialogues) != len(binary_dialogues):
    print("ERROR: la cantidad de diálogos no coincide.")
    errors += 1

if errors:
    print(f"\nFalló la verificación: {errors} problema(s).")
else:
    print("\n¡Verificación completada! Todos los diálogos coinciden.")
