
from pathlib import Path

source = Path("samples/dialogues.bin")
data = source.read_bytes()

MIN_LENGTH = 4

def scan_null_terminated(data):
    results = []
    start = 0

    while start < len(data):
        end = data.find(b"\x00", start)

        if end == -1:
            end = len(data)

        chunk = data[start:end]

        if len(chunk) >= MIN_LENGTH:
            try:
                text = chunk.decode("utf-8")

                if all(char.isprintable() for char in text):
                    results.append((start, text))

            except UnicodeDecodeError:
                pass

        start = end + 1

    return results


for offset, text in scan_null_terminated(data):
    print(f"Offset 0x{offset:08X}: {text}")
