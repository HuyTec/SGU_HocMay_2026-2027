
# House Prices — Hướng dẫn làm thí nghiệm

Dự án dự đoán `SalePrice` từ dữ liệu House Prices. Mỗi thành viên làm notebook theo giai đoạn, lưu kết quả từng lần chạy và ghi một dòng vào sổ thí nghiệm chung.

## Mô hình cuối

Mô hình trộn 80% XGBoost đã tối ưu và 20% Lasso dùng `log1p` cho `GrLivArea` và `TotalSF`. RMSE OOF trên log giá đạt 0,12568 ở bộ fold gốc và 0,12410 với seed 123. Xem [notebook thí nghiệm](experiments/2026-11-15_Huy_xgb_tuned_log_area/xgb_tuned_log_area.ipynb).

Chạy từ thư mục gốc dự án:

```powershell
python -m pip install -r final_model/requirements.txt
python final_model/run_model.py train
python final_model/run_model.py predict
```

Lệnh `train` tạo `final_model/ensemble.joblib`. Lệnh `predict` dùng mô hình đã lưu để tạo `final_model/submission.csv`.

## Vai trò các thư mục

| Đường dẫn                        | Chức năng                                                                    |
| ------------------------------------ | ------------------------------------------------------------------------------ |
| `data/raw/`                        | Dữ liệu gốc, file mô tả và mẫu submission. Giữ nguyên các file này. |
| `notebooks/eda/`                   | Notebook khám phá dữ liệu, biểu đồ và nhận xét.                      |
| `notebooks/preprocessing/`         | Notebook thử cách làm sạch, điền thiếu và mã hóa.                    |
| `notebooks/feature/`               | Notebook thử tạo hoặc chọn đặc trưng.                                   |
| `notebooks/experiment/`            | Notebook đánh giá mô hình, phân tích lỗi và tuning.                   |
| `experiments/`                     | Lưu lịch sử từng lần EDA, xử lý dữ liệu, feature và mô hình.       |
| `experiments/experiments_mau.xlsx` | Sổ chung: một dòng cho mỗi lần thí nghiệm.                              |

## Cách thực hiện và lưu một thí nghiệm

1. **Viết notebook** ở đúng thư mục trong `notebooks/`. Ví dụ: thử Ridge trong `notebooks/experiment/`. Ghi câu hỏi, giả thuyết và mốc so sánh.
2. **Thực hiện và nhận xét** trong notebook: ghi dữ liệu, cách xử lý, phương pháp, tham số, cách đánh giá và kết quả. Ghi cả kết quả chưa tốt hoặc thất bại để người khác hiểu quá trình.
3. **Lưu lịch sử:** tạo thư mục riêng theo mẫu `experiments/YYYY-MM-DD_Ten_MoTa/`, ví dụ `experiments/2026-11-11_Huy_Ridge_alpha_V1/`. Nếu trùng tên, thêm phiên bản hoặc giờ để không ghi đè. Lưu notebook, bản HTML và các biểu đồ, file `.txt` hay kết quả liên quan vào đó khi có.
4. **Ghi một dòng** trong `experiments/experiments_mau.xlsx`: ngày, người thực hiện, tên, mô tả, trạng thái, cách đánh giá, kết quả và đường dẫn thư mục. Để trống điều chưa biết; kết quả EDA không bắt buộc có metric.
5. **Chia sẻ thư mục kết quả** để người khác đọc notebook hoặc HTML, đối chiếu kết quả và tiếp tục thí nghiệm.

### Ví dụ lưu notebook và HTML

Lưu notebook trong Jupyter trước. Trong PowerShell mở tại thư mục gốc dự án:

```powershell
$runDir = "experiments/2026-11-11_Huy_Ridge_alpha_V1"
New-Item -ItemType Directory -Path $runDir
Copy-Item "notebooks/experiment/03_ridge_error_analysis.ipynb" "$runDir/03_ridge_error_analysis.ipynb"
jupyter nbconvert --to html "$runDir/03_ridge_error_analysis.ipynb" --output-dir "$runDir"
```

Thay tên, ngày và đường dẫn theo lần chạy. HTML chứa output đã lưu trong notebook; lệnh này không tự chạy lại. Không dùng lại thư mục cũ để ghi đè kết quả.

## Lưu ý khi đánh giá mô hình

Giữ cùng dữ liệu, cách chia và metric khi so sánh công bằng. Những bước tiền xử lý có học từ dữ liệu phải nằm trong pipeline và được fit trên từng phần huấn luyện của CV. Điểm dùng để tuning không phải đánh giá độc lập cuối cùng; `test.csv` không có giá thực tế để tính RMSE.

`experiment_logger.py` là công cụ tùy chọn tạo workbook chi tiết cho một lần chạy; nó **không tự ghi** vào `experiments_mau.xlsx` và không tự lưu notebook hoặc HTML. Ghi sổ chung thủ công sau mỗi lần thí nghiệm. Quy ước chi tiết: [QUY_UOC_THI_NGHIEM.md](experiments/QUY_UOC_THI_NGHIEM.md).
