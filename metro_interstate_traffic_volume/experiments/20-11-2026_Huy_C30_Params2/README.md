# Hai thí nghiệm C30 với tham số cố định

- `../20-11-2026_Huy_C30_Params2/fit_validation_C30.ipynb`: snapshot best_params hiện tại của tuning C30.
- `../20-11-2026_Huy_C30_Params1/fit_validation_C30.ipynb`: bộ tham số được người dùng trích từ Claude. RF 100 cây và XGBoost 400 cây được tái dựng theo factory cũ; chưa có summary_row.json gốc để xác minh toàn bộ.

Cả hai cùng 22.503 giờ train và 6.050 giờ validation đủ history, 30 cột C30, seed 42 và cùng prepare_fold. Thống kê điền thiếu chỉ học từ train. Đã đối chiếu hash cohort, ma trận và tiền xử lý giữa hai lượt. Mỗi mô hình fit một lần, không chạy tìm kiếm tham số. Ensemble cố định 50/50; baseline chỉ học trên train.

Validation được chấm tuần tự, dùng lưu lượng đã quan sát ở quá khứ validation và giả định thời tiết cùng giờ sẵn có. Validation đã được xem trước các lượt này; đây là thực nghiệm bổ sung, không phải kiểm chứng độc lập. Chưa chấm test. Hai bộ thay đổi nhiều tham số đồng thời nên không suy ra tác động riêng của mỗi tham số.

## Kết quả validation (MAE/RMSE: xe/giờ)

| parameter_set | model | n | MAE | RMSE | R2 |
|---|---|---|---|---|---|
| Tham số hiện tại | Ensemble RF + XGBoost (50/50) | 6050 | 197.228907 | 322.497349 | 0.973048 |
| Tham số hiện tại | Random Forest | 6050 | 200.043773 | 334.530674 | 0.970999 |
| Tham số hiện tại | XGBoost | 6050 | 201.846339 | 322.440935 | 0.973058 |
| Tham số hiện tại | Baseline thứ–giờ | 6050 | 291.738825 | 503.218512 | 0.934378 |
| Tham số hiện tại | Baseline seasonal naive | 6050 | 330.177521 | 635.073473 | 0.895484 |
| Tham số Claude | Ensemble RF + XGBoost (50/50) | 6050 | 193.810221 | 316.084757 | 0.974109 |
| Tham số Claude | Random Forest | 6050 | 196.774807 | 326.772512 | 0.972329 |
| Tham số Claude | XGBoost | 6050 | 197.031359 | 313.639677 | 0.974508 |
| Tham số Claude | Baseline thứ–giờ | 6050 | 291.738825 | 503.218512 | 0.934378 |
| Tham số Claude | Baseline seasonal naive | 6050 | 330.177521 | 635.073473 | 0.895484 |

Mỗi outputs/ lưu validation_metrics.csv, validation_predictions.csv, split_manifest.csv, run_config.json, assessment.md và validation_mae.png. comparison_validation.csv tổng hợp hai lượt. Không sao chép lại dataset và không ghi đè tuning/validation gốc.

Notebook đã được chạy đủ các cell theo thứ tự trong tiến trình IPython mới cho từng file; execution count và đầu ra được lưu. Chưa xác minh thao tác Restart & Run All trong giao diện Jupyter.
