# Usage Guide — batch_las_to_hag.py

**[Tiếng Việt](HUONG_DAN_BATCH_LAS_TO_HAG.md)** | English

Batch convert `.las` files to `.las` with **HeightAboveGround** (HAG) field using PDAL.

---

## 1. Install PDAL (required)

On Windows, **do not use `pip install pdal`** (requires Visual Studio, often fails). Use Miniforge:

### 1.1. Install Miniforge (if not installed)

Download at: https://conda-forge.org/miniforge/

Choose: `Miniforge3-Windows-x86_64.exe`

### 1.2. Create PDAL environment

Open **Miniforge Prompt**, run:

```
conda create -n pdal_env -c conda-forge python=3.11 python-pdal -y
```

### 1.3. Activate environment

Must activate before each use:

```
conda activate pdal_env
```

### 1.4. Verify

```
python -c "import pdal; print('PDAL OK')"
pdal --version
```

If both work, you're ready.

The tool auto-detects backend: prefers Python bindings, falls back to PDAL CLI.

---

## 2. Commands

### 2.1. Convert a single directory (non-recursive)

```
python batch_las_to_hag.py -i "E:\LasData" -o "E:\LasData_hag"
```

Converts all `.las` files in `E:\LasData` to `E:\LasData_hag`.

### 2.2. ⭐ Recursive conversion (mirrors directory structure) — RECOMMENDED

```
python batch_las_to_hag.py -i "E:\Data" -r
```

**This is the main usage.** Just point to the root directory, the tool handles everything:

1. Finds all `.las` files in `E:\Data` and subdirectories.
2. Auto-creates output directory `E:\Data_hag` (sibling to input, with `_hag` suffix).
3. Mirrors the subdirectory structure.

Combine with `--skip-existing` and `--no-smrf` as needed:

```
python batch_las_to_hag.py -i "E:\Data" -r --skip-existing --no-smrf
```

### 2.3. Recursive + specify output directory

```
python batch_las_to_hag.py -i "E:\Data" -o "F:\Results_HAG" -r
```

### 2.4. Skip already converted files

```
python batch_las_to_hag.py -i "E:\Data" -r --skip-existing
```

If output file already exists and has size > 0, skip it. Useful when resuming after interruption.

### 2.5. Pre-classified files (skip SMRF)

```
python batch_las_to_hag.py -i "E:\Data" -r --no-smrf
```

If `.las` files **already have ground classification** (e.g. from LiDAR360 or manual classification), add `--no-smrf` to skip ground classification. The tool will use existing classification to compute HAG, giving more accurate results.

### 2.6. Batch processing from file

Create `batch.txt`:

```
E:\Project1\LasData -> E:\Project1\LasData_hag
E:\Project2\LasData -> F:\Results\Project2
```

Run:

```
python batch_las_to_hag.py -b batch.txt --skip-existing
```

Each line is an `input_dir -> output_dir` pair. Empty lines or lines starting with `#` are ignored.

---

## 3. All Options

| Flag | Description |
|------|-------------|
| `-i`, `--input` | Input directory containing `.las` files |
| `-o`, `--output` | Output directory for HAG `.las` files |
| `-r`, `--recursive` | Search subdirectories. Without `-o`, auto-creates `{input}_hag` |
| `-b`, `--batch` | Text file with `input -> output` pairs, one per line |
| `--skip-existing` | Skip output files that already exist (size > 0) |
| `--no-smrf` | Skip ground classification (use when input already has classification) |

---

## 4. PDAL Pipeline Per File

Each `.las` file is processed through these steps (by default):

1. **readers.las**: Read input LAS file.
2. **filters.smrf**: Ground classification. **Skipped if `--no-smrf` is used.**
3. **filters.hag_delaunay**: Compute Height Above Ground using Delaunay triangulation from ground points.
4. **writers.las**: Write output LAS file with extra dimension `HeightAboveGround=float32`.

---

## 5. Example Output

```
PDAL backend: Python bindings

Found 5 .las file(s)
Input:  E:\Data
Output: E:\Data_hag
Mode: recursive (directory structure mirrored)

[1/5] zone1\scan01.las
  OK: scan01.las -> scan01_hag.las (1,234,567 pts, 45.2 MB)
[2/5] zone1\scan02.las
  OK: scan02.las -> scan02_hag.las (987,654 pts, 36.1 MB)
[3/5] zone2\scan03.las
  SKIP (already exists): scan03_hag.las
[4/5] zone2\scan04.las
  OK: scan04.las -> scan04_hag.las (2,345,678 pts, 89.3 MB)
[5/5] zone2\scan05.las
  ERROR: scan05.las: pdal pipeline failed (exit 1): ...

Done in 124.5s: 3 converted, 1 failed, 1 skipped
```
