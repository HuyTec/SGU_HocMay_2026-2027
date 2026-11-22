# Dự đoán lưu lượng giao thông theo giờ

**Nhóm 07 — Nhóm trưởng: Trần Nhựt Huy.** Dự án hồi quy dự đoán `traffic_volume` (xe/giờ) từ thời gian và thời tiết trên bộ dữ liệu [Metro Interstate Traffic Volume — UCI](https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume).

[Proposal](docs/ML_Project_Proposal.docx) là nguồn gốc về mục tiêu, phạm vi và kế hoạch đánh giá. Mẫu Iris là cấu trúc tổ chức quy trình học máy.

## Mục tiêu và cấu hình

So sánh mô hình, đo mức cải thiện khi thêm thời tiết và phân tích những khung giờ/điều kiện dự đoán sai nhiều.

| Cấu hình theo proposal | Đầu vào | Mục đích |
|---|---|---|
| A — Time | Thời gian, ngày lễ | Mốc đối chứng |
| B — Time + Weather | A + thời tiết | So sánh với A để đo đóng góp của thời tiết |
| C — Time + Weather + History | B + lưu lượng quá khứ | Thí nghiệm mở rộng về lịch sử |

Mô hình chính trong proposal: Ridge, Random Forest, XGBoost/LightGBM. Baseline gồm trung bình theo thứ–giờ, Ridge và seasonal naive cho thí nghiệm có lịch sử. Demo B là phiên bản cũ. Demo hiện tại dùng artifact C30 cuối (RF 25%, XGBoost 25%, ExtraTrees 50%); xem [app/README.md](app/README.md). MnDOT đang ở bước kiểm tra dữ liệu, chưa mở dự đoán khi weather/time/holiday chưa tương thích.

## Quy trình và đánh giá

**EDA → tiền xử lý → baseline/mô hình cơ sở → tuning → validation → test cuối → phân tích lỗi và demo.**

- Gộp timestamp trùng, sắp theo thời gian, chia train/validation/test **70/15/15**, không xáo trộn.
- Tuning bằng **TimeSeriesSplit** trên train; các bước học thống kê tiền xử lý chỉ fit trên phần train tương ứng của từng fold.
- Báo cáo **MAE, RMSE, R²**. So sánh A–B với cùng danh sách mô hình, mốc chia, các giờ đánh giá và quy tắc tuning; giữ nguyên đặc trưng A khi bổ sung thời tiết.
- Chọn cấu hình bằng CV/validation; giữ test cho đánh giá cuối. Thời tiết cùng giờ được hiểu là đã biết tại thời điểm dự đoán; lịch sử chỉ dùng các quan sát trước giờ cần dự đoán.

## Thực nghiệm hiện tại

Các notebook trong `experiments/` dùng chung [`load_experiment_splits`](src/experiment_data.py): mặc định đọc `data/processed/`, chọn `stage="raw"` cho CV trước điền thiếu hoặc `stage="filled"` để giữ schema thời tiết của nhánh cũ. Hàm kiểm tra bộ chia và target giữa các nguồn; mặc định chỉ trả train/validation. Xem [hướng dẫn đối chứng](docs/experiment_tracking/COMPARISON_PROTOCOL.md) và [danh mục theo ngày/RQ](docs/experiment_tracking/EXPERIMENTS_BY_DATE_AND_RQ.md). Output notebook đang lưu là kết quả lịch sử; thay loader chưa phải chạy lại mô hình.

- [Config A của Phúc](experiments/11-11_ConfigA_4Model/V1_ConfigA_phuc.ipynb) so sánh 4 mô hình với đặc trưng thời gian.
- [Config A của Huy](experiments/11-11-2026_Huy_ConfigAWithoutHoliday/V_1_ConfigAWithoutHoliday_Compare5Model_Huy_5-11-2026.ipynb) thử cấu hình thời gian bỏ đặc trưng ngày lễ.
- [Config B của Huy](experiments/11-11-2026_Huy_ConfigB/V_1_ConfigB_Compare5Model_Huy_11-11-2026.ipynb) so sánh mô hình khi bổ sung thời tiết.

Xem [nhật ký thực nghiệm](experiments/experiments_logs.xlsx) để đối chiếu các lần chạy. Trước khi kết luận về đóng góp của thời tiết, kiểm tra A và B dùng cùng mô hình, mốc chia, các giờ validation và quy tắc tuning.

## Tài liệu và thư mục

Cài thư viện từ [requirements.txt](requirements.txt), chọn môi trường Python đó làm kernel. Bắt đầu từ [EDA](notebooks/eda/), [tiền xử lý](notebooks/preprocessing/), rồi [đối chứng đặc trưng](notebooks/features/) và [thí nghiệm bổ sung](experiments/).

`notebooks/`: EDA, tiền xử lý và đối chứng đặc trưng · `src/`: mã dùng chung · `data/`: dữ liệu · `experiments/`: kết quả · `reports/`: báo cáo · `app/`: demo. Xem [hướng dẫn nhật ký](docs/experiment_tracking/README.md).

Thành viên theo proposal: **Vũ** — dữ liệu/EDA; **Phúc** — tiền xử lý/đặc trưng; **Huy** — baseline, mô hình, tuning/phân tích lỗi; **Hào** — đánh giá, demo/báo cáo.
