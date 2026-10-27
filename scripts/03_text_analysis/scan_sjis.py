
from pathlib import Path

SOURCE = Path("extracted/disk_a_files")
MIN_RUN = 4

def is_sjis_pair(data, i):
    """Comprueba si hay un par de bytes compatible con Shift-JIS."""
    if i + 1 >= len(data):
        return False

    lead, trail = data[i], data[i + 1]

    valid_lead = (
        0x81 <= lead <= 0x9F
        or 0xE0 <= lead <= 0xFC
    )
    valid_trail = (
        0x40 <= trail <= 0x7E
        or 0x80 <= trail <= 0xFC
    )

    return valid_lead and valid_trail

def scan_file(path):
    data = path.read_bytes()
    hits = []
    i = 0

    while i < len(data) - 1:
        if is_sjis_pair(data, i):
            start = i
            pairs = []

            while is_sjis_pair(data, i):
                pairs.append(data[i:i + 2])
                i += 2

            if len(pairs) >= MIN_RUN:
                raw = b"".join(pairs)

                try:
                    decoded = raw.decode("shift_jis")
                except UnicodeDecodeError:
                    decoded = "(secuencia no decodificable)"

                hits.append((start, raw.hex(" "), decoded))
        else:
            i += 1

    return hits

for path in sorted(SOURCE.iterdir()):
    if not path.is_file():
        continue
    if "GAME.EXE" not in path.name.upper():
        continue

    try:
        hits = scan_file(path)
    except OSError as error:
        print(f"ERROR {path.name}: {error}")
        continue

    if hits:
        print(f"\n=== {path.name} ===")
        for offset, raw, decoded in hits[:10]:
            print(f"0x{offset:04X}: {raw}")
            print(f"         Texto: {decoded}")
