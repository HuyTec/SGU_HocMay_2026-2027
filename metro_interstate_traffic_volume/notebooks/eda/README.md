# Ba đợt EDA

Mở eda_A.ipynb, eda_B.ipynb, eda_C.ipynb và chạy từ đầu đến cuối. Các thư viện nằm trong ../../requirements.txt; hàm thống kê và vẽ hình ở src/eda/helpers.py. EDA_general.ipynb được giữ nguyên.

Ba notebook chỉ mô tả chất lượng, phân phối, quan hệ và độ ổn định của đặc trưng trên train. EDA không huấn luyện hoặc chọn cấu hình bằng điểm CV. Phần đó chuyển sang năm notebook ../features/feaure_V*.ipynb, cùng RF/tham số/preprocessing/cohort/fold.

CSV đọc keep_default_na=False, gộp theo timestamp; số đo thời tiết lấy median các giá trị phân biệt và nhãn giữ tập hợp. Mask 0 K và điểm mưa nghi vấn, giữ NaN để mô tả. Không điền target cho giờ thiếu. Lịch lấy từ CSV, chưa bổ sung lịch ngoài hoặc phân tích DST.

Lag tra đúng timestamp t−24h/t−168h. mean_24h dùng [t−24h,t), ít nhất 18 quan sát; có so độ phủ với quy tắc đủ 24 giờ. Bootstrap lấy khối 7 ngày, seed42; nhóm n<30 được đánh dấu ít mẫu. Tương quan và VIF không tự quyết định bỏ cột.

Hình lưu ../../figures/eda_*.png. Mục 7 tổng kết bằng Markdown. ../../eda_summary.md ghi kết luận mô tả; khi dữ liệu đổi phải đọc lại kết quả và cập nhật nhận xét. Kết quả CV cũ được lưu riêng tại ../features/legacy_eda/ để truy vết.

Đã kiểm tra thực thi tuần tự các ô trong IPython bên trong sandbox, mỗi notebook một process mới. Chưa xác minh khởi động kernel Jupyter ngoài sandbox. Xem outputs/execution_validation.json cho lần xác minh cuối.
