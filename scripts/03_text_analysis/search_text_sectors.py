from pathlib import Path
import re

SOURCE = Path("extracted/disk_a_sectors")

MAX_RESULTADOS_POR_SECTOR = 3
MAX_RESULTADOS_TOTAL = 100
MIN_ASCII = 5

total = 0
sectores_con_coincidencias = 0

for path in sorted(SOURCE.glob("*.bin")):
    data = path.read_bytes()
    resultados_sector = []

    # Buscar secuencias ASCII imprimibles.
    for match in re.finditer(rb"[\x20-\x7E]{5,}", data):
        text = match.group().decode("ascii")
        resultados_sector.append(
            f"{path.name} | offset 0x{match.start():04X} "
            f"| ASCII: {text[:80]}"
        )

        if len(resultados_sector) >= MAX_RESULTADOS_POR_SECTOR:
            break

    if resultados_sector:
        sectores_con_coincidencias += 1

        for resultado in resultados_sector:
            print(resultado)
            total += 1

            if total >= MAX_RESULTADOS_TOTAL:
                print("\nSe alcanzó el límite de resultados.")
                print(f"Resultados mostrados: {total}")
                print(f"Sectores con coincidencias: {sectores_con_coincidencias}")
                raise SystemExit

print("\n--- Resumen ---")
print(f"Resultados mostrados: {total}")
print(f"Sectores con coincidencias: {sectores_con_coincidencias}")
