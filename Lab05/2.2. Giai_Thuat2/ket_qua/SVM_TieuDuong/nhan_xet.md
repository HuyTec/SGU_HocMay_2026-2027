### Nhận xét kết quả

- Train **76,916 mẫu**, test **19,230 mẫu**. Siêu tham số được chọn bằng **roc_auc**, 4-fold CV trên train.

- Tham số chọn trong lưới: **{'svc__C': 10, 'svc__class_weight': 'balanced'}**. Điểm CV **0.9615**; chênh lệch train - validation tại cấu hình này **0.0001**.

- SVM sau tìm kiếm đạt test accuracy **0.8854**, balanced accuracy **0.8863**, F1-macro **0.7555**.

- Nếu luôn đoán lớp phổ biến, accuracy là **0.9118**. Cần đọc thêm confusion matrix và chỉ số từng lớp để tránh đánh giá sai khi nhãn mất cân bằng.

- Khoảng cách điểm train/validation là dấu hiệu tham khảo về quá khớp, không đo trực tiếp bias/variance. Cấu hình được chọn chỉ tốt nhất trong lưới đã thử.

- Pipeline chỉ fit scaler/imputer/encoder trên phần train của từng fold. Không chọn lại siêu tham số theo test. SVC/LinearSVC dùng decision_function khi đánh giá ROC AUC; đây là điểm quyết định, không phải xác suất đã hiệu chỉnh.

- Lớp ít mẫu là **1**, có **1696 mẫu test**. Precision **0.4278**, recall **0.8874**.

### Diễn giải sự đánh đổi của trọng số lớp

Theo ROC AUC trên CV, lưới chọn LinearSVC(C=10, class_weight=balanced). Trên test, recall lớp 1 tăng từ 62,09% của baseline lên 88,74%, nhưng precision giảm từ 89,01% xuống 42,78%; accuracy cũng giảm từ 95,98% xuống 88,54%. Mức tăng AUC nhỏ không đồng nghĩa mô hình tốt hơn ở mọi chỉ số hoặc ở ngưỡng quyết định mặc định. Báo cáo cả hai cấu hình để thể hiện rõ sự đánh đổi, giữ nguyên quy tắc chọn đã đặt trước khi xem test.
