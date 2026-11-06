# V_3 — Time + Weather

**Trạng thái:** Đã có thí nghiệm trên validation; test chưa dùng.

- Notebook: [baseline_V_3.ipynb](../../../notebooks/BASELINE/baseline_V_3.ipynb); cần chạy V_2 trước.
- Thời tiết: `temp_c`, `rain_1h`, `snow_1h`, `clouds_all` và 11 cờ nhóm `weather_*` tách từ nhãn gộp theo giờ.
- Kết quả chính: XGBoost MAE 243,45 so với A 244,94; giảm 0,6–1,2% ở cả ba mô hình, CI 95% chứa 0. Ở giờ ban ngày ngày làm việc, thời tiết giảm 14,47 xe/giờ (CI 5,03–25,05); ở giờ lễ, B kém A.
- Độ nhạy: bỏ 46 giờ đóng đường 22–24/07/2016 khỏi train giảm MAE khoảng 4,1; che nhiệt độ lặp `276.793` và bổ sung ngày lễ thay đổi trong mức dao động do seed. Các quy tắc này chưa được áp dụng mặc định.
- Giới hạn: dùng thời tiết quan trắc cùng giờ, chưa đo với dự báo thời tiết.
- Log: EXP_016–EXP_018.
