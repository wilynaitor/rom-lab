
from pathlib import Path

samples = {
    "ASCII": b"Hello, traveler.",
    "UTF-8": "こんにちは".encode("utf-8"),
    "Shift-JIS": "こんにちは".encode("shift_jis"),
}

for name, raw in samples.items():
    print(f"\n=== Bytes de ejemplo: {name} ===")
    print("Hex:", raw.hex(" "))

    for encoding in ("utf-8", "shift_jis"):
        try:
            decoded = raw.decode(encoding)
            print(f"{encoding:10} -> {decoded}")
        except UnicodeDecodeError:
            print(f"{encoding:10} -> error de decodificación")
