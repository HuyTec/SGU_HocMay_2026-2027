# Validation và cấu hình cuối

Mô hình được chốt ngày 22/11/2026: **C30, RF 25% + XGBoost 25% + ExtraTrees 50%**.

## Diễn giải mô hình cho mục 4.7

[interpretation_C30.ipynb](interpretation_C30.ipynb) fit lại đúng cấu hình trên cohort train, kiểm tra dự đoán validation với kết quả đã lưu, rồi đo permutation importance của ba nhóm và ba cột history. Bảng, hình và nhận xét lưu tại [outputs/interpretation_C30](outputs/interpretation_C30/). Artifact của notebook chỉ fit trên train để phân tích validation, chưa phải mô hình refit trên train + validation. Không dùng kết quả importance để chọn lại cấu hình.

## Mạch thực nghiệm chính từ 20/11

Cùng C30, cohort 22.503 giờ train và 6.050 giờ validation, với quy tắc tạo history và tiền xử lý đã công bố. OOF chọn phương án trong train; validation kiểm tra phương án đã cố định. Validation đã được xem nhiều lần, cần ghi hạn chế này trong báo cáo.

| Giai đoạn | Notebook / nguồn | Câu hỏi và kết quả của bước |
|---|---|---|
| 20/11 — đối chiếu tham số sau CV | [validation_compare.ipynb](validation_compare.ipynb) và hai thí nghiệm Params1/Params2 | Giữ C30 và dữ liệu, so hai bộ tham số RF/XGBoost. Bộ Claude tái dựng cho kết quả validation tốt hơn trong những lượt đã thử; chưa chứng minh tối ưu toàn bộ không gian tham số. |
| 21/11 — thử trọng số và phân tích lỗi | [validation_C30_OOF.ipynb](validation_C30_OOF.ipynb), [thí nghiệm OOF](../../experiments/21-11-2026_Huy_C30_OOF/fit_C30_OOF.ipynb) | OOF chọn RF/XGBoost 60/40 nhưng validation không cải thiện 50/50. Sai số hai mô hình thường cùng chiều, tạo giả thuyết cần mô hình bổ sung. |
| 22/11 — thử loss MAE và mô hình bổ sung | [fit_C30_MAE_Diversity.ipynb](../../experiments/22-11-2026_Huy_C30_MAE_Diversity/fit_C30_MAE_Diversity.ipynb) | Khóa 5 cấu hình mô hình mới và các tỷ trọng trước khi chấm. OOF chọn 50% ExtraTrees + 50% ensemble RF/XGBoost cũ; phương án này cải thiện validation. |
| 22/11 — tổng hợp và chốt | [validation_final_C30.ipynb](validation_final_C30.ipynb) | So các phương án trên cùng giờ, ghi quyết định RF 25% + XGBoost 25% + ExtraTrees 50% và xuất đặc tả. |
| Bước tiếp theo | [selected_model.json](outputs/final_C30/selected_model.json) | Refit tiền xử lý và ba mô hình trên train + validation theo thời gian, giữ tham số/trọng số, rồi đánh giá test một lần. Chưa thực hiện bước này. |

[validation_C30.ipynb](validation_C30.ipynb) là notebook fit/validation hai mô hình ban đầu; bảng đối chiếu tham số và kết luận tổng hợp hiện nằm ở hai notebook compare/final bên trên. Không cần trình bày nó thành một thí nghiệm độc lập mới trong báo cáo.

Đặc tả đã khóa là nguồn cấu hình cho bước fit cuối, chưa phải artifact mô hình đã refit. Không lấy lại tham số từ các bảng lịch sử khác.

## Gắn với câu hỏi nghiên cứu

- RQ1 về mẫu hình thời gian/thời tiết dùng EDA; bảng mô hình không thay thế EDA hoặc chứng minh nhân quả.
- Phần RQ2 về đóng góp các nhóm đặc trưng dùng [FE cùng protocol](../features/README.md) và [đối chứng tuning A12/B27/C30](../tuning/README.md). Đây là CV trên train, không gọi là validation.
- Phần chọn mô hình cuối và ensemble dùng mạch từ 20/11 ở trên. Phân tích lỗi RQ3 dùng các dự đoán C30 cùng cohort trong notebook OOF/validation hiện tại.

## Lịch sử trước 20/11 — tài liệu bổ trợ

Năm notebook dưới đây từng được gắn nhãn RQ chính trong danh mục lịch sử. Chúng được giữ để truy vết, khảo sát ban đầu hoặc phụ lục; **không đưa thành năm bước trong mạch validation cuối từ 20/11**.

| Mã | Notebook | Phạm vi lịch sử |
|---|---|---|
| E05 | [validation_E05_Hao_AB.ipynb](validation_E05_Hao_AB.ipynb) | Hào: A17/B71 trên LR, RF, GB và MLP. |
| E13 | [validation_E13_RF_numeric.ipynb](validation_E13_RF_numeric.ipynb) | Phúc: A12 → numeric16 → B27 với RF cố định. |
| E15 | [validation_E15_RF_labels.ipynb](validation_E15_RF_labels.ipynb) | Phúc: A12 → labels23 → B27 với RF cố định. |
| E17 | [validation_E17_RF_AB.ipynb](validation_E17_RF_AB.ipynb) | Huy: RF A12/B27 và lỗi cao điểm. |
| E18 | [validation_E18_XGB_AB.ipynb](validation_E18_XGB_AB.ipynb) | Huy: XGBoost A12/B27 chọn theo RMSE và ngày lỗi lớn. |

[validation_RQ_main_compare.ipynb](validation_RQ_main_compare.ipynb) là bản tổng hợp **lịch sử** của năm nguồn này, không phải bảng chốt mô hình cuối. Không xếp hạng chung A17/B71 với A12/B27 hoặc so trực tiếp kết quả 6.086 giờ với C30 trên 6.050 giờ. E05 thiếu predictions; E13/E15 lặp A/B và E18 đọc lại RF/baseline từ E17.

Code đọc/kiểm tra lịch sử nằm ở [src/validation_main.py](../../src/validation_main.py), bảng và hình ở [outputs/main_rq](outputs/main_rq/). Các nguồn và kết quả cũ được giữ nguyên; việc phân loại lại cách trình bày không tạo thêm lần huấn luyện.
