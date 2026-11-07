# Dự đoán lưu lượng giao thông theo giờ

**Nhóm 07 — Nhóm trưởng: Trần Nhựt Huy.**

Tên đề tài: **Dự đoán lưu lượng giao thông theo giờ dựa trên đặc trưng thời gian và điều kiện thời tiết**.

README tổng hợp phạm vi, phương pháp và kế hoạch trong [proposal](docs/ML_Project_Proposal.docx), đồng thời cụ thể hóa phân công và quy trình thực nghiệm. Những phương pháp dự kiến bên dưới chỉ được xem là đã triển khai khi có mã chạy và bằng chứng kết quả tương ứng.

```
metro_interstate_traffic_volume/
├── docs/                  # Sơ đồ, đề xuất, hướng dẫn và chỉ mục V1–V5
├── data/                  # Dữ liệu đầu vào và dữ liệu đã xử lý
├── src/                   # Code dùng chung cho dữ liệu, mô hình và đánh giá
├── notebooks/
│   ├── eda/               # EDA chung và kiểm tra chất lượng dữ liệu
│   ├── preprocessing/     # Notebook giải thích và kiểm chứng tiền xử lý
│   ├── experiments/       # V1–V4 và đối chứng Ridge A/B/C
│   └── evaluation/        # Phân tích sai số, đánh giá cuối khi có
├── experiments/           # Nhật ký các lần chạy
├── outputs/               # Metrics, dự đoán và hình do thí nghiệm tạo ra
├── reports/               # Báo cáo cho nhóm
└── app/                   # Demo
```


## 1. Bài toán và mục tiêu

Đây là bài toán **học có giám sát, hồi quy trên dữ liệu có thứ tự thời gian**. Nhóm xây dựng mô hình dự đoán lưu lượng xe theo giờ, so sánh các phương pháp và phân tích những trường hợp dự đoán sai nhiều.

| Thành phần         | Nội dung                                                                              |
| -------------------- | -------------------------------------------------------------------------------------- |
| Đầu vào chính    | Thời gian, ngày lễ và thông tin thời tiết của giờ cần dự đoán             |
| Đầu ra             | `traffic_volume`, số xe/giờ, không âm                                            |
| Phần mở rộng      | Bổ sung lưu lượng đã quan sát trong quá khứ                                   |
| Sản phẩm minh họa | Demo Time + Weather, nhận ngày giờ và thời tiết, trả dự đoán kèm biểu đồ |

Các câu hỏi nghiên cứu:

1. Đặc trưng thời gian và thời tiết có liên hệ thế nào với lưu lượng?
2. Mô hình nào dự đoán tốt nhất trong thiết kế đánh giá đã thống nhất, và thêm thời tiết cải thiện bao nhiêu?
3. Mô hình sai nhiều ở khung giờ, ngày lễ hoặc điều kiện thời tiết nào?

Kết quả có thể cung cấp cơ sở tham khảo cho các bài toán quản lý giao thông. Khả năng áp dụng thực tế cần được đánh giá thêm theo địa điểm, dữ liệu đầu vào và điều kiện vận hành.

## 2. Dữ liệu và kịch bản dự đoán

- Nguồn: [Metro Interstate Traffic Volume — UCI](https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume).
- Phạm vi theo proposal: I-94 hướng Tây, khu vực Minneapolis–St Paul, Mỹ; giai đoạn 2012–2018.
- CSV gốc của dự án: [Metro_Interstate_Traffic_Volume.csv](data/Metro_Interstate_Traffic_Volume.csv), gồm 48.204 dòng và 9 cột; số dòng không đồng nghĩa với số giờ duy nhất.
- Các cột: `holiday`, `temp`, `rain_1h`, `snow_1h`, `clouds_all`, `weather_main`, `weather_description`, `date_time`, `traffic_volume`.

Với cấu hình Time + Weather, nhóm dự đoán lưu lượng của một giờ khi đã có thời gian và thông tin thời tiết của giờ đó. Nếu dùng thời tiết quan trắc cùng giờ, kết quả được hiểu trong điều kiện đã biết thời tiết; việc dùng dự báo thời tiết trước giờ cần dự đoán là một giả định vận hành cần ghi rõ.

Với phần History, nhóm xét dự đoán từng giờ kế tiếp khi các quan sát trước đó đã được ghi nhận. Chỉ sử dụng thông tin sẵn có trước giờ cần dự đoán; không dùng lưu lượng của chính giờ đó.

## 3. Phân công và đầu ra bàn giao

Phân công dưới đây cụ thể hóa vai trò trong proposal. Đây là trách nhiệm dự kiến; đóng góp thực tế cần được ghi bằng file, cell, commit hoặc mã thí nghiệm trong báo cáo tiến độ.

| Thành viên         | MSSV       | Trách nhiệm                                                                                                                                                                                                      | Đầu ra bàn giao                                                                                                                                     |
| -------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Phùng Anh Vũ       | 3124411351 | Thu thập và mô tả dữ liệu; EDA theo giờ, thứ, tháng, ngày lễ và thời tiết; phối hợp kiểm tra timestamp trùng, giờ thiếu và bất thường                                                      | Notebook EDA, hình gốc, nhận xét có số liệu và danh sách vấn đề dữ liệu                                                                  |
| Nguyễn Hoàng Phúc | 3124411236 | Xây dựng pipeline tiền xử lý từ CSV gốc; chốt quy tắc gộp cho từng cột; xử lý thiếu/bất thường; tạo đặc trưng thời gian, thời tiết và lịch sử; encoding/scaling theo tập huấn luyện | Mã tiền xử lý tái lập, quy tắc dữ liệu, bảng đặc trưng theo timestamp và mô tả thời điểm thông tin sẵn có                        |
| Trần Nhựt Huy      | 3124411112 | Xây dựng ba baseline và các mô hình chính; thống nhất mốc chia với nhóm; thiết kế, ghi log, tinh chỉnh và so sánh Time/Weather/History; trực quan hóa, diễn giải và phân tích lỗi         | Notebook thực nghiệm, cấu hình mô hình, log, dự đoán và bảng metrics; biểu đồ đối chứng, phân tích sai số và SHAP khi thực hiện |
| Bùi Nhật Hào      | 3124411077 | Phối hợp kiểm tra cách tính metrics và khả năng chạy lại; tổng hợp kết quả cùng Huy; xây dựng demo Time + Weather; tổng hợp báo cáo, slide và gói nộp                                      | Bảng đánh giá thống nhất với log, demo, tài liệu chạy, báo cáo, slide và danh mục sản phẩm                                             |

Phúc và Vũ phối hợp xác định chất lượng và quy tắc dữ liệu. Huy tiếp nhận đầu vào đã thống nhất để huấn luyện, đồng thời có thể chạy Time-only trước khi pipeline thời tiết hoàn thiện. Huy và Hào dùng chung mốc chia, tập đánh giá và mã thí nghiệm khi tổng hợp kết quả.

## 4. Khám phá, tiền xử lý và đặc trưng

EDA dự kiến gồm phân phối mục tiêu; lưu lượng theo giờ, thứ và tháng; ngày thường/cuối tuần/ngày lễ; thời tiết; tương quan; giá trị thiếu và bất thường.

Quy trình chuẩn bị dữ liệu:

1. Kiểm tra cấu trúc, kiểu dữ liệu, timestamp và miền giá trị mục tiêu; ghi số dòng và phiên bản dữ liệu.
2. Kiểm tra mục tiêu trong từng timestamp. Nếu nhất quán, giữ một giá trị lưu lượng; nếu mâu thuẫn, kiểm tra nguyên nhân trước khi gộp. Không cộng các mục tiêu lặp.
3. Với thời tiết, kiểm tra từng cột và ghi quy tắc tổng hợp riêng. Xác định cách xử lý nhiệt độ 0 K, mưa cực lớn và dữ liệu thiếu; không tùy ý giữ dòng đầu cho toàn bộ thuộc tính.
4. Sắp xếp theo thời gian, xác định mốc chia; mọi bước học tham số xử lý thiếu, encoding, scaling chỉ fit trên train tương ứng.
5. Tạo đặc trưng phù hợp với kịch bản. Với lịch sử, tra theo timestamp thực, xử lý giờ thiếu và không dùng mục tiêu hiện tại hoặc dữ liệu tương lai.

Theo proposal, các đặc trưng dự kiến gồm `hour`, `day_of_week`, `month`, `is_weekend`, `is_rush_hour`, `is_holiday`, mã hóa tuần hoàn sin/cos, nhiệt độ đổi sang °C, mưa, tuyết, mây và loại thời tiết. Notebook có thể dùng tên `weekday` tương ứng với `day_of_week`; cần ghi đúng tên thực tế vào log.

Đặc trưng lịch sử mở rộng gồm lưu lượng cùng giờ hôm trước, cùng giờ tuần trước và trung bình 24 giờ trước. Không mặc định `shift(24)` hoặc `shift(168)` theo dòng tương ứng với 24 hoặc 168 giờ khi dữ liệu còn thiếu giờ. Không nội suy mục tiêu bằng dữ liệu tương lai.

## 5. Ba baseline

Ba baseline là các phương pháp dự đoán. Chúng khác với ba cấu hình đầu vào A/B/C ở mục 6.

| Baseline                                | Quy tắc                                                                                            | Điều kiện và phạm vi                                                                                                                                     |
| --------------------------------------- | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Trung bình theo thứ–giờ             | Dự đoán bằng trung bình `traffic_volume` của cùng cặp thứ và giờ trong train           | Chỉ tính trung bình từ train; nếu thiếu nhóm, dùng phương án dự phòng đã ghi trong log, chẳng hạn trung bình toàn train                    |
| Seasonal naive cùng giờ tuần trước | Với timestamp `t`, dự đoán bằng lưu lượng quan sát tại `t - 7 ngày`                  | Có sử dụng History; tra theo timestamp, không theo số dòng; ghi quy tắc khi thiếu lịch sử, số mẫu đánh giá và thời điểm quan sát sẵn có |
| Ridge Regression                        | Học mô hình tuyến tính có phạt L2; bắt đầu bằng Time-only, sau đó mở rộng đầu vào | Đưa tiền xử lý vào pipeline, fit trên train; ghi `alpha`, đặc trưng và cấu hình encoding/scaling                                               |

Thứ tự triển khai ban đầu: **trung bình thứ–giờ → Ridge Time-only → seasonal naive khi đã chốt quy tắc lịch sử**. Giai đoạn đầu ưu tiên chạy đúng từ đầu đến cuối và có log trước khi tuning.

Nếu seasonal naive chỉ đánh giá ở các giờ có lịch sử, các mô hình dùng để so sánh trực tiếp cũng phải được đo trên cùng các giờ đó. Ghi số giờ đủ điều kiện và tỷ lệ bao phủ; không so trực tiếp các metrics tính trên hai tập giờ khác nhau.

## 6. Cấu hình đầu vào và mô hình chính

| Cấu hình theo proposal      | Đầu vào                   | Mục đích                                                                         |
| ----------------------------- | ---------------------------- | ----------------------------------------------------------------------------------- |
| A — Time                     | Thời gian và ngày lễ     | Mốc so sánh                                                                       |
| B — Time + Weather           | A và thời tiết            | Đo giá trị dự đoán bổ sung của thời tiết                                  |
| C — Time + Weather + History | B và lưu lượng quá khứ | Đo giá trị dự đoán bổ sung của lịch sử; đánh giá riêng trong notebook |

Baseline Time-only ban đầu có thể chỉ dùng giờ, thứ, tháng và cuối tuần. Đây là bước khởi đầu; chưa bao phủ đầy đủ cấu hình A nếu chưa có ngày lễ. Ghi chính xác tập đặc trưng thực tế thay vì chỉ ghi tên cấu hình.

Các mô hình theo proposal: **Ridge Regression**, **Random Forest** và **XGBoost hoặc LightGBM**. Ridge là mốc tuyến tính; các mô hình cây được dùng để kiểm tra quan hệ phi tuyến và tương tác. Cơ sở lựa chọn cần được kiểm chứng bằng kết quả thực nghiệm.

Đối chứng A–B và B–C sử dụng cùng loại mô hình, cùng mốc chia và cùng tập giờ đánh giá; ghi rõ cấu hình và ngân sách tuning. Nếu History làm giảm số mẫu đủ điều kiện, cần kiểm soát cả sự khác biệt về dữ liệu huấn luyện để tránh quy toàn bộ chênh lệch cho đặc trưng mới.

## 7. Thiết kế thực nghiệm và nhật ký

Sau khi gộp timestamp và sắp xếp thời gian, chia **70% đầu làm train, 15% tiếp theo làm validation, 15% cuối làm test**. Tỷ lệ tính theo số timestamp quan sát được; lưu số mẫu và mốc thời gian thực tế. Một timestamp chỉ thuộc một tập.

- **Train:** học mô hình và các tham số tiền xử lý. Tinh chỉnh dự kiến bằng TimeSeriesSplit kết hợp Random Search hoặc Optuna trong train; fit preprocessing riêng trong mỗi lượt.
- **Validation:** so sánh các phương án trong quá trình phát triển. Không đưa nhãn validation vào việc fit mô hình hoặc tính trung bình baseline.
- **Test:** giữ cho đánh giá cuối khi đã chốt quy trình; không dùng điểm test để chọn tham số.

Với đánh giá History từng giờ, quan sát của các giờ validation/test trước đó chỉ được dùng khi chúng thực sự đã sẵn có trước giờ đang dự đoán. Đây là đánh giá tuần tự, không phải dự đoán đồng thời toàn bộ tương lai khi chưa biết các quan sát trung gian.

Đánh giá bằng **MAE, RMSE và R²**. MAE và RMSE có đơn vị xe/giờ; MAE/RMSE thấp hơn và R² cao hơn là tốt hơn trên cùng tập đánh giá. Không dùng MAPE làm độ đo chính vì mục tiêu có thể bằng 0 hoặc rất nhỏ.

Mỗi lần chạy cần ghi ID, ngày, dữ liệu/phiên bản, giả thuyết, thay đổi, mô hình, tham số, đặc trưng, tỷ lệ và mốc chia, tập đánh giá, số mẫu, metrics, nhận xét, vấn đề và bước tiếp theo. Dùng [hàm ghi log](src/experiment_logger.py) và [hướng dẫn nhật ký](docs/experiment_tracking/README.md); mẫu điền tay ở [EXP_TEMPLATE.txt](docs/experiment_tracking/EXP_TEMPLATE.txt). Mẫu không phải kết quả thực nghiệm.

Các phân tích sau baseline gồm mức cải thiện MAE so với baseline, sai số theo giờ/ngày lễ/thời tiết kèm số mẫu, feature importance và SHAP. Diễn giải đóng góp dự đoán của đặc trưng không đồng nghĩa với kết luận nhân quả.

## 8. Tiến độ hiện tại và kế hoạch

Notebook [baseline Time-only](notebooks/experiments/V_1.ipynb) đã lưu kết quả validation cho sáu phương pháp. Khi chạy lại với cùng dữ liệu (SHA-256 `749c90d7…`), pandas 3.0.6 và scikit-learn 1.9.1 trên Python 3.13.9, bảng so sánh cho cùng giá trị MAE/RMSE/R². V_2–V_4 đã có thí nghiệm trên validation (EXP_007–EXP_027). V_5 (đánh giá test) chưa chạy và cần nhóm chốt quy trình trước. Xem [các phiên bản thử nghiệm](src/versions/README.md) và [bản rà soát tiến độ](docs/ra_soat_tien_do.md).

Kết quả validation chính (MAE, xe/giờ; chi tiết trong từng notebook):

| Bước                      | Mô hình tốt nhất | MAE    | Ghi chú                                                           |
| --------------------------- | -------------------- | ------ | ------------------------------------------------------------------ |
| Trung bình thứ–giờ      | Baseline             | 285,03 | Mốc của V_1                                                      |
| A — Time + ngày lễ (V_2) | XGBoost              | 244,94 | `is_holiday` giảm 33,95 so với chỉ dùng lịch                |
| B — Time + Weather (V_3)   | XGBoost              | 243,45 | Thời tiết giảm 1,49; CI 95% chứa 0                             |
| C — thêm History (V_4)    | XGBoost              | 192,94 | Đo trên 6.050 giờ đủ lịch sử; B trên cùng giờ là 243,04 |

`src/data.py`, `src/features.py`, `src/evaluation.py` và `src/models.py` chứa quy trình dùng chung. `src/data.py` cho kết quả trùng với `final_filled_splits` của `preprocessing_features.ipynb`. Test được giữ riêng.

Lịch dự kiến theo proposal:

| Tuần | Công việc                                    | Phụ trách chính     | Sản phẩm                                        |
| ----- | ---------------------------------------------- | ---------------------- | ------------------------------------------------- |
| 1     | Chốt đề tài, tải dữ liệu, EDA           | Vũ                    | Notebook EDA, biểu đồ                          |
| 2     | Tiền xử lý và feature engineering          | Phúc                  | Pipeline/dataset xử lý, danh sách đặc trưng |
| 3     | Baseline và mô hình chính                  | Huy                    | Kết quả ban đầu và log                       |
| 4     | Tinh chỉnh, đối chứng và phân tích lỗi | Huy, phối hợp Hào   | Bảng kết quả, biểu đồ, diễn giải/SHAP     |
| 5     | Demo, báo cáo và slide                      | Hào, phối hợp nhóm | Demo Time + Weather, báo cáo và gói nộp      |

Các mốc tuần là kế hoạch, không phải xác nhận đã hoàn thành. Bảng công việc `docs/Task.xlsx` đã bị xóa khỏi repo ở commit `9d064fa`; có thể lấy lại bằng `git show 9d064fa^:metro_interstate_traffic_volume/docs/Task.xlsx > Task.xlsx`. Cập nhật bằng chứng thực tế trước khi báo cáo.

## 9. Tổ chức và chạy lại

| Đường dẫn                                          | Nội dung                                                                       |
| ------------------------------------------------------ | ------------------------------------------------------------------------------- |
| `data/`                                              | CSV gốc                                                                        |
| `notebooks/eda/data_validation.ipynb`                    | Kiểm tra chất lượng dữ liệu                                               |
| `notebooks/eda/eda.ipynb`                            | EDA chung và trực quan hóa                                                   |
| `notebooks/versions/V_1_time_only/`                  | Chỉ mục notebook và EDA liên quan V_1                                       |
| `notebooks/preprocessing/preprocessing_features.ipynb`             | Quy tắc gộp giờ, điền thiếu và đặc trưng thời gian                   |
| `notebooks/experiments/V_1.ipynb`              | Baseline Time-only                                                              |
| `notebooks/experiments/V_2.ipynb`              | Thời gian và ngày lễ (cấu hình A)                                         |
| `notebooks/experiments/V_3.ipynb`              | Time + Weather (cấu hình B), đối chứng A–B, độ nhạy dữ liệu          |
| `notebooks/experiments/V_4.ipynb`              | History (cấu hình C), seasonal naive, đối chứng B–C                       |
| `notebooks/evaluation/error_analysis_validation.ipynb` | Sai số theo giờ/ngày/thời tiết và SHAP                                    |
| `src/data.py`                                        | CSV gốc → bảng một dòng mỗi giờ → chia 70/15/15 → điền thiếu        |
| `src/features.py`                                    | Đặc trưng thời gian, thời tiết, lịch sử và danh sách cấu hình A/B/C |
| `src/models.py`                                      | Mô hình, lưới tuning dùng chung, lưu/đọc kết quả                      |
| `src/evaluation.py`                                  | Metrics, hai baseline thống kê, bootstrap theo ngày                          |
| `app/demo_time_weather.py`                           | Demo Streamlit Time + Weather                                                   |
| `outputs/metrics/`, `outputs/predictions/`         | Metrics, tham số đã chọn và dự đoán validation                          |
| `experiments/`                                       | Log từng lần chạy                                                            |
| `docs/`                                              | Proposal, hướng dẫn nhật ký và rà soát tiến độ                       |

Cài môi trường bằng `pip install -r requirements.txt`. Chạy các notebook theo thứ tự V_2 → V_3 → V_4 → `error_analysis_validation`, vì notebook sau đọc dự đoán đã lưu của notebook trước. Các notebook V_2–V_4 chỉ ghi log khi đặt biến môi trường `SAVE_EXPERIMENT_LOGS=1`. Demo: `streamlit run app/demo_time_weather.py` từ thư mục dự án, sau khi đã chạy V_2 và V_3.

Trước khi ghi nhận một lần thực nghiệm hoàn chỉnh, restart kernel và chạy lại toàn bộ notebook, lưu output, phiên bản Python/thư viện và SHA-256 của dữ liệu.

## 10. Sản phẩm và tài liệu

Sản phẩm dự kiến: notebook và mã Python, cấu hình môi trường, experiment log, hình gốc, bảng so sánh test MAE/RMSE/R², báo cáo DOCX, slide PPTX, README và demo Streamlit/Gradio. Lưu mô hình đã huấn luyện nếu có. Demo chính dùng Time + Weather; History được đánh giá riêng trong notebook.

Gói nộp giữa kỳ theo yêu cầu học phần gồm các sản phẩm thực tế đã có, nén theo `Nhom??_TenDeTai_GiuaKy.zip`; nhóm trưởng nộp trên Google Classroom theo hạn của lớp. Báo cáo cần phân biệt kết quả đã đạt, khó khăn và kế hoạch tiếp theo, thống nhất với mã nguồn, log và hình.

- [Proposal Word](docs/ML_Project_Proposal.docx)
- [Proposal PDF](docs/Nhom7_DuDoanLuuLuongGiaoThong_Proposal.pdf)
- [Rà soát tiến độ](docs/ra_soat_tien_do.md)
- [Dataset CSV](data/Metro_Interstate_Traffic_Volume.csv)

Hướng phát triển trong proposal gồm dữ liệu giao thông Việt Nam, dự đoán nhiều bước và mô hình chuỗi thời gian chuyên dụng; chưa phải phạm vi đã triển khai.
