# V_1 — Time-only

**Trạng thái:** Đã chạy lại ngày 06/11/2026 với Python 3.13.9, pandas 3.0.6, scikit-learn 1.9.1 (tắt ghi log); bảng so sánh validation trùng output đã lưu. Phân tích sai số cho cấu hình có ngày lễ và thời tiết nằm ở `notebooks/evaluation/error_analysis_validation.ipynb`.

- [Chỉ mục notebook V_1 và EDA chung](../../../notebooks/versions/V_1_time_only/README.md).
- Notebook đang sử dụng: [baseline_time-only.ipynb](../../../notebooks/experiments/V_1.ipynb).
- Đầu vào hiện tại: `weekday`, `hour`; chưa dùng ngày lễ, thời tiết hoặc lịch sử.
- Nhật ký hiện có: [EXP_001](../../../experiments/EXP_001.txt), [EXP_002](../../../experiments/EXP_002.txt), [EXP_003](../../../experiments/EXP_003.txt), [EXP_004](../../../experiments/EXP_004.txt), [EXP_005](../../../experiments/EXP_005.txt), [EXP_006](../../../experiments/EXP_006.txt).
- [Bảng tổng hợp hiện có](../../../experiments/experiment_log.xlsx) là ảnh chụp, không tự cập nhật.
- Test được giữ riêng theo các log; các metrics đã ghi là validation.

Notebook trên là bản làm việc duy nhất cho V_1; không tạo bản sao trong thư mục này. Khi chạy lại, lưu ý cell `SAVE_EXPERIMENT_LOGS`: giá trị `True` tạo thêm log mới.

Các log đã ghi trước khi đổi tên notebook vẫn giữ đường dẫn lịch sử; không sửa nội dung log cũ. Chưa có pipeline Python hoặc notebook EDA riêng cho V_1.
