
from pathlib import Path
import sys

if len(sys.argv) != 2:
    print("Uso: python inspect_game_file.py <ruta_del_archivo>")
    raise SystemExit(1)

path = Path(sys.argv[1])

if not path.is_file():
    print(f"No se encontró el archivo: {path}")
    raise SystemExit(1)

data = path.read_bytes()

print(f"Archivo: {path.name}")
print(f"Tamaño: {len(data)} bytes")
print(f"Primeros 128 bytes:")
print(" ".join(f"{b:02X}" for b in data[:128]))

print("\nVista ASCII:")
print("".join(chr(b) if 32 <= b < 127 else "." for b in data[:128]))

print("\nCadenas ASCII imprimibles (mínimo 4 caracteres):")
start = None

for i, b in enumerate(data):
    if 32 <= b < 127:
        if start is None:
            start = i
    else:
        if start is not None and i - start >= 4:
            text = data[start:i].decode("ascii")
            print(f"0x{start:04X}: {text}")
        start = None

if start is not None and len(data) - start >= 4:
    print(f"0x{start:04X}: {data[start:].decode('ascii')}")
