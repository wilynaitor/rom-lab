
from pathlib import Path
from collections import defaultdict
import struct

ROOT = Path("extracted/hdi_recursive")
OUTPUT = Path("notes/hdi_mag_size_fields.txt")

def marker(data):
    value = data[0x11:0x16]
    return value.decode("ascii", errors="replace").strip()

def main():
    files = sorted(
        p for p in ROOT.rglob("*")
        if p.is_file() and p.suffix.upper() == ".MAG"
    )

    lines = [
        "PRUEBA DE CAMPOS NUMERICOS MAG",
        "=" * 70,
        f"Archivos: {len(files)}",
        "",
        "Se comparan los bytes 0x03-0x06 con el tamaño real.",
        "No se presupone que sean campos de tamaño.",
        ""
    ]

    groups = defaultdict(list)

    for path in files:
        data = path.read_bytes()

        if len(data) < 7:
            continue

        raw = data[3:5]
        little = struct.unpack("<H", raw)[0]
        big = struct.unpack(">H", raw)[0]
        byte5 = data[5]
        byte6 = data[6]

        groups[marker(data)].append({
            "name": path.name,
            "size": len(data),
            "little": little,
            "big": big,
            "byte5": byte5,
            "byte6": byte6,
        })

    for family, items in sorted(groups.items()):
        lines.append(f"FAMILIA: {family!r}")
        lines.append("-" * 70)

        for item in items:
            size = item["size"]
            le = item["little"]
            be = item["big"]

            lines.append(
                f'{item["name"]:16} '
                f'archivo={size:6} '
                f'LE={le:6} '
                f'BE={be:6} '
                f'LE+7={le + 7:6} '
                f'LE+8={le + 8:6} '
                f'LE+16={le + 16:6} '
                f'byte5={item["byte5"]:02X} '
                f'byte6={item["byte6"]:02X}'
            )

        lines.append("")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")

    print(f"Analizados: {len(files)} archivos")
    print(f"Informe: {OUTPUT}")

if __name__ == "__main__":
    main()
