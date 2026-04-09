# batch-las-to-hag

**[English](#english)** | **[Tiếng Việt](#tiếng-việt)**

📖 **Usage / Hướng dẫn sử dụng:** [English](docs/USAGE_EN.md) | [Tiếng Việt](docs/HUONG_DAN_BATCH_LAS_TO_HAG.md)

Includes two ground filtering tools:

| Tool | Algorithm | Ground filter + HAG | Dependency |
|------|-----------|---------------------|------------|
| `batch_las_to_hag.py` | SMRF | ✅ ground + HAG | PDAL |
| `batch_csf.py` | CSF | ⚠️ ground only (no HAG) | laspy, cloth-simulation-filter |

---

## English

Batch ground filtering and HAG (Height Above Ground) computation for `.las` files.

### batch_las_to_hag.py (SMRF)

Runs PDAL pipeline: SMRF ground classification → HAG Delaunay → write with `HeightAboveGround` extra dim. Output files get `_hag` suffix.

### Quick Start

```bash
# Install PDAL via Miniforge (Windows)
conda create -n pdal_env -c conda-forge python=3.11 python-pdal -y
conda activate pdal_env

# Convert all .las files recursively (for LAS not yet ground-classified)
python batch_las_to_hag.py -i "E:\LasData" -r

# Custom SMRF parameters (for hilly terrain with dense vegetation)
python batch_las_to_hag.py -i "E:\LasData" -r --slope 0.05 --window 30 --threshold 0.45 --scalar 1.1

# Already classified / want to preserve multi-class labels? Skip SMRF
python batch_las_to_hag.py -i "E:\LasData" -r --no-smrf

# Resume after interruption
python batch_las_to_hag.py -i "E:\LasData" -r --skip-existing
```

### Options

| Flag | Description |
|------|-------------|
| `-i`, `--input` | Input directory containing `.las` files |
| `-o`, `--output` | Output directory (default: `{input}_hag` with `-r`) |
| `-r`, `--recursive` | Recursively find `.las` files, mirror directory structure |
| `-b`, `--batch` | Batch file with `input -> output` pairs per line |
| `--skip-existing` | Skip files already converted (non-empty output exists) |
| `--no-smrf` | Skip ground classification and use existing classification (only when input already has valid ground classification) |
| `--slope` | SMRF slope parameter (default: 0.15). Lower = stricter ground detection |
| `--window` | SMRF max window size in meters (default: 18). Larger = smoother terrain model |
| `--threshold` | SMRF elevation threshold (default: 0.5). Height cutoff for ground/non-ground |
| `--scalar` | SMRF elevation scalar (default: 1.25). Scaling factor for morphological threshold |

### PDAL Pipeline

Each file goes through:

1. `readers.las` — read input
2. `filters.smrf` — ground classification *(skipped with `--no-smrf`; by default SMRF assigns ground=2 and non-ground=1)*
3. `filters.hag_delaunay` — compute Height Above Ground from ground points already marked in `Classification`
4. `writers.las` — write output with `HeightAboveGround=float32`

### Requirements

PDAL installed via one of:

1. **Conda** (recommended): `conda install -c conda-forge python-pdal`
2. **PDAL CLI** on PATH: https://pdal.io/en/latest/download.html

Auto-detects Python bindings first, falls back to CLI subprocess.

### batch_csf.py (CSF)

Runs Cloth Simulation Filter for ground classification. Output files get `_csf` suffix. **Does not compute HAG** — only classifies ground (class 2) vs non-ground (class 0).

```bash
pip install laspy cloth-simulation-filter

# Classify ground recursively
python batch_csf.py -i "E:\LasData" -o "E:\LasData_csf" -r

# Custom parameters (mountain terrain)
python batch_csf.py -i "E:\LasData" -o "E:\LasData_csf" -r --cloth-resolution 0.5 --rigidness 1

# Resume
python batch_csf.py -i "E:\LasData" -o "E:\LasData_csf" -r --skip-existing
```

| Flag | Description |
|------|-------------|
| `-i`, `--input` | Input directory containing `.las` files |
| `-o`, `--output` | Output directory for classified `.las` files |
| `-r`, `--recursive` | Recursively find `.las` files |
| `--skip-existing` | Skip files already converted |
| `--cloth-resolution` | Cloth grid resolution (default: 2.0). Smaller = more detail |
| `--rigidness` | Cloth rigidness: 1=mountain, 2=complex, 3=flat (default: 2) |
| `--threshold` | Distance threshold for ground/non-ground (default: 0.5) |
| `--no-slope-smooth` | Disable slope post-processing |

---

## Tiếng Việt

Lọc mặt đất hàng loạt và tính HAG (Height Above Ground) cho file `.las`.

### batch_las_to_hag.py (SMRF)

Chạy pipeline PDAL: phân lớp mặt đất SMRF → tính HAG Delaunay → ghi file với trường `HeightAboveGround`. File đầu ra có đuôi `_hag`.

### Bắt Đầu Nhanh

```bash
# Cài PDAL qua Miniforge (Windows)
conda create -n pdal_env -c conda-forge python=3.11 python-pdal -y
conda activate pdal_env

# Chuyển tất cả file .las đệ quy (cho LAS chưa phân lớp ground)
python batch_las_to_hag.py -i "E:\LasData" -r

# Tuỳ chỉnh tham số SMRF (cho địa hình đồi núi nhiều cây)
python batch_las_to_hag.py -i "E:\LasData" -r --slope 0.05 --window 30 --threshold 0.45 --scalar 1.1

# File đã phân lớp / muốn giữ nguyên multi-class? Bỏ qua SMRF
python batch_las_to_hag.py -i "E:\LasData" -r --no-smrf

# Chạy lại sau khi bị gián đoạn
python batch_las_to_hag.py -i "E:\LasData" -r --skip-existing
```

### Tham Số

| Tham số | Mô tả |
|---------|-------|
| `-i`, `--input` | Thư mục chứa file `.las` đầu vào |
| `-o`, `--output` | Thư mục đầu ra (mặc định: `{input}_hag` khi dùng `-r`) |
| `-r`, `--recursive` | Tìm đệ quy file `.las`, giữ nguyên cấu trúc thư mục |
| `-b`, `--batch` | File batch chứa các cặp `input -> output` mỗi dòng |
| `--skip-existing` | Bỏ qua file đã chuyển (output tồn tại và dung lượng > 0) |
| `--no-smrf` | Bỏ qua phân lớp mặt đất và dùng classification hiện có (chỉ dùng khi file đầu vào đã có ground classification hợp lệ) |
| `--slope` | Tham số slope SMRF (mặc định: 0.15). Thấp hơn = lọc ground chặt hơn |
| `--window` | Kích thước cửa sổ SMRF tính bằng mét (mặc định: 18). Lớn hơn = mô hình địa hình mượt hơn |
| `--threshold` | Ngưỡng độ cao SMRF (mặc định: 0.5). Ngưỡng phân biệt ground/non-ground |
| `--scalar` | Hệ số co giãn SMRF (mặc định: 1.25). Hệ số nhân cho ngưỡng hình thái học |

### Pipeline PDAL

Mỗi file được xử lý qua:

1. `readers.las` — đọc file đầu vào
2. `filters.smrf` — phân lớp mặt đất *(bỏ qua nếu dùng `--no-smrf`; mặc định SMRF gán ground=2 và non-ground=1)*
3. `filters.hag_delaunay` — tính Height Above Ground từ các điểm mặt đất đã được đánh dấu trong `Classification`
4. `writers.las` — ghi file đầu ra với `HeightAboveGround=float32`

### Yêu Cầu

Cài PDAL bằng một trong hai cách:

1. **Conda** (khuyến nghị): `conda install -c conda-forge python-pdal`
2. **PDAL CLI** trên PATH: https://pdal.io/en/latest/download.html

Tool tự phát hiện Python bindings trước, fallback sang CLI.

### batch_csf.py (CSF)

Chạy Cloth Simulation Filter để phân lớp mặt đất. File đầu ra có đuôi `_csf`. **Không tính HAG** — chỉ phân lớp ground (class 2) vs non-ground (class 0).

```bash
pip install laspy cloth-simulation-filter

# Phân lớp đệ quy
python batch_csf.py -i "E:\LasData" -o "E:\LasData_csf" -r

# Tuỳ chỉnh tham số (địa hình đồi núi)
python batch_csf.py -i "E:\LasData" -o "E:\LasData_csf" -r --cloth-resolution 0.5 --rigidness 1

# Chạy lại sau gián đoạn
python batch_csf.py -i "E:\LasData" -o "E:\LasData_csf" -r --skip-existing
```

| Tham số | Mô tả |
|---------|-------|
| `-i`, `--input` | Thư mục chứa file `.las` đầu vào |
| `-o`, `--output` | Thư mục chứa file `.las` đã phân lớp |
| `-r`, `--recursive` | Tìm đệ quy file `.las` |
| `--skip-existing` | Bỏ qua file đã chuyển |
| `--cloth-resolution` | Độ phân giải lưới vải (mặc định: 2.0). Nhỏ hơn = chi tiết hơn |
| `--rigidness` | Độ cứng vải: 1=đồi núi, 2=phức tạp, 3=bằng phẳng (mặc định: 2) |
| `--threshold` | Ngưỡng khoảng cách ground/non-ground (mặc định: 0.5) |
| `--no-slope-smooth` | Tắt slope post-processing |

---

## License

MIT
