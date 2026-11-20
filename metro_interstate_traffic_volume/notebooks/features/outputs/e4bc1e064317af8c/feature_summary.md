# Đối chứng đặc trưng bằng RF cố định

Protocol: `e4bc1e064317af8c`. Chỉ dùng train; không chấm validation/test.

| Phương án | Số cột | MAE CV ± SD (xe/giờ) | RMSE CV ± SD (xe/giờ) | n giờ chấm |
|---|---:|---:|---:|---:|
| V5_C30 | 30 | 247.926 ± 12.404 | 412.907 ± 44.346 | 16875 |
| V1_A12 | 12 | 288.318 ± 35.452 | 469.686 ± 56.278 | 16875 |
| V3_labels23 | 23 | 290.037 ± 34.118 | 470.752 ± 59.287 | 16875 |
| V4_B27 | 27 | 290.725 ± 29.324 | 473.646 ± 59.539 | 16875 |
| V2_numeric16 | 16 | 291.553 ± 29.059 | 476.419 ± 56.677 | 16875 |

Chọn **V5_C30** theo MAE trung bình fold thấp nhất (247.926 xe/giờ); RMSE dùng đối chiếu và phá hòa.
Cả năm dùng 22,503/28,402 giờ train có đủ lịch sử. n trong bảng là tổng các fold-score không trùng timestamp; mỗi phương án có 3 fold.
SD mô tả biến động giữa các giai đoạn, không phải khoảng tin cậy của chênh lệch. Chưa kiểm định ý nghĩa thống kê và chưa ablation từng cột.
Kết luận chỉ áp dụng cho RF/tham số/cohort này. Dự đoán tuần tự từng giờ được dùng target đã quan sát ở các giờ trước trong fold-score; chưa đại diện dự báo nhiều bước từ một mốc.
Weather cùng giờ được giả định sẵn có. Nhãn lễ theo CSV có thể thiếu; timestamp chưa phân tích DST.

Dữ liệu bàn giao: `selected/e4bc1e064317af8c/train_features_unfitted.csv`, kèm `train_hourly_context.csv` và `selection.json`. Chưa điền thiếu toàn train hoặc fit scaler/encoder; khi tuning phải dùng lại quy tắc xử lý trong `src/feature_experiments.py`.
