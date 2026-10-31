
from pathlib import Path
from collections import Counter, defaultdict
import hashlib
import json

SOURCE_DIR = Path("extracted/hdi_recursive")
REPORT_DIR = Path("notes")

REPORT_PATH = REPORT_DIR / "hdi_file_signatures.txt"
JSON_PATH = REPORT_DIR / "hdi_file_signatures.json"

def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def readable_preview(data):
    return "".join(
        chr(byte) if 32 <= byte <= 126 else "."
        for byte in data
    )

def main():
    if not SOURCE_DIR.exists():
        raise FileNotFoundError(SOURCE_DIR)

    files = sorted(p for p in SOURCE_DIR.rglob("*") if p.is_file())

    results = []
    signatures = defaultdict(list)

    for path in files:
        data = path.read_bytes()
        signature = data[:16].hex(" ").upper()
        relative = path.relative_to(SOURCE_DIR).as_posix()

        record = {
            "path": relative,
            "size": len(data),
            "sha256": sha256_file(path),
            "first_16_bytes": signature,
            "first_32_bytes": data[:32].hex(" ").upper(),
            "ascii_preview": readable_preview(data[:64])
        }

        results.append(record)
        signatures[signature].append(relative)

    document = {
        "source": str(SOURCE_DIR),
        "file_count": len(results),
        "files": results,
        "signature_groups": {
            signature: paths
            for signature, paths in signatures.items()
        }
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    JSON_PATH.write_text(
        json.dumps(document, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    lines = [
        "ANÁLISIS DE FIRMAS DE ARCHIVOS HDI",
        f"Archivos analizados: {len(results)}",
        f"Firmas iniciales distintas: {len(signatures)}",
        "",
        "GRUPOS DE FIRMAS"
    ]

    for signature, paths in sorted(
        signatures.items(),
        key=lambda item: (-len(item[1]), item[0])
    ):
        lines.append("")
        lines.append(f"Firma: {signature or '[vacía]'}")
        lines.append(f"Cantidad: {len(paths)}")

        for name in paths:
            lines.append(f"  {name}")

    lines.append("")
    lines.append("DETALLE POR ARCHIVO")

    for item in results:
        lines.extend([
            "",
            f"Archivo: {item['path']}",
            f"Tamaño: {item['size']} bytes",
            f"SHA-256: {item['sha256']}",
            f"Primeros 16 bytes: {item['first_16_bytes']}",
            f"ASCII: {item['ascii_preview']}"
        ])

    REPORT_PATH.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    print(f"Archivos analizados: {len(results)}")
    print(f"Firmas distintas: {len(signatures)}")
    print(f"Informe: {REPORT_PATH}")
    print(f"JSON: {JSON_PATH}")

if __name__ == "__main__":
    main()
