# Ví dụ và phạm vi xác minh

**Bản UCI-first hiện tại:** dùng [kịch bản10–15phút](uci_first_demo.md) và
[nghiệm thu mới](uci_first_verification.md). Những hướng dẫn nguồn ở sidebar,
MnDOT tab2 và fixture làm luồng chính bên dưới là lịch sử UI trước refactor.
Hiện UCI mặc định; tab2walkthrough, tab3history, tab4stored/live, tab5saved-test,
tab6nguồnngoài và fixture nângcao.

## Xem toàn bộ UCI gốc

1. Sidebar chọn **UCI gốc · toàn bộ dữ liệu**.
2. Tab 2 xem/tải CSV 48.204 dòng; bảng theo giờ 40.575 timestamp dùng cho history.
   Xem số giờ và mốc train/validation/test; không mặc định toàn bộ là test.
3. Tab 3 chọn một giờ để xem history và những dòng CSV gốc cùng timestamp.
4. Chọn **19/01/2018 15:00**, sang tab 4 xem dự đoán test đã lưu tại giờ đó.
   Chọn giờ thuộc train/validation thì không có dự đoán test để hiển thị.
5. Tab 5 xem/lọc/tải kết quả test đã lưu; không chạy lại inference hoặc chấm điểm.

## Weather mới trong demo

1. Chọn MnDOT ở sidebar, giữ giả định CST cố định để xem trước.
2. Tab 2 mở **Weather OpenWeather · UTC và quy tắc chuẩn hóa**: xem đủ 8.304 giờ,
   nguồn/tọa độ, cờ mưa/tuyết và tải CSV.
3. Bấm **So sánh weather OpenWeather với UCI**: bảng sai khác trên 6.533 giờ,
   biểu đồ chồng và chênh lệch 7 ngày cuối phần giao. Đây không phải sai số mô hình.
4. Tab 3 chọn một giờ MnDOT: xem UTC tương ứng, weather, provenance và history traffic.
5. Đổi sidebar sang America/Chicago: giờ 04/11/2018 01:00 được giữ thiếu vì DST mơ hồ;
   kết quả đối chiếu cũ bị xóa, cần bấm lập lại theo giả định mới.
6. Dự đoán/đánh giá MnDOT vẫn khóa cho đến khi chốt thời gian, lịch sự kiện và khác biệt nguồn.

## Thử ứng dụng mà không chấm lại UCI

1. Chạy `python -m streamlit run app/app.py`, chọn nguồn **Tổng hợp · kiểm tra kỹ thuật**.
2. Tab 3 chọn `2019-01-08 00:00:00`; tab 4 bấm **Dự đoán giờ đã chọn**. Đây là fixture nhân tạo đủ 168 giờ context.
3. Đổi sang `2019-01-01 00:00:00`: kết quả cũ bị xóa. Bấm dự đoán trả cảnh báo thiếu history, không điền median.
4. Tab 5 chọn 08–10/01/2019, bấm **Đánh giá khoảng đã chọn**. Kết quả chỉ kiểm tra phần mềm; không báo như điểm MnDOT.
5. Chuyển về MnDOT: xem bảng chất lượng; hai nút dự đoán/đánh giá bị vô hiệu hóa và kết quả tổng hợp biến mất.

Fixture là sóng lưu lượng và weather cố định, không đại diện phân phối giao thông thật.
Chưa chọn ví dụ MnDOT sai số nhỏ/lớn vì chưa có dự đoán ngoài hợp lệ.
Khi có kết quả thật, ví dụ được chọn phải ghi là minh họa đã chọn, không đại diện cả tập.

## Kết quả kiểm tra

Phạm vi chạy thực tế và kiểm tra trực quan được ghi sau khi chạy tại `verification.md`.
Không gọi “hoàn thành demo” khi còn khóa MnDOT hoặc chưa kiểm tra đủ luồng thật.

## Các biểu đồ đối chiếu

Tab 2 chọn MnDOT và bấm **Lập biểu đồ đối chiếu nguồn**:

- Độ giao nhau: 6.533/8.160 giờ MnDOT có timestamp chung UCI (~80,06%); 19 giờ chỉ có MnDOT trong giai đoạn UCI,
  1.608 giờ mới sau UCI. Timeline tách từng nhóm và giờ vắng cả hai nguồn.
  Chỉ trong 6.533 giờ chung thì lưu lượng bằng nhau 100%; hai bộ không trùng toàn bộ.
- Đường traffic mặc định từ 28/09 qua 04/10/2018, thể hiện cả phần giao và phần MnDOT tiếp tục sau UCI.
  Chênh lệch `MnDOT − UCI` chỉ vẽ khi có cả hai; ngoài phần giao để trống, không gán sai khác bằng 0.
- Phần mới/cũ: UCI từ đầu năm 2018 đến hết tháng 9 so với MnDOT tháng 10–12 sau UCI;
  bảng độ phủ và thống kê, phân phối theo tỷ lệ với bin dùng chung, mẫu giờ theo từng thứ và số mẫu trong tooltip.
  Khác mùa/nguồn/độ phủ; không kết luận nguyên nhân hoặc model drift từ những hình này.

Tab 5 bấm **Xem biểu đồ sai số UCI đã lưu** để đọc histogram residual, MAE theo ngày và giờ từ
`test_predictions.csv` đã kiểm hash. Không gọi mô hình để tái tạo test.
Kết quả khoảng fixture cũng có các biểu đồ sai số nhưng ghi rõ tổng hợp.
MnDOT chưa có sai số mô hình do đầu vào chưa đạt hợp đồng.

Tab 6 có [nguồn chính thức và cơ sở tin cậy](demo_sources.md): MnDOT, tài liệu phương pháp ATR,
trang UCI dataset, DOI, giấy phép và giới hạn kiểm chứng file địa phương.
