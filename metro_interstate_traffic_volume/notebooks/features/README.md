# Lựa chọn nhóm đặc trưng

Chạy lần lượt `feaure_V1_A12.ipynb`, `feaure_V2_numeric16.ipynb`, `feaure_V3_labels23.ipynb`, `feaure_V4_B27.ipynb`, `feaure_V5_C30.ipynb`. Mỗi notebook chạy độc lập, lưu điểm và nhận xét phương án của mình; V2–V5 có đối chứng với cấu hình trước nếu đã có kết quả. Sau V1–V5, chạy `feature_comparison.ipynb` để kiểm tra tính đồng nhất, xem bảng chung, chọn cấu hình và xuất dữ liệu cho tuning. NB1 chỉ là cấu hình mốc, không chứa bảng xếp hạng cả năm.

| Notebook | Cấu hình | Câu hỏi |
|---|---|---|
| V1 | A12 | Mốc lịch và ngày lễ |
| V2 | A12 + 4 biến số = 16 | Giá trị bổ sung của weather dạng số |
| V3 | A12 + 11 cờ = 23 | Giá trị bổ sung của weather dạng nhãn |
| V4 | A12 + cả hai nhóm = B27 | Hai nhóm có bổ trợ nhau không? |
| V5 | B27 + 3 history = C30 | Giá trị bổ sung của history |

Năm phương án này tổng hợp câu hỏi từ các thí nghiệm chính cũ thành một đối chứng theo nhóm. Không sao chép estimator hoặc protocol khác nhau của E05/E13/E15/E17/E18. Notebook trong `experiments/` giữ nguyên làm thí nghiệm bổ sung và truy vết.

Mọi bước dùng chung trong `src/feature_experiments.py`: `data/preprocessed/hourly_unfilled.csv` → chia 70/15/15 → tạo feature không học thống kê → chọn cohort đủ history → 3 TimeSeriesSplit → fit điền thiếu trên fold-train → cùng RF cố định → MAE/RMSE. Không chấm validation/test. Không brute force từng cột và không tuning tham số.

Cả năm được chấm trên tập giờ đủ history để có thể so trực tiếp. Điều này bỏ một số giờ A/B vốn dự đoán được; kết quả là lựa chọn trong cohort chung, chưa trả lời phương án nào tốt nhất trên mọi giờ. Tất cả dùng dtype float32, RF 400 cây/depth12/leaf5/max_features1.0/seed42, n_jobs=4. Không scaler; cờ weather theo từ điển cố định. Median điền thiếu chỉ học fold-train; temperature backward-fill chỉ dùng quan sát gốc trước tối đa 6 giờ. Lịch sử tra timestamp, mean dùng ít nhất 18/24 giờ trước t. Đây là đánh giá tuần tự có quan sát target quá khứ, chưa phải dự báo cả đoạn tương lai tại một mốc.

`outputs/<protocol_id>/` lưu protocol, phiên bản, hash mã nguồn/dữ liệu, fold manifest, metrics, dự đoán OOF và thống kê điền thiếu. Kết quả khác hash được tách thư mục. Trước khi xếp hạng, code xác nhận cả năm có cùng timestamp, target, params và bảng 30 cột sau xử lý. MAE trung bình fold là tiêu chí chính, RMSE để đối chiếu và phá hòa. SD giữa fold không phải khoảng tin cậy của chênh lệch.

Sau khi đủ năm phương án, chạy `feature_comparison.ipynb`; kết quả được lưu trong `feature_summary.md` và `feature_comparison.csv`. `selected/<protocol_id>/` chứa tập feature được chọn **chưa điền thiếu**, kèm toàn bộ ngữ cảnh giờ train để tuning tái lập điền thiếu trong từng fold. Không fit model cuối ở bước này. Không dùng ngay CSV còn thiếu cho estimator; xem quy tắc `prepare_fold` trong module dùng chung.

Cài thư viện từ `../../requirements.txt`. Các notebook được kiểm tra bằng cách chạy tuần tự mọi ô trong IPython, mỗi notebook một process mới trong sandbox; chưa xác minh khởi động kernel Jupyter ngoài sandbox.

`legacy_eda/` giữ kết quả CV cũ đã chuyển khỏi EDA; không đưa vào bảng so sánh mới.

Sau khi chuyển thư mục, khởi động lại kernel để nạp đường dẫn mới của các module. Dữ liệu vẫn ở `../../data/`, hình ở `../../figures/`; outputs và selected nằm cùng thư mục notebook FE. Các lần đổi đường dẫn và nguồn đọc đã được đối chiếu lại dữ liệu từng fold trước khi tái sử dụng điểm và dự đoán cũ.

Chạy `../preprocessing/preprocessing.ipynb` trước FE. Notebook này xuất một CSV tổng; không cần ba CSV train/validation/test. FE tự chia trong bộ nhớ và chỉ fit điền thiếu trên mỗi fold-train.

Chỉ giữ protocol hiện tại `e4bc1e064317af8c` trong `outputs/` và `selected/`. Hai protocol cũ có CSV giống từng byte đã được gộp; metadata lịch sử và dấu SHA-256 nằm trong `outputs/e4bc1e064317af8c/deduplication.json`. Các mã protocol cũ trong bản ghi truy vết tham chiếu lịch sử này, không yêu cầu giữ lại thư mục dữ liệu trùng.
