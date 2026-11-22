# Kiểm tra OpenWeather cho MnDOT / C30

## Thử One Call — cập nhật 23/11/2026

Đã kiểm tra biến môi trường có tên OpenWeather/OWM/WEATHER_API và các đường dẫn
`.env`, `.env.local`, `app/.env`, `app/.env.local`, `.streamlit/secrets.toml`,
`app/.streamlit/secrets.toml`: chưa tìm thấy key để gọi API. Chưa lấy được mẫu
Minnesota 2018 qua tài khoản; chưa phát sinh yêu cầu có xác thực hoặc thanh toán.

[One Call 4.0](https://openweathermap.org/api/one-call-4) hỗ trợ timeline lịch sử
theo giờ, tối đa 20 bản ghi mỗi trang. Cần API key và subscription One Call riêng;
1.000 lượt gọi/ngày đầu miễn phí. Tài liệu nêu hạn mức tài khoản mặc định sau đăng ký
là 2.000/ngày, vì vậy người dùng nên đặt giới hạn tối đa 1.000 trong Billing plans
nếu chỉ muốn dùng hạn mức miễn phí. Script không thể xác nhận quota còn lại của tài khoản.

Đã chuẩn bị `app/src/demo/probe_openweather.py`: một yêu cầu duy nhất,
không retry/pagination, mặc định điểm khu vực 44.95/−93.15 và 01/11/2018 UTC.
Đây không phải tọa độ weather UCI đã được xác minh. Lưu phản hồi và thống kê
trường dữ liệu trong `data/external/mndot/weather/openweather_probe/`;
xóa các URL phân trang có thể chứa key trước khi lưu. Thiếu mưa/tuyết vẫn để thiếu.

Sau khi thiết lập `OPENWEATHER_API_KEY` trong môi trường cục bộ, chạy từ gốc dự án:

```powershell
& app/.venv/Scripts/python.exe -m app.src.demo.probe_openweather
```

Ngày mặc định chỉ là mẫu kiểm tra truy cập; không đảm bảo có tuyết trong 20 giờ đó.
Chưa ghép dữ liệu, chưa chạy mô hình. Không gửi API key trong chat hoặc commit vào Git.

Ngày kiểm tra: 22/11/2026 (Asia/Saigon). **Kết luận: ứng viên phù hợp về schema; chưa đủ bằng chứng mở khóa C30.**
Không đăng nhập, không đặt mua, không gọi API dùng khóa, không dự đoán/chấm UCI hoặc MnDOT.

## Sản phẩm và quyền truy cập

[History Bulk](https://openweathermap.org/api/history-bulk) công bố dữ liệu giờ từ 1979,
chọn tọa độ/khoảng thời gian, xuất CSV hoặc JSON. Năm 2018 nằm trong phạm vi sản phẩm.
[Trang giá](https://openweathermap.org/price) niêm yết **10 USD/location** tại lúc kiểm tra;
chưa xác minh giá checkout, thuế hoặc điều kiện đơn hàng cụ thể. Quy trình Bulk có thanh toán.
Không suy từ hạn mức miễn phí của One Call sang quyền tải History Bulk.

## Các trường liên quan C30

| OpenWeather | Đầu vào dự án | Kết quả kiểm tra |
|---|---|---|
| main.temp / temp | temp (K) | Cần chọn và lưu đơn vị xuất; đổi về K nếu xuất Celsius |
| rain.1h / rain_1h | rain_1h | mm trong giờ trước; không thay bằng rain.3h |
| snow.1h / snow_1h | snow_1h | Tài liệu ghi mm nước; gần định nghĩa cần dùng hơn snowfall_cm |
| clouds.all / clouds_all | clouds_all | % |
| weather[].main | weather_main | Chuẩn hóa chữ thường, giữ mọi nhãn trong mảng |
| dt, dt_iso, timezone | date_time | Giữ UTC và offset gốc; chưa tự đổi thành giờ naive UCI |

[Bảng weather code](https://openweathermap.org/api/weather-conditions) có đủ 11 nhóm tên đang dùng trong UCI;
cũng có Dust/Sand/Ash/Tornado ngoài C30. Nhãn ngoài tập phải báo lỗi, không xóa ngầm.
Tên nhóm khớp không chứng minh giá trị weather lịch sử khớp UCI.

## Đã tải và kiểm tra mẫu thật

File nằm tại `data/external/mndot/weather/openweather_samples/`.
`sample_manifest.json` giữ URL, kích thước, Content-Type, SHA256 và mục đích.

| Kiểm tra trên mẫu công khai | Kết quả |
|---|---|
| JSON | 48 bản ghi, London (51.507351, −0.127758) |
| Thời gian | 01/07/2020 00:00 → 02/07/2020 23:00 UTC |
| Bước giờ | 47 khoảng liên tiếp, mỗi khoảng 3.600 giây |
| dt so với dt_iso | Khớp UTC trên 48/48 bản ghi |
| CSV | 48 dòng, 25 cột |
| temp / clouds.all / weather | Có trên 48/48 bản ghi JSON |
| Nhãn trong mẫu | Clouds: 22, Rain: 20, Clear: 6 |
| rain.1h | Có trên 2/48 bản ghi; CSV trống 46/48 |
| rain.3h | Có trên 12/48 bản ghi |
| snow.1h | Không có trong JSON; CSV trống 48/48 |
| Riêng 20 giờ nhãn Rain | 2 có rain.1h; 12 có rain.3h; 6 không có trường rain |

Đây là kiểm tra **định dạng và khả năng biểu diễn**, không phải dữ liệu thời tiết tại ATR 301.
Không ghép mẫu London vào demo MnDOT. Mẫu không có tuyết nên chưa kiểm tra được giá trị snow thực tế.

**Vấn đề cần làm rõ:** chỉ từ mẫu này không phân biệt được mọi ô mưa trống là không có mưa,
không có số đo một giờ, hay quy ước xuất khác. Đặc biệt có nhãn Rain mà không có rain.1h.
Không gán tất cả ô trống bằng 0, không chia rain.3h cho 3, không dùng median để che thiếu toàn nguồn.
Chỉ dùng quy tắc điền đã khóa khi đã xác nhận định nghĩa và nguyên nhân thiếu tương thích.

## Quan hệ với UCI và giới hạn

CSV UCI trong dự án có đúng 11 nhóm: Clear, Clouds, Drizzle, Fog, Haze, Mist, Rain, Smoke,
Snow, Squall, Thunderstorm. Đây là đối chiếu trực tiếp từ file gốc.
[Metadata UCI](https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume) nêu trạm traffic ATR 301,
đơn vị và local CST, nhưng chưa đủ để xác định tọa độ và phiên bản sản phẩm weather gốc.
Chưa chứng minh OpenWeather là nguồn/phiên bản chính xác đã tạo weather UCI.

OpenWeather mô tả hệ thống kết hợp quan trắc và mô hình trong [tài liệu công nghệ](https://openweather.co.uk/technology).
Vì vậy không giới thiệu tất cả bản ghi History Bulk là quan trắc trực tiếp tại trạm giao thông.

## Bước cần làm trước khi mua hoặc tích hợp

1. Chốt tọa độ weather có căn cứ. Điểm 44,95/−93,15 hiện có chỉ là điểm khu vực, chưa phải tọa độ weather UCI.
2. Xác nhận nhà cung cấp có rain.1h/snow.1h cho tọa độ đó trong 2018, và giải thích ô trống so với trường 3h.
   Câu hỏi hỗ trợ đề xuất: “For the requested coordinates in 2018, are rain.1h and snow.1h available hourly?
   How should missing 1h fields be interpreted when weather.main is Rain/Snow or only a 3h total is present?”
   Đây là nội dung đề xuất, chưa gửi cho bên nào.
3. Nếu có dữ liệu thật: giữ giai đoạn giao UCI để đối chiếu weather độc lập với traffic prediction;
   giữ 01/10–11/12 để đánh giá ngoài sau khi khóa chuẩn hóa. Đối chiếu thời gian UTC/CST/DST trước khi ghép.
4. Kiểm tra đủ số giờ, nhãn gộp, lượng mưa/tuyết, đơn vị và provenance. Không lựa chọn mapping/tọa độ theo điểm test.
   Ngày lễ vẫn cần xử lý riêng; OpenWeather không tự giải quyết lịch sự kiện UCI.

Trạng thái ứng dụng giữ nguyên: dự đoán MnDOT bị khóa. Chưa tạo adapter hoặc CSV chuẩn hóa từ nguồn chưa xác minh.
