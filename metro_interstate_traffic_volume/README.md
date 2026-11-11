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

Mô hình chính trong proposal: Ridge, Random Forest, XGBoost/LightGBM. Baseline gồm trung bình theo thứ–giờ, Ridge và seasonal naive cho thí nghiệm có lịch sử. Demo cuối dùng cấu hình B; History đánh giá riêng trong notebook.

## Quy trình và đánh giá

**EDA → tiền xử lý → baseline/mô hình cơ sở → tuning → validation → test cuối → phân tích lỗi và demo.**

- Gộp timestamp trùng, sắp theo thời gian, chia train/validation/test **70/15/15**, không xáo trộn.
- Tuning bằng **TimeSeriesSplit** trên train; các bước học thống kê tiền xử lý chỉ fit trên phần train tương ứng của từng fold.
- Báo cáo **MAE, RMSE, R²**. So sánh A–B với cùng danh sách mô hình, mốc chia, các giờ đánh giá và quy tắc tuning; giữ nguyên đặc trưng A khi bổ sung thời tiết.
- Chọn cấu hình bằng CV/validation; giữ test cho đánh giá cuối. Thời tiết cùng giờ được hiểu là đã biết tại thời điểm dự đoán; lịch sử chỉ dùng các quan sát trước giờ cần dự đoán.

## Thực nghiệm hiện tại

Đang thử cấu hình thời gian trong `notebooks/experiments/ConfigA-Datetime_Compare5Model_Huy_5-11-2026.ipynb` (đổi tên từ V_1). Đặc trưng hiện tại là giờ và thứ, chưa đầy đủ cấu hình A của proposal.

**Tiếp theo:** chốt bộ đặc trưng A và danh sách **5 mô hình**, thực nghiệm B (A + thời tiết), rồi đối chiếu từng mô hình với A trên cùng các giờ validation. Notebook hiện còn mã chạy 6 mô hình; tên file chưa phản ánh đầy đủ nội dung. Chưa coi kế hoạch này là kết quả đã hoàn thành.

## Tài liệu và thư mục

Cài thư viện từ [requirements.txt](requirements.txt), chọn môi trường Python đó làm kernel. Bắt đầu từ [EDA](notebooks/eda/), [tiền xử lý](notebooks/preprocessing/), rồi [thực nghiệm](notebooks/experiments/).

`src/`: mã dùng chung · `data/`: dữ liệu · `experiments/`: kết quả · `reports/`: báo cáo · `app/`: demo. Xem [hướng dẫn nhật ký](docs/experiment_tracking/README.md).

Thành viên theo proposal: **Vũ** — dữ liệu/EDA; **Phúc** — tiền xử lý/đặc trưng; **Huy** — baseline, mô hình, tuning/phân tích lỗi; **Hào** — đánh giá, demo/báo cáo.
