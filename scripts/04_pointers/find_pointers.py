
from pathlib import Path
import struct

source = Path("samples/dialogues.bin")
data = source.read_bytes()
candidates = []

# Buscar posibles tablas de punteros de 32 bits.
# En este formato de práctica, los offsets son little-endian.
for table_start in range(0, min(len(data), 64), 4):
    pointers = []
    position = table_start

    while position + 4 <= len(data):
        value = struct.unpack_from("<I", data, position)[0]

        # Un puntero válido debería apuntar dentro del archivo,
        # después de la propia tabla.
        if value < position + 4 or value >= len(data):
            break

        # Comprobar si el destino parece texto UTF-8 terminado en NUL.
        end = data.find(b"\x00", value)

        if end == -1:
            break

        chunk = data[value:end]

        try:
            text = chunk.decode("utf-8")
        except UnicodeDecodeError:
            break

        if not text or not all(char.isprintable() for char in text):
            break

        pointers.append((position, value, text))
        position += 4

    if len(pointers) >= 2:
        candidates.append((table_start, pointers))

    # Mostrar primero las tablas con más punteros válidos.
    candidates.sort(key=lambda candidate: len(candidate[1]), reverse=True)

    print("\n=== Candidatos ordenados ===")

    for table_start, pointers in candidates:
        print(
            f"\nInicio: 0x{table_start:04X} "
            f"| Entradas válidas: {len(pointers)}"
        )

        for entry_pos, target, text in pointers:
            print(
                f"  0x{entry_pos:04X} -> 0x{target:04X}: {text}"
            )
