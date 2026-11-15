# XGBoost + Lasso với log diện tích

Thí nghiệm ngày 15/11/2026 dựa trên ensemble 80% XGBoost và 20% Lasso của Phúc. Mục tiêu là kiểm tra xem `log1p(GrLivArea)` và `log1p(TotalSF)` trong nhánh Lasso có cải thiện RMSE trên log giá hay không. Hai nhánh dùng cấu hình đã lưu trong `baseline_config.json` và trộn dự đoán theo trọng số trên log giá.

Notebook [ensemble_log_area.ipynb](ensemble_log_area.ipynb) dùng fold đã lưu theo `Id` từ hai lần chạy của Phúc. Mỗi fold fit imputer, encoder, scaler và mô hình trên tập huấn luyện. Điều kiện lọc ngoại lệ chỉ áp dụng cho tập huấn luyện của từng fold; cả 1.460 dòng đều có dự đoán validation.

| Fold lấy từ | RMSE OOF gốc | RMSE OOF mới | Số fold giảm lỗi |
|---|---:|---:|---:|
| Ensemble gốc | 0.130066 | 0.128776 | 4/5 |
| Ensemble seed 123 | 0.128204 | 0.126913 | 4/5 |

RMSE OOF được tính một lần trên toàn bộ dự đoán validation. Xem `outputs/metrics.csv` để có điểm từng fold, và `outputs/oof_*.csv` để có dự đoán từng căn. `outputs/submission.csv` chứa 1.459 dòng giá dự đoán; điểm Kaggle chưa được đo.

Mở notebook trong Jupyter hoặc VS Code, chọn kernel có các thư viện bên dưới rồi chọn **Run All**. Cell cuối tạo lại `outputs/submission.csv`.

Môi trường đã chạy: Python 3.14.7, NumPy 2.5.3, pandas 3.0.6, SciPy 1.18.1, scikit-learn 1.9.1, XGBoost 3.4.1.
