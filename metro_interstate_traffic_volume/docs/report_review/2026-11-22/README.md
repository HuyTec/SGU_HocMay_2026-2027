# Hồ sơ rà soát báo cáo ngày 22/11/2026

Đọc [report_review.md](report_review.md) trước: tóm tắt, bản đồ sự thật, đủ 114 hàng truy vết, 17 đề xuất sửa có đoạn thay thế, phần cần bổ sung và việc chưa xác minh.

- [replacement_proposals.md](replacement_proposals.md): chỉ các đoạn sửa/bổ sung để duyệt và dán.
- [trace_matrix.csv](trace_matrix.csv): 97 tuyên bố, 16 phần bổ sung, một giới hạn kiểm công thức; có nguyên văn và giải thích.
- [agent_a/report_snapshot.txt](agent_a/report_snapshot.txt): bản chụp Google Docs, 408 đoạn có định vị; [metadata](agent_a/snapshot_metadata.json).
- [agent_a/claims.md](agent_a/claims.md), [agent_a/issues.md](agent_a/issues.md): danh mục đầy đủ của agent đọc báo cáo.
- [agent_b/facts.md](agent_b/facts.md): 46 nhóm bằng chứng từ source và kết quả đã lưu.
- [verification.json](verification.json): kiểm tra độ bao phủ, mã tham chiếu, vị trí nguồn và hash bản chụp.

Không sửa Google Docs, source, notebook hoặc kết quả thực nghiệm. Không fit hoặc chấm test. Các lệnh đọc dữ liệu và đối chiếu hash không tạo thêm kết quả mô hình.

Mô hình chốt hiện có MAE 190,1900 trên 6.050 giờ validation. Đặc tả ghi chưa refit cuối và chưa chấm test. Validation đã xem nhiều lần; kết quả có tính thăm dò. Chín ảnh đã được kiểm nội dung; 28 equation native và bố cục trang chưa được xác minh.

Mã Pxxxx chỉ có ý nghĩa đối với snapshot đang lưu. Nếu báo cáo thay đổi, cần đối chiếu lại vị trí và trích dẫn trước khi dán.
