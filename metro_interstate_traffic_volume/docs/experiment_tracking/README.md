# Nhật ký thực nghiệm

Xem [các phiên bản thử nghiệm](../../src/versions/README.md) để đối chiếu phạm vi, trạng thái và các log liên quan.

## Workbook kết quả V1–V4

Cell lưu của V1–V4 ghi kết quả vào `experiments/experiments_logs.xlsx`. Mỗi phiên bản cập nhật các sheet mang tiền tố của mình và các bảng tổng hợp chung. Đặt `SAVE_EXPERIMENT_LOGS=1` để bật nhật ký TXT. Trong V1, `SAVE_EXPERIMENT_RESULTS=1` bật xuất ảnh PNG.

- **Validation** ghi metrics, cấu hình, cột đầu vào và tham số được chọn.
- **Tuning CV**, **Mốc dữ liệu** và **Mốc fold** ghi ứng viên, điểm, mốc chia và số giờ.
- **Dự đoán** lưu lưu lượng thật và dự đoán theo từng giờ. V3 và V4 thêm sheet đối chứng.
- **Hướng dẫn** giải thích cách đọc kết quả và ghi nguồn notebook, mã lần chạy, commit gốc, hash CSV và workbook dùng để đối chứng.
- **Hyper Parameters** ghi giá trị thực tế của từng tham số mô hình sau fit và phân biệt tham số cố định với tham số đã tuning.
- **Evaluation** gom mô hình và baseline thứ–giờ của các phiên bản sẵn sàng. So trực tiếp trong cùng nhóm giờ chấm. Cột Giờ train cho biết số giờ đã fit của từng cấu hình.

Địa điểm đo là **I-94 hướng Tây, trạm MnDOT ATR 301, khu vực Minneapolis–St. Paul, Minnesota, Mỹ**. Mốc dữ liệu và các fold giữ giờ CST như mô tả của [UCI](https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume). Thời điểm ghi workbook và mã lần chạy dùng UTC+7.

Chạy theo thứ tự V2 → V3 → V4. V3 đọc các sheet V2 và V4 đọc các sheet V3 trong file chung. Mỗi phép đối chứng xác nhận mã lần chạy, hash CSV, giờ và mục tiêu trước khi chấm. Sheet **Tổng quan** đánh dấu **Cần chạy lại** khi một phiên bản đối chứng đã được cập nhật.

Workbook `experiment_log_old.xlsx` và các file `EXP_*.txt` hiện có là hiện vật lịch sử.

## Nhật ký TXT

`src/experiment_logger.py` lưu mỗi lần gọi thành một file `EXP_001.txt`,
`EXP_002.txt`... trong thư mục `experiments/`, không ghi đè các lần chạy trước.
[`EXP_TEMPLATE.txt`](EXP_TEMPLATE.txt) là mẫu điền tay, không phải kết quả thực nghiệm.
Ngày mặc định theo UTC+7; có thể truyền `experiment_date="YYYY-MM-DD"`.

## Gọi từ notebook

Chạy sau khi đã có `project_dir`, `time_features`, `train`, `validation`,
`test` và `ridge_metrics` từ lần huấn luyện thực tế:

```python
import sys

if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from src.experiment_logger import save_experiment_log

log_path = save_experiment_log(
    model="Ridge Regression (alpha=1.0)",
    features=time_features,
    results=ridge_metrics,  # {"MAE": ..., "RMSE": ..., "R2": ...}
    observations=[
        "Tập đánh giá: validation",
        f"Train: {len(train)} mẫu; "
        f"{train['date_time'].min()} → {train['date_time'].max()}",
        f"Validation: {len(validation)} mẫu; "
        f"{validation['date_time'].min()} → {validation['date_time'].max()}",
        f"Test: {len(test)} mẫu; "
        f"{test['date_time'].min()} → {test['date_time'].max()}",
        "Bổ sung phiên bản dữ liệu/code và nhận xét từ kết quả thực tế",
    ],
    problems=["Bổ sung giới hạn của lần chạy"],
    next_steps=["So sánh với baseline trung bình theo thứ–giờ"],
)

print("Đã lưu:", log_path)
```

Hàm nhận cả khóa `R2` và `R²`, luôn xuất nhãn `R²` trong file.
Nếu notebook dùng tên `val`, thay `validation` bằng `val` trong ví dụ.
Mặc định tỷ lệ là 70/15/15 và chiến lược là Chronological. Khi thay đổi,
truyền `data_split={"Train": 60, "Validation": 20, "Test": 20}` và
`split_strategy` tương ứng. Tỷ lệ dùng đơn vị phần trăm.

Hàm chỉ ghi nhật ký, không huấn luyện hoặc kiểm tra cách chia dữ liệu.
Ghi rõ tập đánh giá trong Observations vì ba metrics chỉ đại diện cho tập
được dùng để tính chúng. Các mốc chia, phiên bản dữ liệu/code và tham số
cần khớp với lần chạy. Mỗi lần chạy lại cell ghi log sẽ tạo một ID mới.
Có thể dùng `output_dir` để chọn thư mục khác; ID được cấp riêng theo thư mục.

## Các log của V_2–V_4

`EXP_007`–`EXP_027` được ghi từ `V_2.ipynb`, `V_3.ipynb` và `V_4.ipynb`. Các notebook này chỉ ghi log khi đặt biến môi trường `SAVE_EXPERIMENT_LOGS=1` trước khi chạy, nên chạy lại bình thường không tạo log trùng. Sheet `Validation V2-V4` trong `experiment_log.xlsx` tổng hợp các log này. Nếu một thành viên khác ghi log trên nhánh riêng cùng lúc, ID có thể trùng khi gộp; kiểm tra thư mục `experiments/` trước khi ghi.
