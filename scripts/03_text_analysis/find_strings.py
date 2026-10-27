
from pathlib import Path
import re

def find_strings(filename, min_length=4):
    data = Path(filename).read_bytes()

    pattern = rb"[\x20-\x7E]{" + str(min_length).encode() + rb",}"
    matches = re.finditer(pattern, data)

    for match in matches:
        offset = match.start()
        text = match.group().decode("ascii")

        print(f"Offset 0x{offset:08X}: {text}")

find_strings("samples/example.bin")
