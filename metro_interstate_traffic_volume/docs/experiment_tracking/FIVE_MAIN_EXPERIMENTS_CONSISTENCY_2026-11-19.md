# Kiểm tra tính đồng nhất của năm thí nghiệm chính

Ngày kiểm tra: 19/11/2026. Phạm vi: E05, E13, E15, E17, E18 theo danh mục hiện có. Đọc code, Markdown, output notebook, run_config và CSV; dựng lại dữ liệu đầu vào để đối chiếu. Không huấn luyện lại, không chấm test, không sửa notebook hoặc hiện vật lịch sử. Không tạo file `.py` hỗ trợ.

## Kết luận

**Chưa đồng nhất hoàn toàn.** E13/E15/E17/E18 cùng dùng A12/B27 và đã xác nhận cùng toàn bộ timestamp, target, cờ cao điểm của 6.086 giờ validation. E05 là nhánh A17/B71, khác biểu diễn và tham số nên phải trình bày riêng. Cách lựa chọn tham số cũng khác giữa các nhóm, có chủ đích theo câu hỏi nghiên cứu; không gộp thành một leaderboard đồng protocol.

| Mã | Notebook | Đặc trưng | Protocol | Đánh giá |
|---|---|---|---|---|
| E05 | Hào: `V2_ConfigB_Hao.ipynb` | A17 → B71, số cột trước OneHotEncoder | Giữ tham số LR/RF/GB/MLP từ A của Hào; không tuning mới trong notebook B | Đồng nhất với A17 cùng nhánh về model params, nhưng khác A12/B27; hash snapshot lịch sử khác hiện tại |
| E13 | Phúc: WeatherNumeric | A12 / numeric16 / B27 | RF cố định; 3 fold; đọc kết quả theo MAE | Đồng nhất với E15 về code xử lý, params, fold và các dòng A/B |
| E15 | Phúc: WeatherLabels | A12 / labels23 / B27 | RF cố định; 3 fold; đọc kết quả theo MAE | Đồng nhất với E13; có thể nối hai ablation nhóm feature |
| E17 | Huy: RandomForest_AB | A12 / B27 | RF cố định; validation và error slices; không có một CV mới trong notebook này | Cùng params khai báo với Phúc, nhưng dự đoán là run riêng và không trùng |
| E18 | Huy: XGBoost_AB_RMSE | A12 / B27 | Tuning riêng A/B: 12 ứng viên × 3 fold, chọn RMSE CV | Công bằng trong cặp XGB A/B; khác estimator/selection so RF, không cô lập riêng hiệu ứng đổi metric |

## Các phần đã xác nhận đồng nhất

1. E13/E15/E17/E18 có cùng **6.086 timestamp theo đúng thứ tự, traffic_volume và is_rush_hour** trong CSV predictions, không chỉ cùng số dòng. Không có timestamp bị bỏ hoặc đổi target giữa bốn file này.
2. E13/E15: cell params (sau khi chuẩn hóa tên experiment), cell import/pipeline, prepare_pair, CV và validation giống nhau theo AST. Params RF: 400 cây, max_depth=12, min_samples_leaf=5, max_features=1.0, random_state=42, n_jobs=-1.
3. E13/E15: dự đoán A/B trùng trong tolerance 1e-9; max_abs chênh lần lượt khoảng 2,73e-12 và 3,64e-12. Metrics và mốc fold của các dòng A/B cũng khớp trong 1e-9. Không đếm các dòng lặp này như bằng chứng độc lập.
4. E13/E15/E18: 3 fold có cùng fit_end, score_start/end và số mẫu fit/chấm: 7.102/7.100; 14.202/7.100; 21.302/7.100. Các khoảng lịch không dài bằng nhau vì thiếu giờ.
5. E18 đọc lại baseline/RF từ E17: giá trị khớp trong sai số số học, max_abs RF dưới 1e-12. Đây là tham chiếu tái sử dụng, không phải một lượt RF mới.

Đã tính lại MAE/RMSE/R² từ predictions và đối chiếu các dòng A/B RF của E13/E15/E17 và XGB A/B của E18: khớp CSV metrics với tolerance tuyệt đối 1e-9. Việc này kiểm tra tính nhất quán hiện vật, không tái lập huấn luyện.

Đã dựng lại dữ liệu bằng loader hiện tại, không ghi processed: train 28.402 và validation 6.086; timestamp/target khớp processed. Chín cột số/lịch chung khớp trong 1e-10; 11 cờ weather khớp chính xác khi ánh xạ `weather_<label>` với `weather_main_<label>`. Bốn notebook A12/B27 dùng cùng danh sách feature và các cờ cleaning mặc định false.

## Các điểm chưa đồng nhất hoặc cần sửa nội dung

### 1. E05 chưa thuộc cấu hình A12/B27 đã chốt

Nguồn: `experiments/12-11-2026_ConfigA_4Model-Hao/V2_ConfigB_Hao.ipynb`, cell 4, 6 và 8 (index bắt đầu từ 0).

A17 dùng hour/day_of_week/month, is_weekend/is_holiday và các cột tên ngày lễ; ba cột thời gian được one-hot trong pipeline. B71 thêm các biến số và cả weather_main/weather_description chi tiết. Nhánh này không có is_rush_hour và sáu cột sin/cos của A12. RF của Hào dùng 200 cây/depth16/leaf3, khác 400/depth12/leaf5 ở các nhánh RF A12/B27.

**Cách trình bày:** ghi “nhánh A17/B71, tham số cố định” và tách khỏi bảng A12/B27. Nếu yêu cầu mọi thí nghiệm chính phải theo A12/B27, cần thay danh sách feature và chạy lại A/B của Hào; không đổi nhãn rồi giữ điểm B71.

### 2. Nhận xét RMSE trong E05 sai chiều

Nguồn: cùng notebook, cell Markdown 11; số liệu kiểm tra từ output HTML của cell 10 và notebook A cùng nhánh.

- MLP MAE: 232,197 → 260,3576, tăng khoảng 28,161 xe/giờ.
- MLP RMSE: 359,991 → 385,2087, **tăng khoảng 25,218 xe/giờ**, không phải giảm.
- R²: 0,9665 → 0,9616, giảm.

MLP đứng đầu trong các model B71 không đồng nghĩa thêm weather cải thiện MLP so với A17. Nhận xét từ đồ thị 72 giờ cũng chỉ áp dụng cho đoạn minh họa.

### 3. Output E05 thuộc snapshot khác hiện tại

Cell 4 đang so với các hash lịch sử:

| Tập | Hash notebook coi là lần chạy mẫu | Hash file hiện tại |
|---|---|---|
| Train | `f7693e70c29feb9502209f5bfbfd67066ad3466b8b718eb242a1d42a931c37e9` | `28904438aed187d4f30fd0ea116518451a04abad706c37a3a77910b8667f5078` |
| Validation | `badbebc15f324ac942bd62cc93b95f853b67584646ed097600f536e03513c4e0` | `dcd42fd0cbf52573a6c28f242775da37a8d7970cfb15c9038d2fbe4b56ac2c66` |

Output cũ vẫn ghi “Hai file dữ liệu trùng với lần chạy mẫu”. Dòng đó chỉ mô tả lần chạy cũ. Code hiện tại sẽ cảnh báo hash khác. Hash khác chưa tự chứng minh feature hoặc điểm sẽ thay đổi, nhưng không được coi output cũ đã tái lập trên snapshot hiện tại. E05 có số mẫu/mốc chia trong output, nhưng chưa có prediction CSV để xác nhận toàn bộ cohort lịch sử giống bốn notebook còn lại.

### 4. RF của Phúc và Huy chưa phải một run thống nhất

Nguồn: prediction CSV E13/E15 so với E17, sau khi đã xác nhận cùng timestamp/target/cờ cao điểm.

| Cấu hình | MAE Phúc | MAE Huy | n giờ có dự đoán khác >1e-9 | max_abs chênh dự đoán (xe/giờ) |
|---|---:|---:|---:|---:|
| A12 | 241,969148 | 241,986389 | 4.475 | 32,730450 |
| B27 | 240,098085 | 240,150979 | 4.772 | 82,068769 |

Code hiện tại của Phúc dùng Pipeline có SimpleImputer trước RF; Huy dùng RF trực tiếp sau fill_missing_weather. Các params khai báo giống nhau nhưng chưa tái huấn luyện để phân biệt ảnh hưởng pipeline, dtype hoặc trạng thái code/run lịch sử. Không tự gán nguyên nhân cho chênh lệch.

**Cách dùng:** có thể thảo luận cùng câu hỏi A/B, nhưng bảng Numeric/Labels phải dùng bộ predictions Phúc; bảng RF/error slices của Huy dùng bộ Huy. Không lấy MAE ở một run và RMSE/slices ở run kia rồi ghi thành một kết quả duy nhất.

### 5. Các kết quả EDA mới không thay thế kết quả năm thí nghiệm chính

`eda/eda_B.ipynb` vừa tạo dùng RF 100 cây, SimpleImputer median trong fold và chỉ CV bên trong train. Các thí nghiệm RF chính dùng 400 cây và fill_missing_weather (nhiệt độ quá khứ trong giới hạn 6 giờ, dự phòng theo thống kê train) trước pipeline/model. Cả hai có thể đúng theo protocol riêng; không trộn số CV EDA mới với số validation lịch sử rồi giải thích như một lần chạy.

## Các khác biệt hợp lệ cần ghi rõ

- E13/E15 là ablation fixed params; E17 dùng fixed params để phân tích validation; E18 tuning A/B đối xứng theo RMSE. Không bắt buộc tất cả phải có cùng protocol, nhưng mọi phép so trực tiếp cần khai báo những gì thay đổi.
- MAE/RMSE/R² đều có mặt và dự đoán âm được clip về 0 trước tính metric. Metric chọn tham số là MAE ở nhánh RF hỗ trợ/ablation, RMSE ở E18; chưa có “mô hình thắng” theo một metric chung cho cả năm.
- “Có mưa” ở E17 là rain_1h>0 sau preprocessing, n=0 trên validation. Nhãn Rain vẫn có thể xuất hiện. Không gọi phần còn lại là đã xác nhận “trời không mưa”; nên dùng “lượng mưa ghi nhận bằng 0”.

## Vấn đề trình bày/phụ thuộc phụ

- E05 cell 13 xuất hình vào tên thư mục `12-11-2026_ConfigB_4Model-Hao`, khác thư mục chứa notebook `12-11-2026_ConfigA_4Model-Hao`; cần thống nhất nơi lưu artifact khi tái lập.
- E18 mở đầu còn dẫn `notebooks/separate/V_3.ipynb`; file không có trong snapshot hiện tại. Nguồn RF thực sự được code đọc là E17; nên dùng liên kết tới E17 làm mạch đọc hiện có.
- README hiện lại ghi danh sách model chính không khớp nội dung proposal đã kiểm tra trước và có đường dẫn `notebooks/experiments/...` không phải đường dẫn thực nghiệm hiện có. Không dùng README để suy ra trạng thái đã chạy lại. File `RESEARCH_NARRATIVE_REVIEW.md` được dẫn trong chỉ mục không còn trong thư mục tại lần kiểm tra này.

## Thứ tự hoàn thiện đề xuất

1. Chốt cách trình bày E05: nhánh A17/B71 riêng, hoặc thực hiện lại A12/B27 nếu muốn cùng cấu hình.
2. Sửa nhận xét RMSE của Hào, nguồn chuyển tiếp của XGB và nhãn slice mưa; giữ nguyên số gốc khi chỉ biên tập.
3. Giữ một nguồn predictions đại diện cho mỗi bảng; nối E13/E15 thành một ablation nhóm weather, giữ E17/E18 riêng đúng run/protocol.
4. Khi cần chứng nhận tái lập, chạy lại các run đại diện sau khi khóa loader/pipeline, lưu hash dữ liệu/feature/timestamp, params, phiên bản thư viện và ID của lần chạy mới. Không ghi đè hiện vật lịch sử.

Kết quả kiểm tra hiện tại đủ để nói bốn nhánh A12/B27 cùng cohort validation và các artifact metrics khớp predictions. Chưa đủ để chứng nhận cả năm cùng một biểu diễn, cùng protocol hoặc đã tái lập trên code hiện tại.
