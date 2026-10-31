
from pathlib import Path
import math

IMAGE = Path("samples/rusty/rusty.hdi")
REPORT = Path("notes/hdi_fat12_validation.txt")
VOLUME_OFFSET = 0x9400

def u16(data, offset):
    return int.from_bytes(data[offset:offset + 2], "little")

def u32(data, offset):
    return int.from_bytes(data[offset:offset + 4], "little")

def fat12_entry(fat, cluster):
    offset = cluster + cluster // 2
    value = fat[offset] | (fat[offset + 1] << 8)

    if cluster & 1:
        return value >> 4
    return value & 0x0FFF

def main():
    data = IMAGE.read_bytes()
    b = VOLUME_OFFSET

    bytes_per_sector = u16(data, b + 11)
    sectors_per_cluster = data[b + 13]
    reserved_sectors = u16(data, b + 14)
    fat_count = data[b + 16]
    root_entries = u16(data, b + 17)
    total_sectors = u16(data, b + 19) or u32(data, b + 32)
    sectors_per_fat = u16(data, b + 22)

    root_sectors = math.ceil(
        root_entries * 32 / bytes_per_sector
    )

    fat_size = sectors_per_fat * bytes_per_sector
    fat1_offset = b + reserved_sectors * bytes_per_sector
    fat2_offset = fat1_offset + fat_size
    root_offset = fat1_offset + fat_count * fat_size
    data_offset = root_offset + root_sectors * bytes_per_sector

    cluster_size = bytes_per_sector * sectors_per_cluster
    data_sectors = (
        total_sectors
        - reserved_sectors
        - fat_count * sectors_per_fat
        - root_sectors
    )
    cluster_count = data_sectors // sectors_per_cluster
    max_cluster = cluster_count + 1
    volume_end = b + total_sectors * bytes_per_sector

    fat1 = data[fat1_offset:fat1_offset + fat_size]
    fat2 = data[fat2_offset:fat2_offset + fat_size]
    fat_equal = fat1 == fat2

    errors = []
    warnings = []
    checked = 0
    directories_skipped = 0
    owners = {}

    for i in range(root_entries):
        pos = root_offset + i * 32
        entry = data[pos:pos + 32]

        if len(entry) < 32 or entry[0] == 0x00:
            break
        if entry[0] == 0xE5:
            continue

        attr = entry[11]

        # Ignorar entradas LFN y etiquetas de volumen.
        if attr == 0x0F or attr & 0x08:
            continue

        name = entry[0:8].decode("ascii", errors="replace").strip()
        ext = entry[8:11].decode("ascii", errors="replace").strip()
        filename = f"{name}.{ext}" if ext else name

        start_cluster = u16(entry, 26)
        file_size = u32(entry, 28)

        if attr & 0x10:
            directories_skipped += 1
            continue

        if file_size == 0:
            if start_cluster not in (0, 1):
                warnings.append(
                    f"{filename}: archivo vacío con clúster inicial {start_cluster}"
                )
            continue

        checked += 1
        needed = math.ceil(file_size / cluster_size)

        if start_cluster < 2 or start_cluster > max_cluster:
            errors.append(
                f"{filename}: clúster inicial fuera de rango ({start_cluster})"
            )
            continue

        chain = []
        visited = set()
        current = start_cluster
        problem = None

        while True:
            if current < 2 or current > max_cluster:
                problem = f"clúster fuera de rango ({current})"
                break

            if current in visited:
                problem = f"ciclo detectado en clúster {current}"
                break

            visited.add(current)
            chain.append(current)

            next_cluster = fat12_entry(fat1, current)

            if next_cluster >= 0xFF8:
                break
            if next_cluster == 0:
                problem = "cadena termina en clúster libre"
                break
            if next_cluster == 1:
                problem = "referencia al clúster reservado 1"
                break
            if next_cluster == 0xFF7:
                problem = "cadena contiene clúster marcado como dañado"
                break
            if 0xFF0 <= next_cluster <= 0xFF6:
                problem = f"referencia a clúster reservado ({next_cluster:#x})"
                break

            current = next_cluster

            if len(chain) > cluster_count:
                problem = "cadena supera el número posible de clústeres"
                break

        if problem:
            errors.append(f"{filename}: {problem}")

        if len(chain) < needed:
            errors.append(
                f"{filename}: cadena corta; necesita {needed}, tiene {len(chain)}"
            )
        elif len(chain) > needed:
            warnings.append(
                f"{filename}: cadena más larga de lo necesario "
                f"({len(chain)} frente a {needed})"
            )

        for cluster in chain:
            owners.setdefault(cluster, []).append(filename)

        # Comprobar que el espacio del archivo cabe en el volumen.
        file_start = data_offset + (start_cluster - 2) * cluster_size
        if file_start + file_size > volume_end:
            errors.append(f"{filename}: datos exceden el límite del volumen")

    shared = {
        cluster: names
        for cluster, names in owners.items()
        if len(names) > 1
    }

    for cluster, names in shared.items():
        warnings.append(
            f"Clúster compartido {cluster}: {', '.join(names)}"
        )

    lines = [
        "VALIDACIÓN FAT12 - HDI",
        "=" * 40,
        f"Imagen: {IMAGE}",
        f"Volumen: {VOLUME_OFFSET:#x}",
        f"Tamaño de clúster: {cluster_size} bytes",
        f"Clústeres de datos: {cluster_count}",
        f"Rango válido: 2 - {max_cluster}",
        f"Copias FAT idénticas: {fat_equal}",
        f"Archivos revisados en raíz: {checked}",
        f"Directorios omitidos: {directories_skipped}",
        f"Errores: {len(errors)}",
        f"Advertencias: {len(warnings)}",
        "",
        "ERRORES",
        "-" * 40,
    ]

    lines.extend(errors if errors else ["Ninguno"])
    lines += ["", "ADVERTENCIAS", "-" * 40]
    lines.extend(warnings if warnings else ["Ninguna"])

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")

    print(f"Reporte guardado en: {REPORT}")

if __name__ == "__main__":
    main()
