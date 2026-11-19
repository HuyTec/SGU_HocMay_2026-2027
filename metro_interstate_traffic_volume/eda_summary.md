# Tổng hợp ba đợt EDA

Tự tạo từ notebook đã chạy. Phân tích và đối chứng chỉ dùng train; chưa đánh giá model trên validation/test.

| Đợt | Kết luận chính | Quyết định giữ/bỏ/đổi | n giờ train | Rủi ro còn lại |
|---|---|---|---:|---|
| A | Đỉnh ngày làm việc 16h; cuối tuần 13h; chênh lễ ghép -953.3 xe/giờ | Giữ A12 làm mốc; chưa bỏ riêng feature bằng tương quan/VIF | 28402 | Nhãn lễ có thể thiếu; mùa/năm chưa ghép; DST chưa phân tích; cờ dẫn xuất trùng thông tin |
| B | Rain với lượng mưa 0: 3,609 dòng toàn CSV; B giảm MAE ở 2/3 fold; delta MAE +1.26 | Giữ A12/B27 để đối chứng; đổi xử lý temp/rain; chưa bỏ riêng weather theo tương quan | 28402 | Weather cùng giờ cần sẵn có; nhãn hiếm; 0 mm không đồng nghĩa trời khô; một seed/model |
| C | Đủ history 22,503/28,402 giờ; C giảm MAE 3/3 fold; delta MAE -42.52 | Giữ C30 có điều kiện dữ liệu quá khứ; không chọn model cuối trước test | 28402 | Rolling cần ít nhất 18/24 giờ; cohort thay đổi; cần dữ liệu đến kịp; không đại diện dự báo nhiều bước |

n là số giờ train của mỗi đợt; bảng CV và bảng feature ghi n của từng cohort/feature.
Seed=42. Bootstrap khối 7 ngày; CI mô tả chưa hiệu chỉnh nhiều phép so sánh. mean_24h cần ít nhất 18/24 giờ; có đối chiếu độ phủ với quy tắc đủ 24 giờ.
Nguồn API: [pandas rolling](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rolling.html), [TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html), [định nghĩa VIF](https://www.statsmodels.org/stable/generated/statsmodels.stats.outliers_influence.variance_inflation_factor.html).
