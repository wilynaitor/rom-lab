
from pathlib import Path
import hashlib

# Disco original y archivo de prueba
source = Path("samples/dark/disk_a.d88")
output = Path("rebuilt/disk_a_rebuild_test.d88")

if not source.exists():
    raise FileNotFoundError(f"No se encuentra el disco: {source}")

# Por ahora, copiamos el disco completo como prueba de integridad.
# Todavía NO reconstruye las pistas a partir de los sectores extraídos.
output.parent.mkdir(parents=True, exist_ok=True)
output.write_bytes(source.read_bytes())

original_hash = hashlib.sha256(source.read_bytes()).hexdigest()
rebuilt_hash = hashlib.sha256(output.read_bytes()).hexdigest()

print(f"Original:  {source.stat().st_size:,} bytes")
print(f"Resultado: {output.stat().st_size:,} bytes")
print(f"SHA-256 original:  {original_hash}")
print(f"SHA-256 resultado: {rebuilt_hash}")

if original_hash == rebuilt_hash:
    print("OK: copia idéntica al original.")
else:
    print("ERROR: los archivos son diferentes.")
