# Nguồn chính thức và cơ sở tin cậy

## OpenWeather · weather mới đã tích hợp

[One Call API 4.0](https://openweathermap.org/api/one-call-4) cung cấp dữ liệu lịch sử
theo giờ, timestamp UTC, nhiệt độ Kelvin mặc định, mây %, mưa/tuyết mm/h.
API đã trả thành công 8.304 giờ từ 01/01 đến hết 12/12/2018 UTC tại điểm người dùng
chọn 44.951424/−93.147145. Dự án giữ phản hồi đã bỏ link chứa key, SHA256 từng trang,
CSV gốc và bản chuẩn hóa có provenance. Đây là bằng chứng truy nguyên và kiểm tra file.

[Công nghệ OpenWeather](https://openweather.co.uk/technology) kết hợp các nguồn quan trắc
và mô hình; không giới thiệu toàn bộ giá trị là đo trực tiếp tại ATR 301.
[FAQ chính thức](https://openweathermap.org/faq) giải thích trường hiện tượng vắng mặt;
quy tắc 0 có cờ riêng và kiểm tra mâu thuẫn nhãn trước khi áp dụng.
Nguồn mới không được xác nhận là cùng tọa độ hoặc phiên bản đã tạo UCI.

Trong tab 2 có đối chiếu weather UCI–OpenWeather trên phần giao theo giả định giờ
đang chọn. Không dùng độ khớp này làm bằng chứng chất lượng tuyệt đối hoặc tự xác nhận DST.

Đối chiếu nguồn ngày 22/11/2026. Uy tín cơ quan công bố không thay thế kiểm tra chất lượng từng file.

## MnDOT · nguồn traffic hành chính

[Minnesota Department of Transportation](https://www.dot.state.mn.us/about/index.html) là cơ quan giao thông
của bang Minnesota. [Trang ATR/WIM theo giờ chính thức](https://www.dot.state.mn.us/traffic/data/reports-hrvol-atr.html)
công bố dữ liệu theo năm, có mục 2018. Đây là đường dẫn từ đơn vị quản lý chương trình đếm xe.

[Tài liệu phương pháp thu thập của MnDOT](https://www.dot.state.mn.us/traffic/data/coll-methods.html)
giải thích ATR là thiết bị đếm tự động liên tục và cách dữ liệu được dùng trong phân tích giao thông.
Tài liệu cũng nêu có thể bổ sung số ước lượng khi thiết bị không ghi nhận được.
Vì vậy không mặc định mọi giờ trong CSV là quan sát trực tiếp; file địa phương chưa có cờ để phân biệt.

Bản 2018 trong dự án do người dùng cung cấp, đã lưu hash và đối chiếu nội dung.
Lần kiểm tra này trang giới thiệu truy cập được nhưng liên kết tải 2018 timeout;
chưa xác nhận file địa phương giống byte-for-byte với file tải trực tiếp chính thức.

## UCI · kho công bố phục vụ nghiên cứu

[Trang dataset Metro Interstate Traffic Volume](https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume)
công bố tác giả John Hogue, năm 2019, 48.204 dòng gốc và giấy phép CC BY 4.0.
Mô tả ghi traffic I-94 hướng Tây tại trạm MnDOT ATR 301, có weather và ngày lễ, giai đoạn 2012–2018.
Số dòng gốc khác số giờ sau xử lý timestamp trùng trong dự án.

Dataset có định danh trích dẫn [DOI 10.24432/C5X60B](https://doi.org/10.24432/C5X60B),
giúp truy xuất đúng nguồn. DOI và giấy phép là bằng chứng truy nguyên, không bảo đảm dữ liệu không có lỗi.
[Trang giới thiệu UCI Repository](https://archive.ics.uci.edu/about) ghi kho hoạt động từ 1987,
phục vụ nghiên cứu/giảng dạy học máy và ghi nhận hỗ trợ từ National Science Foundation.

## Bằng chứng tương thích trong dự án

Hai bộ có liên hệ nguồn traffic, không phải hai bộ hoàn toàn độc lập:

| Nhóm trong toàn bộ 8.160 giờ MnDOT đã chọn | Số giờ |
|---|---:|
| Có cùng timestamp với UCI, lưu lượng bằng nhau trong phần giao | 6.533 |
| Chỉ MnDOT có timestamp, nhưng vẫn trong giai đoạn UCI | 19 |
| MnDOT sau mốc cuối UCI | 1.608 |

Phần giao chiếm khoảng **80,06%** số bản ghi MnDOT; **19,94%** còn lại không có timestamp tương ứng trong UCI.
“Khớp 100% giá trị trên phần giao” không phải “hai bộ trùng toàn bộ”.
Đối chiếu này chỉ xác minh traffic tại các giờ chung, không xác nhận weather, DST hay holiday ngoài UCI.
Xem `demo_audit.md` và `demo_data_contract.md` trước khi dùng để đánh giá mô hình.
