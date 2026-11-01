
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path("extracted/hdi_recursive")
OUTPUT = Path("notes/hdi_header_analysis.txt")

groups = defaultdict(list)

for path in ROOT.rglob("*"):
    if not path.is_file():
        continue

    data = path.read_bytes()
    if len(data) < 16:
        continue

    if data.startswith(b"LZ\x1a"):
        family = "LZ"
    elif data.startswith(b"MAKI02A"):
        family = "MAKI02A"
    else:
        continue

    groups[family].append((path, data))

lines = []

for family, files in sorted(groups.items()):
    lines.append(f"\n{'=' * 60}")
    lines.append(f"FAMILIA: {family}")
    lines.append(f"ARCHIVOS: {len(files)}")
    lines.append("=" * 60)

    for path, data in sorted(files):
        header = data[:32].hex(" ").upper()
        lines.append(
            f"{path.name} | {len(data)} bytes | {header}"
        )

    # Frecuencia de cada byte por posición
    lines.append("\nVARIACIÓN POR POSICIÓN:")

    for offset in range(32):
        values = Counter(
            data[offset] for _, data in files if len(data) > offset
        )
        common = values.most_common(5)
        formatted = ", ".join(
            f"{value:02X} ({count})" for value, count in common
        )
        lines.append(f"+0x{offset:02X}: {formatted}")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(lines), encoding="utf-8")

print(f"Familias analizadas: {len(groups)}")
for family, files in groups.items():
    print(f"{family}: {len(files)} archivos")
print(f"Informe creado: {OUTPUT}")
