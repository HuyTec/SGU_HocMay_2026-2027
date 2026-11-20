# Hàm dùng chung cho EDA

Ba notebook import from src.eda import helpers as eda_tools.

| Nhóm | Hàm |
|---|---|
| Dữ liệu và đặc trưng | load_context, causal_history, feature_spec, quality |
| Quan hệ với mục tiêu | grouped, continuous_relation, binned, binary_effect, matched_holidays |
| Chuỗi thời gian, trùng thông tin | acf_pairs, correlation_and_vif, stability |
| Hiển thị và vẽ hình | say, table, figure, binary_plot, corr_plot |

Module không huấn luyện model. Đối chứng đặc trưng dùng src/feature_experiments.py và năm notebook notebooks/features/feaure_V*.ipynb. Mục quyết định của EDA chỉ là tổng kết Markdown.
