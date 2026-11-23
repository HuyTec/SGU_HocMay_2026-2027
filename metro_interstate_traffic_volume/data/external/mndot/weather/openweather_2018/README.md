# OpenWeather 2018 · weather cho demo MnDOT

Nguồn: [One Call API 4.0](https://openweathermap.org/api/one-call-4).
Điểm người dùng chọn: **44.951424, −93.147145**, khu vực Saint Paul.
Đây chưa phải tọa độ nguồn weather UCI đã được xác minh.

Phạm vi yêu cầu: **01/01/2018 00:00 UTC ≤ t < 13/12/2018 00:00 UTC**.
Ngày 12/12 được giữ làm phần đệm cho giờ địa phương cuối ngày 11/12 của MnDOT.
Không dùng timezone_offset của một phản hồi làm offset cố định cho cả năm.

## Các lớp dữ liệu

- `pages/`: từng phản hồi 20 giờ; bỏ URL next/prev chứa API key.
  Trang cuối có thể vượt phạm vi; CSV chỉ giữ giờ trong khoảng yêu cầu.
- `download_manifest.json`: SHA256 từng trang đã lưu.
- `openweather_2018_hourly.csv`: bảng gốc theo giờ, giữ trường mưa/tuyết vắng mặt
  là ô trống, kèm cờ `*_present`. Nhãn weather giữ dưới dạng mảng JSON.
- `inspection_summary.json`: kiểm tra đầy đủ timestamp và trường dữ liệu.
- `openweather_2018_weather_prepared.csv`: bảng weather chuẩn hóa riêng,
  nhiệt độ Kelvin, mưa/tuyết mm/h, mây %. Chưa ghép traffic.
- `preparation_audit.json`: thống kê giá trị đo/tính trực tiếp, zero theo quy ước
  nhà cung cấp và trường còn thiếu/mâu thuẫn.

## Quy tắc mưa và tuyết

[FAQ chính thức](https://openweathermap.org/faq) mục “Why I do not see some
parameters in the API response?” giải thích các hiện tượng không có mặt trong
phản hồi không xảy ra tại thời điểm đó; chỉ dữ liệu đo hoặc tính toán mới được trả.
Bản chuẩn hóa dùng 0 cho trường vắng mặt khi không có nhãn/code tương ứng mâu thuẫn.
Cờ `zero_by_provider_omission_rule` phân biệt với `api_1h`.
Nếu có nhãn mưa/tuyết tương ứng nhưng thiếu lượng, object rỗng/null hoặc chỉ có
khoảng tích lũy khác, giữ thiếu với cờ `unresolved_missing_or_conflict`.
Không chia lượng 3h cho 3 hoặc suy tuyết từ độ dày phủ mặt đất.

## Tái tạo

Chạy từ gốc dự án, key chỉ đặt trong môi trường tiến trình:

```powershell
& app/.venv/Scripts/python.exe -m app.src.demo.download_openweather
& app/.venv/Scripts/python.exe -m app.src.demo.prepare_openweather
```

Downloader tiếp tục từ trang đã lưu, tối đa 416 yêu cầu trong phạm vi cố định,
không retry tự động khi lỗi; không fit, chấm mô hình hoặc thay weather UCI.
Để dùng với mô hình cần khóa chính sách UTC/CST/DST, holiday và kiểm tra sai khác
weather với UCI trên giai đoạn chồng lấp. Hoàn tất tải weather không tự xác nhận
khả năng dự báo thực tế: weather lịch sử quan sát/tái phân tích có thể chưa sẵn
có tại thời điểm phải đưa ra dự đoán.
