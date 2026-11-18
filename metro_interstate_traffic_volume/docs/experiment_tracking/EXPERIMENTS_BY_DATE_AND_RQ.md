# Danh mục thí nghiệm theo ngày và câu hỏi proposal

Xem [hướng dẫn đối chứng và chọn nguồn dữ liệu](COMPARISON_PROTOCOL.md) để áp dụng cùng protocol cho các mã E01–E32.

Ngày rà soát: **19/11/2026**. Đây là chỉ mục phân loại lại hiện vật hiện có, không phải kết quả chạy mới. Giữ nguyên notebook, dữ liệu và log gốc; không huấn luyện hoặc chấm test. Ngày chạy ưu tiên run ID/thời gian trong hiện vật, sau đó mới dùng ngày tiêu đề/thư mục và ghi rõ mức chắc chắn. Không dùng ngày sửa file để suy ra ngày thực nghiệm.

## 1. Câu hỏi gốc và quy ước phân loại

Nguồn: [ML_Project_Proposal.docx](../ML_Project_Proposal.docx), phần “Mục tiêu và câu hỏi nghiên cứu”, mục 4–5. Proposal liệt kê ba câu hỏi, không đặt sẵn mã; các mã RQ bên dưới là ký hiệu của chỉ mục này.

- **RQ1:** Đặc trưng thời gian và thời tiết ảnh hưởng thế nào đến lưu lượng xe?
- **RQ2:** Mô hình nào dự đoán tốt nhất, và thông tin thời tiết cải thiện độ chính xác bao nhiêu so với chỉ dùng đặc trưng thời gian?
- **RQ3:** Mô hình sai nhiều nhất ở khung giờ hoặc điều kiện nào?

**RQ2-M** chỉ phần so sánh mô hình/pipeline; **RQ2-W** chỉ phần đóng góp thời tiết của cùng RQ2. **MỞ RỘNG-H** là B→C hoặc A→A+lịch sử theo mục đặc trưng/kế hoạch mở rộng; không tự đặt thành RQ4. Tuning và kiểm tra dữ liệu hỗ trợ RQ, không tự động là một câu trả lời nghiên cứu mới. RQ1 ở đây là quan hệ/mẫu hình dự đoán; không suy ra tác động nhân quả từ importance hoặc ablation.

## 2. Theo ngày: câu hỏi → kết quả → vai trò

Các con số là validation, trừ dòng ghi CV-only. Metrics được trích từ hiện vật liên kết; chưa tái huấn luyện để tái lập. Không lập bảng xếp hạng toàn cục từ các cohort/feature set khác nhau. Trong cùng ngày, các dòng không có timestamp riêng không được suy diễn thứ tự giờ chạy.

### 11/11/2026

| Mã | Người / thí nghiệm | Hướng proposal / câu hỏi cụ thể | Kết quả và giới hạn | Cách dùng |
|---|---|---|---|---|
| E01 | Phúc · A17: 4 mô hình | **RQ2-M** — Với thời gian/ngày lễ, pipeline nào tốt hơn trên validation? | MLP MAE 237,905; RMSE 364,147. Là mốc A của nhánh Phúc, không phải A2/A12. | Hỗ trợ: baseline mô hình |
| E02 | Huy · A2/B17: checkpoint 23:05 | **RQ2-W** — Thêm thời tiết vào giờ–thứ giúp bao nhiêu khi tuning theo cùng quy tắc? | CSV còn A/B XGB và B MLP; bộ metrics của cả 5 mô hình chưa đầy đủ trong riêng thư mục này. Không ghép các checkpoint khác ngày/params tùy ý. | Giữ có điều kiện: checkpoint |
| E03 | Huy · A2/B17: checkpoint 23:26 | **RQ2-W** — Thời tiết cải thiện dự đoán so với A tối giản không? | RF MAE 285,113→274,174; RMSE 501,423→477,408. Có metrics A/B LR, RF, GB. Đã tuning, không phải mặc định; không so hiệu ứng tuning với A12. | Giữ có điều kiện: đối chứng A2/B17 |

### 12/11/2026

| Mã | Người / thí nghiệm | Hướng proposal / câu hỏi cụ thể | Kết quả và giới hạn | Cách dùng |
|---|---|---|---|---|
| E04 | Hào · A17: 4 mô hình | **RQ2-M** — So sánh pipeline chỉ dùng thời gian/ngày lễ; lập mốc cho B của Hào. | MLP MAE 232,197; RMSE 359,991. Chỉ đối chiếu với các nhánh cùng định nghĩa A và cohort. | Hỗ trợ: baseline A của Hào |
| E05 | Hào · B71: 4 mô hình | **RQ2-W + RQ2-M** — Giữ các pipeline/tham số của A17, thêm thời tiết làm thay đổi lỗi thế nào? | MLP MAE 232,197→260,358; RMSE 359,991→385,209 so với A cùng nhánh. Đây là kết quả của biểu diễn và tham số Hào. | Giữ có điều kiện: A17/B71 |
| E06 | Phúc · B27: 4 mô hình | **RQ2-M** — Pipeline nào tốt trên B27 với bộ tham số khai báo? | RF MAE 240,1085; RMSE 395,1767. Không dùng B27 này với A17 của lượt khác để cô lập đóng góp thời tiết. | Hỗ trợ: sàng lọc mô hình B |

### 13/11/2026

| Mã | Người / thí nghiệm | Hướng proposal / câu hỏi cụ thể | Kết quả và giới hạn | Cách dùng |
|---|---|---|---|---|
| E07 | Vũ · C30: tuning 4 mô hình | **MỞ RỘNG-H + RQ2-M** — Trong cùng cấu hình có lịch sử C30, pipeline nào tốt nhất sau tuning? | RF MAE 195,336; RMSE 321,983. Có 22.503 giờ train/6.050 validation. Một mình bảng C không đo được lợi ích lịch sử nếu thiếu B đối chứng. | Giữ: xếp hạng trong C30 |

### 14/11/2026

| Mã | Người / thí nghiệm | Hướng proposal / câu hỏi cụ thể | Kết quả và giới hạn | Cách dùng |
|---|---|---|---|---|
| E08 | Phúc · B27: bộ tham số đầu 09:09 | **RQ2-M / tuning** — Thay bộ tham số của các mô hình B có cải thiện kết quả không? | RF MAE 248,061/RMSE 405,188; MLP RMSE 450,960 với (128,64). LR intercept=True, MAE 569,610. | Hỗ trợ: lịch sử tuning |
| E09 | Phúc · B27: lượt intercept=False 10:11 | **SỬA LỖI / tuning** — Bộ tham số thay đổi cho kết quả gì; có cấu hình lỗi cần loại khỏi chọn mô hình không? | LR MAE 2.563,528 với intercept=False. MLP đổi sang (64,32), RMSE 413,617. Không quy chênh MLP cho nhiễu seed. | Lịch sử: loại dòng LR này khỏi chọn mô hình; các mô hình khác vẫn giữ provenance |
| E10 | Phúc · B27: sửa intercept 10:12 | **RQ2-M / sửa lỗi** — Sau khi sửa intercept, bộ kết quả B27 hợp lệ là gì? | LR MAE 569,610; RF MAE 240,098/RMSE 395,485; MLP MAE 272,667/RMSE 413,617. Ưu tiên lượt này khi báo bộ kết quả đã sửa. | Giữ: kết quả B27 đã sửa |

### 16/11/2026

| Mã | Người / thí nghiệm | Hướng proposal / câu hỏi cụ thể | Kết quả và giới hạn | Cách dùng |
|---|---|---|---|---|
| E11 | Phúc · RF B27: grid depth/leaf | **HỖ TRỢ RQ2-M/W** — Bộ tham số RF nào được chọn bằng MAE CV trên train? | 16 tổ hợp×3 fold; tốt nhất 400 cây, depth12, leaf5, max_features1.0; MAE CV 281,284. Output cho biết validation tắt; không ghi thành một lượt validation mới. | Hỗ trợ: chọn tham số; CV-only |

### 17/11/2026

| Mã | Người / thí nghiệm | Hướng proposal / câu hỏi cụ thể | Kết quả và giới hạn | Cách dùng |
|---|---|---|---|---|
| E12 | Hào · A17/B71/C74 trên cohort lịch sử | **MỞ RỘNG-H; phụ RQ2-W/M** — Thêm 3 đặc trưng lịch sử giúp từng pipeline bao nhiêu trên cùng train/validation? | MLP B MAE 279,097/RMSE 403,343→C 218,389/323,063. Chạy lại cả A/B trên 22.503/6.050 giờ; C74 khác C30. | Giữ: ablation B/C của nhánh Hào |
| E13 | Phúc · RF: A12 / A+numeric16 / B27 | **RQ2-W; phụ RQ1** — Nhóm thời tiết số đóng góp gì, và thêm nhãn sau nhóm số có giúp không? | MAE A 241,969; numeric 242,269; B 240,098. RMSE lần lượt 380,941/397,213/395,485; MAE nhỏ hơn không có nghĩa RMSE tốt hơn. | Giữ chính: ablation nhóm thời tiết, fixed params |
| E14 | Phúc · RF numeric: lượt trung gian | **HỖ TRỢ RQ2-W** — Các checkpoint trước lượt cuối ghi được gì? | 13:42 có config+CV; 14:15:07 có config+CV; không có validation_metrics trong hai thư mục này. Không đếm thành hai kết luận validation độc lập. | Lịch sử: checkpoint CV/config |
| E15 | Phúc · RF: A12 / A+labels23 / B27 | **RQ2-W; phụ RQ1** — Nhãn thời tiết đóng góp gì, và thêm các biến số sau nhãn có giúp không? | MAE A 241,969; labels 241,602; B 240,098. RMSE 380,941/386,601/395,485. Kết luận giới hạn ở RF, cùng tham số, một seed. | Giữ chính: ablation nhóm thời tiết, fixed params |
| E16 | Phúc · RF labels: checkpoint CV | **HỖ TRỢ RQ2-W** — Lượt 20:30 đã có đủ kết quả chấm ngoài chưa? | Có config/CV, không có validation_metrics; dùng làm provenance, không đếm thêm một lượt validation. | Lịch sử: checkpoint |
| E17 | Huy · RF A12/B27 + slice cao điểm | **RQ2-W + RQ3** — Thêm thời tiết có giảm lỗi tổng thể, cao điểm và nhóm mưa không? | MAE 241,986→240,151; RMSE 380,934→395,440. Cao điểm giảm MAE 6,564 trên 1.091 giờ. Slice rain_1h>0 có n=0: không diễn giải thành không có mưa. | Giữ chính: A/B và error slices có điều kiện |
| E18 | Huy · XGB A12/B27 chọn RMSE + ngày lỗi | **RQ2-W + RQ3** — Tuning A/B ngang nhau theo RMSE có thay đổi kết luận thời tiết không; lỗi lớn ở đâu? | 12 ứng viên×3 fold mỗi nhánh, seed42. MAE 242,348→241,431; RMSE 381,038→389,401. Có CSV daily SSE. RF trong bảng là đối chứng đọc lại, không phải RF chạy mới. | Giữ chính: A/B tuned theo RMSE |
| E19 | Huy · C: hai baseline cùng cohort | **MỞ RỘNG-H / baseline** — Seasonal naive có vượt trung bình thứ–giờ khi chấm đúng cùng giờ đủ lịch sử không? | MAE thứ–giờ 291,739, seasonal naive 330,178; RMSE 503,219 và 635,073. Cùng 6.050 giờ chấm. | Giữ: baseline cho mở rộng lịch sử |
| E20 | Huy · RF/GB: B27→C30 cùng cohort | **MỞ RỘNG-H** — Giữ tham số và giờ train/chấm, lịch sử cải thiện lỗi bao nhiêu? | 22.503 train/6.050 validation. RF RMSE 410,006→354,353; GB 422,352→366,125. Đây là ablation lịch sử sạch trong từng mô hình. | Giữ chính cho mở rộng lịch sử |
| E21 | Huy · Ensemble RF C + GB C 50/50 | **RQ2-M mở rộng + RQ3** — Lấy trung bình hai pipeline C có cải thiện đủ để thay RF C không? | RMSE 354,353→353,056; MAE 215,191→216,907; RMSE cao điểm xấu đi. Cải thiện phụ thuộc metric, không có một chiến thắng chung. | Hỗ trợ: thử ensemble; không phải ablation lịch sử mới |
| E22 | Phúc · MLP A17: baseline 21:48 | **HỖ TRỢ RQ2-M** — Mốc MLP A17 trước grid CV đạt mức lỗi nào? | MAE 232,197; RMSE 359,991; (64,32), batch256, alpha0.0001. Workbook có run ID rõ; không đồng nhất với output V1 hiện tại. | Hỗ trợ: baseline trước tuning |
| E23 | Phúc · MLP A17 V2: grid 8 tổ hợp | **HỖ TRỢ RQ2-M** — Tuning batch/alpha/learning-rate bằng CV có cải thiện MLP A17 không? | Chọn MAE CV 288,516; validation MAE 232,022/RMSE 359,827. Chênh MAE với mốc cũ chỉ 0,175; chưa kết luận vượt nhiễu. | Giữ hỗ trợ: chọn bộ MLP dùng cho 18/11 |
| E24 | Phúc · MLP A17 V1: output 23:15 | **HỖ TRỢ RQ2-M / provenance** — Output V1 hiện tại có khớp baseline XLSX 21:48 không? | Không: notebook hiện ghi MAE 255,974/RMSE 377,495, và đường dẫn file 23:15:40 chưa có trong snapshot. Không thay số này vào baseline 21:48. | Chờ đối chứng: output có nhưng thiếu workbook được nhắc |
| E25 | Phúc · MLP A17 V3: mạng (128,32) | **HỖ TRỢ RQ2-M** — Đổi kiến trúc/batch của MLP có tốt hơn mốc V2 không? | MAE 235,871; RMSE 363,798; kém V2 trong lượt lưu. Không phải nghiên cứu thêm thời tiết. | Hỗ trợ: thử tham số không cải thiện |
| E26 | Phúc · MLP A17 V4: grid kiến trúc×batch | **HỖ TRỢ RQ2-M** — Trong 6 cấu hình kiến trúc/batch, bộ nào thắng MAE CV? | Bộ thắng vẫn (64,32), batch256, giống V2; MAE 232,022/RMSE 359,827. Xác nhận lựa chọn, không phải cải thiện mới. | Hỗ trợ: kiểm tra độ rộng lưới |

### 18/11/2026

| Mã | Người / thí nghiệm | Hướng proposal / câu hỏi cụ thể | Kết quả và giới hạn | Cách dùng |
|---|---|---|---|---|
| E27 | Phúc · MLP V1: A17→A+lịch sử20 | **MỞ RỘNG-H** — Thêm lịch sử vào A giúp bao nhiêu khi giữ cùng pipeline/tham số và cohort? | 22.503 train/6.050 validation. MAE 260,068→194,780; RMSE 385,645→302,769. So với A đã refit trên cùng cohort, không dùng MAE 232,022 của 6.086 giờ làm đối chứng. | Giữ chính cho mở rộng: A→A+H, không gọi thành B→C |
| E28 | Phúc · MLP V2: thêm cờ đóng đường | **RQ3 ứng dụng → thử sửa; phụ mở rộng** — Đánh dấu khoảng bất thường đã chọn có giúp mô hình A+lịch sử không? | MAE 194,780→205,722; RMSE 302,769→314,558. Validation không có giờ cờ=1; không chứng minh dự đoán tốt khi đóng đường. Khoảng 20 giờ là giả định của thí nghiệm, nguồn ảnh chưa xác minh đầy đủ ngày/địa điểm đo. | Thăm dò: giữ kết quả âm; chưa đưa cờ vào pipeline chuẩn |
| E29 | Phúc · MLP V3: thêm weather_description | **RQ2-W có điều kiện lịch sử** — Khi đã có A+lịch sử, mô tả thời tiết chi tiết có giá trị bổ sung không? | 20→58 cột, cùng cohort và MLP. MAE 194,780→214,413; RMSE 302,769→322,783. Không hỗ trợ thêm nhóm này trong lượt lưu; không kết luận mọi thông tin thời tiết vô ích. | Giữ phụ: ablation mô tả thời tiết trên nhánh có lịch sử |
| E30 | Phúc · MLP V4: A+H20 so với C30 của Vũ | **RQ2-M: so pipeline mở rộng** — Cùng tham số MLP, chuyển cả feature và preprocessing sang nhánh C30 có tốt hơn không? | MAE 194,780→234,768; RMSE 302,769→357,203. Đổi cả feature lẫn preprocessing; không phải ablation chỉ thêm thời tiết. | Giữ phụ: so pipeline; không dùng để cô lập weather |
| E31 | Phúc · Tổng kết 4 thí nghiệm MLP | **TỔNG HỢP** — Bốn lượt cùng ngày dẫn tới lựa chọn nào trong nhóm đã thử? | Tóm tắt V1–V4; không fit một mô hình mới và không tính thêm là run thứ năm. | Tài liệu tổng hợp, không phải run |

### Chưa xác nhận

| Mã | Người / thí nghiệm | Hướng proposal / câu hỏi cụ thể | Kết quả và giới hạn | Cách dùng |
|---|---|---|---|---|
| E32 | Huy · A2: baseline thời gian tối giản | **RQ2-M / baseline** — Giờ–thứ và baseline thống kê tạo mốc dự đoán nào? | RF RMSE 501,423; baseline thứ–giờ 501,407. Đây là A2, không phải A12 đầy đủ và không phải kiểm tra riêng tác dụng bỏ ngày lễ. | Lịch sử hỗ trợ: chưa xác nhận ngày chạy |

## 3. Lọc theo mục đích viết báo cáo

| Phần báo cáo | Hiện vật nên dùng | Không nên suy ra |
|---|---|---|
| RQ1 — mẫu hình thời gian/thời tiết | Cần EDA/biểu đồ có provenance. Các ablation RF nhóm numeric/labels ngày 17/11 chỉ bổ sung bằng chứng giá trị dự đoán. | Bảng model metrics một mình không giải thích quan hệ thời gian/thời tiết và không chứng minh nhân quả. |
| RQ2 — mô hình nào tốt | Các bảng so mô hình trong cùng A/B/C của mỗi nhánh; Vũ C30 và Hào C74 báo riêng. Grid RF 16/11 và MLP 17/11 làm phần chọn tham số. | Không gộp thành một leaderboard rồi gọi thuật toán thắng khi pipeline, feature/cohort hoặc ngân sách tuning khác nhau. |
| RQ2 — thời tiết giúp bao nhiêu | Ưu tiên RF numeric/labels, RF A12/B27, XGB A12/B27 ngày 17/11. A2/B17 11/11 là đối chứng tối giản bổ sung. | Không dùng thay đổi giữa A2 và A12 để quy toàn bộ hiệu ứng cho tuning. Không gọi MLP A+H20 so C30 ngày 18/11 là weather-only. |
| RQ3 — lỗi ở đâu | RF cao điểm 17/11; XGB daily SSE 17/11; peak slices trong B/C và ensemble. Cờ đóng đường 18/11 là thử sửa lỗi thăm dò. | Slice lượng mưa n=0 không nghĩa không mưa. Cờ đóng đường không có mẫu dương validation không đánh giá được hiệu quả trên ngày đóng đường. |
| Mở rộng lịch sử | Huy B27→C30; Hào B71→C74, cùng cohort; Phúc A17→A+H20 với A refit cùng giờ ngày 18/11. Baseline thứ–giờ và seasonal naive trên cùng 6.050 giờ. | Không dùng A/ B trên 6.086 giờ làm đối chứng trực tiếp với C trên 6.050 giờ. Không gọi A+H20 là C=B+H. |

## 4. Những gì được giữ riêng, không đếm thành bằng chứng mới

Lượt LR intercept=False ngày 14/11 giữ làm lịch sử sửa cấu hình; không chọn làm đại diện LR. Checkpoint chỉ có config/CV không được đếm thêm là validation. V4 MLP A ngày 17/11 chọn lại đúng bộ V2 là xác nhận lựa chọn, không phải cải thiện thêm. Notebook tổng kết 18/11 và workbook tổng hợp là bản trình bày lại, không phải run mới. Hai file khóa Excel `~$*.xlsx` không phải kết quả.

Ngày của A2 cũ còn mâu thuẫn giữa tên thư mục và tên notebook nên được để “Chưa xác nhận”. V1 MLP ngày 17/11 hiện có output 23:15 khác XLSX 21:48; không gộp hai kết quả thành cùng run. Hai notebook WeatherNumeric/WeatherLabels có checkpoint trung gian; báo kết quả cuối có validation_metrics, đồng thời giữ ID của checkpoint làm provenance.

## 5. Phần còn thiếu để trả lời đủ proposal

1. **RQ1:** tại lần lập chỉ mục này, thư mục `notebooks/` không có notebook. Các EDA/V2–V4/error-analysis đã được nhắc ở lần rà soát trước không còn là file hiện có để dẫn nguồn; không sao chép số lịch sử đó vào một ngày chạy giả định. Cần tìm lại nguồn EDA nếu dùng để viết phần quan hệ thời gian/thời tiết.

2. **RQ2:** có đối chứng weather hợp lệ nhưng chủ yếu một seed ở các run ngày 17/11; MAE/RMSE cho kết luận khác nhau. Giữ riêng fixed-parameter ablation và re-tuned comparison. Chưa có cơ sở kết luận một pipeline thắng cuối cùng trên test.

3. **RQ3:** đã có slice cao điểm và ngày lỗi. Slice mưa/tuyết cần định nghĩa lại: lượng mưa/tuyết validation đều 0 nhưng vẫn có nhãn Rain/Snow. Chưa có phân tích lỗi đủ mọi điều kiện trong một protocol thống nhất.

4. **Tiền xử lý (mục 4.2 proposal):** có code gộp timestamp, mask giá trị bất thường, điền thiếu và mã hóa; chưa tìm thấy một bộ run riêng có đối chứng chỉ thay quy tắc median/điền nhiệt độ/lịch lễ trong các notebook hiện có. Ablation feature thời tiết không đồng nghĩa kiểm định cách tiền xử lý. Các notebook nhập từ src dùng chung vẫn cần phiên bản code/hash để tái lập đúng lần cũ.

5. **Đánh giá cuối:** chưa tìm thấy metrics test trong các hiện vật được lập chỉ mục. Giữ test cho sau khi khóa mô hình/protocol; danh mục này không thực hiện đánh giá test.

## 6. Dấu vết nguồn và ngày

| Mã | Bằng chứng ngày / run ID | Notebook hiện có | Hiện vật kết quả |
|---|---|---|---|
| E01 | Nhãn ngày trong workbook; chưa có timestamp run độc lập | [V1_ConfigA_phuc.ipynb](../../experiments/11-11_ConfigA_4Model/V1_ConfigA_phuc.ipynb) | [V1_ConfigA_phuc.xlsx](../../experiments/11-11_ConfigA_4Model/V1_ConfigA_phuc.xlsx) |
| E02 | Run ID trong thư mục; `20261111_230501_c3b031` | [V_1_ConfigB_Compare5Model_Huy_11-11-2026.ipynb](../../experiments/11-11-2026_Huy_ConfigB/V_1_ConfigB_Compare5Model_Huy_11-11-2026.ipynb) | [20261111_230501_c3b031](../../experiments/11-11-2026_Huy_ConfigB/20261111_230501_c3b031) |
| E03 | Run ID trong thư mục; `20261111_232606_0818ce` | [V_1_ConfigB_Compare5Model_Huy_11-11-2026.ipynb](../../experiments/11-11-2026_Huy_ConfigB/V_1_ConfigB_Compare5Model_Huy_11-11-2026.ipynb) | [20261111_232606_0818ce](../../experiments/11-11-2026_Huy_ConfigB/20261111_232606_0818ce) |
| E04 | Run ID trong notebook; `20261112_140304_504718` | [V1_ConfigA_Hao.ipynb](../../experiments/12-11-2026_ConfigA_4Model-Hao/V1_ConfigA_Hao.ipynb) | [V1_Config_Hao.xlsx](../../experiments/12-11-2026_ConfigA_4Model-Hao/V1_Config_Hao.xlsx) |
| E05 | Run ID trong notebook; `20261112_171909_587648` | [V2_ConfigB_Hao.ipynb](../../experiments/12-11-2026_ConfigA_4Model-Hao/V2_ConfigB_Hao.ipynb) | [V2_ConfigB_Hao.xlsx](../../experiments/12-11-2026_ConfigA_4Model-Hao/V2_ConfigB_Hao.xlsx) |
| E06 | Run ID trong notebook; `20261112_213206_138720` | [configB_Phuc.ipynb](../../experiments/12-11-2026_ConfigB_4Model_Phuc/configB_Phuc.ipynb) | [ConfigB_4molde.xlsx](../../experiments/12-11-2026_ConfigB_4Model_Phuc/ConfigB_4molde.xlsx) |
| E07 | Run ID outputs và ngày trong TXT; `20261113_220619` | [ConfigC_4Model_Tuning.ipynb](../../experiments/13-11-2026_ConfigC_4Model_Vu/ConfigC_4Model_Tuning.ipynb) | [ConfigC_validation.csv](../../experiments/13-11-2026_ConfigC_4Model_Vu/outputs/20261113_220619/metrics/ConfigC_validation.csv) |
| E08 | Run ID; thư mục chứa vẫn ghi 13/11; `20261114_090942_883146` | [configB_Phuc.ipynb](../../experiments/13-11-2026_ConfigB_4Model_Phuc/configB_Phuc.ipynb) | [20261114_090942_883146](../../experiments/13-11-2026_ConfigB_4Model_Phuc/outputs/20261114_090942_883146) |
| E09 | Run ID; không lấy ngày tên thư mục; `20261114_101101_536744` | [configB_Phuc.ipynb](../../experiments/13-11-2026_ConfigB_4Model_Phuc/configB_Phuc.ipynb) | [20261114_101101_536744](../../experiments/13-11-2026_ConfigB_4Model_Phuc/outputs/20261114_101101_536744) |
| E10 | Run ID; `20261114_101255_154804` | [configB_Phuc.ipynb](../../experiments/13-11-2026_ConfigB_4Model_Phuc/configB_Phuc.ipynb) | [20261114_101255_154804](../../experiments/13-11-2026_ConfigB_4Model_Phuc/outputs/20261114_101255_154804) |
| E11 | Run ID và grid_cv_config; `20261116_214515_288550` | [configB_RandomForest_Phuc.ipynb](../../experiments/16-11-2026_ConfigB_RandomForest_Phuc/configB_RandomForest_Phuc.ipynb) | [20261116_214515_288550](../../experiments/16-11-2026_ConfigB_RandomForest_Phuc/outputs/20261116_214515_288550) |
| E12 | Notebook có ID 07:53 và 08:02; xác định ngày, chưa gán tất cả hiện vật cho một ID; `20261117_075339_350294; 20261117_080203_847598` | [ConfigC_4Model_Tuning.ipynb](../../experiments/17_11_2026_configC_4Model_Hao/ConfigC_4Model_Tuning.ipynb) | [V3_ConfigC_Hao_metrics.csv](../../experiments/17_11_2026_configC_4Model_Hao/V3_ConfigC_Hao_metrics.csv) |
| E13 | Run ID cuối có validation metrics; `20261117_141557_451140` | [configB_WeatherNumeric_Phuc.ipynb](../../experiments/17-11-2026_ConfigB_WeatherNumeric_Phuc/configB_WeatherNumeric_Phuc.ipynb) | [20261117_141557_451140](../../experiments/17-11-2026_ConfigB_WeatherNumeric_Phuc/outputs/20261117_141557_451140) |
| E14 | Run IDs của hai thư mục; `20261117_134233_133426; 20261117_141507_865779` | [configB_WeatherNumeric_Phuc.ipynb](../../experiments/17-11-2026_ConfigB_WeatherNumeric_Phuc/configB_WeatherNumeric_Phuc.ipynb) | [outputs](../../experiments/17-11-2026_ConfigB_WeatherNumeric_Phuc/outputs) |
| E15 | Run ID có validation metrics; `20261117_203112_824733` | [configB_WeatherLabels_Phuc.ipynb](../../experiments/17-11-2026_ConfigB_WeatherLabels_Phuc/configB_WeatherLabels_Phuc.ipynb) | [20261117_203112_824733](../../experiments/17-11-2026_ConfigB_WeatherLabels_Phuc/outputs/20261117_203112_824733) |
| E16 | Run ID; `20261117_203005_738013` | [configB_WeatherLabels_Phuc.ipynb](../../experiments/17-11-2026_ConfigB_WeatherLabels_Phuc/configB_WeatherLabels_Phuc.ipynb) | [20261117_203005_738013](../../experiments/17-11-2026_ConfigB_WeatherLabels_Phuc/outputs/20261117_203005_738013) |
| E17 | Tiêu đề notebook/thư mục ngày 17/11; run_config không có timestamp chạy | [RandomForest_AB_Huy.ipynb](../../experiments/17-11-2026_Huy_Xulydulieu/RandomForest_AB_Huy.ipynb) | [validation_metrics.csv](../../experiments/17-11-2026_Huy_Xulydulieu/outputs/validation_metrics.csv) |
| E18 | Tiêu đề/thư mục ngày 17/11; không có timestamp chạy riêng | [XGBoost_AB_RMSE_Huy.ipynb](../../experiments/17-11-2026_Huy_XGBoost_RMSE/XGBoost_AB_RMSE_Huy.ipynb) | [run_config.json](../../experiments/17-11-2026_Huy_XGBoost_RMSE/outputs/run_config.json) |
| E19 | README/thư mục ghi 17/11; không có timestamp chạy riêng | [ConfigC_Baselines_Huy.ipynb](../../experiments/17-11-2026_Huy_ConfigC/01_baselines/ConfigC_Baselines_Huy.ipynb) | [validation_metrics.csv](../../experiments/17-11-2026_Huy_ConfigC/01_baselines/outputs/validation_metrics.csv) |
| E20 | README/thư mục ngày 17/11 | [RF_GB_BC.ipynb](../../experiments/17-11-2026_Huy_ConfigC/02_models_bc/RF_GB_BC.ipynb) | [run_config.json](../../experiments/17-11-2026_Huy_ConfigC/02_models_bc/outputs/run_config.json) |
| E21 | README/thư mục ngày 17/11 | [ConfigC_Ensemble.ipynb](../../experiments/17-11-2026_Huy_ConfigC/03_ensemble/ConfigC_Ensemble.ipynb) | [validation_metrics.csv](../../experiments/17-11-2026_Huy_ConfigC/03_ensemble/outputs/validation_metrics.csv) |
| E22 | run_id và thời gian trong workbook; `20261117_214812_726153` | [V1_ConfigA_phuc.ipynb](../../experiments/17-11-2026_ConfigA_ModelLMP_Phuc/V1_ConfigA_phuc.ipynb) | [ConfigA_MLP_20261117_214812_726153.xlsx](../../experiments/17-11-2026_ConfigA_ModelLMP_Phuc/ConfigA_MLP_20261117_214812_726153.xlsx) |
| E23 | run_id và thời gian workbook; `20261117_220400_078079` | [V2_ConfigA_phuc.ipynb](../../experiments/17-11-2026_ConfigA_ModelLMP_Phuc/V2_ConfigA_phuc.ipynb) | [ConfigA_MLP_V2_20261117_220400_078079.xlsx](../../experiments/17-11-2026_ConfigA_ModelLMP_Phuc/ConfigA_MLP_V2_20261117_220400_078079.xlsx) |
| E24 | Run ID trong output đường dẫn lưu; file đích không có; `20261117_231540_795214` | [V1_ConfigA_phuc.ipynb](../../experiments/17-11-2026_ConfigA_ModelLMP_Phuc/V1_ConfigA_phuc.ipynb) | — |
| E25 | run_id và thời gian workbook; `20261117_232020_291453` | [V3_ConfigA_phuc.ipynb](../../experiments/17-11-2026_ConfigA_ModelLMP_Phuc/V3_ConfigA_phuc.ipynb) | [ConfigA_MLP_20261117_232020_291453.xlsx](../../experiments/17-11-2026_ConfigA_ModelLMP_Phuc/ConfigA_MLP_20261117_232020_291453.xlsx) |
| E26 | run_id và thời gian workbook; `20261117_233306_014915` | [V4_ConfigA_phuc.ipynb](../../experiments/17-11-2026_ConfigA_ModelLMP_Phuc/V4_ConfigA_phuc.ipynb) | [ConfigA_MLP_V4_20261117_233306_014915.xlsx](../../experiments/17-11-2026_ConfigA_ModelLMP_Phuc/ConfigA_MLP_V4_20261117_233306_014915.xlsx) |
| E27 | run_id của workbook; `20261118_090434_773047` | [V1_ConfigA_HistoryMLP_Phuc.ipynb](../../experiments/18-11-2026_ConfigA_HistoryMLP_Phuc/V1_ConfigA_HistoryMLP_Phuc.ipynb) | [ConfigA_MLP_History_20261118_090434_773047.xlsx](../../experiments/18-11-2026_ConfigA_HistoryMLP_Phuc/ConfigA_MLP_History_20261118_090434_773047.xlsx) |
| E28 | run_id của workbook; `20261118_093947_117004` | [V2_ConfigA_HistoryMLP_Phuc.ipynb](../../experiments/18-11-2026_ConfigA_HistoryMLP_Phuc/V2_ConfigA_HistoryMLP_Phuc.ipynb) | [ConfigA_MLP_History_V2_RoadClosure_20261118_093947_117004.xlsx](../../experiments/18-11-2026_ConfigA_HistoryMLP_Phuc/ConfigA_MLP_History_V2_RoadClosure_20261118_093947_117004.xlsx) |
| E29 | run_id của workbook; `20261118_095954_877515` | [V3_ConfigA_HistoryMLP_Phuc.ipynb](../../experiments/18-11-2026_ConfigA_HistoryMLP_Phuc/V3_ConfigA_HistoryMLP_Phuc.ipynb) | [ConfigA_MLP_History_V3_WeatherDescription_20261118_095954_877515.xlsx](../../experiments/18-11-2026_ConfigA_HistoryMLP_Phuc/ConfigA_MLP_History_V3_WeatherDescription_20261118_095954_877515.xlsx) |
| E30 | run_id của workbook; `20261118_102041_215507` | [V4_ConfigC_MLP_Phuc.ipynb](../../experiments/18-11-2026_ConfigA_HistoryMLP_Phuc/V4_ConfigC_MLP_Phuc.ipynb) | [ConfigC_MLP_V4_20261118_102041_215507.xlsx](../../experiments/18-11-2026_ConfigA_HistoryMLP_Phuc/ConfigC_MLP_V4_20261118_102041_215507.xlsx) |
| E31 | Tiêu đề notebook và 4 run ID tham chiếu | [KetLuan_4thinghiem.ipynb](../../experiments/18-11-2026_ConfigA_HistoryMLP_Phuc/KetLuan_4thinghiem.ipynb) | — |
| E32 | Thư mục ghi 11/11, tên notebook ghi 05/11; XLSX là bản trích số liệu, không có run ID | [V_1_ConfigAWithoutHoliday_Compare5Model_Huy_5-11-2026.ipynb](../../experiments/11-11-2026_Huy_ConfigAWithoutHoliday/V_1_ConfigAWithoutHoliday_Compare5Model_Huy_5-11-2026.ipynb) | [ConfigA_comparison_from_notebook.xlsx](../../experiments/11-11-2026_Huy_ConfigAWithoutHoliday/ConfigA_comparison_from_notebook.xlsx) |

Phạm vi kiểm tra: **26 notebook trong experiments/** được ánh xạ vào **32 dòng chỉ mục**. Một notebook có thể có nhiều run; một run có nhiều mô hình. Đây không phải số lần fit mô hình. Các mốc không có run timestamp riêng được ghi theo tiêu đề/thư mục và đánh dấu rõ.
