# Bảng kiểm tra demo

Tạo từ file thật; không huấn luyện, dự đoán hoặc chấm lại UCI.

| Hạng mục | Trạng thái | Bằng chứng/đường dẫn | Ảnh hưởng | Việc cần làm |
| --- | --- | --- | --- | --- |
| Artifact cuối / ba mô hình / C30 / trọng số / hash | Đã có · đã xác minh | notebooks\validation\outputs\final_C30\final_model.joblib | Inference | Đạt |
| Thống kê điền thiếu | Đã có · đã xác minh | artifact.fill_statistics | Chỉ temp và rain theo quy tắc khóa; không điền history | Không fit median trên MnDOT |
| Phạm vi fit | Đã có · đã xác minh | final_fit_plan.json; artifact.train_end; hourly_unfilled.csv | n_fit=28553, đầu=2012-10-09 09:00:00, cuối=2018-01-19 14:00:00 | Không dùng mtime làm ngày huấn luyện |
| Phiên bản thư viện | Đã có · đã xác minh | final_fit_plan.json: versions | {"fit": {"python": "3.14.7", "numpy": "2.5.3", "pandas": "3.0.6", "sklearn": "1.9.1", "xgboost": "3.4.1"}, "runtime": {"python": "3.14.7", "numpy": "2.5.3", "pandas": "3.0.6", "sklearn": "1.9.1", "xgboost": "3.4.1"}} | Đối chiếu môi trường khi triển khai |
| Code tiền xử lý/inference | Đã có · đã xác minh | final_fit_plan.json: code_sha256 | So khớp code lúc fit | Giữ pipeline dùng chung; kiểm tra khác biệt nếu hash đổi |
| load_model | Đã có · đã xác minh | predict.py: (path=WindowsPath('E:/Project/SGU_HocMay_2026-2027/metro_interstate_traffic_volume/notebooks/validation/outputs/interpretation_C30/train_C30_interpretation.joblib')) | bundle | Luôn truyền artifact cuối tường minh |
| prepare_features | Đã có · đã xác minh | predict.py: (hourly, times, bundle) | DataFrame C30 float32 | Giữ toàn bộ context trước khi chọn giờ |
| predict_hours | Đã có · đã xác minh | predict.py: (hourly, times, bundle) | date_time, prediction, status | Giữ toàn bộ context trước khi chọn giờ |
| MnDOT trạm / hướng / tổng làn / giờ 1–24 | Đã có · đã xác minh | data\external\mndot\prepared\atr_2018_manifest.json | {"station_id": 301, "dir_of_travel": 7, "direction": "West", "lane_of_travel": 0, "lane_meaning": "combined lanes by direction; consistent with FHWA code and exact UCI overlap"}; giờ h → h−1; kiểm lại raw: 8160 giờ; giao UCI: 6533/6533 khớp | Kiểm DST và cờ chất lượng ngoài phần giao |
| Weather OpenWeather / schema / provenance | Đã có · đã xác minh | data\external\mndot\weather\openweather_2018\openweather_2018_weather_prepared.csv | 8304 giờ UTC; K, mm/h, %; nhãn C30; cờ zero theo quy ước nguồn | Đã tích hợp xem trước và đối chiếu UCI; chưa chứng nhận cùng nguồn/thời gian |
| time | Đã có · chưa xác minh tương thích | data/external/mndot/weather/README.md; atr_2018_manifest.json | Chưa xác minh CST cố định hay America/Chicago, DST và mốc khoảng đo weather. | Khóa dự đoán MnDOT; xem phương án trong demo_data_contract.md |
| holiday | Chưa có dữ liệu | data/external/mndot/weather/README.md; atr_2018_manifest.json | Chưa có lịch lễ/sự kiện ngoài CSV UCI và chính sách khác biệt được duyệt. | Khóa dự đoán MnDOT; xem phương án trong demo_data_contract.md |
| location | Đã có · chưa xác minh tương thích | data/external/mndot/weather/README.md; atr_2018_manifest.json | OpenWeather ở điểm khu vực 44.951424/−93.147145; chưa xác minh điểm weather gốc UCI. | Khóa dự đoán MnDOT; xem phương án trong demo_data_contract.md |
| Bảng giờ chuẩn hóa MnDOT | Chưa có dữ liệu | data/external/mndot/processed/hourly_demo.csv | Không xuất CSV giả đủ C30 khi weather/time/holiday chưa chốt | Không yêu cầu CSV C30 có sẵn |
| Kết quả test UCI đã lưu | Đã có · đã xác minh | notebooks/validation/outputs/final_C30/test_metrics.csv | Chỉ đọc; không gọi lại quy trình test | Giữ riêng với điểm MnDOT |
| README trạng thái cũ | Đã có · đã xác minh | README.md; data/external/mndot/README.md; app/demo_time_weather.py | Demo B cũ là lịch sử; checkpoint C30 cuối đã tồn tại | Xem app/README.md và báo cáo audit hiện tại |

## MnDOT sau UCI

Mốc cuối UCI: 2018-09-30 23:00:00. OpenWeather: 8304 giờ UTC; app ghép xem trước theo giả định được hiển thị.

| Chỉ tiêu | Số giờ |
| --- | ---: |
| Giờ kỳ vọng | 1728 |
| Có bản ghi | 1608 |
| Vắng bản ghi | 120 |
| Có target hợp lệ | 1608 |
| Đủ history | 1488 |
| Đủ đầu vào sau xử lý | 0 |
| Đủ điều kiện chấm | 0 |

Nhóm thiếu có thể chồng lấn. Đủ history chưa đồng nghĩa đủ đầu vào C30.

Xem [hợp đồng và phương án cần quyết định](demo_data_contract.md).
