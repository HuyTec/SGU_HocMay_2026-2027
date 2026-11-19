# Ba đợt EDA

Mở `eda_A.ipynb`, `eda_B.ipynb`, `eda_C.ipynb` bằng kernel có các thư viện trong `requirements.txt`, rồi chọn **Restart Kernel & Run All**. Mỗi notebook tự đọc dữ liệu và chạy độc lập, không cần chạy notebook khác trước. Giữ thư mục dự án làm workspace; code tự tìm CSV khi kernel bắt đầu từ gốc dự án hoặc `eda/`.

```powershell
python -m pip install -r eda/requirements.txt
```

Mỗi notebook chứa trực tiếp các hàm phục vụ phân tích; các cell định nghĩa hàm được đánh dấu thu gọn để ưu tiên phần diễn giải. Có thể mở các cell đó để xem công thức bootstrap, VIF và đối chứng. Các notebook sử dụng các hàm chuẩn bị dữ liệu đã có trong `src/`; không phụ thuộc file `.py` hỗ trợ mới trong `eda/`. `EDA_general.ipynb` được giữ riêng.

## Phạm vi và quy tắc

- Kiểm toán số dòng, timestamp, giờ thiếu và mâu thuẫn nhãn trên toàn CSV. Quan hệ với mục tiêu, quyết định feature và model CV chỉ dùng 70% đầu theo giờ duy nhất. Không đánh giá model trên validation/test.
- Cấu hình A12/B27/C30 theo code dự án. Nhãn lễ từ CSV, không bổ sung lịch ngoài. Không phân tích DST; timestamp giữ như nguồn.
- Mask temp=0 K và điểm rain_1h=9831.3 tại 2016-07-11 17:00, giữ NaN trong EDA. Các nhãn weather giữ tập hợp; số đo cùng giờ gộp median giá trị phân biệt. `SimpleImputer` chỉ fit trên fold-train.
- `mean_24h` dùng cửa sổ [t−24h,t), ít nhất 18 quan sát, cùng định nghĩa code hiện tại. Quy tắc đủ 24 giờ có bảng so độ phủ; chưa là đối chứng model về thay đổi định nghĩa rolling.
- Đối chứng RF giữ model và tham số cố định, cùng timestamp ở mỗi fold. B/C fit lại trên cohort đủ ba feature history. History ở held-out chỉ dùng quan sát đã đến trước giờ cần dự đoán; đây không phải dự báo cả khối tương lai từ một thời điểm.

## Đầu ra

`../figures/eda_A_01_*.png` và tương tự cho B/C: toàn bộ hình. Mỗi hình hiển thị trong notebook có lời đọc ngay dưới. `outputs/` lưu CV từng fold, quyết định từng feature và JSON kết luận có hash CSV/phiên bản thư viện. `../eda_summary.md` tự cập nhật từ ba JSON, luôn có ba dòng A/B/C; dòng chưa chạy được đánh dấu thay vì tạo số giả.

Các ô đã được thực thi theo thứ tự trong IPython bên trong sandbox, mỗi đợt có namespace mới. Việc khởi động kernel Jupyter ngoài sandbox không được chấp thuận nên chưa kiểm tra đường khởi động đó. Notebook C chứa kiểm tra biên cửa sổ, gaps và can thiệp target để xác nhận đặc trưng không dùng tương lai. Xem `outputs/execution_validation.json` để biết lần xác minh cuối.

VIF và tương quan dùng để mô tả chồng lấp thông tin, không tự quyết định bỏ cột cho RF. CI bootstrap lấy khối 7 ngày lịch, seed 42, chưa hiệu chỉnh nhiều phép so sánh. Nhóm có ít hơn 30 quan sát được đánh dấu để đọc thận trọng.
