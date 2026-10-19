### Nhận xét kết quả

- Train **672 mẫu**, test **169 mẫu**. Siêu tham số được chọn bằng **balanced_accuracy**, 4-fold CV trên train.

- Tham số chọn trong lưới: **{'svc__C': 0.1, 'svc__class_weight': 'balanced', 'svc__gamma': 'scale', 'svc__kernel': 'rbf'}**. Điểm CV **0.7805**; chênh lệch train - validation tại cấu hình này **0.2195**.

- SVM sau tìm kiếm đạt test accuracy **1.0000**, balanced accuracy **1.0000**, F1-macro **1.0000**.

- Nếu luôn đoán lớp phổ biến, accuracy là **0.9763**. Cần đọc thêm confusion matrix và chỉ số từng lớp để tránh đánh giá sai khi nhãn mất cân bằng.

- Khoảng cách điểm train/validation là dấu hiệu tham khảo về quá khớp, không đo trực tiếp bias/variance. Cấu hình được chọn chỉ tốt nhất trong lưới đã thử.

- Pipeline chỉ fit scaler/imputer/encoder trên phần train của từng fold. Không chọn lại siêu tham số theo test. SVC/LinearSVC dùng decision_function khi đánh giá ROC AUC; đây là điểm quyết định, không phải xác suất đã hiệu chỉnh.

- Lớp ít mẫu là **0**, có **4 mẫu test**. Precision **1.0000**, recall **1.0000**.

### Diễn giải giới hạn của điểm test 100%

Cấu hình chọn là RBF, C=0,1, gamma=scale, class_weight=balanced. Dự đoán đúng 169/169 mẫu test, nhưng lớp No chỉ có 4 mẫu. Balanced accuracy trung bình CV là 78,05% và điểm train là 100%, chênh lệch khoảng 21,95 điểm phần trăm. Điều này cho thấy một lần chia test thuận lợi không chứng minh mô hình luôn đạt 100%; cần thêm dữ liệu lớp No và đánh giá nhiều lần nếu mở rộng nghiên cứu.
