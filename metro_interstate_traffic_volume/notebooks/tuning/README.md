# Tuning dùng cùng protocol FE

Chạy theo thứ tự tuning_C30.ipynb → tuning_A12.ipynb → tuning_B27.ipynb → tuning_compare.ipynb. Mỗi notebook chạy độc lập từ đầu, chỉ đặt CONFIG; cohort, fold, ma trận và ngân sách nằm trong src/tuning_cv.py. src/tuning.py chỉ xuất lại API này. Pipeline mô hình nằm trong src/model.py; mã thí nghiệm cũ ở *_exp.py.

Cả ba dùng 22.503 giờ đủ history và ba fold của FE, chấm 16.875 giờ OOF. prepare_fold xử lý thiếu; không điền median cho lag. Ridge dùng weekday_hour và month one-hot, các biến số được scale trong fold. Mỗi mô hình/cấu hình có sáu ứng viên. XGBoost được giữ vì README báo cáo có nhắc tới; phiên bản được ghi trong protocol.

outputs/A12, outputs/B27, outputs/C30 mỗi nơi có protocol.json và results.json. Hash protocol phải giống nhau; tuning_compare dừng nếu lệch hoặc kết quả chưa hoàn tất. Mỗi lần Run All huấn luyện lại riêng cấu hình đó. progress.json chỉ tồn tại khi đang chạy và được xóa sau khi hoàn tất. Không tạo thêm bản sao dữ liệu gốc hoặc thư mục protocol_id.

Hai baseline: trung bình thứ–giờ từ fold-train và lag_168h. OOF chỉ lưu cho mô hình đã chọn; toàn bộ điểm từng ứng viên/fold được giữ trong results.json. Không fit hoặc chấm validation/test ở bước này. Lượt A/B cũ dùng toàn bộ train nằm trong legacy/, không đưa vào bảng mới.

Thư viện theo ../../requirements.txt. Trong môi trường Codex, kiểm tra bằng IPython mới cho từng notebook, chạy tuần tự toàn bộ ô và lưu execution count/output; đường khởi động dịch vụ kernel Jupyter ngoài sandbox chưa được kiểm tra. Trên VS Code dùng Restart Kernel & Run All với cùng môi trường Python.

Tổng ngân sách: 5 mô hình × 6 ứng viên × 3 fold × 3 cấu hình = 270 lần fit. C30 được chạy trước; A12/B27 là đối chứng sau tuning. Ridge thay cách biểu diễn lịch thành one-hot thứ–giờ/tháng, nên chỉ so sánh với Ridge cùng pipeline này; đối chiếu với FE RF cố định được thực hiện riêng trên RF C30.

Sửa lỗi lấy mẫu RF: gọi ParameterSampler với đúng 6 ứng viên, không lấy toàn grid rồi cắt prefix. RF thử n_estimators 100/200/400, max_depth 8/12/16/20/None, min_samples_leaf 1/2/5/10, max_features 0.33/0.5/0.8/1.0. Cùng ngân sách là cùng số ứng viên/fold, không đồng nghĩa đã bao phủ toàn lưới hoặc cùng thời gian CPU. outputs/cv_candidates.csv kiểm toán các ứng viên đã thực sự chạy; rf_sampling_correction.json lưu mô tả lượt sửa lỗi và tham số RF cũ, không nhân bản OOF.
