
from pathlib import Path
import struct

SOURCE = Path("samples/dialogues.bin")
TABLE_START = 0
POINTER_SIZE = 4
POINTER_COUNT = 3

data = SOURCE.read_bytes()
table_end = TABLE_START + POINTER_SIZE * POINTER_COUNT

print(f"Archivo: {SOURCE}")
print(f"Tamaño: {len(data)} bytes")
print(f"Tabla: 0x{TABLE_START:04X} - 0x{table_end:04X}")
print()

if table_end > len(data):
    raise ValueError("La tabla de punteros excede el archivo.")

targets = []

for i in range(POINTER_COUNT):
    entry_offset = TABLE_START + i * POINTER_SIZE
    target = struct.unpack_from("<I", data, entry_offset)[0]

    print(f"Puntero {i}: entrada 0x{entry_offset:04X} -> 0x{target:04X}")

    if target < table_end or target >= len(data):
        print("  ERROR: destino fuera de la zona de textos.")
        continue

    end = data.find(b"\x00", target)

    if end == -1:
        print("  ERROR: no se encontró terminador NUL.")
        continue

    raw_text = data[target:end]

    try:
        text = raw_text.decode("utf-8")
    except UnicodeDecodeError:
        print("  ERROR: la cadena no es UTF-8 válido.")
        continue

    targets.append(target)
    print(f"  Texto: {text}")
    print(f"  Longitud: {len(raw_text)} bytes")
    print(f"  Fin exclusivo: 0x{end:04X}")

print("\n=== Resumen ===")

if len(targets) == len(set(targets)):
    print("OK: los destinos válidos son distintos.")
else:
    print("AVISO: hay punteros que comparten el mismo destino.")

print(f"Destinos válidos: {len(targets)} de {POINTER_COUNT}")
