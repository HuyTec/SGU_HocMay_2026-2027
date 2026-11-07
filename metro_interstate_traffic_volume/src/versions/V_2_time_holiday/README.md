# V_2 — Time + ngày lễ

**Trạng thái:** Đã có thí nghiệm trên validation; test chưa dùng.

- Notebook: [V_2.ipynb](../../../notebooks/experiments/V_2.ipynb).
- Cấu hình: `T0_thu_gio` (giờ, thứ), `T1_lich` (thêm tháng, cuối tuần, cao điểm, sin/cos), `A_lich_le` (thêm `is_holiday` theo nhãn CSV, gắn cho cả ngày).
- Mô hình: Ridge (one-hot cặp thứ–giờ), Random Forest, XGBoost; cùng lưới tuning trong `src/models.py`, 3 fold `TimeSeriesSplit` trong train.
- Kết quả chính: XGBoost `A_lich_le` MAE 244,94; thêm `is_holiday` giảm 33,95 xe/giờ (CI 95% theo ngày: 15,64–55,43).
- Phát hiện dữ liệu: 3 ngày lễ liên bang có dữ liệu nhưng thiếu nhãn vì thiếu dòng 00:00 (21/01/2013, 04/07/2014, 18/01/2016); bổ sung chưa làm thay đổi rõ MAE.
- Log: EXP_007–EXP_015. Kết quả lưu: `outputs/metrics/V_2_*`, `outputs/predictions/V_2_validation.csv`.
