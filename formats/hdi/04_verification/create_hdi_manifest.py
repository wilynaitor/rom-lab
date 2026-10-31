
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone
from collections import Counter

SOURCE_DIR = Path("extracted/hdi_recursive")
OUTPUT_DIR = Path("notes")

MANIFEST_PATH = OUTPUT_DIR / "hdi_manifest.json"
REPORT_PATH = OUTPUT_DIR / "hdi_manifest_report.txt"


def sha256_file(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest()


def main():
    if not SOURCE_DIR.exists():
        raise FileNotFoundError(
            f"No existe la carpeta: {SOURCE_DIR}"
        )

    files = sorted(
        path for path in SOURCE_DIR.rglob("*")
        if path.is_file()
    )

    manifest = []
    extensions = Counter()
    total_size = 0

    for path in files:
        relative_path = path.relative_to(SOURCE_DIR).as_posix()
        size = path.stat().st_size
        digest = sha256_file(path)

        extension = path.suffix.lower() or "[sin extensión]"
        extensions[extension] += 1
        total_size += size

        manifest.append({
            "path": relative_path,
            "size": size,
            "sha256": digest
        })

    document = {
        "source": str(SOURCE_DIR),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "file_count": len(manifest),
        "total_size": total_size,
        "algorithm": "SHA-256",
        "files": manifest
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    MANIFEST_PATH.write_text(
        json.dumps(document, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    lines = [
        "MANIFIESTO DE EXTRACCIÓN HDI",
        f"Carpeta: {SOURCE_DIR}",
        f"Fecha UTC: {document['created_utc']}",
        "Algoritmo: SHA-256",
        "",
        f"Archivos registrados: {len(manifest)}",
        f"Tamaño total: {total_size:,} bytes",
        "",
        "ARCHIVOS POR EXTENSIÓN"
    ]

    for extension, count in sorted(extensions.items()):
        lines.append(f"{extension}: {count}")

    lines.extend([
        "",
        f"Manifiesto JSON: {MANIFEST_PATH}"
    ])

    REPORT_PATH.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    print("Manifiesto creado correctamente.")
    print(f"Archivos: {len(manifest)}")
    print(f"Tamaño total: {total_size:,} bytes")
    print(f"JSON: {MANIFEST_PATH}")
    print(f"Informe: {REPORT_PATH}")


if __name__ == "__main__":
    main()
