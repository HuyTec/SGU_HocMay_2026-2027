# Biên bản xác minh

Ngày kiểm tra theo Asia/Saigon: 22/11/2026.

## Đã chạy

```powershell
app/.venv/Scripts/python.exe -X utf8 -m app.src.demo.audit_cli
app/.venv/Scripts/python.exe -u -X utf8 -m unittest discover -s app/tests -v
app/.venv/Scripts/python.exe -X utf8 -m compileall -q app/app.py app/src/demo app/tests
app/.venv/Scripts/python.exe -X utf8 -m streamlit run app/app.py --server.headless true --server.address 127.0.0.1 --server.port 8502 --browser.gatherUsageStats false
```

Bộ kiểm tra cuối: **14 tests, OK**, 48,716 giây. Gồm 13 kiểm tra contract/service và một kiểm tra
AppTest bao trùm sáu tab, nút khóa MnDOT, biểu đồ phần giao/phân phối, biểu đồ sai số UCI đọc sẵn,
inference fixture, giờ thiếu history, đổi giờ, đổi khoảng và đổi nguồn.
AppTest chạy không có exception. Cảnh báo thiếu ScriptRunContext ở thread chính là chế độ test, không phải lỗi app.
Cảnh báo concat DatetimeIndex đã được xử lý bằng `sort=True` tường minh sau lượt test.

Các kiểm tra quan trọng: C30 đúng thứ tự, ba model và hash/plan đúng; lag tra timestamp khi thiếu giờ;
thay target tại t/tương lai không đổi features/prediction tại t; history thiếu giữ NaN;
adapter và clipping/ensemble khớp `predict_hours`; chỉ chấm giao prediction/actual hợp lệ;
cache thay khi nội dung file đổi; không có lời gọi huấn luyện/quy trình test UCI.

## Quan sát giao diện

Server chạy thành công tại `http://127.0.0.1:8502`. Đã kiểm tra trực quan sáu tab trên Edge, màn hình desktop.
Không kiểm tra mobile hoặc toàn bộ các trình duyệt.

- Tab 1: bảng audit ba trạng thái; artifact, code hash và phiên bản runtime khớp kế hoạch fit.
- Tab 2: 1.728 giờ lịch, 1.608 bản ghi, 120 giờ vắng, 1.488 giờ đủ history; đầu vào ngoài vẫn khóa.
- Tab 3: cửa sổ mean và số quan sát; mở xem context nguồn, không đưa giờ t vào mean.
- Tab 4: artifact cuối, hash, ba trọng số; fixture tại 08/01/2019 00:00 có dự đoán khoảng 1.587,2 xe/giờ.
  Chuyển giờ về 01/01/2019 00:00 xóa kết quả cũ; bấm dự đoán hiện cảnh báo thiếu history.
- Tab 5: bảng test UCI đọc sẵn; nút MnDOT khóa; đánh giá khoảng fixture đã được xác minh qua AppTest.
- Tab 6: blockers và tài liệu hợp đồng, không có công tắc bỏ qua tương thích.

Biểu đồ phần giao hiển thị hai đường UCI/MnDOT trùng nhau và chênh lệch bằng 0;
phân phối và mẫu theo giờ so sánh hai giai đoạn riêng, có mẫu số và giới hạn.
Đã kiểm tra trực quan thêm histogram sai số (cột dọc), MAE theo ngày và giờ trên 6.052 dự đoán UCI lưu sẵn.
Ảnh giao diện: [phần giao](overlap_preview.png), [sai số](errors_preview.png), [mẫu theo giờ mới/cũ](comparison_preview.png).

Cập nhật theo phản hồi: tách tỷ lệ giao timestamp (6.533/8.160 = 80,06%) khỏi tỷ lệ khớp giá trị
trong phần giao; còn 19 giờ chỉ MnDOT trong giai đoạn UCI và 1.608 giờ sau UCI.
Thêm biểu đồ độ phủ theo tháng; cửa sổ đường traffic mặc định đi qua 30/09–01/10.
Kiểm tra cập nhật phân loại và luồng AppTest: 2 tests OK, 17,524 giây.
Tab 6 hiển thị các liên kết chính thức MnDOT/UCI, DOI và thông tin truy nguyên nguồn.

Lượt tiếp tục: biểu đồ cột chồng Altair vẫn render trống trong trình duyệt dù có dữ liệu,
được thay bằng `coverage_figure` (Matplotlib), dùng cùng bảng số giờ theo tháng.
Đã xuất và kiểm tra trực quan [hình độ phủ đã sửa](coverage_chart.png): thấy rõ phần giao,
phần MnDOT mới và 120 giờ thiếu trong tháng 12. Tháng 12 chỉ tính đến 11/12 theo phạm vi file.
Bộ 14 kiểm tra đạt sau thay bộ vẽ (44,880 giây). Server đã khởi động lại để nạp bản sửa.
Quyền trình duyệt của chat không khả dụng ở lượt tiếp tục nên chưa kiểm tra lại bố cục
trình duyệt của bản Matplotlib; AppTest và ảnh xuất được dùng để xác minh, không gọi đó là QA trình duyệt mới.

## Giới hạn hoàn thành

Đã có ứng dụng audit/preview và đường inference kỹ thuật có kiểm tra. **Chưa hoàn thành demo MnDOT đầu cuối**:
chưa có weather/time/holiday tương thích, chưa xuất hourly_demo.csv, chưa dự đoán/chấm MnDOT và chưa có ví dụ sai số MnDOT.
Không huấn luyện lại, không gọi lại dự đoán/chấm test UCI; các file output test và artifact gốc được giữ nguyên.
Chọn nguồn weather và giải quyết các vấn đề trong `demo_data_contract.md` trước khi mở khóa.
