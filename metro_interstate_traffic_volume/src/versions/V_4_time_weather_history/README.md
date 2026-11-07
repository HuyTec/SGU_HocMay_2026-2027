# V_4 — Time + Weather + History

**Trạng thái:** Đã có thí nghiệm trên validation; test chưa dùng.

- Notebook: [baseline_V_4.ipynb](../../../notebooks/experiments/baseline_V_4.ipynb); cần chạy V_3 trước.
- Lịch sử: `lag_24h`, `lag_168h`, `mean_24h` (cửa sổ `[t − 24 giờ, t)`, ít nhất 18 giờ), tra theo timestamp; giờ thiếu lịch sử giữ `NaN`.
- Đánh giá trên 6.050/6.086 giờ validation đủ lịch sử; train đủ lịch sử 22.503/28.402 giờ.
- Kết quả chính: seasonal naive 330,18; trung bình thứ–giờ 284,98; B 243,04; C (XGBoost, toàn bộ train) 192,94. Cùng train đủ lịch sử, thêm lịch sử giảm 58,36 xe/giờ (CI 46,45–71,03).
- Giả định: đánh giá tuần tự từng giờ, lưu lượng đến `t − 1` đã được ghi nhận.
- Log: EXP_019–EXP_027.
