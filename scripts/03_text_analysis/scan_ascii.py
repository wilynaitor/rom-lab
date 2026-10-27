from pathlib import Path
import re

file = Path("extracted/disk_a_files/KABE4.X")
data = file.read_bytes()

for match in re.finditer(rb"[ -~]{4,}", data):
    print(f"0x{match.start():04X}: {match.group().decode('ascii')}")