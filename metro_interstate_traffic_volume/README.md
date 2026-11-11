# Dự đoán lưu lượng giao thông theo giờ

**Nhóm 07 — Nhóm trưởng: Trần Nhựt Huy.**

Tên đề tài: **Dự đoán lưu lượng giao thông theo giờ dựa trên đặc trưng thời gian và điều kiện thời tiết**.

README mô tả cách chạy dự án hiện tại. Phạm vi và phân công của nhóm được trình bày trong [proposal](docs/ML_Project_Proposal.docx).

```
metro_interstate_traffic_volume/
├── docs/                  # Sơ đồ, đề xuất và hướng dẫn nhật ký
├── data/                  # Dữ liệu đầu vào và dữ liệu đã xử lý
├── src/                   # Code dùng chung cho dữ liệu, mô hình và đánh giá
├── notebooks/
│   ├── eda/               # EDA chung và kiểm tra chất lượng dữ liệu
│   ├── preprocessing/     # Notebook giải thích và kiểm chứng tiền xử lý
│   ├── experiments/       # Thực nghiệm V1–V4
│   └── evaluation/        # Phân tích sai số và đối chứng Ridge A/B/C
├── experiments/           # Workbook thực nghiệm và nhật ký tùy chọn
├── outputs/               # Kết quả và hình đã xuất
├── reports/               # Báo cáo cho nhóm
└── app/                   # Demo
```

<<<<<<< Updated upstream
## 1. Bài toán và mục tiêu

Đây là bài toán **học có giám sát, hồi quy trên dữ liệu có thứ tự thời gian**. Nhóm xây dựng mô hình dự đoán lưu lượng xe theo giờ, so sánh các phương pháp và phân tích những trường hợp dự đoán sai nhiều.
=======
| Cấu hình theo proposal      | Đầu vào                 | Mục đích                                           |
| ----------------------------- | -------------------------- | ----------------------------------------------------- |
| A — Time                     | Thời gian, ngày lễ      | Mốc đối chứng                                     |
| B — Time + Weather           | A + thời tiết            | So sánh với A để đo đóng góp của thời tiết |
| C — Time + Weather + History | B + lưu lượng quá khứ | Thí nghiệm mở rộng về lịch sử                  |

Mô hình chính trong proposal: Linear Regression/Ridge, Random Forest, Gradient Boosting, MLP. Baseline gồm trung bình theo thứ–giờ, Ridge và seasonal naive cho thí nghiệm có lịch sử. Demo cuối dùng cấu hình B; History đánh giá riêng trong notebook.
>>>>>>> Stashed changes

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

## 4. Quy trình hiện tại

| Bước                  | Notebook                                                                                                                                               | Việc cần kiểm tra                                                                                             |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------- |
| 1. Kiểm tra dữ liệu  | [Data Validation](notebooks/eda/data_validation.ipynb)                                                                                                  | Kiểu dữ liệu, timestamp trùng, số giờ thiếu và bất thường của thời tiết.                           |
| 2. Khám phá dữ liệu | [EDA chung](notebooks/eda/eda.ipynb)                                                                                                                    | Phân phối lưu lượng, tương quan, boxplot và các mốc bất thường.                                     |
| 3. Tiền xử lý        | [Preprocessing &amp; Features](notebooks/preprocessing/preprocessing_features.ipynb)                                                                    | Gộp các dòng cùng timestamp, chia 70/15/15 theo thời gian, kiểm tra điền thiếu và đặc trưng.        |
| 4. Thực nghiệm        | [V1](notebooks/experiments/V_1.ipynb), [V2](notebooks/experiments/V_2.ipynb), [V3](notebooks/experiments/V_3.ipynb), [V4](notebooks/experiments/V_4.ipynb) | Tinh chỉnh trong train bằng `TimeSeriesSplit`, so sánh mô hình và baseline trên validation, lưu Excel. |
| 5. Phân tích sai số  | [Error Analysis](notebooks/evaluation/error_analysis_validation.ipynb)                                                                                  | Đọc kết quả V3/V4 từ Excel và phân tích sai số validation.                                              |

| Phiên bản | Cấu hình                                 | Mục tiêu                                                                                                                                                                             |
| ----------- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| V1          | `T0_thu_gio`                             | So sánh LR, RF, GB, MLP, Ridge và XGBoost với baseline trung bình theo thứ–giờ. Ridge dùng cột `weekday_hour`.                                                              |
| V2          | `T0_thu_gio`, `T1_lich`, `A_lich_le` | Đo phần tăng thêm của đặc trưng lịch và ngày lễ.                                                                                                                           |
| V3          | `B_thoi_tiet`                            | Bổ sung thời tiết, đối chứng A–B trên cùng các giờ validation.                                                                                                              |
| V4          | Cấu hình C có lịch sử                 | Thêm lưu lượng cùng giờ hôm trước, cùng giờ tuần trước và trung bình 24 giờ trước. Đọc kết quả B của V3 và đối chiếu trên cùng các giờ đủ lịch sử. |

Baseline thứ–giờ lấy trung bình lưu lượng theo cặp thứ và giờ từ train. V4 còn có seasonal naive lấy lưu lượng quan sát cùng giờ tuần trước khi có dữ liệu. Dùng **MAE, RMSE và R²** để đọc kết quả. So sánh trực tiếp các dòng được chấm trên cùng tập giờ.

Dữ liệu được chia theo các timestamp quan sát được. Các tham số tiền xử lý dùng trong tuning được fit theo phần train của từng fold. Validation dùng để so sánh cấu hình. Dự án dành test cho đánh giá cuối và hiện chưa có notebook chạy đánh giá cuối hay kết hợp dự đoán từ nhiều mô hình.

## 5. Hướng dẫn chạy trên Windows

### 5.1. Tạo môi trường

Mở PowerShell tại thư mục `metro_interstate_traffic_volume`. File [requirements.txt](requirements.txt) ghi nhận môi trường Python 3.13.9 dùng để chạy các thí nghiệm.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Trong VS Code, mở notebook và chọn **Select Kernel → Python Environments → .venv**. Giữ [CSV gốc](data/Metro_Interstate_Traffic_Volume.csv) ở đúng đường dẫn trước khi chạy.

### 5.2. Chạy notebook và lưu kết quả

1. Chạy các notebook kiểm tra dữ liệu, EDA và tiền xử lý theo bảng ở mục 4 khi cần kiểm tra đầu vào.
2. Chạy từng notebook thí nghiệm từ trên xuống. **V1 chạy độc lập**. Với chuỗi đối chứng, chạy **V2 → V3 → V4**. Mỗi notebook tạo đầu vào từ CSV gốc. V3 đọc kết quả V2 đã ghi vào Excel và V4 đọc kết quả V3.
3. Đóng Excel trước khi chạy cell lưu của mỗi notebook. Khi cell báo đã lưu, mở [experiments_logs.xlsx](experiments/experiments_logs.xlsx) và kiểm tra sheet **Tổng quan**. Mỗi phiên bản lưu kết quả của lần chạy mới nhất.
4. Chạy **Error Analysis** sau khi kết quả V3 và V4 sẵn sàng.

Nếu cần xuất CSV đã xử lý, chạy lệnh sau từ thư mục dự án. Lệnh cập nhật ba file `train.csv`, `validation.csv` và `test.csv` trong `data/processed/`. Notebook [Ridge A/B/C bổ sung](notebooks/evaluation/ridge_phuc_A_B_C_doi_chung_bo_sung.ipynb) dùng các CSV này.

```powershell
.\.venv\Scripts\python.exe -m src.prepare_data
```

Để bật nhật ký TXT, đặt `os.environ["SAVE_EXPERIMENT_LOGS"] = "1"` trong kernel trước cell ghi nhật ký. V1 còn hỗ trợ xuất ảnh PNG khi đặt `os.environ["SAVE_EXPERIMENT_RESULTS"] = "1"` trước cell vẽ. Các cell lưu Excel chạy trực tiếp.

### 5.3. Đọc Excel và xử lý lỗi

| Sheet                  | Nội dung                                                                                                                                            |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Tổng quan`         | Trạng thái, mã lần chạy, mã chạy đối chứng, địa điểm và múi giờ. Mốc dữ liệu dùng CST, thời điểm ghi lần chạy dùng UTC+7. |
| `Validation`         | MAE, RMSE, R², tham số đã chọn và điểm so với baseline.                                                                                     |
| `Hyper Parameters`   | Giá trị tham số của mô hình đã fit và nguồn giá trị.                                                                                     |
| `Tuning CV`          | Các ứng viên, điểm từng fold và thứ hạng theo MAE CV.                                                                                       |
| `Evaluation`         | Bảng so sánh mô hình theo nhóm giờ chấm. Phần kết hợp dự đoán nhiều mô hình chưa được triển khai.                               |
| Sheet theo phiên bản | Dự đoán từng giờ, mốc chia, thông tin lần chạy và bảng đối chứng tương ứng.                                                         |

- **WinError 5 khi lưu.** Đóng workbook trong Excel, rồi chạy lại riêng cell lưu nếu kernel còn kết quả.
- **Báo thiếu V2/V3 hoặc trạng thái Cần chạy lại.** Kiểm tra sheet **Tổng quan**, chạy và lưu phiên bản trước, sau đó chạy lại notebook phụ thuộc. Workbook kiểm tra SHA-256 của CSV và mã lần chạy đối chứng.
- **Kernel mới thiếu biến hoặc thiếu module.** Chọn kernel `.venv` rồi chạy lại các cell từ đầu.

## 6. Mã dùng chung và tài liệu

| File                                                                                                          | Vai trò                                                                                        |
| ------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| [data.py](src/data.py), [data_validation.py](src/data_validation.py)                                            | Đọc CSV, kiểm tra dữ liệu và tạo bảng theo timestamp.                                   |
| [preprocessing.py](src/preprocessing.py), [features.py](src/features.py), [prepare_data.py](src/prepare_data.py) | Chia tập, xử lý thiếu, tạo đặc trưng và xuất dữ liệu đã xử lý khi được gọi. |
| [models.py](src/models.py), [tuning.py](src/tuning.py)                                                          | Pipeline mô hình, không gian tham số và cross-validation theo thời gian.                  |
| [evaluation.py](src/evaluation.py), [experiment_excel.py](src/experiment_excel.py)                              | Baseline, metrics, đối chứng và đọc/ghi workbook.                                         |
| [experiment_logger.py](src/experiment_logger.py)                                                               | Nhật ký TXT tùy chọn. Xem [hướng dẫn nhật ký](docs/experiment_tracking/README.md).      |

[Sơ đồ quy trình](<docs/Quy%20trình.drawio>) · [Proposal PDF](docs/Nhom7_DuDoanLuuLuongGiaoThong_Proposal.pdf)
