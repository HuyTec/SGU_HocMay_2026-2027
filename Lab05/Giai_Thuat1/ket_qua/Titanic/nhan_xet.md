### Nhận xét kết quả

- Sau làm sạch có **891 dòng**; train **712**, test **179**. Tỷ lệ lớp 1 là **38.38%**.

- Cây quyết định chọn **max_depth = 4**, CV ROC AUC **0.8490**. Khoảng cách train - validation là **0.0470**.

- Random Forest chọn **50 cây**, giữ **max_depth = 3** như bài mẫu; CV ROC AUC **0.8589**. Khoảng cách train - validation là **0.0218**.

- Chọn **Random Forest** theo CV trước khi xem test. Mô hình được chọn có test **ROC AUC 0.8438**, **F1 0.7194**, **recall lớp 1 0.7246**.

- Ba đặc trưng đứng đầu theo MDI của rừng: **cat__Sex_male, cat__Sex_female, num__Fare**. Đây là mức quan trọng phụ thuộc mô hình, không chứng minh quan hệ nhân quả.

- Điểm train cao hơn validation nhiều gợi ý quá khớp; hai điểm thấp có thể gợi ý thiếu khớp. Khoảng cách điểm là dấu hiệu tham khảo, không đo trực tiếp bias và variance.

- Tăng số cây làm tăng chi phí nhưng không bảo đảm AUC tăng liên tục. Cấu hình tốt nhất chỉ trong lưới đã thử, với rừng giới hạn độ sâu 3 để bám bài mẫu.

- Test chỉ được dùng ở phần đánh giá cuối, không dùng chọn lại tham số. Recall, precision, F1 và average precision bổ sung cho accuracy khi nhãn mất cân bằng. Báo cáo dùng ngưỡng phân loại mặc định.