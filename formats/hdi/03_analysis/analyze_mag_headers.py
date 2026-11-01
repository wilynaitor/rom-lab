
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path("extracted/hdi_recursive")
OUTPUT = Path("notes/hdi_mag_header_report.txt")

MARKERS = [
    b"MAKI02",
    b"MPS",
    b"Magd",
]

def printable(data):
    return "".join(
        chr(b) if 32 <= b <= 126 else "."
        for b in data
    )

def main():
    files = sorted(
        p for p in ROOT.rglob("*")
        if p.is_file() and p.suffix.upper() == ".MAG"
    )

    if not files:
        print(f"No se encontraron archivos .MAG en {ROOT}")
        return

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("ANALISIS DE CABECERAS MAG")
    lines.append("=" * 60)
    lines.append(f"Archivos encontrados: {len(files)}")
    lines.append("")

    headers = []
    sizes = []

    for path in files:
        data = path.read_bytes()
        header = data[:64]
        headers.append((path, data, header))
        sizes.append(len(data))

    lines.append("RESUMEN DE TAMAÑOS")
    lines.append("-" * 60)
    lines.append(f"Menor: {min(sizes)} bytes")
    lines.append(f"Mayor: {max(sizes)} bytes")
    lines.append(f"Promedio: {sum(sizes) / len(sizes):.1f} bytes")
    lines.append("")

    lines.append("BYTES MAS REPETIDOS POR POSICION")
    lines.append("-" * 60)

    for offset in range(32):
        values = Counter(
            header[offset]
            for _, _, header in headers
            if len(header) > offset
        )
        common = values.most_common(5)
        formatted = ", ".join(
            f"{value:02X} ({count})"
            for value, count in common
        )
        lines.append(f"Offset {offset:02X}: {formatted}")

    lines.append("")
    lines.append("MARCADORES Y SUS POSICIONES")
    lines.append("-" * 60)

    for path, data, header in headers:
        lines.append(f"\nArchivo: {path.name}")
        lines.append(f"Tamaño: {len(data)} bytes")

        for marker in MARKERS:
            positions = []
            start = 0

            while True:
                pos = data.find(marker, start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1

            if positions:
                lines.append(
                    f"  {marker.decode('ascii')}: "
                    + ", ".join(f"0x{x:X}" for x in positions)
                )

        lines.append("  HEX: " + header.hex(" ").upper())
        lines.append("  ASCII: " + printable(header))

    lines.append("")
    lines.append("ARCHIVOS CON CABECERAS IDENTICAS")
    lines.append("-" * 60)

    groups = defaultdict(list)

    for path, data, header in headers:
        groups[header[:16]].append(path.name)

    for signature, names in sorted(
        groups.items(),
        key=lambda item: (-len(item[1]), item[0])
    ):
        if len(names) > 1:
            lines.append(
                f"{signature.hex(' ').upper()} "
                f"({len(names)} archivos):"
            )
            lines.append("  " + ", ".join(names))

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")

    print(f"Archivos analizados: {len(files)}")
    print(f"Informe guardado en: {OUTPUT}")

if __name__ == "__main__":
    main()
