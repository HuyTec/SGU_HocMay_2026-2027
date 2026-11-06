# Các phiên bản thử nghiệm

Phiên bản mô tả phạm vi nghiên cứu; `EXP_...` là nhật ký của một lần chạy. Các log hiện có và notebook được giữ tại vị trí cũ để tránh đứt đường dẫn. Mỗi phiên bản dẫn tới hiện vật thực tế; không sao chép dữ liệu hoặc notebook. Các thư mục này chứa tài liệu định hướng; mã dùng chung nằm trong `src/data.py`, `src/features.py`, `src/models.py`, `src/evaluation.py`.

| Phiên bản | Phạm vi | Trạng thái |
| --- | --- | --- |
| [V_1](V_1_time_only/README.md) | Time-only | Đã chạy lại; kết quả trùng output đã lưu |
| [V_2](V_2_time_holiday/README.md) | Time + ngày lễ | Đã có thí nghiệm validation (EXP_007–EXP_015) |
| [V_3](V_3_time_weather/README.md) | Time + Weather | Đã có thí nghiệm validation (EXP_016–EXP_018) |
| [V_4](V_4_time_weather_history/README.md) | Time + Weather + History | Đã có thí nghiệm validation (EXP_019–EXP_027) |
| [V_5](V_5_final_evaluation/README.md) | Đánh giá cuối và đóng gói | Kế hoạch |

Khi bắt đầu một phiên bản, cập nhật README tương ứng với đường dẫn notebook, dữ liệu, mốc chia, cấu hình và các ID log thực tế. Khi triển khai pipeline Python, đặt mã của phiên bản trong thư mục tương ứng và ghi rõ cách chạy tại đây; notebook vẫn phục vụ thử nghiệm. Giữ nguyên log cũ; không ghi kết quả dự kiến thành kết quả đã chạy.
