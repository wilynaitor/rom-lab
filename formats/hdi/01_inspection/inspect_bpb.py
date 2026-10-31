
from pathlib import Path

IMAGE = Path("samples/rusty/rusty.hdi")
DATA_OFFSET = 0x1000

data = IMAGE.read_bytes()
boot = data[DATA_OFFSET:DATA_OFFSET + 512]

print("=== BOOT SECTOR HEX DUMP ===")

for offset in range(0, len(boot), 16):
    chunk = boot[offset:offset + 16]

    hex_part = " ".join(f"{b:02X}" for b in chunk)
    ascii_part = "".join(
        chr(b) if 32 <= b <= 126 else "."
        for b in chunk
    )

    print(f"{offset:04X}  {hex_part:<47}  {ascii_part}")

print("\n=== POSSIBLE BPB VALUES ===")

for offset in range(0, 0x100, 2):
    value = int.from_bytes(boot[offset:offset + 2], "little")

    if value in (512, 1024, 2048, 4096):
        print(f"Posible tamaño de sector en 0x{offset:03X}: {value}")
