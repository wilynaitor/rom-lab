
from pathlib import Path

SOURCE = Path("samples/dialogues.bin")

data = SOURCE.read_bytes()

# En este formato de práctica, los textos empiezan en estos offsets.
# En un archivo real, primero tendríamos que localizar las cadenas.
offsets = [0x0C, 0x21, 0x3A]

encodings = ["utf-8", "shift_jis", "cp932"]

for offset in offsets:
    end = data.find(b"\x00", offset)

    print(f"\n=== Offset 0x{offset:04X} ===")

    if end == -1:
        print("No se encontró un terminador NUL.")
        continue

    raw = data[offset:end]
    print("Hex:", raw.hex(" "))

    for encoding in encodings:
        try:
            text = raw.decode(encoding)
            print(f"{encoding:10}: {text}")
        except UnicodeDecodeError:
            print(f"{encoding:10}: no se pudo decodificar")
