# XGBoost A/B chọn theo RMSE

Thí nghiệm ngày 17/11/2026 của Huy kiểm tra liệu chọn XGBoost theo RMSE có giảm sai số lớn của Config B so với Random Forest B hay không. Notebook dùng cách chia theo thời gian và tiền xử lý theo fold của [V3](../../notebooks/separate/V_3.ipynb). A gồm 12 đặc trưng thời gian và ngày lễ. B thêm 15 đặc trưng thời tiết cùng giờ.

## Thiết kế

- Chia 70/15/15 theo thời gian sau khi gộp dữ liệu theo giờ. A, B và Random Forest đối chứng khớp toàn bộ timestamp và mục tiêu trên 6.086 giờ validation.
- Dùng 3 fold mở rộng trên 28.402 giờ train. Mỗi fold học thống kê điền thiếu từ phần fit. Dùng cùng lưới 12 ứng viên cho mỗi cấu hình và chọn RMSE trung bình thấp nhất. Tổng cộng 72 lượt fit trong CV.
- Fit lại hai mô hình được chọn trên toàn bộ train. Thử nghiệm chấm trên validation và giả định thời tiết cùng giờ có sẵn lúc dự đoán.

| Cấu hình | max_depth | min_child_weight | reg_lambda | RMSE CV | MAE CV |
|---|---:|---:|---:|---:|---:|
| A | 6 | 5 | 15 | 456,81 | 279,97 |
| B | 6 | 10 | 15 | 458,00 | 281,46 |

## Kết quả trên validation

| Mô hình | MAE (xe/giờ) | RMSE (xe/giờ) | R² |
|---|---:|---:|---:|
| Baseline thứ–giờ | 285,03 | 501,41 | 0,9349 |
| Random Forest A | 241,99 | **380,93** | 0,9624 |
| Random Forest B | **240,15** | 395,44 | 0,9595 |
| XGBoost A | 242,35 | 381,04 | 0,9624 |
| XGBoost B | 241,43 | 389,40 | 0,9608 |

- Trong Config B, XGBoost giảm RMSE **6,04 xe/giờ (1,53%)** so với Random Forest, đồng thời MAE tăng **1,28 xe/giờ**. Đây là so sánh giữa hai mô hình, nên chưa tách riêng tác động của tiêu chí tuning.
- Trong XGBoost, B giảm MAE **0,92 xe/giờ** so với A, đồng thời RMSE tăng **8,36 xe/giờ**. Kết quả này sử dụng bộ tham số tốt nhất riêng cho từng cấu hình.
- Ngày 24/08/2017 và 23/11/2017 vẫn có tổng sai số bình phương của B cao hơn A đối với XGBoost. Chênh lệch trong hai ngày đều nhỏ hơn ở Random Forest.

Nếu demo bắt buộc dùng Config B và ưu tiên RMSE, XGBoost B dẫn đầu trong hai mô hình B đã đối chiếu. Nếu được chọn cả cấu hình, Random Forest A đang có RMSE thấp nhất trên validation, gần như ngang XGBoost A.

Mở [notebook đã chạy](XGBoost_AB_RMSE_Huy.ipynb), xem [điểm từng fold](outputs/cv_fold_scores.csv), [điểm validation](outputs/validation_metrics.csv), [dự đoán theo giờ](outputs/validation_predictions.csv), [sai số bình phương theo ngày](outputs/validation_daily_sse.csv) và [biểu đồ](figures/validation_metrics.png). [Cấu hình lần chạy](outputs/run_config.json) ghi mốc dữ liệu, SHA-256, lưới tham số và phiên bản thư viện.
