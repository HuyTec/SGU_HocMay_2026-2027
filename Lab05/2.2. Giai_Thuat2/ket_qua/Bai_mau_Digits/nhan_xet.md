### Nhận xét kết quả

- Train **1,500 mẫu**, test **297 mẫu**. Siêu tham số được chọn bằng **accuracy**, 4-fold CV trên train.

- Tham số chọn trong lưới: **{'scale': 'passthrough', 'svc__C': 10, 'svc__gamma': 0.001}**. Điểm CV **0.9940**; chênh lệch train - validation tại cấu hình này **0.0060**.

- SVM sau tìm kiếm đạt test accuracy **0.9529**, balanced accuracy **0.9536**, F1-macro **0.9531**.

- Nếu luôn đoán lớp phổ biến, accuracy là **0.1111**. Cần đọc thêm confusion matrix và chỉ số từng lớp để tránh đánh giá sai khi nhãn mất cân bằng.

- Khoảng cách điểm train/validation là dấu hiệu tham khảo về quá khớp, không đo trực tiếp bias/variance. Cấu hình được chọn chỉ tốt nhất trong lưới đã thử.

- Pipeline chỉ fit scaler/imputer/encoder trên phần train của từng fold. Không chọn lại siêu tham số theo test. SVC/LinearSVC dùng decision_function khi đánh giá ROC AUC; đây là điểm quyết định, không phải xác suất đã hiệu chỉnh.

### Diễn giải cho lần chạy đã lưu

CV chọn không scaling (passthrough), RBF với C=10, gamma=0,001. Baseline và cấu hình sau tìm kiếm cùng đạt 95,29% test (283/297 mẫu), trong khi CV khoảng 99,4%. CV xáo trộn trong 1.500 mẫu train; test là 297 mẫu cuối theo cách chia của PDF, có thể khác độ khó. Không thay cách chia hoặc chọn lại tham số chỉ để nâng điểm test này.
