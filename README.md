# batch-las-to-hag

**[English](#english)** | **[Tiếng Việt](#tiếng-việt)**

📖 **Usage / Hướng dẫn sử dụng:** [English](docs/USAGE_EN.md) | [Tiếng Việt](docs/HUONG_DAN_BATCH_LAS_TO_HAG.md)

---

## English

Batch convert `.las` files to HAG (Height Above Ground) `.las` using PDAL.

Recursively scans input directory, mirrors folder structure to output, and runs PDAL pipeline (SMRF ground classification → HAG Delaunay → write with `HeightAboveGround` extra dim) on each file. Output files get `_hag` suffix (e.g. `scan01.las` → `scan01_hag.las`).

### Quick Start

```bash
# Install PDAL via Miniforge (Windows)
conda create -n pdal_env -c conda-forge python=3.11 python-pdal -y
conda activate pdal_env

# Convert all .las files recursively (for LAS not yet ground-classified)
python batch_las_to_hag.py -i "E:\LasData" -r

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

---

## Tiếng Việt

Chuyển hàng loạt file `.las` thành file HAG (Height Above Ground) `.las` bằng PDAL.

Quét đệ quy thư mục đầu vào, tạo thư mục đầu ra với cấu trúc giống hệt, chạy pipeline PDAL (phân lớp mặt đất SMRF → tính HAG Delaunay → ghi file với trường `HeightAboveGround`) cho từng file. File đầu ra có đuôi `_hag` (ví dụ `scan01.las` → `scan01_hag.las`).

### Bắt Đầu Nhanh

```bash
# Cài PDAL qua Miniforge (Windows)
conda create -n pdal_env -c conda-forge python=3.11 python-pdal -y
conda activate pdal_env

# Chuyển tất cả file .las đệ quy (cho LAS chưa phân lớp ground)
python batch_las_to_hag.py -i "E:\LasData" -r

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

---

## License

MIT
