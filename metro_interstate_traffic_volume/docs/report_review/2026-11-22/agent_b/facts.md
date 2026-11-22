# Bản đồ sự thật của repo — 22/11/2026

Phạm vi: chỉ đọc source, notebook và hiện vật đã lưu. Không huấn luyện lại, không chấm test, không sửa file gốc. Chỉ đối chiếu dữ liệu và SHA256 bằng thao tác đọc.

Mô hình đã khóa là **C30: RF25% + XGBoost25% + ExtraTrees50%**. MAE validation đã lưu là **190,190 xe/giờ trên 6.050 giờ**. Chưa refit trên train + validation; chưa có điểm test cho mô hình cuối. Đây là kết quả thăm dò sau nhiều lần xem validation.

## Cấu trúc và điểm chạy

```text
data/Metro_Interstate_Traffic_Volume.csv   dữ liệu gốc
data/preprocessed/hourly_unfilled.csv   bảng sạch, chưa học điền thiếu
data/processed/                        đầu ra pipeline lịch sử
notebooks/preprocessing/               xuất bảng sạch
notebooks/eda/                         EDA_general toàn CSV; A/B/C trên train
notebooks/features/                    năm phương án RF cố định
notebooks/tuning/                      A12/B27/C30 cùng CV, chọn tham số
experiments/20-11-2026_Huy_C30_Params*/ fit train và so validation hai bộ tham số
experiments/21-11-2026_Huy_C30_OOF/      thử trọng số OOF
experiments/22-11-2026_Huy_C30_MAE_Diversity/ thử loss/mô hình bổ sung
notebooks/validation/outputs/final_C30/ đặc tả và bảng chốt, chưa phải checkpoint
src/{data,preprocessing,features}.py    đọc, làm sạch, tạo đặc trưng
src/feature_experiments.py             cohort, fold, dữ liệu FE
src/{model,tuning_cv,evaluation}.py      mô hình, tìm kiếm chung, metrics
src/eda/helpers.py                     thống kê và vẽ EDA
src/{models_exp,tuning_exp}.py          mã thí nghiệm lịch sử
src/prepare_data.py                    entrypoint processed lịch sử
app/demo_time_weather.py               toàn bộ chú thích
```

Entry point thực nghiệm chính nằm trong notebook. FE gọi load_protocol → prepare_fold → run_configuration; tuning gọi src/tuning_cv.py. src/prepare_data.py:105 có entrypoint CLI lịch sử; không nhầm processed với nguồn preprocessed của FE hiện tại. Chưa tìm thấy entrypoint fit cuối/inference hoạt động hoặc checkpoint .pkl/.joblib/.ubj. README validation đang liên kết một số notebook/module không tồn tại (B-040).

## Mô hình cuối và tham số

| Thành phần | Tham số quan trọng | Nguồn |
|---|---|---|
| RF 25% | 100 cây; depth=None; leaf=2; max_features=0.33; bootstrap=True; criterion=squared_error | B-031 |
| XGBoost 25% | 400 cây; depth=6; learning_rate=0.03; subsample=0.7; colsample_bytree=0.8; min_child_weight=1; objective=reg:squarederror; tree_method=hist | B-032 |
| ExtraTrees 50% | 200 cây; depth=None; leaf=2; max_features=0.8; bootstrap=False; criterion=squared_error | B-033 |

Cả ba seed=42, n_jobs=4. Mô hình cây không dùng epoch/batch size như MLP. Thư viện ghi theo frozen manifest; Python chỉ được xác minh từ log nguồn Params1 và bước tiền xử lý, không có trong frozen library_versions.

Các bộ tham số tuning C30 dưới đây khác bộ cuối từ nhánh Claude tái dựng:

| Mô hình tuning | best_params đã lưu |
|---|---|
| Ridge | `{"model__alpha": 0.1}` |
| Random Forest | `{"model__n_estimators": 400, "model__min_samples_leaf": 5, "model__max_features": 0.33, "model__max_depth": 16}` |
| Gradient Boosting | `{"model__n_estimators": 200, "model__max_depth": 3, "model__learning_rate": 0.1}` |
| MLP | `{"model__regressor__learning_rate_init": 0.003, "model__regressor__hidden_layer_sizes": [64], "model__regressor__alpha": 0.01}` |
| XGBoost | `{"model__subsample": 1.0, "model__min_child_weight": 1, "model__max_depth": 6, "model__learning_rate": 0.03}` |

Nguồn: notebooks/tuning/outputs/C30/results.json. Ridge dùng one-hot weekday_hour/month và chuẩn hóa phần số; MLP scale X/y, max_iter=500. Số tham số học được, mặc định activation/solver/batch size và convergence từng fit chưa được xác minh từ artifact đã lưu.

## Bảng điểm — chỉ so trong cùng giao thức

| Giai đoạn | Cấu hình/mô hình | n chấm | MAE | RMSE | Bằng chứng |
|---|---|---:|---:|---:|---|
| FE cố định | V5_C30 | 16875 | 247.9260 | 412.9069 | B-020 |
| FE cố định | V1_A12 | 16875 | 288.3182 | 469.6859 | B-020 |
| FE cố định | V3_labels23 | 16875 | 290.0372 | 470.7517 | B-020 |
| FE cố định | V4_B27 | 16875 | 290.7253 | 473.6463 | B-020 |
| FE cố định | V2_numeric16 | 16875 | 291.5528 | 476.4187 | B-020 |
| Tuning CV | C30 Ridge | 16875 | 261.9641 | 417.4234 | B-025 |
| Tuning CV | C30 Random Forest | 16875 | 231.0395 | 381.3597 | B-025 |
| Tuning CV | C30 Gradient Boosting | 16875 | 255.9309 | 410.3063 | B-025 |
| Tuning CV | C30 MLP | 16875 | 277.1134 | 418.1760 | B-025 |
| Tuning CV | C30 XGBoost | 16875 | 235.9835 | 386.0600 | B-025 |
| Tuning CV | common Mean weekday-hour | 16875 | 305.6283 | 512.5212 | B-025 |
| Tuning CV | common Seasonal naive 168h | 16875 | 336.7889 | 619.3206 | B-025 |
| Validation | RF 25% + XGBoost 25% + ExtraTrees 50% | 6050 | 190.1900 | 313.5266 | B-034 |
| Validation | ExtraTrees | 6050 | 191.2160 | 319.8542 | B-034 |
| Validation | RF/XGBoost 50/50 | 6050 | 193.8102 | 316.0848 | B-034 |
| Validation | RF/XGBoost chọn trọng số OOF | 6050 | 193.9326 | 317.5803 | B-034 |
| Validation | Random Forest | 6050 | 196.7748 | 326.7725 | B-034 |
| Validation | XGBoost | 6050 | 197.0314 | 313.6397 | B-034 |
| Validation | Baseline thứ–giờ | 6050 | 291.7388 | 503.2185 | B-034 |
| Validation | Baseline seasonal naive | 6050 | 330.1775 | 635.0735 | B-034 |

CV và validation khác tập giờ, khoảng lịch và kích thước train. Chỉ đọc thứ hạng trong từng nhóm. Không gọi R²≈0,97 là 97% số giờ dự đoán đúng. Không thay câu hỏi đóng góp thời tiết bằng chiến thắng của C30 có history.

## Phát hiện có bằng chứng

### B-001 — Phạm vi kiểm tra

Rà soát chỉ đọc source, notebook và log; không huấn luyện hoặc chấm test.

Bằng chứng: `docs/report_review/2026-11-22/agent_b/read_only_checks.json:2`.

### B-002 — Quy mô dữ liệu

Dữ liệu gốc có 48.204 dòng, 9 cột, 40.575 timestamp; 7.629 dòng dư theo thời gian, 17 dòng trùng hoàn toàn và 11.976 giờ thiếu.

Bằng chứng: `notebooks/preprocessing/outputs/preprocessing_manifest.json:6`; `notebooks/eda/EDA_general.ipynb:749`; `docs/report_review/2026-11-22/agent_b/read_only_checks.json:3`.

Giới hạn: Không gọi toàn bộ 7.629 dòng là duplicate hoàn toàn; chưa phân tích DST.

### B-003 — Timestamp lặp

Có 5.445 timestamp lặp với 13.074 dòng; target trong mỗi timestamp nhất quán.

Bằng chứng: `notebooks/eda/EDA_general.ipynb:749`; `notebooks/eda/EDA_general.ipynb:750`; `notebooks/eda/EDA_general.ipynb:1078`; `notebooks/eda/EDA_general.ipynb:1079`.

### B-004 — Đọc CSV

Đọc CSV với keep_default_na=False để giữ nhãn holiday="None".

Bằng chứng: `src/data.py:28`; `src/data.py:30`.

### B-005 — Gộp theo giờ

Gộp target nhất quán theo giờ; thời tiết lấy median các giá trị phân biệt, nhãn lấy tập hợp đã chuẩn hóa.

Bằng chứng: `src/preprocessing.py:8`; `src/preprocessing.py:23`; `src/preprocessing.py:56`; `src/preprocessing.py:65`; `src/preprocessing.py:71`.

### B-006 — Ngoại lệ

Đánh dấu temp=0 K và đúng điểm mưa 9.831,3 mm là thiếu; giữ các giờ target=0.

Bằng chứng: `src/preprocessing.py:42`; `src/preprocessing.py:49`; `notebooks/eda/EDA_general.ipynb:3187`; `notebooks/eda/EDA_general.ipynb:3261`; `notebooks/eda/EDA_general.ipynb:3262`.

Giới hạn: Mask không có nghĩa đã xác minh nguyên nhân cảm biến; rain outlier là quy tắc cụ thể của repo.

### B-007 — Một CSV bàn giao

Một CSV sạch được xuất tại data/preprocessed/hourly_unfilled.csv: 40.575 dòng, 10 cột; còn 10 temp và 1 rain_1h thiếu. Chưa fit imputation; không điền target.

Bằng chứng: `notebooks/preprocessing/outputs/preprocessing_manifest.json:4`; `notebooks/preprocessing/outputs/preprocessing_manifest.json:21`; `notebooks/preprocessing/outputs/preprocessing_manifest.json:30`; `docs/report_review/2026-11-22/agent_b/read_only_checks.json:22`.

### B-008 — Ngày lễ

Cờ ngày lễ áp dụng cho cả ngày có nhãn trong CSV; chưa bổ sung lịch ngoài.

Bằng chứng: `src/data.py:101`; `src/data.py:109`; `src/data.py:115`; `src/data.py:117`; `notebooks/preprocessing/outputs/preprocessing_manifest.json:30`.

Giới hạn: Nhãn lễ có thể không đầy đủ; không diễn giải is_holiday=0 như chắc chắn không phải ngày lễ.

### B-009 — Split lịch

Chia theo thứ tự giờ quan sát 70/15/15: train 28.402, validation 6.086, test 6.087. Ranh giới train/validation là 10/05/2017 04:00/05:00; validation/test là 19/01/2018 14:00/15:00.

Bằng chứng: `src/preprocessing.py:137`; `src/preprocessing.py:140`; `src/preprocessing.py:147`; `docs/report_review/2026-11-22/agent_b/read_only_checks.json:41`.

Giới hạn: Tỷ lệ theo số giờ có dữ liệu, không phải các khoảng lịch liên tục bằng tỷ lệ.

### B-010 — Điền thiếu

Điền temp bằng quan sát gốc trước tối đa 6 giờ, rồi median tháng–giờ hoặc median toàn fit. Điền rain bằng median của fit.

Bằng chứng: `src/preprocessing.py:151`; `src/preprocessing.py:157`; `src/preprocessing.py:198`; `src/preprocessing.py:216`; `src/preprocessing.py:235`; `src/preprocessing.py:251`.

### B-011 — An toàn fold

prepare_fold chỉ học median trên fold-train; giữ các quan sát thời tiết gốc ngoài cohort làm ngữ cảnh. Không điền median cho lag.

Bằng chứng: `src/feature_experiments.py:133`; `src/feature_experiments.py:141`; `src/feature_experiments.py:148`; `src/feature_experiments.py:153`.

### B-012 — A12

A12 gồm 11 đặc trưng lịch và cờ is_holiday; 6 trong số đó là sin/cos của giờ, thứ, tháng.

Bằng chứng: `src/features.py:212`; `src/features.py:217`; `src/features.py:223`; `src/features.py:239`.

### B-013 — B27

B27 thêm bốn biến thời tiết số và 11 cờ multi-label weather_main; temp đổi từ K sang °C.

Bằng chứng: `src/features.py:203`; `src/features.py:218`; `src/features.py:224`; `src/features.py:259`; `src/features.py:262`.

### B-014 — C30

C30 thêm lag_24h, lag_168h và mean_24h. Lag tra đúng timestamp; mean lấy [t−24h,t) với ít nhất 18 quan sát.

Bằng chứng: `src/features.py:209`; `src/features.py:221`; `src/features.py:225`; `src/features.py:279`; `src/features.py:283`.

Giới hạn: mean_24h không đòi đủ 24/24 giờ; cần ghi đúng tối thiểu 18 quan sát.

### B-015 — Phạm vi dự báo

Đây là dự đoán tuần tự từng giờ với target quá khứ đã quan sát. Thời tiết cùng giờ được giả định sẵn có; chưa phải dự báo cả đoạn tương lai từ một mốc.

Bằng chứng: `src/features.py:273`; `src/feature_experiments.py:256`; `notebooks/features/README.md:17`.

Giới hạn: Tính khả dụng thời tiết cùng giờ và độ trễ dữ liệu khi triển khai chưa được xác minh; không suy ra khả năng day-ahead.

### B-016 — EDA và FE

Ba notebook EDA_A/B/C chỉ mô tả train và không chọn cấu hình bằng CV. EDA_general mô tả toàn CSV. FE riêng so năm nhóm bằng cùng RF, fold và cohort, không brute force từng cột.

Bằng chứng: `notebooks/eda/README.md:5`; `notebooks/eda/EDA_general.ipynb:16`; `notebooks/features/README.md:15`.

Giới hạn: Phân biệt EDA_general toàn CSV với ba EDA trên train; không gọi bảng EDA toàn CSV là kết quả test.

### B-017 — Cohort và folds

Cả năm phương án FE dùng cohort train đủ history gồm 22.503 giờ. Ba fold có 5.625 mẫu chấm mỗi fold, tổng 16.875 OOF; số mẫu fit là 5.628, 11.253 và 16.878.

Bằng chứng: `src/feature_experiments.py:85`; `src/feature_experiments.py:87`; `notebooks/features/outputs/e4bc1e064317af8c/protocol.json:183`; `notebooks/features/outputs/e4bc1e064317af8c/fold_manifest.csv:2`.

Giới hạn: Loại cả những giờ A/B vốn có thể dự đoán; không suy rộng hiệu quả cho mọi giờ.

### B-018 — Khoảng lịch CV

Ba fold-score phủ 16.931, 10.163 và 5.867 giờ lịch; số mẫu bằng nhau không có nghĩa khoảng lịch bằng nhau.

Bằng chứng: `notebooks/features/outputs/e4bc1e064317af8c/fold_manifest.csv:2`; `notebooks/features/outputs/e4bc1e064317af8c/fold_manifest.csv:3`; `notebooks/features/outputs/e4bc1e064317af8c/fold_manifest.csv:4`.

Giới hạn: Ba cửa sổ lịch không bằng nhau; chỉ có ba fold và một seed.

### B-019 — RF cố định FE

FE dùng RF cố định: 400 cây, depth=12, leaf=5, max_features=1.0, seed=42, n_jobs=4; ma trận float32.

Bằng chứng: `src/feature_experiments.py:41`; `src/feature_experiments.py:42`; `src/feature_experiments.py:153`.

### B-020 — Kết quả FE

FE cùng RF cho MAE: C30=247,9260; A12=288,3182; labels23=290,0372; B27=290,7253; numeric16=291,5528. Không có bằng chứng mọi cột đều cần thiết.

Bằng chứng: `notebooks/features/outputs/e4bc1e064317af8c/feature_comparison.csv:2`; `notebooks/features/outputs/e4bc1e064317af8c/feature_comparison.csv:3`; `notebooks/features/outputs/e4bc1e064317af8c/feature_comparison.csv:4`; `notebooks/features/outputs/e4bc1e064317af8c/feature_comparison.csv:5`; `notebooks/features/outputs/e4bc1e064317af8c/feature_comparison.csv:6`.

Giới hạn: C30 thắng trong RF/tham số/cohort này; không chứng minh từng cột đều cần hoặc thời tiết vô ích.

### B-021 — Tuning hiện tại

Tuning so Ridge, RF, Gradient Boosting, MLP và XGBoost trên A12/B27/C30. Mỗi cặp có 6 ứng viên × 3 fold; tổng 270 fit, seed=42. Không chấm validation hoặc test trong bước này.

Bằng chứng: `src/model.py:18`; `src/tuning_cv.py:22`; `src/tuning_cv.py:56`; `src/tuning_cv.py:86`; `notebooks/tuning/outputs/rf_sampling_correction.json:408`.

### B-022 — Đặc thù Ridge/MLP

Ridge dùng one-hot weekday_hour/month và chuẩn hóa phần số; MLP chuẩn hóa X và y, max_iter=500. Không mô tả cả năm mô hình đều dùng cùng biểu diễn cột.

Bằng chứng: `src/model.py:84`; `src/model.py:118`; `src/model.py:128`; `src/model.py:129`; `src/model.py:135`.

Giới hạn: Ridge có biểu diễn lịch khác. Số tham số neural network chính xác và convergence của từng fit: CHƯA XÁC MINH.

### B-023 — Kiểm tra giao thức

tuning_compare kiểm tra protocol digest, candidates, timestamp/target/fold OOF, features, fold hash và điểm OOF. Ba protocol JSON hiện tại giống nhau; protocol_hash của ba results cùng khớp 6042efc8e56db7968fddaa33ee9d8b43d53c817fb778b15a7431d016a0576686.

Bằng chứng: `src/tuning_cv.py:197`; `src/tuning_cv.py:203`; `src/tuning_cv.py:215`; `src/tuning_cv.py:228`; `src/tuning_cv.py:235`; `src/tuning_cv.py:240`; `docs/report_review/2026-11-22/agent_b/read_only_checks.json:118`.

### B-024 — Sửa lỗi RF

Lỗi sampler RF cũ đã được sửa và có log. Kết quả C30 RF hiện tại là MAE CV=231,03948, RMSE=381,35972; 247,926 là FE hoặc kết quả tuning lỗi cũ.

Bằng chứng: `notebooks/tuning/outputs/rf_sampling_correction.json:3`; `notebooks/tuning/outputs/rf_sampling_correction.json:4`; `notebooks/tuning/outputs/rf_sampling_correction.json:415`.

Giới hạn: 247,926 là RF cố định FE hoặc lượt tuning lỗi cũ; 229,9 trong chat không phải điểm tuning hiện lưu.

### B-025 — Tuning C30

MAE CV C30 hiện tại: RF=231,0395; XGBoost=235,9835; GB=255,9309; Ridge=261,9641; MLP=277,1134. Không so trực tiếp các điểm CV này với validation để kết luận mức cải thiện.

Bằng chứng: `notebooks/tuning/outputs/comparison_summary.csv:12`; `notebooks/tuning/outputs/comparison_summary.csv:13`; `notebooks/tuning/outputs/comparison_summary.csv:14`; `notebooks/tuning/outputs/comparison_summary.csv:15`; `notebooks/tuning/outputs/comparison_summary.csv:16`.

### B-026 — Baseline/metric

Có hai baseline: trung bình thứ–giờ của train và seasonal naive lag_168h. Tất cả điểm qua regression_metrics đều cắt dự đoán âm về 0, rồi tính MAE, RMSE và R².

Bằng chứng: `src/evaluation.py:8`; `src/evaluation.py:13`; `src/evaluation.py:23`; `src/evaluation.py:32`.

### B-027 — Params1/Params2 ngược tên nhãn

Params1 chứa nhãn 02_claude_params và ensemble MAE validation=193,8102; Params2 chứa nhãn 01_current_params và MAE=197,2289. Tên thư mục không trùng thứ tự nhãn thí nghiệm.

Bằng chứng: `experiments/20-11-2026_Huy_C30_Params1/outputs/run_config.json:59`; `experiments/20-11-2026_Huy_C30_Params1/outputs/validation_metrics.csv:2`; `experiments/20-11-2026_Huy_C30_Params2/outputs/run_config.json:57`; `experiments/20-11-2026_Huy_C30_Params2/outputs/validation_metrics.csv:2`.

Giới hạn: Không suy thứ tự 01/02 hoặc current/Claude từ tên thư mục. Artifact Claude gốc chưa được xác minh; gọi là bộ tham số tái dựng.

### B-028 — Thử trọng số21/11

Lượt 21/11 chọn RF60/XGB40 bằng OOF; validation MAE=193,93255, chưa cải thiện RF50/XGB50=193,81022.

Bằng chứng: `experiments/21-11-2026_Huy_C30_OOF/outputs/selected_weights.json:52`; `notebooks/validation/outputs/final_C30/validation_comparison.csv:4`; `notebooks/validation/outputs/final_C30/validation_comparison.csv:5`.

### B-029 — Thử đa dạng22/11

Lượt 22/11 thử năm cấu hình mô hình mới, 15 fit CV và 16 phương án OOF. OOF chọn 50% ExtraTrees_leaf2 + 50% ensemble cũ; MAE OOF=225,27258 so đối chứng 227,24100.

Bằng chứng: `experiments/22-11-2026_Huy_C30_MAE_Diversity/outputs/verification.json:2`; `experiments/22-11-2026_Huy_C30_MAE_Diversity/outputs/selected_option.json:2`; `experiments/22-11-2026_Huy_C30_MAE_Diversity/outputs/selected_option.json:5`; `experiments/22-11-2026_Huy_C30_MAE_Diversity/outputs/selected_option.json:7`.

Giới hạn: OOF dùng để chọn nên không còn là ước lượng độc lập sau selection; ngân sách tìm kiếm nhỏ.

### B-030 — Mô hình đã khóa

Đặc tả được chốt: C30, RF25% + XGBoost25% + ExtraTrees50%, kết hợp bằng trung bình có trọng số.

Bằng chứng: `notebooks/validation/outputs/final_C30/selected_model.json:2`; `notebooks/validation/outputs/final_C30/selected_model.json:3`; `notebooks/validation/outputs/final_C30/selected_components.csv:2`; `notebooks/validation/outputs/final_C30/selected_components.csv:3`; `notebooks/validation/outputs/final_C30/selected_components.csv:4`.

### B-031 — RF cuối

RF cuối: 100 cây, depth=None, leaf=2, max_features=0.33, bootstrap=True, squared_error, seed=42, n_jobs=4.

Bằng chứng: `notebooks/validation/outputs/final_C30/selected_model.json:50`; `notebooks/validation/outputs/final_C30/selected_model.json:52`; `notebooks/validation/outputs/final_C30/selected_model.json:54`; `notebooks/validation/outputs/final_C30/selected_model.json:58`; `notebooks/validation/outputs/final_C30/selected_model.json:62`; `notebooks/validation/outputs/final_C30/selected_model.json:65`.

### B-032 — XGB cuối

XGBoost cuối: 400 cây, depth=6, learning_rate=0.03, subsample=0.7, colsample_bytree=0.8, min_child_weight=1, reg:squarederror, tree_method=hist, seed=42, n_jobs=4.

Bằng chứng: `notebooks/validation/outputs/final_C30/selected_model.json:73`; `notebooks/validation/outputs/final_C30/selected_model.json:79`; `notebooks/validation/outputs/final_C30/selected_model.json:90`; `notebooks/validation/outputs/final_C30/selected_model.json:95`; `notebooks/validation/outputs/final_C30/selected_model.json:97`; `notebooks/validation/outputs/final_C30/selected_model.json:100`; `notebooks/validation/outputs/final_C30/selected_model.json:108`; `notebooks/validation/outputs/final_C30/selected_model.json:138`.

### B-033 — ExtraTrees cuối

ExtraTrees cuối: 200 cây, depth=None, leaf=2, max_features=0.8, bootstrap=False, squared_error, seed=42, n_jobs=4. Mô hình được chốt không dùng loss MAE.

Bằng chứng: `notebooks/validation/outputs/final_C30/selected_model.json:117`; `notebooks/validation/outputs/final_C30/selected_model.json:119`; `notebooks/validation/outputs/final_C30/selected_model.json:121`; `notebooks/validation/outputs/final_C30/selected_model.json:125`; `notebooks/validation/outputs/final_C30/selected_model.json:129`; `notebooks/validation/outputs/final_C30/selected_model.json:132`.

Giới hạn: Mô hình cuối không dùng loss MAE dù có thử loss MAE trong các phương án khác.

### B-034 — Validation hiện tại

Trên 6.050 giờ validation đủ history, sau fit trên 22.503 giờ train, ensemble cuối đạt MAE=190,1899684; RMSE=313,5265898; R²=0,9745267. Đây là kết quả validation tốt nhất trong bảng cùng cohort đã lưu.

Bằng chứng: `notebooks/validation/outputs/final_C30/validation_scope.csv:2`; `notebooks/validation/outputs/final_C30/validation_comparison.csv:2`.

Giới hạn: Đây là kết quả validation tốt nhất đã quan sát trong bảng cùng cohort; R²=0,9745 không có nghĩa 97,45% số giờ dự đoán đúng.

### B-035 — Độ bất định validation

So RF50/XGB50, MAE giảm 3,62025 xe/giờ, CI bootstrap 95%=[1,63028;5,79750]. So ExtraTrees đơn, CI của mức giảm chứa 0. Validation đã được xem nhiều lần nên đây là phân tích thăm dò.

Bằng chứng: `notebooks/validation/outputs/final_C30/paired_bootstrap.csv:2`; `notebooks/validation/outputs/final_C30/paired_bootstrap.csv:3`.

Giới hạn: Validation đã xem nhiều lần; CI chỉ có ý nghĩa thăm dò và có điều kiện, không phải kiểm định độc lập.

### B-036 — Trạng thái cuối

Đặc tả cuối đã khóa, nhưng refit_completed=false và test_evaluated=false. Quét repo không thấy checkpoint dạng .pkl/.joblib/.ubj.

Bằng chứng: `notebooks/validation/outputs/final_C30/selected_model.json:3`; `notebooks/validation/outputs/final_C30/selected_model.json:193`; `notebooks/validation/outputs/final_C30/selected_model.json:194`; `notebooks/validation/outputs/final_C30/selected_model.json:195`; `docs/report_review/2026-11-22/agent_b/read_only_checks.json:105`.

Giới hạn: Cờ false chỉ áp dụng cho nhánh mô hình cuối này; không chứng minh toàn bộ lịch sử chưa có ai đọc test.

### B-037 — Integrity cấu hình

Tám artifact nguồn và bốn file source được hash trong frozen manifest đều tồn tại và khớp SHA256 hiện tại. Hash CSV gốc và CSV hourly khớp manifest tiền xử lý.

Bằng chứng: `notebooks/validation/outputs/final_C30/selected_model.json:147`; `notebooks/validation/outputs/final_C30/selected_model.json:183`; `docs/report_review/2026-11-22/agent_b/read_only_checks.json:53`; `docs/report_review/2026-11-22/agent_b/read_only_checks.json:87`.

Giới hạn: Hash đồng nhất không chứng minh kernel cũ đã nạp đúng code hoặc huấn luyện đã được tái lập.

### B-038 — Runtime lưu

Manifest cuối ghi numpy 2.5.3, pandas 3.0.6, scikit-learn 1.9.1 và xgboost 3.4.1, không ghi Python. run_config Params1 và manifest tiền xử lý ghi Python 3.14.7; requirements pin numpy 2.5.4 và comment Python 3.13.9.

Bằng chứng: `notebooks/validation/outputs/final_C30/selected_model.json:176`; `experiments/20-11-2026_Huy_C30_Params1/outputs/run_config.json:1596`; `notebooks/preprocessing/outputs/preprocessing_manifest.json:42`; `requirements.txt:1`; `requirements.txt:4`.

Giới hạn: Ghi phiên bản theo hiện vật của từng lượt; requirements không chứng minh runtime thực tế.

### B-039 — Demo chưa chạy

app/demo_time_weather.py toàn bộ là chú thích. File mô tả demo Time + Weather bằng XGBoost B lịch sử; chưa có entrypoint inference hoạt động nối với C30 hiện tại.

Bằng chứng: `app/demo_time_weather.py:1`; `app/demo_time_weather.py:6`; `docs/report_review/2026-11-22/agent_b/read_only_checks.json:112`.

Giới hạn: Demo Time + Weather có thể vẫn là phạm vi đề cương. C30 cần history đầu vào nên không tự thay thế giao diện hiện tại.

### B-040 — Liên kết thiếu

README validation liên kết validation_final_C30.ipynb, các notebook validation lịch sử và src/validation_main.py, nhưng các đường dẫn đại diện hiện không tồn tại. Thư mục kết quả final_C30 vẫn có.

Bằng chứng: `notebooks/validation/README.md:14`; `notebooks/validation/README.md:33`; `notebooks/validation/README.md:41`; `docs/report_review/2026-11-22/agent_b/read_only_checks.json:106`.

Giới hạn: Không báo các notebook này đã được tái tạo trong repo hiện tại; không tạo lại chúng trong đợt audit.

### B-041 — Thống kê mục tiêu trong báo cáo

Thống kê full hourly trong báo cáo khớp output đã lưu: mean=3.290,650474; std=1.984,772909; Q1=1.248,5; median=3.427; Q3=4.952; IQR=3.703,5; min=0; max=7.280, n=40.575.

Bằng chứng: `notebooks/eda/EDA_general.ipynb:8344`; `notebooks/eda/EDA_general.ipynb:8345`; `notebooks/eda/EDA_general.ipynb:8346`; `notebooks/eda/EDA_general.ipynb:8348`; `notebooks/eda/EDA_general.ipynb:8351`.

Giới hạn: Đây không phải thống kê raw 48.204 dòng (mean=3.259,818355) hoặc train 28.402 giờ.

### B-042 — Tương quan thời tiết trong báo cáo

Bảng tương quan sau gộp và mask khớp output: temp Pearson/Spearman=0,1392/0,1401 (n=40.565); rain=−0,0134/0,0043 (40.574); snow=−0,0021/−0,0052 và clouds=0,0783/0,0729 (40.575).

Bằng chứng: `notebooks/eda/EDA_general.ipynb:10391`; `notebooks/eda/EDA_general.ipynb:10392`; `notebooks/eda/EDA_general.ipynb:10393`; `notebooks/eda/EDA_general.ipynb:10394`.

Giới hạn: Tương quan riêng lẻ yếu không chứng minh không có giá trị bổ sung; không suy ra nhân quả.

### B-043 — Nhóm thời gian trong báo cáo

Bảng 3.6 khớp output toàn hourly: giờ 16 có mean=5.708,614528/n=1.707; giờ 3 là 373,210306/1.669; thứ Sáu là 3.674,777608/5.877; Chủ nhật là 2.426,249484/5.812; tháng 8 là 3.430,323887/3.705; tháng 12 là 3.040,194486/3.337.

Bằng chứng: `notebooks/eda/EDA_general.ipynb:8650`; `notebooks/eda/EDA_general.ipynb:8663`; `notebooks/eda/EDA_general.ipynb:8769`; `notebooks/eda/EDA_general.ipynb:8771`; `notebooks/eda/EDA_general.ipynb:8903`; `notebooks/eda/EDA_general.ipynb:8907`.

### B-044 — Nhóm nhãn thời tiết trong báo cáo

Bảng 3.8 khớp số giờ theo từng nhãn: Clouds=15.127, Clear=13.371, Rain=5.563, Snow=2.795, Smoke=20, Squall=4. Có 5.349 giờ mang nhiều nhãn; một giờ có thể nằm trong nhiều nhóm.

Bằng chứng: `notebooks/eda/EDA_general.ipynb:1259`; `notebooks/eda/EDA_general.ipynb:9589`; `notebooks/eda/EDA_general.ipynb:9590`; `notebooks/eda/EDA_general.ipynb:9592`; `notebooks/eda/EDA_general.ipynb:9593`; `notebooks/eda/EDA_general.ipynb:9598`; `notebooks/eda/EDA_general.ipynb:9599`.

Giới hạn: Nhóm hiếm chỉ mô tả, không suy luận nhân quả; tổng số nhóm không phải số giờ duy nhất.

### B-045 — Thiếu thô và thiếu sau mask

Output kiểm tra toàn CSV ghi 0 null và 0 chuỗi rỗng; temp=0 có 10 dòng. Điều này không mâu thuẫn CSV sạch còn 10 temp và 1 rain thiếu sau mask.

Bằng chứng: `notebooks/eda/EDA_general.ipynb:568`; `notebooks/eda/EDA_general.ipynb:575`; `notebooks/eda/EDA_general.ipynb:2961`; `docs/report_review/2026-11-22/agent_b/read_only_checks.json:22`.

### B-046 — Lịch sử không cùng giao thức

Năm nhóm lịch sử E05/E13/E15/E17/E18 được tổng hợp riêng, không xếp hạng toàn cục: E05 chỉ còn metrics làm tròn trong XLSX và khác snapshot; E13/E15 lặp A/B; E18 đọc RF/baseline của E17.

Bằng chứng: `notebooks/validation/outputs/main_rq/comparison/summary.md:1`; `notebooks/validation/outputs/main_rq/comparison/summary.md:13`; `notebooks/validation/outputs/main_rq/comparison/summary.md:25`.

Giới hạn: Không coi các bảng lặp là các xác nhận độc lập; không so trực tiếp 6.086 giờ lịch sử với C30 trên 6.050 giờ.

## Chưa xác minh

- Không có artifact Claude gốc để chứng minh bộ tham số tái dựng trùng hoàn toàn kết quả ngoài repo.
- Không xác nhận toàn bộ lịch sử dự án chưa từng xem test; cờ false chỉ nói về nhánh mô hình cuối. Tìm kiếm test_metrics/test_predictions/MAE_test trong source/notebook/log không cho bằng chứng điểm test đã lưu.
- Không chạy Restart & Run All trong đợt rà soát này. Output notebook là hiện vật đã lưu; hash khớp không chứng minh kernel đã nạp đúng mọi phiên bản.
- Tính khả dụng và độ trễ weather/history khi triển khai, cùng DST, còn chưa xác minh.
- Số tầng/optimizer/scheduler của mô hình không phải neural network không áp dụng; kiến trúc MLP được tuning trong src/model.py:27 và được lưu riêng theo kết quả.
