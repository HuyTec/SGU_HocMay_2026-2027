### Nhận xét kết quả

- Train **120 mẫu**, test **30 mẫu**. Siêu tham số được chọn bằng **accuracy**, 4-fold CV trên train.

- Tham số chọn trong lưới: **{'svc__C': 10, 'svc__kernel': 'linear'}**. Điểm CV **0.9750**; chênh lệch train - validation tại cấu hình này **0.0083**.

- SVM sau tìm kiếm đạt test accuracy **0.9667**, balanced accuracy **0.9667**, F1-macro **0.9666**.

- Nếu luôn đoán lớp phổ biến, accuracy là **0.3333**. Cần đọc thêm confusion matrix và chỉ số từng lớp để tránh đánh giá sai khi nhãn mất cân bằng.

- Khoảng cách điểm train/validation là dấu hiệu tham khảo về quá khớp, không đo trực tiếp bias/variance. Cấu hình được chọn chỉ tốt nhất trong lưới đã thử.

- Pipeline chỉ fit scaler/imputer/encoder trên phần train của từng fold. Không chọn lại siêu tham số theo test. SVC/LinearSVC dùng decision_function khi đánh giá ROC AUC; đây là điểm quyết định, không phải xác suất đã hiệu chỉnh.

### Diễn giải cho lần chạy đã lưu

Kernel linear với C=10 được chọn bằng CV. Accuracy test của baseline và cấu hình sau tìm kiếm đều là 96,67% (29/30 mẫu); tối ưu trên CV không bảo đảm điểm test tăng. Hình vector hỗ trợ chỉ chiếu dữ liệu 4 chiều xuống hai số đo cánh hoa.
