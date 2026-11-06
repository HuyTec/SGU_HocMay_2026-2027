# Các phiên bản thử nghiệm

Phiên bản mô tả phạm vi nghiên cứu; `EXP_...` là nhật ký của một lần chạy. Các log hiện có và notebook được giữ tại vị trí cũ để tránh đứt đường dẫn. Mỗi phiên bản dẫn tới hiện vật thực tế; không sao chép dữ liệu hoặc notebook. Các thư mục này hiện chỉ chứa tài liệu định hướng; chưa có pipeline Python cho từng phiên bản.

| Phiên bản | Phạm vi | Trạng thái |
| --- | --- | --- |
| [V_1](V_1_time_only/README.md) | Time-only | Đã có thử nghiệm; cần xác nhận chạy lại |
| [V_2](V_2_time_holiday/README.md) | Time + ngày lễ | Kế hoạch |
| [V_3](V_3_time_weather/README.md) | Time + Weather | Kế hoạch |
| [V_4](V_4_time_weather_history/README.md) | Time + Weather + History | Kế hoạch |
| [V_5](V_5_final_evaluation/README.md) | Đánh giá cuối và đóng gói | Kế hoạch |

Khi bắt đầu một phiên bản, cập nhật README tương ứng với đường dẫn notebook, dữ liệu, mốc chia, cấu hình và các ID log thực tế. Khi triển khai pipeline Python, đặt mã của phiên bản trong thư mục tương ứng và ghi rõ cách chạy tại đây; notebook vẫn phục vụ thử nghiệm. Giữ nguyên log cũ; không ghi kết quả dự kiến thành kết quả đã chạy.
