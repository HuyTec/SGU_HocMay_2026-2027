OOF chọn RF 60%/XGBoost 40% trên 16,875 giờ, giảm MAE trung bình fold 0.0249 xe/giờ so với 50/50. Trên cùng 6,050 giờ validation, MAE 50/50 là 193.8102, còn ensemble OOF là 193.9326 xe/giờ. Chênh RMSE (50/50 trừ OOF) là -1.4955 xe/giờ. Giữ ensemble 50/50 làm phương án hiện tại; trọng số OOF chưa cải thiện MAE validation.

Sai số RF và XGBoost có tương quan 0.949; 87.6% giờ sai cùng chiều. Đổi trọng số không sửa được hướng sai ở những giờ đó. Giờ 07 có MAE 50/50 cao nhất trong phân nhóm giờ; 10% giờ lỗi lớn nhất đóng góp 39.7% tổng sai số tuyệt đối. Các mẫu hình này mô tả validation, không chứng minh nguyên nhân.

Khoảng bootstrap chứa 0, chưa tách được chênh lệch khỏi mức bất định theo cách lấy mẫu này. Validation đã được xem nhiều lần; bootstrap theo ngày chưa bao quát hết phụ thuộc qua nhiều ngày. Một seed, ba fold và lưới trọng số hữu hạn chưa chứng minh đã đạt giới hạn của bài toán. Phân tích chưa huấn luyện lại và chưa chấm test.
