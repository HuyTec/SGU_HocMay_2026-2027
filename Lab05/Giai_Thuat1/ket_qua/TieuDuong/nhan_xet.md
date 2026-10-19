### Nhận xét kết quả

- Sau làm sạch có **96,146 dòng**; train **76,916**, test **19,230**. Tỷ lệ lớp 1 là **8.82%**.

- Cây quyết định chọn **max_depth = 8**, CV ROC AUC **0.9728**. Khoảng cách train - validation là **0.0017**.

- Random Forest chọn **10 cây**, giữ **max_depth = 3** như bài mẫu; CV ROC AUC **0.9640**. Khoảng cách train - validation là **0.0001**.

- Chọn **Decision Tree** theo CV trước khi xem test. Mô hình được chọn có test **ROC AUC 0.9743**, **F1 0.5760**, **recall lớp 1 0.9328**.

- Ba đặc trưng đứng đầu theo MDI của rừng: **num__blood_glucose_level, num__HbA1c_level, num__age**. Đây là mức quan trọng phụ thuộc mô hình, không chứng minh quan hệ nhân quả.

- Điểm train cao hơn validation nhiều gợi ý quá khớp; hai điểm thấp có thể gợi ý thiếu khớp. Khoảng cách điểm là dấu hiệu tham khảo, không đo trực tiếp bias và variance.

- Tăng số cây làm tăng chi phí nhưng không bảo đảm AUC tăng liên tục. Cấu hình tốt nhất chỉ trong lưới đã thử, với rừng giới hạn độ sâu 3 để bám bài mẫu.

- Test chỉ được dùng ở phần đánh giá cuối, không dùng chọn lại tham số. Recall, precision, F1 và average precision bổ sung cho accuracy khi nhãn mất cân bằng. Báo cáo dùng ngưỡng phân loại mặc định.