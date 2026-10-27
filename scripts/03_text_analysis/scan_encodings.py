
from pathlib import Path

SOURCE = Path("samples/dialogues.bin")
MIN_BYTES = 4

data = SOURCE.read_bytes()

def scan_null_strings(data):
    results = []
    start = 0

    while start < len(data):
        end = data.find(b"\x00", start)

        if end == -1:
            end = len(data)

        raw = data[start:end]

        if len(raw) >= MIN_BYTES:
            results.append((start, raw))

        start = end + 1

    return results


for offset, raw in scan_null_strings(data):
    print(f"\nOffset 0x{offset:08X}")
    print(f"Hex: {raw.hex(' ')}")

    for encoding in ("utf-8", "shift_jis", "cp932"):
        try:
            text = raw.decode(encoding)

            if all(char.isprintable() for char in text):
                print(f"{encoding:10}: {text}")
        except UnicodeDecodeError:
            print(f"{encoding:10}: no válido")
