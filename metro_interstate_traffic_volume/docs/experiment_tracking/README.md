# Nhật ký thực nghiệm

Xem [các phiên bản thử nghiệm](../../src/versions/README.md) để đối chiếu phạm vi, trạng thái và các log liên quan.

`experiment_log.xlsx` là bảng tổng hợp **ảnh chụp** của lần chạy Time-only
trong notebook `notebooks/experiments/V_1.ipynb`: sheet Validation
ghi kết quả theo mô hình, Tuning CV ghi từng bộ tham số và MAE của ba fold,
Fold thoi gian ghi các mốc chia. Các file `EXP_001.txt`–`EXP_006.txt` chứa
chi tiết do `save_experiment_log` ghi từ lần chạy trước qua script ngoài notebook.
Notebook hiện có các cell gọi trực tiếp logger; đặt `SAVE_EXPERIMENT_LOGS = True`
và chạy cell ghi để tạo log mới sau khi đã chạy các cell mô hình. Mỗi lần ghi tạo
file mới. Excel không tự cập nhật; cần cập nhật riêng sau mỗi lần chạy tiếp theo. Tên notebook trong các log cũ phản ánh tên tại thời điểm ghi và được giữ nguyên.

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
