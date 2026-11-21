Năm thí nghiệm RQ chính được tái dựng từ hiện vật lịch sử, không phải các lần fit mới. E05 giữ riêng A17/B71; E13/E15/E17/E18 đã kiểm tra cùng timestamp, target và cờ cao điểm. E13/E15 lặp A/B, E18 đọc lại RF/baseline từ E17. Không xếp hạng toàn cục giữa các protocol.

### E05 — Hào: A17 và B71 trên bốn mô hình

MLP, A17 → B71: MAE tăng 28.161 và RMSE tăng 25.218 xe/giờ trên 6,086 giờ.

Random Forest, A17 → B71: MAE giảm 1.609 và RMSE giảm 0.378 xe/giờ trên 6,086 giờ.

Gradient Boosting, A17 → B71: MAE tăng 0.671 và RMSE tăng 4.857 xe/giờ trên 6,086 giờ.

Linear Regression, A17 → B71: MAE tăng 0.837 và RMSE tăng 0.156 xe/giờ trên 6,086 giờ.

Chỉ còn metrics làm tròn trong XLSX; không có dự đoán theo giờ để xác minh cohort hoặc tính bootstrap. Snapshot lịch sử khác snapshot hiện tại.

Tái dựng từ hiện vật lịch sử, không huấn luyện lại và không chấm test. Không suy ra nhân quả hoặc kết quả tổng quát chỉ từ một validation.

### E13 — Phúc: RF với nhóm thời tiết dạng số

Random Forest, A12 → numeric16: MAE tăng 0.300 và RMSE tăng 16.272 xe/giờ trên 6,086 giờ.

Random Forest, numeric16 → B27: MAE giảm 2.171 và RMSE giảm 1.728 xe/giờ trên 6,086 giờ.

Random Forest, A12 → B27: MAE giảm 1.871 và RMSE tăng 14.544 xe/giờ trên 6,086 giờ.

A12/B27 trùng dự đoán với E15 trong sai số số học; không đếm là hai lần xác nhận độc lập.

Tái dựng từ hiện vật lịch sử, không huấn luyện lại và không chấm test. Không suy ra nhân quả hoặc kết quả tổng quát chỉ từ một validation.

### E15 — Phúc: RF với nhóm nhãn thời tiết

Random Forest, A12 → labels23: MAE giảm 0.367 và RMSE tăng 5.660 xe/giờ trên 6,086 giờ.

Random Forest, labels23 → B27: MAE giảm 1.504 và RMSE tăng 8.884 xe/giờ trên 6,086 giờ.

Random Forest, A12 → B27: MAE giảm 1.871 và RMSE tăng 14.544 xe/giờ trên 6,086 giờ.

Các dòng A12/B27 được đối chiếu với E13 trước khi nối hai ablation; không dùng như bằng chứng độc lập.

Tái dựng từ hiện vật lịch sử, không huấn luyện lại và không chấm test. Không suy ra nhân quả hoặc kết quả tổng quát chỉ từ một validation.

### E17 — Huy: RF A12/B27 và phân tích cao điểm

Random Forest, A12 → B27: MAE giảm 1.835 và RMSE tăng 14.506 xe/giờ trên 6,086 giờ.

Cùng tham số khai báo với Phúc nhưng dự đoán là run khác; không tráo metrics hoặc slice giữa hai run. has_rain là rain_1h>0 sau xử lý, không phải nhãn Rain.

Tái dựng từ hiện vật lịch sử, không huấn luyện lại và không chấm test. Không suy ra nhân quả hoặc kết quả tổng quát chỉ từ một validation.

### E18 — Huy: XGBoost A12/B27 chọn theo RMSE CV

XGBoost, A12 → B27: MAE giảm 0.917 và RMSE tăng 8.363 xe/giờ trên 6,086 giờ.

RF/baseline đọc lại từ E17, không phải RF chạy mới. Khác mô hình và cách chọn so với ablation RF; không quy chênh lệch cho riêng metric chọn.

Tái dựng từ hiện vật lịch sử, không huấn luyện lại và không chấm test. Không suy ra nhân quả hoặc kết quả tổng quát chỉ từ một validation.
