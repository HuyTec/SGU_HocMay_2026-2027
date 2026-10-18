# Dự đoán lưu lượng giao thông theo giờ

Đề tài nhóm 07: dự đoán `traffic_volume` (số xe/giờ) từ thời gian và điều kiện thời tiết, sử dụng bộ dữ liệu Metro Interstate Traffic Volume.

## Phân công

Phân công dự kiến theo [proposal](docs/ML_Project_Proposal.docx). Nhóm trưởng: **Trần Nhựt Huy**.

| Thành viên | MSSV | Công việc |
| --- | --- | --- |
| Phùng Anh Vũ | 3124411351 | Thu thập dữ liệu, EDA và trực quan hóa |
| Nguyễn Hoàng Phúc | 3124411236 | Tiền xử lý dữ liệu và xây dựng đặc trưng |
| Trần Nhựt Huy | 3124411112 | Xây dựng baseline và mô hình chính; tinh chỉnh, ablation, trực quan hóa và phân tích lỗi |
| Bùi Nhật Hào | 3124411077 | Đánh giá, xây dựng demo, tổng hợp báo cáo và slide |

## Hướng thực hiện

- Mô hình dự kiến: Ridge Regression, Random Forest, XGBoost/LightGBM.
- Chia dữ liệu theo thời gian: train 70%, validation 15%, test 15%; đánh giá bằng MAE, RMSE và R².
- Kế hoạch: tuần 1 — Vũ; tuần 2 — Phúc; tuần 3–4 — Huy; tuần 5 — Hào.
- Sản phẩm dự kiến: notebook thực nghiệm, bảng so sánh mô hình, demo Streamlit/Gradio, báo cáo và slide.

## Tài liệu và dữ liệu

- [Đề cương Word](docs/ML_Project_Proposal.docx)
- [Đề cương PDF](docs/Nhom7_DuDoanLuuLuongGiaoThong_Proposal.pdf)
- [Dữ liệu CSV](data/Metro_Interstate_Traffic_Volume.csv)
