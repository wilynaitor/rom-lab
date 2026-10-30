from pathlib import Path
import hashlib

source = Path("samples/dark/disk_a.d88")
output = Path("rebuilt/disk_a_test.d88")

if not source.exists():
    raise FileNotFoundError(f"No se encuentra: {source}")

output.parent.mkdir(parents=True, exist_ok=True)
output.write_bytes(source.read_bytes())

original_hash = hashlib.sha256(source.read_bytes()).hexdigest()
copy_hash = hashlib.sha256(output.read_bytes()).hexdigest()

print(f"Original: {source.stat().st_size:,} bytes")
print(f"Copia:    {output.stat().st_size:,} bytes")
print(f"SHA-256 original: {original_hash}")
print(f"SHA-256 copia:    {copy_hash}")
print("RESULTADO:", "OK: copias idénticas" if original_hash == copy_hash else "ERROR")