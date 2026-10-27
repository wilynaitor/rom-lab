
from pathlib import Path
import struct

SOURCE = Path("samples/dialogues.bin")
data = SOURCE.read_bytes()

POINTER_SIZE = 4
MIN_POINTERS = 2

def get_string(offset):
    if offset < 0 or offset >= len(data):
        return None

    end = data.find(b"\x00", offset)

    if end == -1:
        return None

    raw = data[offset:end]

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None

    if not text or not all(char.isprintable() for char in text):
        return None

    return text


candidates = []

# Probar posibles comienzos alineados a 4 bytes.
for start in range(0, len(data) - POINTER_SIZE + 1, POINTER_SIZE):
    entries = []
    position = start

    while position + POINTER_SIZE <= len(data):
        target = struct.unpack_from("<I", data, position)[0]

        # El destino debe estar después de la entrada actual
        # y dentro del archivo.
        if target < position + POINTER_SIZE or target >= len(data):
            break

        text = get_string(target)

        if text is None:
            break

        entries.append((position, target, text))
        position += POINTER_SIZE

    if len(entries) >= MIN_POINTERS:
        candidates.append((start, entries))


candidates.sort(
    key=lambda candidate: len(candidate[1]),
    reverse=True
)

print("=== Tablas candidatas ===")

for start, entries in candidates:
    print(
        f"\nInicio: 0x{start:04X} "
        f"| Entradas consecutivas: {len(entries)}"
    )

    for entry, target, text in entries:
        print(f"  0x{entry:04X} -> 0x{target:04X}: {text}")
