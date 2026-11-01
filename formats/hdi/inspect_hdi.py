
from pathlib import Path
import struct

IMAGE = Path("samples/rusty/rusty.hdi")
data = IMAGE.read_bytes()

DATA_OFFSET = 0x1000
boot_sector = data[DATA_OFFSET:DATA_OFFSET + 512]

print("=== HDI RAW HEADER INSPECTOR ===")
print(f"Archivo: {IMAGE}")
print(f"Tamaño: {len(data):,} bytes")

print("\n=== VALORES UINT32 (LITTLE-ENDIAN) ===")

for offset in range(0, 0x80, 4):
    value = struct.unpack_from("<I", data, offset)[0]
    print(f"0x{offset:02X}: {value:12,}  (0x{value:08X})")

print("\n=== HEX DUMP ===")

for offset in range(0, 0x80, 16):
    chunk = data[offset:offset + 16]
    hex_data = " ".join(f"{b:02X}" for b in chunk)
    print(f"{offset:04X}: {hex_data}")


print("\n=== HDI DATA INSPECTOR ===")

for offset in (DATA_OFFSET, DATA_OFFSET + 0x1F0, DATA_OFFSET + 0x200):
    chunk = data[offset:offset + 64]

    print(f"\nOffset absoluto: 0x{offset:X}")
    print(" ".join(f"{b:02X}" for b in chunk))

# Posible firma de tabla de particiones MBR
signature_offset = DATA_OFFSET + 510

print("\n=== MBR SIGNATURE CHECK ===")
print("Bytes:", data[signature_offset:signature_offset + 2].hex(" "))
print("Firma 55 AA:", data[signature_offset:signature_offset + 2] == b"\x55\xAA")

print("\n=== BOOT SECTOR ASCII ===")

for i in range(0, len(boot_sector), 16):
    chunk = boot_sector[i:i + 16]
    ascii_text = "".join(
        chr(b) if 32 <= b <= 126 else "."
        for b in chunk
    )
    print(f"{i:04X}: {ascii_text}")

print("\n=== POSIBLES FIRMAS ===")