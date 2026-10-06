# Báo cáo Lab 04

Bài thực hành sử dụng dữ liệu Ames House Price để so sánh SVR, Random Forest và XGBoost trên biến mục tiêu log1p(SalePrice). Mục tiêu là xây dựng quy trình tiền xử lý và đánh giá tác động của các phương pháp chọn đặc trưng đến sai số, số chiều và thời gian huấn luyện. Trong kết quả lưu ở notebook, XGBoost baseline đạt RMSE thấp nhất là 0,1159.

## 0 Tóm tắt EDA Lab 03

Tập train gồm 1.460 dòng và 81 cột; tập test gồm 1.459 dòng và 80 cột. Sau khi bỏ Id và SalePrice, có 79 biến giải thích: 33 biến số, 20 biến thứ bậc và 26 biến định danh. MSSubClass, MoSold và YrSold được xem là biến danh mục dù được lưu bằng số.

EDA chỉ ra các cặp tương quan mạnh GarageCars–GarageArea (0,88), GrLivArea–TotRmsAbvGrd (0,83) và TotalBsmtSF–1stFlrSF (0,82). GarageArea và TotRmsAbvGrd được đưa vào phương án loại theo VIF ở phần 2; baseline vẫn giữ các biến này. Hai dòng Id 524 và 1299 bị loại, trong khi Id 692 và 1183 được giữ.

## 1 Tiền xử lý dữ liệu

### 1.1 Tổng quan dữ liệu và biến mục tiêu

Hàm load_csv đặt keep_default_na=False và chỉ coi chuỗi NA hoặc ô trống là dữ liệu thiếu. Nhờ đó, giá trị None của MasVnrType được giữ như một mức danh mục có ý nghĩa, tránh nhầm “không có ốp tường” với dữ liệu khuyết. Kết quả đọc dữ liệu có 864 dòng MasVnrType=None và 8 dòng khuyết thực sự.

| Chỉ tiêu SalePrice     | Giá trị            |
| ------------------------ | -------------------- |
| Trung bình              | 180.921,20 USD       |
| Trung vị                | 163.000 USD          |
| Độ lệch chuẩn        | 79.442,50 USD        |
| Nhỏ nhất / lớn nhất  | 34.900 / 755.000 USD |
| Skew trước / sau log1p | 1,883 / 0,121        |

Biến đổi y = log1p(SalePrice) làm phân phối bớt lệch phải và giảm ảnh hưởng của các giá trị giá nhà lớn. Dự đoán trên thang log có thể đổi về giá tiền bằng expm1. RMSE trong bài được tính trên thang log, không phải USD và không được diễn giải trực tiếp thành phần trăm sai số giá nhà.

Hình 1 Phân phối SalePrice trước và sau log1p

### 1.2 Xử lý outlier

Notebook loại đúng hai dòng Id 524 và 1299 vì GrLivArea trên 4.000 sq ft nhưng SalePrice dưới 300.000 USD; số dòng huấn luyện giảm từ 1.460 xuống 1.458. Hai dòng Id 692 và 1183 có diện tích lớn đi kèm giá cao nên được giữ. Đây là quyết định dựa trên EDA, không phải quy tắc tự học lại trong mỗi fold.

| Chỉ tiêu                   | Trước loại | Sau loại |
| ---------------------------- | ------------- | --------- |
| Hệ số góc USD trên sq ft | 107,13        | 115,04    |
| Pearson r                    | 0,709         | 0,735     |

Hình 2 Đối chiếu diện tích và giá nhà tại các điểm ngoại lệ

IQR chỉ dùng để thống kê, không dùng để xóa thêm dòng. LotArea, MasVnrArea, LotFrontage và OpenPorchSF lần lượt có 66, 96, 86 và 75 giá trị bị gắn cờ. Các biến lệch được xử lý bằng biến đổi phân phối ở mục 1.5 để giữ lại các quan sát có thể vẫn hợp lý.

### 1.3 Kiểm tra dữ liệu thiếu

Cần phân biệt NA mang nghĩa không có tiện ích với giá trị khuyết thực sự. PoolQC thiếu 1.452 dòng (99,59%), MiscFeature 1.404 dòng (96,30%), Alley 1.367 dòng (93,76%), Fence 1.177 dòng (80,73%) và FireplaceQu 690 dòng (47,33%); các trường này được giữ để bảo toàn thông tin về sự vắng mặt của tiện ích.

| Nhóm dữ liệu                                                 | Cách xử lý trong pipeline                                                                                   |
| --------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Tiện ích dạng chữ không tồn tại                          | Điền None cho các nhóm Garage, Basement, Pool, Fence, Alley…                                              |
| MasVnrType khuyết 8 dòng                                      | Điền None; đây là giả định xử lý của notebook, không chứng minh chắc chắn tiện ích vắng mặt |
| LotFrontage 259 dòng, MasVnrArea 8 dòng, GarageYrBlt 81 dòng | Điền trung vị học trên train của từng fold                                                              |
| Electrical khuyết 1 dòng và các danh mục khác             | Điền giá trị xuất hiện nhiều nhất trong train của fold                                                |

81 dòng GarageType khuyết đều có GarageYrBlt khuyết và GarageArea bằng 0. Notebook dùng HasGarage để giữ thông tin có gara, đồng thời điền trung vị cho GarageYrBlt nhằm tránh tạo giá trị năm 0. MasVnrArea được điền trung vị theo fold; không nên mặc định trung vị luôn bằng 0 trong mọi lần chia dữ liệu.

### 1.4 Encoding

Hàm prepare bỏ Id và SalePrice, tạo HasGarage từ GarageArea > 0 và ép MSSubClass, MoSold, YrSold sang chuỗi. Sau bước này, dữ liệu có 34 biến số gồm HasGarage, 20 biến thứ bậc và 26 biến định danh; train và test có cùng danh sách cột đầu vào.

Các biến thứ bậc dùng OrdinalEncoder với thứ tự mức định trước. Ví dụ chất lượng được mã hóa theo None, Po, Fa, TA, Gd, Ex; mức chưa biết nhận giá trị -1. Biến định danh dùng OneHotEncoder với handle_unknown="ignore", nên mức chưa xuất hiện khi fit không làm bước transform thất bại. Neighborhood có 25 mức, Exterior2nd có 16 mức, Exterior1st và MSSubClass có 15 mức.

One-Hot không áp đặt quan hệ lớn nhỏ giữa các danh mục và không dùng nhãn giá nhà như Target Encoding. Tuy nhiên, thông tin của một biến gốc bị chia ra nhiều cột dummy; chọn theo từng cột có thể giữ một phần Neighborhood thay vì giữ hoặc loại toàn bộ biến gốc.

### 1.5 Biến đổi và chuẩn hóa cho SVM

Notebook chọn các biến có |skew| > 0,75, trên 10 giá trị khác nhau và tỷ lệ bằng 0 dưới 90% để áp dụng Yeo–Johnson. Có 12 biến được chọn: LotFrontage, LotArea, MasVnrArea, BsmtFinSF1, BsmtFinSF2, BsmtUnfSF, 1stFlrSF, 2ndFlrSF, GrLivArea, WoodDeckSF, OpenPorchSF và EnclosedPorch.

ColumnTransformer chia dữ liệu thành các nhóm số lệch, số còn lại, ordinal và nominal với cách điền thiếu tương ứng. Các tham số điền thiếu, Yeo–Johnson, encoder và scaler được fit lại trong pipeline của từng fold. SVR dùng StandardScaler cho nhóm numeric và ordinal; nhóm One-Hot giữ giá trị 0/1. Random Forest và XGBoost không dùng scaler trong bộ tiền xử lý.

Luồng đánh giá: dữ liệu đầu vào → chia 5 fold → fit bộ tiền xử lý trên train của fold → chọn đặc trưng trên train của fold → fit mô hình → transform và đánh giá trên validation của fold. KFold dùng shuffle=True và random_state=42. RMSE càng thấp càng tốt; R² càng cao càng tốt. RMSE được đổi dấu lại vì cross_validate trả về neg_root_mean_squared_error.

Kiểm tra fit trên toàn bộ train và transform test cho ma trận (1.458, 254) và (1.459, 254), không có NaN. Đây là kiểm tra tính tương thích đầu vào; ma trận này không được dùng thay cho bước tiền xử lý bên trong cross-validation. Số cột trong CV khoảng 250 vì mỗi fold có thể thiếu một số mức danh mục hiếm.

| Mô hình baseline        | RMSE ± std      | R² ± std       |
| ------------------------- | ---------------- | ---------------- |
| SVR RBF C=10 epsilon=0,02 | 0,1388 ± 0,0127 | 0,8780 ± 0,0223 |
| Random Forest 150 cây    | 0,1375 ± 0,0089 | 0,8803 ± 0,0190 |
| XGBoost 400 cây depth=3  | 0,1159 ± 0,0082 | 0,9151 ± 0,0126 |

XGBoost dùng learning_rate=0,05, subsample=0,8 và colsample_bytree=0,8. Các mô hình giữ cấu hình cố định để so sánh phương pháp chọn đặc trưng. Epsilon của SVR đã được chọn sau thử nhanh 0,1, 0,05 và 0,02; vì vậy kết quả không phải đánh giá cuối cùng trên tập dữ liệu độc lập chưa tham gia lựa chọn.

## 2 Feature Selection

Bộ chọn nằm giữa preprocessor và model trong Pipeline. Notebook xét 16 cấu hình × 3 mô hình × 5 fold, tương ứng 240 lượt fit ở phần chọn đặc trưng. Các kỹ thuật dùng cùng KFold và cùng cấu hình mô hình để hạn chế khác biệt do cách chia dữ liệu.

| Nhóm    | Kỹ thuật và cấu hình                                                                |
| -------- | ---------------------------------------------------------------------------------------- |
| Baseline | Giữ toàn bộ khoảng 250 cột                                                          |
| Filter   | VIF bỏ GarageArea và TotRmsAbvGrd; f_regression và Mutual Information với k=20,40,80 |
| Embedded | RF importance dùng 100 cây và top k=20,40,80; Lasso alpha=0,002 và 0,01              |
| Wrapper  | RFE dùng RF 40 cây, step=0,2 và k=20,40,80                                            |

f_regression đánh giá quan hệ tuyến tính riêng từng cột; Mutual Information đo mức phụ thuộc có thể phi tuyến nhưng vẫn chấm điểm đơn biến. RF importance dùng độ quan trọng của rừng cây để chọn top k. RFE loại dần cột dựa trên mô hình và fit lại nhiều lần. Lasso dùng phạt L1 để loại các hệ số nhỏ; bộ chọn có StandardScaler riêng, không thay đổi thang dữ liệu đưa vào mô hình phía sau.

### 2.1 Kết quả so sánh

Bảng sau chép số liệu từ output đã lưu trong notebook, làm tròn 4 chữ số thập phân. Các giá trị tốt nhất gần nhau có thể trùng sau làm tròn; thứ tự tốt nhất trong notebook được xác định từ giá trị chưa làm tròn.

| Kỹ thuật           | SVM    | Random Forest | XGBoost |
| -------------------- | ------ | ------------- | ------- |
| Baseline (tất cả)  | 0.1388 | 0.1375        | 0.1159  |
| VIF (EDA)            | 0.1390 | 0.1375        | 0.1161  |
| f_regression (k=20)  | 0.1665 | 0.1525        | 0.1451  |
| Mutual Info (k=20)   | 0.1723 | 0.1510        | 0.1390  |
| RF importance (k=20) | 0.1548 | 0.1398        | 0.1287  |
| RFE-RF (k=20)        | 0.1531 | 0.1400        | 0.1279  |
| f_regression (k=40)  | 0.1519 | 0.1452        | 0.1336  |
| Mutual Info (k=40)   | 0.1403 | 0.1387        | 0.1244  |
| RF importance (k=40) | 0.1410 | 0.1378        | 0.1235  |
| RFE-RF (k=40)        | 0.1417 | 0.1376        | 0.1235  |
| f_regression (k=80)  | 0.1402 | 0.1410        | 0.1263  |
| Mutual Info (k=80)   | 0.1339 | 0.1378        | 0.1227  |
| RF importance (k=80) | 0.1345 | 0.1371        | 0.1169  |
| RFE-RF (k=80)        | 0.1339 | 0.1368        | 0.1168  |
| Lasso (alpha=0.002)  | 0.1426 | 0.1348        | 0.1162  |
| Lasso (alpha=0.01)   | 0.1430 | 0.1337        | 0.1189  |

Với SVM, Mutual Info k=80 đạt 0,1339, giảm khoảng 3,5% so với 0,1388; RFE-RF k=80 cũng đạt 0,1339 sau làm tròn. Với Random Forest, Lasso alpha=0,01 đạt 0,1337, giảm khoảng 2,8%. XGBoost baseline đạt 0,1159; tất cả phương án chọn đặc trưng trong bảng đều có RMSE cao hơn baseline.

### 2.1 Kết quả so sánh tiếp theo

Số đặc trưng là trung bình giữa các fold, trình bày làm tròn theo notebook. Baseline khoảng 250, VIF khoảng 248; các phương pháp top k giữ đúng 20, 40 hoặc 80 cột. Lasso alpha=0,002 giữ khoảng 60 cột, alpha=0,01 giữ khoảng 34 cột. Chọn 80 cột giảm khoảng 68% số chiều so với baseline; 34 cột giảm khoảng 86%.

| Kỹ thuật           | SVM giây | RF giây | XGB giây |
| -------------------- | --------- | -------- | --------- |
| Baseline (tất cả)  | 0.30      | 2.99     | 0.45      |
| VIF (EDA)            | 0.29      | 2.83     | 0.48      |
| f_regression (k=20)  | 0.34      | 1.00     | 0.23      |
| Mutual Info (k=20)   | 1.53      | 2.08     | 1.25      |
| RF importance (k=20) | 2.19      | 3.18     | 2.15      |
| RFE-RF (k=20)        | 3.80      | 4.47     | 3.70      |
| f_regression (k=40)  | 0.32      | 1.37     | 0.24      |
| Mutual Info (k=40)   | 1.52      | 2.54     | 1.42      |
| RF importance (k=40) | 2.19      | 3.36     | 2.22      |
| RFE-RF (k=40)        | 3.99      | 5.12     | 3.86      |
| f_regression (k=80)  | 0.24      | 2.03     | 0.31      |
| Mutual Info (k=80)   | 1.44      | 3.15     | 1.55      |
| RF importance (k=80) | 2.06      | 3.90     | 2.34      |
| RFE-RF (k=80)        | 3.30      | 5.33     | 3.45      |
| Lasso (alpha=0.002)  | 0.27      | 1.36     | 0.27      |
| Lasso (alpha=0.01)   | 0.32      | 1.13     | 0.23      |

fit_time là thời gian fit toàn bộ pipeline, gồm tiền xử lý, chọn đặc trưng và huấn luyện, không phải thời gian riêng của bộ chọn. f_regression có chi phí thấp; RFE-RF thường tốn nhất với khoảng 3,30–5,33 giây ở k=80. Với RF, f_regression k=20 giảm thời gian từ 2,99 xuống 1,00 giây nhưng tăng RMSE từ 0,1375 lên 0,1525, thể hiện đánh đổi tốc độ và chất lượng. Thời gian phụ thuộc môi trường chạy và chỉ nên so sánh trong cùng một lần đo.

Hình 3 RMSE theo số đặc trưng và kỹ thuật chọn cho ba mô hình

### 2.2 Đặc trưng nào được chọn đối chiếu với EDA

Phần diễn giải fit bộ tiền xử lý và các bộ xếp hạng trên toàn bộ train. RF dùng 300 cây; Mutual Information dùng random_state=42; Lasso dùng alpha=0,005, khác hai alpha ở bảng đánh giá. Các thứ hạng này phục vụ giải thích, không phải kết quả đánh giá trên dữ liệu chưa thấy.

| Biến gốc   | Hạng RF | Hạng MI | Hạng Lasso |
| ------------ | -------- | -------- | ----------- |
| OverallQual  | 1        | 1        | 2           |
| GrLivArea    | 2        | 2        | 1           |
| GarageCars   | 4        | 6        | 11          |
| TotalBsmtSF  | 3        | 4        | 5           |
| GarageArea   | 5        | 3        | 9           |
| TotRmsAbvGrd | 26       | 17       | 162         |

OverallQual và GrLivArea đứng đầu ở cả ba cách xếp hạng, phù hợp với EDA về chất lượng và diện tích nhà. TotalBsmtSF cũng đứng trong top 5. GarageArea vẫn xếp cao dù tương quan mạnh với GarageCars; điều này cho thấy biến tương quan có thể cùng chứa tín hiệu dự báo. Kết quả VIF gần baseline hỗ trợ khả năng bỏ một biến trong cặp ở thí nghiệm này, nhưng không chứng minh chúng hoàn toàn thay thế nhau ở mọi mô hình.

TotRmsAbvGrd xếp thấp hơn, nhất là với Lasso, phù hợp giả thuyết dư thừa thông tin so với GrLivArea. Cột Neighborhood tốt nhất đứng hạng 52 ở RF, 47 ở MI và 13 ở Lasso (Neighborhood_Crawfor). Không thể kết luận vị trí địa lý ít quan trọng chỉ từ thứ hạng từng dummy; cần tổng hợp theo biến gốc để diễn giải đầy đủ hơn.

### 2.3 Kết luận

Trong các kết quả đã lưu, XGBoost baseline là phương án tốt nhất với RMSE 0,1159 và R² 0,9151. Feature Selection hữu ích chủ yếu ở việc giảm số chiều; mức cải thiện của SVM và Random Forest khoảng 0,004–0,005, nhỏ hơn độ lệch chuẩn giữa các fold. Chưa có kiểm định cặp hay lặp cross-validation để xác nhận ý nghĩa thống kê; độ lệch chuẩn không phải khoảng tin cậy của chênh lệch.

Giữ quá ít cột thường làm giảm chất lượng. Với k=20, bộ lọc đơn biến làm SVM tăng RMSE lên 0,1665 hoặc 0,1723; RF importance và RFE giữ kết quả tốt hơn ở mức k nhỏ. Khi k=80, các phương pháp dựa trên RF tiến gần baseline của XGBoost, nhưng vẫn chưa vượt baseline. Lasso alpha=0,01 phù hợp với RF trong thí nghiệm, song làm SVM tăng RMSE lên 0,1430.

Nếu ưu tiên sai số dự báo trong phạm vi bài thực hành, chọn XGBoost baseline. Nếu ưu tiên giảm chiều với Random Forest, Lasso alpha=0,01 là phương án đáng xem xét; với SVM, Mutual Info k=80 đạt kết quả tốt nhất chưa làm tròn trong output. Đây là lựa chọn từ cùng bộ kết quả CV, cần một vòng đánh giá độc lập trước khi kết luận khả năng tổng quát hóa.

#### Hạn chế và lưu ý về bằng chứng

Các tham số học của imputer, encoder, Yeo–Johnson, scaler và selector nằm trong pipeline; tuy nhiên danh sách SKEWED được chọn bằng thống kê trên toàn bộ X trước CV. Quyết định outlier và loại biến theo EDA cũng được đưa ra trước CV, trong đó có sử dụng SalePrice. Vì vậy tuyên bố “không rò rỉ dữ liệu” cần giới hạn ở các bước fit trong pipeline. Có thể tăng tính độc lập bằng cách chọn biến lệch trong transformer được fit theo fold và đánh giá cuối trên holdout hoặc CV lồng nhau.

Thí nghiệm dùng một lần chia 5-fold, chưa tối ưu k và alpha bằng CV lồng nhau. Việc thử nhiều phương án và chọn tốt nhất trên cùng CV có thể làm ước lượng kết quả lạc quan. Test.csv không có SalePrice và notebook chưa xuất dự đoán submission; bước transform test chỉ kiểm tra khả năng áp dụng tiền xử lý.

Nguồn số liệu chính là output lưu trong house_price_feature_selection.ipynb. File feature_selection_results.csv hiện có số liệu khác ở một số hàng: XGBoost baseline RMSE khoảng 0,1166 thay vì 0,1159 và thời gian RF baseline khoảng 0,70 thay vì 2,99 giây. Chưa xác định nguyên nhân khác biệt; báo cáo không trộn hai nguồn hoặc coi chúng là cùng một lần chạy. Báo cáo được lập từ source và output đã lưu, chưa chạy lại notebook từ đầu.

Tài liệu nguồn: Lab04/house_price_feature_selection.ipynb, các cell 0–28; feature_selection_results.csv được dùng để kiểm tra tính nhất quán, không thay thế số liệu notebook.
