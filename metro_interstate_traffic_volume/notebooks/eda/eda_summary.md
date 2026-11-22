# Tổng hợp ba đợt EDA

Chỉ mô tả trên train; huấn luyện đối chứng và lựa chọn cấu hình nằm trong notebooks/features/.

| Đợt | Kết luận chính | Đề xuất đặc trưng | n giờ train | Rủi ro còn lại |
|---|---|---|---:|---|
| A | Đỉnh trung bình ngày làm việc 16h, cuối tuần 13h; lễ ghép cùng thứ/giờ chênh -953.3 xe/giờ, n=844 giờ lễ | A12 làm mốc; chưa bỏ cột theo VIF | 28402 | Nhãn lễ có thể thiếu; chưa kiểm soát mùa/năm; DST chưa phân tích |
| B | Toàn CSV có 3,609 dòng rain_1h=0 nhưng weather_main=Rain; tương quan riêng lẻ chưa đánh giá giá trị bổ sung | Đề xuất numeric16, labels23, B27 cho FE | 28402 | Nhãn hiếm; weather cùng giờ cần sẵn có; 0 mm không đồng nghĩa trời khô |
| C | 22,503/28,402 giờ đủ cả ba history; gaps ảnh hưởng độ phủ | Đề xuất C30 có điều kiện; tra lag theo timestamp và mean trên quá khứ | 28402 | Cửa sổ ít nhất 18/24 giờ; cần quan sát quá khứ đến kịp; chưa đại diện dự báo nhiều bước |

Các cấu hình trên là đề xuất từ EDA, chưa phải kết luận về sai số mô hình. Xem notebooks/features/feature_summary.md để đọc đối chứng RF cùng protocol.
