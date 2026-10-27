from pathlib import Path

def inspect_file(filename):
    data = Path(filename).read_bytes()

    print(f"Tamaño: {len(data)} bytes")

    for offset in range(0, min(len(data), 256), 16):
        chunk = data[offset:offset + 16]

        hex_data = " ".join(
            f"{byte:02X}" for byte in chunk
        )

        ascii_data = "".join(
            chr(byte) if 32 <= byte < 127 else "."
            for byte in chunk
        )

        print(
            f"{offset:08X}  "
            f"{hex_data:<47}  "
            f"{ascii_data}"
        )

inspect_file("samples/example.bin")