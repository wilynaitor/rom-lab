# ROM-LAB

**Laboratorio de inspección, extracción, análisis y preservación de imágenes de disco.**

ROM-LAB es un proyecto de investigación que reúne herramientas en Python para estudiar imágenes de disco antiguas, analizar sistemas de archivos, extraer contenidos y documentar estructuras binarias.

Este README funciona como guía de navegación y manual de uso. Describe la organización del repositorio y el propósito de sus herramientas.

---

## 1. Requisitos

- Windows.
- Python 3.
- PowerShell.
- Visual Studio Code (recomendado).
- ImHex para inspección hexadecimal avanzada (incluido en el directorio portable del proyecto).

Para comprobar Python:

```powershell
python --version
```

Los scripts deben ejecutarse desde la raíz del proyecto, salvo que se indique lo contrario.

---

## 2. Estructura del proyecto

```text
rom-lab/
│
├── formats/
│   ├── d88/
│   │   └── Herramientas específicas para imágenes D88
│   │
│   └── hdi/
│       ├── 01_inspection/
│       ├── 02_extraction/
│       ├── 03_analysis/
│       ├── 04_verification/
│       └── Scripts auxiliares HDI
│
├── scripts/
│   ├── 01_inspection/
│   ├── 02_extraction/
│   ├── 03_text_analysis/
│   ├── 04_pointers/
│   └── 05_dialogue/
│
├── samples/
│   └── Imágenes y archivos de prueba locales
│
├── extracted/
│   └── Resultados de extracción
│
├── rebuilt/
│   └── Imágenes reconstruidas
│
└──  notes/
    └── Informes, manifiestos y documentación
```

### 2.1. Directorio `formats/`

Contiene herramientas específicas para cada formato de imagen de disco.

**`formats/d88/`**

Reúne los scripts destinados a inspeccionar, extraer, validar y reconstruir imágenes D88.

**`formats/hdi/`**

Contiene las herramientas para estudiar imágenes HDI. Sus subcarpetas separan las etapas del trabajo:

| Carpeta | Función |
|---|---|
| `01_inspection/` | Inspección de cabeceras, sectores, directorios y estructuras. |
| `02_extraction/` | Extracción de archivos y directorios. |
| `03_analysis/` | Análisis de firmas y estructuras internas. |
| `04_verification/` | Generación de manifiestos y comprobaciones. |

Algunos scripts auxiliares HDI están directamente en `formats/hdi/`.

### 2.2. Directorio `scripts/`

Contiene herramientas generales de investigación y análisis, organizadas por etapas.

| Carpeta | Función |
|---|---|
| `01_inspection/` | Inspección de sectores, directorios y FAT12. |
| `02_extraction/` | Pruebas de modificación y verificación de sectores. |
| `03_text_analysis/` | Búsqueda de cadenas y análisis de codificaciones. |
| `04_pointers/` | Investigación de punteros y tablas de referencias. |
| `05_dialogue/` | Extracción, lectura y reconstrucción de diálogos. |

### 2.3. Directorios de datos

| Carpeta | Contenido |
|---|---|
| `samples/` | Imágenes y archivos de entrada. |
| `extracted/` | Archivos extraídos de las imágenes. |
| `rebuilt/` | Imágenes reconstruidas o modificadas. |
| `notes/` | Informes y resultados de análisis. |

**Importante:** las imágenes originales y los datos extraídos pueden estar excluidos de Git. No deben añadirse al repositorio sin comprobar antes las reglas de `.gitignore` y los permisos correspondientes.

## 3. Herramientas D88

Los scripts D88 se encuentran directamente en `formats/d88/`.

| Script | Función según su nombre |
|---|---|
| `inspect_d88.py` | Inspección general de una imagen D88. |
| `inspect_d88_sectors.py` | Inspección de sectores. |
| `extract_d88_sectors.py` | Extracción de sectores. |
| `extract_fat12_files_d88.py` | Extracción de archivos FAT12. |
| `validate_d88.py` | Validación de la imagen o su estructura. |
| `copy_d88_test.py` | Prueba de copia de una imagen. |
| `verify_d88_copy.py` | Verificación de una copia. |
| `rebuild_d88.py` | Reconstrucción de una imagen D88. |
| `replace_file_d88.py` | Reemplazo de un archivo dentro de una imagen D88. |

### Orden de trabajo recomendado

1. Inspeccionar la imagen.
2. Examinar los sectores.
3. Validar su estructura.
4. Extraer sectores o archivos.
5. Verificar los resultados.
6. Realizar pruebas de reconstrucción o reemplazo sobre una copia de trabajo.

Los comandos exactos, argumentos y rutas de entrada y salida deben consultarse en cada script antes de ejecutarlo.

---

## 4. Herramientas HDI

### 4.1. Inspección — `01_inspection/`

| Script | Función según su nombre |
|---|---|
| `inspect_hdi.py` | Inspección general de la imagen HDI. |
| `inspect_bpb.py` | Inspección de parámetros BPB. |
| `inspect_fat_root.py` | Inspección de FAT y directorio raíz. |
| `inspect_hdi_blocks.py` | Inspección de bloques. |
| `inspect_hdi_directories.py` | Inspección de directorios. |
| `scan_hdi.py` | Exploración de contenido de la imagen. |

### 4.2. Extracción — `02_extraction/`

| Script | Función según su nombre |
|---|---|
| `extract_fat12_files_hdi.py` | Extracción de archivos FAT12. |
| `extract_hdi_recursive.py` | Extracción recursiva de archivos y directorios. |

### 4.3. Análisis — `03_analysis/`

| Script | Función según su nombre |
|---|---|
| `analyze_file_signatures.py` | Análisis de firmas de archivos. |
| `analyze_hdi_headers.py` | Análisis de cabeceras HDI. |
| `analyze_mag_headers.py` | Análisis de cabeceras MAG. |
| `test_mag_size_fields.py` | Pruebas de interpretación de campos numéricos MAG. |

### 4.4. Verificación — `04_verification/`

| Script | Función según su nombre |
|---|---|
| `create_hdi_manifest.py` | Generación de un manifiesto de archivos HDI. |

### 4.5. Scripts auxiliares HDI

En la raíz de `formats/hdi/` también existen:

- `inspect_hdi.py`
- `check_fat12.py`
- `fat12_layout.py`
- `find_signatures.py`
- `inspect_signatures.py`
- `validate_fat12_chains_hdi.py`

Estos scripts complementan las tareas de inspección y validación. Su relación exacta con los scripts organizados por subcarpetas debe documentarse revisando su código.

---

## 5. Scripts generales

### 5.1. Inspección — `scripts/01_inspection/`

- `inspect.py`
- `inspect_boot_sector.py`
- `inspect_directory_entries.py`
- `inspect_sector_content.py`
- `list_fat12_root.py`
- `summarize_sectors.py`

### 5.2. Extracción y pruebas — `scripts/02_extraction/`

- `inspect_sector_headers.py`
- `test_sector_modification.py`
- `test_sector_write.py`
- `verify_file_sectors.py`
- `verify_replaced_file.py`

### 5.3. Análisis de texto — `scripts/03_text_analysis/`

- `encoding_probe.py`
- `find_strings.py`
- `inspect_game_file.py`
- `scan_ascii.py`
- `scan_encodings.py`
- `scan_sjis.py`
- `scan_text.py`
- `search_text_sectors.py`
- `test_encoding.py`

### 5.4. Análisis de punteros — `scripts/04_pointers/`

- `audit_pointers.py`
- `detect_pointer_table.py`
- `find_pointers.py`
- `map_file_clusters.py`

### 5.5. Diálogos — `scripts/05_dialogue/`

- `create_dialogue.py`
- `extract_json.py`
- `read_dialogue.py`
- `rebuild_dialogue.py`
- `rebuild_from_json.py`
- `verify_rebuild.py`

Estos scripts forman un conjunto de herramientas para investigar y trabajar con estructuras de texto y diálogos. Los formatos de entrada y salida deben documentarse individualmente.

---

## 6. Flujo general de trabajo

El procedimiento de investigación recomendado es:

1. **Preparar:** colocar una copia de trabajo de la imagen en `samples/`.
2. **Inspeccionar:** ejecutar las herramientas correspondientes al formato.
3. **Identificar:** estudiar el sistema de archivos y sus estructuras.
4. **Extraer:** guardar los resultados en `extracted/`.
5. **Analizar:** investigar firmas, codificaciones, punteros y archivos internos.
6. **Verificar:** comparar tamaños, estructuras y hashes cuando corresponda.
7. **Reconstruir:** realizar pruebas sobre copias, guardando los resultados en `rebuilt/`.
8. **Documentar:** guardar informes y resultados en `notes/`.

---

## 7. Resultados documentados

### D88

- Se identificó una estructura FAT12.
- Se extrajeron 167 archivos en una prueba documentada sin errores.
- Se realizaron pruebas de copia y reconstrucción.
- Se verificó una reconstrucción de prueba mediante SHA-256.

### HDI

- Se identificó una estructura FAT12.
- Se validaron las dos copias de la FAT.
- Se extrajeron recursivamente 455 archivos y se crearon 2 directorios en una prueba documentada.
- Se generaron manifiestos e informes.
- Se inició la investigación de las cabeceras MAG.

### MAG

Se observó una cabecera común en 62 archivos, con la firma inicial `4C 5A 1A` y el marcador `MAKI02`.

Se identificaron variantes como `Magd`, `MPS`, `ESEQ` y `PC98`.

La interpretación de algunos campos numéricos y la estructura interna siguen bajo investigación.

---

## 8. Precauciones

- Trabajar siempre sobre copias de las imágenes originales.
- No asumir que una firma identifica por completo un formato.
- No modificar sectores sin conocer sus estructuras y referencias.
- Verificar los resultados después de cada operación.
- Mantener los archivos originales fuera del control de versiones cuando corresponda.
- Documentar las hipótesis como hipótesis, no como hechos confirmados.

---

## 9. Filosofía del proyecto

ROM-LAB busca que cada proceso pueda entenderse, reproducirse y verificarse.

La documentación debe distinguir entre resultados comprobados, interpretaciones provisionales y preguntas todavía abiertas.

**Investigar, documentar y preservar.**