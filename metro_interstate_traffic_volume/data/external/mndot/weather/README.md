# Thời tiết bổ sung cho MnDOT 2018

Đã tải ngày 22/11/2026 bằng [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api), chọn model ERA5. Đây là dữ liệu tái phân tích theo lưới, không phải một bản sao đã xác minh của nguồn weather trong UCI, cũng không phải bản dự báo đã phát hành trước giờ cần dự đoán.

## File đã có

- `open_meteo_era5_2018_region_raw.json`: phản hồi API gốc.
- `open_meteo_era5_2018_region_hourly.csv`: bảng phẳng theo UTC, giữ tên và đơn vị riêng.
- `request_metadata.json`: URL, hash, tọa độ yêu cầu và ô lưới trả về.
- `quality_checks.json`: số mẫu, khoảng giờ, ô thiếu, mã thời tiết và trạng thái chưa sẵn sàng cho C30.

Phạm vi: 8.304 giờ, từ 01/01/2018 00:00 UTC đến 12/12/2018 23:00 UTC; không có ô thiếu ở năm biến đã yêu cầu. Đủ độ phủ thời gian cho phần lưu lượng mới 01/10–11/12 theo giả định giờ CST cố định UTC−6; điều đó chưa xác nhận giả định timezone của MnDOT là đúng cho mọi ngày.

Vị trí: tọa độ yêu cầu 44,95 / −93,15 là điểm khu vực được chọn gần mô tả trạm, không phải tọa độ khảo sát đã xác minh. API trả ô lưới 45,00 / −93,25. [Báo cáo MnDOT tháng 6/2018 của trạm 301](https://dot.mn.gov/traffic/data/reports/atr/Monthly_PDFs/Jun18/301.pdf) mô tả vị trí ở phía Tây N Victoria St, St Paul. Dùng bộ này để kiểm tra khả năng ghép nguồn mới; không giới thiệu là quan trắc chính xác tại trạm 301.

## Liên hệ với C30

| File mới | Đơn vị | Cột C30 liên quan | Trạng thái |
|---|---|---|---|
| `temperature_2m_c` | °C | `temp_c` | Cùng đơn vị; khác nguồn/độ phân giải |
| `rain_mm` | mm, tổng giờ trước | `rain_1h` | Cần thống nhất mốc giờ của khoảng đo |
| `snowfall_cm` | cm tuyết rơi | `snow_1h` | Chưa tương đương lượng nước; không tự nhân 10 rồi gán |
| `cloud_cover_pct` | % | `clouds_all` | Cùng đơn vị; cần kiểm phân phối trên giai đoạn giao UCI |
| `weather_code_wmo` | mã WMO | 11 cờ weather | Không tương đương trực tiếp nhãn gốc; chưa ánh xạ |

WMO không cung cấp đầy đủ sự phân biệt giữa mọi nhóm `mist`, `haze`, `smoke`, `squall` của cấu hình hiện tại. Không tự gán các cờ không quan sát được thành 0 và gọi dữ liệu tương đương UCI. API ERA5 cũng có giới hạn suy ra một số hiện tượng như giông; cần đọc tài liệu của đúng model.

Nguồn có các trường gần cấu trúc UCI hơn để xem xét là [OpenWeather History Bulk](https://openweathermap.org/api/history-bulk), gồm `rain.1h`, `snow.1h` theo mm nước và `clouds.all`; quyền truy cập và tọa độ weather ban đầu chưa được xác minh, chưa tải nguồn này.

Cập nhật kiểm tra OpenWeather: đã tải **mẫu tài liệu công khai** vào `openweather_samples/`, chưa tải weather ATR301 năm 2018.
Mẫu London có 48 giờ, nhưng 20 giờ nhãn Rain chỉ 2 giờ có rain.1h; 12 giờ có rain.3h và 6 giờ không có trường rain.
Không thể tự coi mọi ô trống là 0 hoặc chia tổng 3h thành lượng 1h.
Xem [báo cáo kiểm tra OpenWeather](../../../../app/docs/openweather_review.md) và manifest hash trong thư mục mẫu.

## NOAA miễn phí · đã tải dữ liệu trạm 2018

Đã tải hai file Global Hourly ISD 2018 từ kho NOAA NODD công khai vào `noaa/`:
KSTP (St Paul Downtown) và KMSP (Minneapolis–St Paul). Mỗi trạm có bản tin phủ 8.760 giờ UTC,
nhưng có nhiều bản tin trong giờ, sentinel và cờ chất lượng; chưa phải bảng giờ C30 chuẩn hóa.
KSTP không có nhóm AJ/AL tuyết; KMSP có độ sâu/tích lũy, chưa tương đương `snow_1h`.
Xem [kết quả kiểm tra NOAA](../../../../app/docs/noaa_review.md),
`noaa/download_manifest.json` và `noaa/inspection_summary.json`.
Không tốn phí, không cần API key; chưa ghép traffic, chưa dự đoán hoặc chấm MnDOT.

## Bước tiếp theo trước khi chấm mô hình

1. Xác minh tọa độ weather cần dùng, quy ước timezone/CST/DST và mốc giờ đo của hai nguồn. Giữ UTC trong dữ liệu gốc, không ghép timestamp naive trước bước này.
2. Đối chiếu weather trên phần giao UCI năm 2018, chỉ báo chênh lệch nguồn và phạm vi. Không dùng sai số traffic để chọn tọa độ hoặc chỉnh ánh xạ trên tập đánh giá mới.
3. Công bố cách xử lý khác biệt về snow và nhãn. Nếu tiếp tục dùng dữ liệu tái phân tích với ánh xạ xấp xỉ, ghi đây là thử nghiệm chuyển nguồn weather, không phải đánh giá C30 với đầu vào hoàn toàn tương đương.
4. Ghép history theo timestamp quá khứ, xử lý nhãn lễ ngoài giai đoạn UCI theo chính sách riêng, rồi nạp checkpoint mô hình và preprocessing đã fit. Hiện chưa dự đoán, chưa tạo MAE/RMSE/R².
