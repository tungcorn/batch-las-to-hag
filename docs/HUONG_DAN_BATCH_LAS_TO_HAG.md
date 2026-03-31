# Hướng Dẫn Chạy batch_las_to_hag.py

Chuyển hàng loạt file `.las` thành file `.las` có thêm trường **HeightAboveGround** (HAG) bằng PDAL.

---

## 1. Cài Đặt PDAL (bắt buộc)

Trên Windows, **không dùng `pip install pdal`** (cần Visual Studio, hay lỗi). Dùng Miniforge:

### 1.1. Cài Miniforge (nếu chưa có)

Tải tại: https://conda-forge.org/miniforge/

Chọn file: `Miniforge3-Windows-x86_64.exe`

### 1.2. Tạo môi trường PDAL

Mở **Miniforge Prompt**, chạy:

```
conda create -n pdal_env -c conda-forge python=3.11 python-pdal -y
```

### 1.3. Kích hoạt môi trường

Mỗi lần chạy tool đều phải kích hoạt trước:

```
conda activate pdal_env
```

### 1.4. Kiểm tra

```
python -c "import pdal; print('PDAL OK')"
pdal --version
```

Nếu cả hai đều chạy được thì đã sẵn sàng.

Tool tự phát hiện backend: ưu tiên Python bindings, fallback sang PDAL CLI.

---

## 2. Các Lệnh Chạy

### 2.1. Chuyển 1 thư mục (không đệ quy)

```
python batch_las_to_hag.py -i "E:\LasData" -o "E:\LasData_hag"
```

Chuyển tất cả file `.las` trong `E:\LasData` sang `E:\LasData_hag`.

### 2.2. ⭐ Chuyển đệ quy (giữ cấu trúc thư mục) — KHUYẾN NGHỊ

```
python batch_las_to_hag.py -i "E:\DuLieu" -r
```

**Đây là cách dùng chính.** Chỉ cần trỏ vào thư mục gốc, tool tự xử lý toàn bộ:

1. Tìm tất cả file `.las` trong `E:\DuLieu` và các thư mục con.
2. Tự tạo thư mục output `E:\DuLieu_hag` (cùng cấp với input, thêm hậu tố `_hag`).
3. Giữ nguyên cấu trúc thư mục con bên trong.

Kết hợp thêm `--skip-existing` và `--no-smrf` nếu cần:

```
python batch_las_to_hag.py -i "E:\DuLieu" -r --skip-existing --no-smrf
```

### 2.3. Đệ quy + chỉ định thư mục output

```
python batch_las_to_hag.py -i "E:\DuLieu" -o "F:\KetQua_HAG" -r
```

### 2.4. Bỏ qua file đã chuyển

```
python batch_las_to_hag.py -i "E:\DuLieu" -r --skip-existing
```

Nếu file output đã tồn tại và có dung lượng > 0 thì bỏ qua, không chuyển lại. Hữu ích khi chạy lại sau khi bị gián đoạn.

### 2.5. File đã phân lớp mặt đất (bỏ qua SMRF)

```
python batch_las_to_hag.py -i "E:\DuLieu" -r --no-smrf
```

Nếu file `.las` **đã có classification ground** (ví dụ từ LiDAR360 hoặc phân lớp thủ công), thêm `--no-smrf` để bỏ qua bước phân lớp mặt đất. Tool sẽ dùng classification có sẵn để tính HAG, kết quả chính xác hơn.

### 2.6. Chạy hàng loạt từ file batch

Tạo file `batch.txt`:

```
E:\DuAn1\LasData -> E:\DuAn1\LasData_hag
E:\DuAn2\LasData -> F:\KetQua\DuAn2
```

Chạy:

```
python batch_las_to_hag.py -b batch.txt --skip-existing
```

Mỗi dòng là 1 cặp `thư_mục_input -> thư_mục_output`. Dòng trống hoặc bắt đầu bằng `#` sẽ bị bỏ qua.

---

## 3. Tham Số Đầy Đủ

| Tham số | Mô tả |
|---------|-------|
| `-i`, `--input` | Thư mục chứa file `.las` đầu vào |
| `-o`, `--output` | Thư mục chứa file `.las` HAG đầu ra |
| `-r`, `--recursive` | Tìm đệ quy trong thư mục con. Nếu không có `-o`, tự tạo `{input}_hag` |
| `-b`, `--batch` | File text chứa các cặp `input -> output`, mỗi dòng 1 cặp |
| `--skip-existing` | Bỏ qua file output đã tồn tại (dung lượng > 0) |
| `--no-smrf` | Bỏ qua phân lớp mặt đất (dùng khi file đã có classification sẵn) |

---

## 4. Pipeline PDAL Mỗi File

Mỗi file `.las` được xử lý qua các bước (mặc định):

1. **readers.las**: Đọc file LAS đầu vào.
2. **filters.smrf**: Phân lớp mặt đất (ground classification). **Bỏ qua nếu dùng `--no-smrf`.**
3. **filters.hag_delaunay**: Tính Height Above Ground dựa trên tam giác Delaunay từ điểm mặt đất.
4. **writers.las**: Ghi file LAS đầu ra với trường bổ sung `HeightAboveGround=float32`.

---

## 5. Ví Dụ Output

```
PDAL backend: Python bindings

Found 5 .las file(s)
Input:  E:\DuLieu
Output: E:\DuLieu_hag
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
