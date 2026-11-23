# Hợp đồng dữ liệu demo C30

**UI UCI-first hiện tại:** UCI mặc định; nguồn ngoài chỉ mở ở tab6. Tab4 cho phép
stored lookup hoặc real single-hour inference khi artifact/hash/C30 hợp lệ, so với
file lưu; không fit hoặc chấm lại toàn test. Khóa MnDOT vẫn giữ nguyên. Các mô tả
về nguồn ngoài dưới đây là hợp đồng adapter, không có nghĩa nguồn đó là luồng chính.

## Cập nhật tích hợp OpenWeather — 23/11/2026

Nguồn đang dùng trong demo là `weather/openweather_2018/openweather_2018_weather_prepared.csv`:
8.304 giờ UTC; nhiệt độ K, mưa/tuyết mm/h, mây %, nhãn weather từ API chuẩn hóa chữ thường.
Trước khi dùng, kiểm hash bản gốc và đối chiếu giá trị/cờ từng dòng với bản chuẩn hóa.
Giá trị 0 suy theo FAQ nhà cung cấp có cờ riêng; không gọi đó là quan trắc trực tiếp.

`weather.attach_preview` ghép **chỉ** các dòng MnDOT sau UCI, giữ UCI context nguyên vẹn.
CST UTC−06:00 ghép 1.608/1.608 giờ. Với America/Chicago, giờ 04/11/2018 01:00
không thể phân biệt hai offset từ traffic naive, nên giữ thiếu. Giờ không tồn tại vào
mùa xuân cũng không được dịch hoặc tự tạo. Sidebar chỉ đổi giả định xem trước,
không chứng nhận giả định hoặc mở khóa dự đoán.

Biểu đồ weather đối chiếu theo giả định hiển thị trên giai đoạn giao UCI năm 2018,
không chạy/chọn mô hình theo điểm UCI. Khác biệt weather không chứng minh nguồn nào đúng;
không tự chọn policy theo độ khớp để khẳng định timezone thật. Điểm khu vực chưa được
xác minh là nguồn UCI. Ngày lễ ngoài UCI vẫn thiếu. Các mô tả ERA5 bên dưới là đối chiếu
nguồn cũ; không còn là nguồn weather chính của app. Xem `openweather_review.md`.

## Schema chuẩn cho predict.py

Một dòng mỗi giờ, timestamp đầu giờ duy nhất, tăng dần. Bảng gồm cả context quá khứ, không chỉ dòng t.

| Cột | Đơn vị / định nghĩa | Quy tắc |
|---|---|---|
| date_time | giờ naive theo quy ước nguồn đã xác minh | Không tự bỏ/gộp giờ DST |
| temp | Kelvin | `add_weather_features` trừ 273,15 thành temp_c |
| rain_1h | mm mưa của một giờ | Không thay bằng tổng precipitation |
| snow_1h | mm; cần định nghĩa vật lý nguồn tương đương | Không gán snowfall_cm × 10 |
| clouds_all | % | Nguồn/độ phân giải cần công bố |
| weather_main | nhãn chữ thường, có thể gộp bằng dấu phân cách ` \| ` | 11 nhóm theo `src/features.py`; nhãn không biết gây lỗi |
| is_holiday | 0/1, nhãn sự kiện ở cấp ngày | Không tự gán 0 cho ngày thiếu thông tin |
| traffic_volume | xe/giờ, số đo thực | Dùng history và actual; tại t có thể thiếu, không đưa vào C30 tại t |

30 đặc trưng và thứ tự chỉ đọc từ artifact, kiểm tra bằng `CONFIG_C`; không triển khai riêng trong app.
Các cột provenance không được chọn vào model matrix.

## Nguồn và quy ước thời gian

Traffic: `data/external/mndot/raw/atr_2018.csv`, chọn trạm 301, hướng 7 (West), làn 0 (tổng làn theo hướng).
Theo manifest, giờ 1–24 ánh xạ `date + (h−1) giờ`; 6.533 timestamp giao UCI khớp target chính xác.
Audit kiểm tra lại bảng giờ từ raw và phần giao target; đây là đối chiếu nguồn, không chấm mô hình.

UCI: dữ liệu hiện có là timestamp naive. [Metadata UCI chính thức](https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume)
mô tả `date_time` là “local CST time”; mô tả này chưa giải thích chính sách xử lý DST/giờ lặp trong CSV.
Chưa có bằng chứng đủ để chọn CST cố định hay giờ địa phương có DST khi ghép với MnDOT/weather.
OpenWeather: giữ `date_time_utc` +00:00 và ghép xem trước theo giả định sidebar.
Chính sách hiện tại cho giờ mơ hồ/không tồn tại: **giữ weather thiếu**, giữ nguyên timestamp traffic gốc;
không tự cộng, lấy trung bình, bỏ giờ lặp hoặc shift giờ không tồn tại.

Provenance tương lai cần giữ: timestamp gốc traffic, timestamp UTC weather, timestamp sau quy đổi,
timezone/policy, station/direction/lane, nguồn biến, trạng thái observed/filled/unresolved và hash nguồn.
App hiển thị nguồn traffic, manifest, timestamp UTC weather, chính sách quy đổi và trạng thái ghép.

## Ánh xạ ERA5 cũ · chỉ tham khảo

Bảng này ghi nhận dữ liệu và đơn vị từ `weather/request_metadata.json` và `weather/README.md` hiện có,
không chứng nhận tương thích giữa các nguồn.

| Biến nguồn | Đơn vị / định nghĩa | Biến mô hình | Phép chuyển đổi dự kiến | Tương thích | Hạn chế |
|---|---|---|---|---|---|
| temperature_2m_c | °C, nhiệt độ 2 m ERA5 | temp → temp_c | +273,15 K; model tự đổi lại °C | Đơn vị phù hợp, chưa xác minh nguồn/time | Ô lưới khu vực khác nguồn UCI |
| rain_mm | mm mưa, tổng giờ trước theo README nguồn | rain_1h | Giữ mm khi xác minh cùng khoảng đo | Chưa xác minh mốc giờ | Rain khác precipitation; không dùng thay thế ngầm |
| snowfall_cm | cm độ dày tuyết rơi | snow_1h | Chưa có phép đổi được duyệt | Chưa tương thích | Độ dày tuyết không đồng nhất mm nước, cần mật độ/định nghĩa nguồn |
| cloud_cover_pct | % mây che phủ | clouds_all | Giữ % khi time/source được chốt | Cùng đơn vị, chưa xác minh | Khác độ phân giải và nguồn |
| weather_code_wmo | mã WMO | 11 cờ weather | Chưa có mapping được duyệt | Xấp xỉ nếu triển khai | Không suy ra đủ mist/haze/smoke/squall; không coi vắng thông tin là 0 |

Weather có đủ năm biến đã yêu cầu và 8.304 giờ, không đồng nghĩa đủ đầu vào tương thích C30.
Tọa độ yêu cầu 44,95/−93,15; ô lưới trả về 45,00/−93,25; chưa xác minh tọa độ weather gốc UCI.

**Nhãn cho nguồn mới:** “Demo lịch sử: traffic MnDOT và weather OpenWeather cùng giờ.”
Không gọi là dự báo vận hành với weather biết trước.

## Ngày lễ

UCI context giữ `is_holiday` có sẵn, từ nhãn sự kiện CSV UCI được lan theo ngày bằng code dự án.
Không thay bằng lịch lễ liên bang một cách ngầm định; lịch đó còn có thể thiếu sự kiện như State Fair.
MnDOT ngoài UCI: `is_holiday` chưa có, giữ thiếu và khóa dự đoán. Chưa chọn lịch ngoài.
Fixture tổng hợp có cờ 0 được đặt rõ trong dữ liệu nhân tạo; không suy diễn lịch lễ thật.

## Thiếu dữ liệu và context

Phân biệt giờ vắng bản ghi, bản ghi thiếu target, thiếu weather gốc, thiếu history và weather chưa tương thích.
Lưới báo cáo thêm dòng thiếu để kiểm tra/vẽ; không dùng dòng đó làm số đo 0.
Không điền traffic/history. Lag tra đúng timestamp t−24h, t−168h; mean dùng [t−24h,t), ít nhất 18 quan sát.
Nguồn context là UCI quan sát gốc + chỉ timestamp MnDOT sau `2018-09-30 23:00`.
Không bù 19 timestamp ngoài phần giao từ MnDOT vào UCI.

Khi nguồn tương thích, chỉ temp và rain thiếu cục bộ được xử lý bằng `fill_weather` và thống kê trong artifact:
temp tra quan sát quá khứ tối đa 6 giờ, sau đó median tháng–giờ/fallback; rain dùng median đã lưu.
Không fit median mới. snow/cloud/calendar/label thiếu vẫn phải giải quyết theo hợp đồng; không được che bằng imputer.
UI hiển thị giá trị gốc, giá trị sau xử lý và trạng thái riêng.

## Artifact và scoring

Artifact tường minh: `notebooks/validation/outputs/final_C30/final_model.joblib`.
RF 0,25; XGBoost 0,25; ExtraTrees 0,50; fit 28.553 giờ đủ history, kết thúc `2018-01-19 14:00`.
Phiên bản lúc fit trong `final_fit_plan.json`; hash artifact đối chiếu `test_evaluation.json`.
Không có created_at đáng tin cậy; không dùng mtime làm ngày huấn luyện.
Clip từng dự đoán thành phần ở 0, nhân trọng số và cộng, clip kết quả như `predict_hours`.
Làm tròn chỉ hiển thị; lỗi tính từ float gốc.

MnDOT chỉ chấm sau mốc UCI, trong khoảng chọn ∩ prediction hữu hạn ∩ actual hữu hạn không âm.
Báo mẫu số lịch và số loại theo từng nhóm (có thể chồng lấn), cùng tổng loại đã khử trùng.
UCI test chỉ đọc bảng lưu; không tái dự đoán hoặc chấm lại. Hai khối khác thời gian/weather/n, không tính “cải thiện”.

## Những quyết định còn cần người dùng chọn

1. Weather OpenWeather đã có và kiểm tra schema/provenance; cần công bố khác biệt với nguồn UCI,
   không coi cùng tên biến hoặc đơn vị là bằng chứng cùng nguồn/địa điểm.
2. Thời gian: CST cố định hay America/Chicago chỉ sau khi có bằng chứng cho UCI/MnDOT và mốc đo rain.
   Khi có DST, cần chính sách định danh giờ lặp và xử lý giờ không tồn tại phù hợp dữ liệu.
3. Ngày lễ: chọn lịch có sự kiện tương ứng UCI hoặc lịch ngoài và công bố khác biệt, không tự mặc định ngày thường.

App không có checkbox bỏ qua kiểm tra. Bảng ghép weather xem trước có trong phiên;
chưa xuất hourly_demo được chứng nhận tương thích cho inference.
Các bảng kiểm tra và xem trước vẫn hoạt động trong khi chờ giải quyết.
