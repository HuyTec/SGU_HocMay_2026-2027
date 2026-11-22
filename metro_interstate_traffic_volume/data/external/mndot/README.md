# Dữ liệu MnDOT ngoài giai đoạn UCI

Ngày kiểm tra: 22/11/2026, múi giờ Asia/Saigon.

## Đã nhận dữ liệu 2018

Người dùng cung cấp `C:/Users/NHUT HUY/Downloads/atr_2018.xlsx`. Kiểm tra nội dung cho thấy đây là CSV văn bản, không phải workbook XLSX. Giữ nguyên file người dùng; lưu bản sao byte-for-byte với đúng đuôi tại [raw/atr_2018.csv](raw/atr_2018.csv).

Đã lọc `station_id=301`, `dir_of_travel=7`, `lane_of_travel=0`. Theo [mã FHWA](https://www.fhwa.dot.gov/policyinformation/tmguide/tmg_2022/traffic-data-formats.cfm), 7 là hướng Tây và 0 là gộp các làn theo hướng. Quy đổi cột giờ 1–24 thành timestamp 00:00–23:00 của ngày tương ứng. Toàn bộ 6.533 giờ giao với UCI khớp chính xác lưu lượng; đây là kiểm tra tương thích nguồn, không phải MAE của mô hình.

| Phạm vi | Số giờ | Kết quả |
|---|---:|---|
| Trạm 301 hướng Tây trong file | 8.160 | 01/01/2018 00:00 đến 11/12/2018 23:00 |
| Giao với timestamp của UCI | 6.533 | 6.533 giờ khớp target chính xác |
| Sau mốc cuối UCI | 1.608 | 01/10/2018 00:00 đến 11/12/2018 23:00; 67 ngày có bản ghi |
| Phần mới đủ cả ba history khi dùng UCI làm ngữ cảnh quá khứ | 1.488 | Chưa có weather; đây chưa phải bộ C30 hoàn chỉnh |

Các ngày vắng bản ghi trong khoảng trạm đã quan sát: 01, 02, 03, 05 và 06/12/2018. Không thêm lưu lượng 0 cho các ngày này. Có 19 giờ MnDOT trong giai đoạn trước/tháng 9 không có timestamp tương ứng trong UCI; không tự điền chúng vào dữ liệu UCI cũ.

- [Bảng giờ của trạm 301 hướng Tây](prepared/atr301_westbound_2018_hourly.csv).
- [Chỉ phần mới sau UCI](prepared/atr301_westbound_post_uci_2018.csv).
- [Đối chiếu từng giờ trùng UCI](prepared/atr301_2018_overlap_uci.csv).
- [Manifest, hash và giới hạn](prepared/atr_2018_manifest.json).

File MnDOT chỉ có lưu lượng. Đã tải riêng [weather ERA5 khu vực](weather/README.md) để khảo sát khả năng ghép; bộ weather này chưa tương đương trực tiếp C30. Chưa dự đoán mô hình hoặc chấm điểm. Cần ghép weather tương thích và có checkpoint đã fit trước khi đánh giá C30. Chưa xác minh đầy đủ chất lượng dữ liệu ước lượng và timezone/DST ngoài phần giao với UCI. Mô hình và các tập UCI không thay đổi.

## Trạng thái tải 2024 trước đó

Chưa tải được file dữ liệu hợp lệ; chưa dự đoán hoặc tính MAE/RMSE/R². Không thay đổi dữ liệu UCI hoặc các tập train/validation/test hiện có.

Trang chính thức liệt kê dữ liệu lưu lượng theo giờ 2017–2024 và thông báo dữ liệu 2025 tạm chưa cung cấp trong lúc chuyển hệ thống. Năm 2024 là năm mới nhất có liên kết tải trên trang này tại thời điểm kiểm tra, không phải khẳng định toàn bộ các dịch vụ MnDOT đều chưa có dữ liệu mới hơn.

- Trang nguồn: https://www.dot.state.mn.us/traffic/data/reports-hrvol-atr.html
- File “2024 Yearly Volume Data (excel)”: https://edocs-public.dot.state.mn.us/edocs_public/DMResultSet/download?docId=38594357
- Cổng Traffic Viewer/TCDS: https://www.dot.state.mn.us/traffic/data/tdms.html
- Phạm vi dữ liệu UCI cần đối chiếu: https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume

Tải trực tiếp từ máy và tải qua trình duyệt đều timeout ở máy chủ edocs-public.dot.state.mn.us. Web retrieval không lấy được workbook; Traffic Viewer trả lỗi 403 qua công cụ web. Không lưu trang lỗi HTML thành CSV hoặc Excel. Chưa biết dung lượng, schema, danh sách trạm hoặc số mẫu hợp lệ của file 2024.

## Khi có file thật

1. Giữ file nguyên trạng trong `raw/`; ghi URL, thời điểm tải, kích thước và SHA256.
2. Kiểm tra cấu trúc workbook, hướng dẫn mã trạm/hướng/làn, cờ chất lượng và đơn vị. Lọc trạm ATR 301 trên I-94 hướng Tây chỉ sau khi xác nhận ý nghĩa các mã. Không dùng tổng hai hướng hoặc một làn thay cho mục tiêu UCI.
3. Đối chiếu với một giai đoạn trùng UCI nếu lấy được dữ liệu 2018: xác nhận quy ước giờ bắt đầu/kết thúc, tổng làn, số đếm và cờ dữ liệu ước lượng. Dữ liệu hiện tại chưa đủ để xác minh tương đương này.
4. Xác định timezone/DST của nguồn mới và quy ước CST/local time của UCI. Không tự bỏ giờ lặp, cộng dồn hai giờ hoặc dùng số hàng để tạo lag.
5. Xác minh nguồn thời tiết theo giờ và cách ánh xạ sang `temp`, `rain_1h`, `snow_1h`, `clouds_all`, 11 nhóm `weather_main`. Không tự gán thời tiết quang đãng hoặc toàn bộ giá trị 0 để đủ C30. Nhãn lễ ngoài giai đoạn CSV cũng cần chính sách được công bố.
6. Tạo history từ các quan sát quá khứ của chính chuỗi mới: lag tại đúng t−24h/t−168h; mean trên [t−24h,t), tối thiểu 18 quan sát. Ghi số mẫu bị loại vì thiếu history.
7. Dùng mô hình và thống kê tiền xử lý đã khóa; không tuning hoặc học median từ tập ngoài. Đặc tả `notebooks/validation/outputs/final_C30/selected_model.json` hiện ghi chưa refit cuối; tại lúc kiểm tra chưa tìm thấy checkpoint để nạp inference trong repo.
8. Ghi kết quả vào một thí nghiệm đánh giá ngoài riêng, với mốc lịch, số mẫu, nguồn thời tiết và kiểm tra tương thích. Không trộn điểm này với validation/test UCI. Nếu dùng dữ liệu mới để sửa mô hình, phải mô tả nó là dữ liệu phát triển thay vì đánh giá ngoài độc lập.

## Bước đang cần

Lấy workbook thật từ liên kết chính thức hoặc xuất hourly volume của trạm qua Traffic Viewer/TCDS. Việc kiểm tra schema, ghép weather và đánh giá mô hình phụ thuộc vào dữ liệu thật, chưa thể thực hiện từ trang giới thiệu.
