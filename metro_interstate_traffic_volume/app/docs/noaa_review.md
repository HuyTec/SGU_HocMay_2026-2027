# Kiểm tra NOAA miễn phí cho C30

Ngày kiểm tra: 22/11/2026 (Asia/Saigon). Mục tiêu: khảo sát thời tiết 2018 gần vùng ATR301,
không huấn luyện, ghép thời gian theo giả định hoặc chấm mô hình.

## Nguồn và cách truy cập

[NOAA Global Hourly / ISD](https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database)
là kho quan trắc có kiểm tra chất lượng. [Thông báo chuyển dịch vụ của NOAA](https://www.nesdis.noaa.gov/news/service-location-change-integrated-surface-data-global-hourly)
chỉ rõ đường tải CSV công khai từ `noaa-global-hourly-pds.s3.amazonaws.com`.
ISD là nguồn lưu trữ lịch sử; NOAA khuyến nghị GHCNh cho dữ liệu hiện hành.
Các lần tải ở đây không cần API key, tài khoản hoặc thanh toán.

Đã tải danh mục trạm `isd-history.csv`, lọc trạm có thời gian hoạt động giao năm 2018,
tính khoảng cách Haversine đến **điểm khu vực** 44,95/−93,15. Điểm này chưa phải tọa độ khảo sát ATR301;
khoảng cách không được giới thiệu là khoảng cách chính xác từ trạm giao thông.

| Trạm ứng viên | Mã file NOAA | Vị trí theo danh mục | Khoảng cách đến điểm khu vực |
|---|---|---|---:|
| St Paul Downtown / Holman Field (KSTP) | 72658414927 | 44,932 / −93,056 | 7,66 km |
| Minneapolis–St Paul International (KMSP) | 72658014922 | 44,885 / −93,231 | 9,64 km |

Đây là hai trạm gần nhất trong danh mục đã lọc, không chọn theo sai số dự đoán traffic.
Danh sách tám trạm gần nhất: `data/external/mndot/weather/noaa/nearby_stations_2018.csv`.
File đã chọn là **Global Hourly ISD CSV**, không phải LCD; không áp dụng đơn vị/quy ước LCD v1/v2 lên file này.

## Đối chiếu sơ bộ với C30

Theo [đặc tả ISD](https://www.ncei.noaa.gov/pub/data/noaa/isd-format-document.pdf):

| Nhóm NOAA | Liên quan C30 | Điều cần xử lý |
|---|---|---|
| TMP | temp | Số mã hóa phần mười °C và QC; đổi đơn vị sau loại sentinel |
| AA1–AA4 | rain_1h | Có chu kỳ tích lũy, lượng và QC; chỉ chu kỳ 01 giờ chưa đủ chứng minh tương đương mưa UCI |
| GA/GD/GF | clouds_all | Cấu trúc lớp mây/độ che phủ, chưa có mapping phần trăm được khóa |
| AW/AU/MW | weather_main | Mã hiện tượng, phải xử lý đa nhãn và trường vắng; chưa có mapping 11 nhóm được duyệt |
| AJ/AL nếu có | snow_1h | Độ sâu/tuyết tích lũy không tự tương đương lượng nước tuyết rơi trong giờ |
| DATE | date_time | Giữ UTC gốc; không tự làm tròn/gộp báo cáo vào đầu giờ |

Trong đoạn đầu KSTP tải riêng, bản tin ghi `00:53`, `01:53`, ...; vì vậy việc chọn báo cáo
và gắn nó vào giờ traffic cần được quyết định rõ. Không gán quan sát ở t+53 phút làm đầu vào biết trước tại đầu giờ t.
Nguồn weather tại sân bay cũng không đồng nhất vị trí với weather UCI hoặc cảm biến traffic.

## File và kết quả kiểm tra

Các file gốc, manifest SHA256, bản xem trước và kết quả kiểm tra được lưu riêng tại
`data/external/mndot/weather/noaa/`. Script kiểm tra:

```powershell
app/.venv/Scripts/python.exe -X utf8 -m app.src.demo.inspect_noaa
```

Script không tạo C30; số giờ trong báo cáo chỉ là **bucket UTC có ít nhất một bản tin**, không phải
số giờ đã ghép hoặc đủ điều kiện inference. Giữ mọi bản tin trùng giờ, không tự lấy trung bình/bỏ bản tin.
Đếm field trước QC không được gọi là số quan sát đã xác minh hợp lệ.

### Kết quả đọc toàn bộ hai file 2018

| Chỉ tiêu | KSTP | KMSP |
|---|---:|---:|
| Dung lượng gốc (byte) | 6.648.186 | 8.157.522 |
| Tổng số bản tin, gồm cả bản tin tổng hợp ngày/tháng | 11.740 | 13.206 |
| Bucket UTC có ít nhất một bản tin / 8.760 giờ lịch | 8.760 | 8.760 |
| Dòng trùng timestamp vượt quá dòng đầu | 14 | 98 |
| Bucket giờ chứa nhiều bản tin | 1.679 | 2.927 |
| Bản tin không đúng đầu giờ | 11.650 | 11.643 |
| Bucket có trường AA1 chu kỳ 01h và lượng không phải sentinel, trước QC | 8.760 | 8.258 |
| Bucket AA1 chu kỳ 01h, QC 1/5 và condition 9/2 | 8.752 | 8.209 |
| Trường GF1 hiện diện, chưa giải mã sentinel/QC bên trong | 10.858 | 12.310 |
| Trường AJ1 độ sâu tuyết | Không có cột | Có trên 1.355 bản tin |
| Trường AL1 tích lũy tuyết | Không có cột | Có trên 118 bản tin |

Mẫu số của các chỉ tiêu dạng bucket là 8.760 giờ lịch UTC năm 2018; một giờ có thể chứa nhiều bản tin.
Chỉ tiêu QC trên là **phép sàng lọc chẩn đoán**, chưa phải chính sách chuẩn hóa đã được duyệt.
Trace được giữ trạng thái riêng trong dữ liệu gốc, không quy thành 0; condition 3 (bắt đầu chu kỳ tích lũy)
không được tính trong phép sàng lọc này dù phần lượng có thể mang số mã hóa.
Không cộng trường AA1/AA2/AA3 vì có các khoảng tích lũy khác nhau, có thể chồng lấn.

Khoảng khảo sát `2018-10-01 00:00Z <= t < 2018-12-13 00:00Z` có mẫu số 1.752 giờ UTC:
cả hai trạm có bản tin và nhiệt độ không phải sentinel trong toàn bộ 1.752 bucket.
Sàng lọc AA1 một giờ nêu trên còn KSTP 1.751/1.752, KMSP 1.590/1.752 bucket.
Đây **không phải** cohort 1.608 giờ traffic MnDOT; chưa chuyển CST/DST, chưa ghép traffic.

## Quyết định từ kiểm tra

- **KSTP là ứng viên ưu tiên cho bước chuẩn hóa thử nghiệm** nhờ gần điểm khu vực hơn và độ phủ precipitation 1h tốt hơn.
  Đây chưa phải quyết định nguồn weather thay thế UCI; chưa đo độ tương đương với UCI.
- **Chưa có đầu vào snow_1h tương thích:** KSTP không có AJ/AL; KMSP chỉ có nhóm độ sâu/tích lũy,
  không được tự chia thời gian hay đổi độ dày thành mm nước để đủ C30.
- **Không mở inference:** cần chốt chọn bản tin, QC, mốc đo, mapping mây/nhãn, timezone và ngày lễ.
  Không bù các vấn đề định nghĩa bằng median hoặc gán 0.

Nếu cần hoàn thành bằng nguồn miễn phí, hướng hợp lệ là thiết kế một thí nghiệm sử dụng các biến NOAA
có định nghĩa rõ và đánh giá theo giao thức riêng. Điều đó thay đổi đầu vào mô hình, cần người dùng quyết định;
lượt kiểm tra này không tự sửa C30, huấn luyện hoặc chấm lại test UCI.

Kết luận phải tách hai việc: NOAA có dữ liệu miễn phí đáng khảo sát; dữ liệu có đủ định nghĩa C30 hay không
phụ thuộc báo cáo thực tế. Giữ khóa dự đoán MnDOT cho đến khi kiểm tra nguồn, thời gian, snow, nhãn và ngày lễ hoàn tất.
