# Rà soát tiến độ so với proposal

Ngày rà soát: 06/11/2026, trên commit `442fca3` cộng các thay đổi chưa commit mô tả trong mục 2. Mọi kết quả là trên **validation**; test chưa được dùng.

## 1. Đối chiếu với proposal

| Hạng mục trong proposal / README | Trạng thái | Bằng chứng |
| --- | --- | --- |
| EDA và trực quan hóa | Đã có | `notebooks/eda/eda.ipynb`, `figures/traffic_*.png` |
| Kiểm tra chất lượng dữ liệu | Đã có | `notebooks/eda/data_validation.ipynb`, `docs/station_data_info.docx` |
| Gộp timestamp, điền thiếu, chia 70/15/15 | Đã có | `preprocessing_features.ipynb` Bước 02–07; `src/data.py` cho kết quả trùng khớp |
| `hour`, `day_of_week`, `month`, `is_weekend`, `temp_c`, `is_holiday` | Đã có | `preprocessing_features.ipynb` Bước 05, 08 |
| `is_rush_hour`, sin/cos, mã hóa thời tiết, đặc trưng lịch sử | Mới bổ sung, cần Phúc xem lại | `src/features.py`; căn cứ ở `V_2.ipynb` mục 2.3 và `V_3.ipynb` mục 3.2 |
| Encoding/scaling fit theo train | Mới bổ sung | Pipeline Ridge trong `src/models.py` (one-hot, imputer, scaler fit trong từng fold) |
| Baseline trung bình thứ–giờ | Đã có | V_1, MAE 285,03 |
| Baseline Ridge | Đã có | V_1 (one-hot riêng, 581,94); V_2 (one-hot cặp thứ–giờ, 285,13) |
| Baseline seasonal naive | Mới bổ sung | `V_4.ipynb`, MAE 330,18 trên 6.050 giờ |
| Ridge, Random Forest, XGBoost | Đã có | V_2–V_4. LightGBM chưa thử (proposal ghi XGBoost **hoặc** LightGBM) |
| Tuning bằng TimeSeriesSplit + Random Search | Mới bổ sung | `src/models.py`: 3 fold, cùng lưới và số lượt thử cho mọi cấu hình. Optuna chưa dùng |
| Đối chứng A–B (thời tiết) | Mới bổ sung | `V_3.ipynb` |
| Đối chứng B–C (lịch sử) | Mới bổ sung | `V_4.ipynb` |
| Phân tích sai số theo giờ/ngày lễ/thời tiết | Mới bổ sung | `error_analysis_validation.ipynb`, `figures/error_by_*.png` |
| Feature importance, SHAP | Mới bổ sung | `error_analysis_validation.ipynb` mục 6, `figures/shap_time_weather.png` |
| Đánh giá test (V_5) | **Chưa làm** | Cần nhóm chốt các quyết định ở mục 4 trước |
| Demo Streamlit Time + Weather | Mới bổ sung | `app/demo_time_weather.py` |
| File môi trường | Mới bổ sung | `requirements.txt` |
| Báo cáo giữa kỳ | **Chưa làm** | `outputs/Mau_Bao_cao_giua_ky_Nhom_07.docx` vẫn là mẫu trống |
| Slide | **Chưa làm** | Chưa có file |

## 2. Những gì đã bổ sung trong lần này

- `src/data.py`, `src/features.py`, `src/evaluation.py` trước đây rỗng; nay chứa quy trình dùng chung. Thêm `src/models.py`. `src/data.py` được đối chiếu bằng cách chạy lại toàn bộ code của `preprocessing_features.ipynb`: ba tập sau điền thiếu trùng khớp từng cột.
- Chạy lại `V_1.ipynb` (tắt ghi log): bảng so sánh validation trùng output đã lưu.
- Ba notebook thí nghiệm trong `notebooks/experiments/` và một notebook phân tích trong `notebooks/evaluation/` cùng output, nhận xét và log `EXP_007`–`EXP_027`.
- `outputs/metrics/`, `outputs/predictions/`: metrics, tham số được chọn và dự đoán validation để notebook sau dùng lại.
- Sheet `Validation V2-V4` trong `experiments/experiment_log.xlsx`.
- Cập nhật README dự án, README các phiên bản V_1–V_4 và hướng dẫn nhật ký.

## 3. Kết quả chính trên validation

| Bước | XGBoost MAE | Thay đổi | Ghi chú |
| --- | --- | --- | --- |
| Trung bình thứ–giờ | 285,03 | — | Mốc V_1 |
| T1 — thêm đặc trưng lịch | 278,90 | −6,08 (CI chứa 0) | Chưa cải thiện rõ |
| A — thêm `is_holiday` | 244,94 | −33,95 (CI 15,64–55,43) | Cải thiện rõ nhất trong nhóm thời gian |
| B — thêm thời tiết | 243,45 | −1,49 (CI chứa 0) | Rõ hơn ở giờ ban ngày ngày làm việc (−14,47), kém hơn ở giờ lễ |
| C — thêm lịch sử | 192,94 | −50,10 so với B trên cùng 6.050 giờ | Giả định đã biết lưu lượng đến `t − 1` |

Trả lời ngắn cho ba câu hỏi nghiên cứu, ở mức validation:

1. Giờ và thứ chiếm phần lớn đóng góp (SHAP: 73,6% và 17,1%). Thời tiết chiếm 3,2%.
2. Mô hình tốt nhất là XGBoost (Random Forest rất sát). Thời tiết cải thiện khoảng 0,6–1,2% so với Time + ngày lễ, chưa đủ rõ so với dao động theo ngày.
3. Sai nhiều ở giờ cao điểm 07:00 và 16:00, ngày lễ và ngày sát lễ, giai đoạn 07–11/2017 (dự đoán thấp liên tục) và ngày có tuyết.

## 4. Quyết định nhóm cần chốt trước V_5

| Quyết định | Căn cứ hiện có | Người liên quan |
| --- | --- | --- |
| Có bổ sung 3 ngày lễ thiếu nhãn theo lịch liên bang không | V_2 mục 2.2, 2.7: dữ liệu đúng hơn, MAE gần như không đổi | Phúc, Vũ |
| Có coi `temp = 276.793` (78 giờ, 10/2013–01/2014) là thiếu không | V_3 mục 3.6: nhiệt độ trung bình các giờ này 276,34 K, sau khi che còn 261,94 K | Phúc, Vũ |
| Có bỏ 46 giờ đóng đường 22–24/07/2016 khỏi train không | V_3 mục 3.6: MAE giảm khoảng 4,1, lớn hơn dao động do seed; `docs/station_data_info.docx` | Phúc, Vũ |
| Mô hình và cấu hình cuối, có fit lại trên train + validation trước khi chạy test không | V_2–V_4 | Huy, Hào |
| Kịch bản báo cáo chính: B (demo) hay C (có lịch sử) | B không cần lưu lượng thời gian thực; C tốt hơn nhiều | Cả nhóm |

Khi đổi quy tắc dữ liệu, bật tham số tương ứng trong `src/data.py` (`mask_stuck_temp`, `complete_holidays`) hoặc thêm bước lọc, cập nhật `preprocessing_features.ipynb`, rồi chạy lại V_2 → V_4 để giữ so sánh công bằng. Test chỉ chạy **một lần** sau khi đã chốt.

## 5. Việc còn thiếu, theo thứ tự đề xuất

1. Chốt các quyết định ở mục 4.
2. Thử đặc trưng biết trước cho các lỗi lớn: loại lễ, ngày sát lễ, kỳ nghỉ cuối năm; kiểm tra bằng CV trong train.
3. V_5: fit cấu hình đã chốt, đánh giá test một lần, ghi log.
4. Điền báo cáo giữa kỳ theo mẫu trong `outputs/`, dùng số liệu và hình từ các notebook; làm slide.
5. Tùy chọn: LightGBM hoặc Optuna nếu còn thời gian; thử thời tiết của giờ trước để mô phỏng việc chỉ có dự báo.

## 6. Ghi chú nhỏ phát hiện khi rà soát

- `README.md` ở gốc repo ghi nhóm trưởng là Phùng Anh Vũ; proposal, README dự án và mẫu báo cáo ghi Trần Nhựt Huy. Cần thống nhất.
- Thư mục `.jupyter-tmp/` ở gốc repo chứa ảnh tạm đã được commit.
- `V_1.ipynb` đang lưu `SAVE_EXPERIMENT_LOGS = True`. Chạy lại toàn bộ notebook sẽ tạo thêm 6 log trùng, trái với hướng dẫn trong `docs/experiment_tracking/README.md`.
- `preprocessing_features.ipynb` Bước 08: lệnh `print` danh sách cột nằm trong vòng lặp nên in ba lần.
- Các lần chạy trong rà soát dùng Python 3.13.9; V_1 gốc chạy trên Python 3.14.7. Hai môi trường cho cùng kết quả V_1.
