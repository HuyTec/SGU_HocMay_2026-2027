# Claims từ báo cáo trực tuyến

Nguồn: snapshot toàn bộ Tab t.0; không gán số trang. Trạng thái ban đầu chờ Agent B/root đối chiếu. TableN là thứ tự bảng nội bộ trong API, không phải số bảng của báo cáo. 9 hình đã được xem trong contact sheet; 28 node công thức native chưa thấy ký hiệu.

## A-001 — 1.1. Bối cảnh và ý nghĩa đề tài

Vị trí: P0026; Docs index 802:1069. Loại: tools.

> Mỗi năm, một tài xế ở Mỹ mất trung 49 giờ vì tắc đường vậy muốn biết giờ nào đường nào sẽ đông thì sao?Cùng một con đường  7 giờ sáng và 10 giờ sáng có thể khác nhau hoàn toàn để biết trước các khung giờ trên có lưu lượng như thế nào đó là mục tiêu của đề tài này.

Cần kiểm: Nguồn gốc con số49giờ: báo cáo giao thông, quốc gia, năm, định nghĩa và trích dẫn.

CHƯA XÁC MINH; không có nguồn trong báo cáo.

## A-002 — 1.2. Mục tiêu và câu hỏi nghiên cứu

Vị trí: P0028; Docs index 1105:1251. Loại: process.

> Mục tiêu nghiên cứu xác định các yếu tố ảnh hưởng đến lưu lượng giao thông trên đường I-94 và xây dựng mô hình dự đoán lưu lượng theo thời gian.

Cần kiểm: Định nghĩa mục tiêu dự đoán/horizon, phạm vi trạm I-94, RQ định danh; tránh diễn đạt nhân quả.



## A-003 — 1.2. Mục tiêu và câu hỏi nghiên cứu

Vị trí: P0030; Docs index 1268:1361. Loại: process.

> Làm sạch dữ liệu và mô tả quy luật lưu lượng theo giờ , thứ , ngày , tháng, mua và theo năm.

Cần kiểm: Notebook EDA và bảng theo giờ/thứ/ngày/tháng/mùa/năm có thực hiện đủ không.



## A-004 — 1.2. Mục tiêu và câu hỏi nghiên cứu

Vị trí: P0031; Docs index 1361:1408. Loại: process.

> Đánh giá ảnh hưởng của thời tiết đến lưu lượng

Cần kiểm: Đối chứng thời tiết cùngcohort,cùngmodel,cùngfold; chỉ kết luận ích lợi dự đoán.



## A-005 — 1.2. Mục tiêu và câu hỏi nghiên cứu

Vị trí: P0032; Docs index 1408:1468. Loại: process.

> Đánh giá ảnh hưởng của ngày lễ so với ngày thường cùng thứ.

Cần kiểm: So ngày lễ ghép cùng thứ VÀ cùng giờ, n mỗi nhóm.



## A-006 — 1.2. Mục tiêu và câu hỏi nghiên cứu

Vị trí: P0033; Docs index 1468:1517. Loại: model comparison.

> Xây dựng và so sánh các mô hình dự báo lưu lượng

Cần kiểm: Notebook và kết quả baseline/models có cùngprotocol.



## A-007 — 1.2. Mục tiêu và câu hỏi nghiên cứu

Vị trí: P0034; Docs index 1517:1554. Loại: process.

> Rút ra gợi ý cho quản lý giao thông.

Cần kiểm: Gợi ý quản lý giao thông có giới hạn phạm vi và bằng chứng.



## A-008 — 2.1. Bài toán hồi quy và mô hình baseline

Vị trí: P0040; Docs index 1726:1938. Loại: training.

> Baseline thứ–giờ dự đoán bằng trung bình traffic_volume của cùng thứ và giờ trong train, dùng trung bình toàn train nếu thiếu nhóm. Seasonal naive dự đoán bằng quan sát tại t−168h; chỉ so trên cohort đủ lịch sử.

Cần kiểm: BaselineWeekdayHour.fit/predict, fallbackmeantrain; seasonalnaive đúngtimestamp t−168h, cohort chung.



## A-009 — 2.2. Các thuật toán sử dụng

Vị trí: P0055; Docs index 2350:2502. Loại: terminology.

> Linear Regression giả định đầu ra là tổ hợp tuyến tính của các đặc trưng: [EQUATION]. Tham số được chọn để cực tiểu sai số bình phương trung bình:

Cần kiểm: Công thức tuyến tính/loss bình phương và estimator thực dùng; equation nodes không trả ký hiệu.



## A-010 — 2.2. Các thuật toán sử dụng

Vị trí: P0057; Docs index 2580:2694. Loại: terminology.

> Ridge thêm số hạng phạt L2 để thu nhỏ trọng số, giúp giảm phương sai khi các đặc trưng tương quan mạnh với nhau:

Cần kiểm: Công thức Ridge L2, scaler trên foldtrain, estimator thực dùng.



## A-011 — 2.2. Các thuật toán sử dụng

Vị trí: P0059; Docs index 2756:2903. Loại: training.

> Hệ số [EQUATION] điều chỉnh mức phạt (thường không phạt [EQUATION]). Do phạt phụ thuộc độ lớn của [EQUATION], các đặc trưng cần được chuẩn hóa trước khi huấn luyện.

Cần kiểm: Alpha/intercept/scaling qua pipeline thực; ký hiệu phương trình cần kiểm hình.



## A-012 — 2.2. Các thuật toán sử dụng

Vị trí: P0060; Docs index 2903:3145. Loại: architecture.

> Random Forest (RF): huấn luyện với [EQUATION] cây quyết định, mỗi cây trên một mẫu bootstrap của dữ liệu. Tại mỗi nút, cây chỉ xét một tập con ngẫu nhiên [EQUATION] đặc trưng để chọn điểm chia. Hai nguồn ngẫu nhiên này làm các cây ít tương quan với nhau.

Cần kiểm: RandomForestRegressor bootstrap,max_features và random_state của lần chạy thực.



## A-013 — 2.2. Các thuật toán sử dụng

Vị trí: P0062; Docs index 3176:3405. Loại: training.

> Với bài toán phân loại, kết quả lấy theo đa số phiếu. Việc lấy trung bình giúp giảm phương sai so với một cây đơn mà gần như không tăng độ chệch. Sai số out-of-bag (OOB) cho ước lượng đánh giá mà không cần tập validation riêng.

Cần kiểm: Tách lý thuyết OOB khỏi giao thức chuỗi thời gian; kiểm có thực dùngOOB không; OOB không thay thế temporalvalidation.



## A-014 — 2.2. Các thuật toán sử dụng

Vị trí: P0063; Docs index 3405:3575. Loại: terminology.

> Gradient Boosting (GB): xây mô hình cộng tính, mỗi cây mới sửa lỗi của mô hình hiện tại. Tại bước [EQUATION], cây [EQUATION] được khớp vào phần dư giả (âm gradient của hàm loss):

Cần kiểm: GradientBoostingRegressor loss, mô hình cộng tính, pseudo-residual.



## A-015 — 2.2. Các thuật toán sử dụng

Vị trí: P0066; Docs index 3666:3839. Loại: hyperparameter.

> Với loss bình phương, [EQUATION], tức đúng là phần dư. Tốc độ học [EQUATION] làm mỗi cây đóng góp nhỏ, đổi lại cần nhiều cây hơn nhưng khái quát tốt hơn.

Cần kiểm: loss bình phương vàlearning_rate thực; tránh khẳng định khái quát luôn tốt hơn.



## A-016 — 2.2. Các thuật toán sử dụng

Vị trí: P0067; Docs index 3839:3958. Loại: architecture.

> MLP: gồm nhiều tầng, mỗi tầng là phép biến đổi tuyến tính theo sau bởi hàm kích hoạt phi tuyến [EQUATION] (ReLU, GELU, ...):

Cần kiểm: MLPRegressor activation thực; ReLU/GELU chỉ ví dụ lý thuyết.



## A-017 — 2.2. Các thuật toán sử dụng

Vị trí: P0069; Docs index 4035:4283. Loại: training.

> Tham số [EQUATION] được cập nhật bằng lan truyền ngược và gradient descent: [EQUATION] (hoặc biến thể như Adam). MLP nhạy với thang đo của đầu vào nên cần chuẩn hóa dữ liệu. Kết quả cũng phụ thuộc nhiều vào khởi tạo, tốc độ học [EQUATION] và điều kiện dừng.

Cần kiểm: MLP solver,seed,scaler,learning_rate,stopping thực.



## A-018 — 2.2. Các thuật toán sử dụng

Vị trí: P0070; Docs index 4283:4416. Loại: terminology.

> XGBoost (XGB): là Gradient Boosting có thêm regularization trực tiếp trong hàm mục tiêu, và dùng khai triển Taylor bậc hai của loss:

Cần kiểm: XGBoost objective/regularization/Taylor và tài liệu gốc.



## A-019 — 2.2. Các thuật toán sử dụng

Vị trí: P0071; Docs index 4416:4619. Loại: figures.

> [IMAGE kix.w9z2mkqqadwv]Trong đó [EQUATION] là số lá và [EQUATION] là trọng số lá. Với [EQUATION] là đạo hàm bậc một và bậc hai của loss, [EQUATION] và [EQUATION], trọng số tối ưu của lá và độ lợi khi chia nút là:

Cần kiểm: XGBoost hìnhobjective và ký hiệuT,w,g,h; nodeequation không chứa glyph.



## A-020 — 2.2. Các thuật toán sử dụng

Vị trí: P0072; Docs index 4619:4621. Loại: figures.

> [IMAGE kix.9ruxm9cqjlyg]

Cần kiểm: Công thức trọng sốlá vàgain trong ảnh; so tài liệugốc.



## A-021 — 2.2. Các thuật toán sử dụng

Vị trí: P0073; Docs index 4621:4714. Loại: hyperparameter.

> Tham số [EQUATION] và [EQUATION] kiểm soát độ phức tạp của cây: nút chỉ được chia khi độ lợi lớn hơn [EQUATION].

Cần kiểm: Gamma/lambda regularization và điều kiện chia đúnglossconvention.



## A-022 — 2.3. Độ đo đánh giá hồi quy

Vị trí: P0075; Docs index 4742:4837. Loại: metrics.

> Đánh giá hồi quy bằng 3 thông số sau, với eᵢ = yᵢ − ŷᵢ và ȳ là trung bình y trên tập đang xét:

Cần kiểm: Định nghĩa error e_i vàmean evaluation cohort.



## A-023 — 2.3. Độ đo đánh giá hồi quy

Vị trí: P0076; Docs index 4837:4839. Loại: figures.

> [IMAGE kix.3xshvl3zek52]

Cần kiểm: Công thức MAE trong ảnh cần quan sát hình.



## A-024 — 2.3. Độ đo đánh giá hồi quy

Vị trí: P0077; Docs index 4839:4841. Loại: figures.

> [IMAGE kix.ojenq5gde4a2]

Cần kiểm: Công thức RMSE trong ảnh cần quan sát hình.



## A-025 — 2.3. Độ đo đánh giá hồi quy

Vị trí: P0078; Docs index 4841:4843. Loại: figures.

> [IMAGE kix.107jhofbxxr9]

Cần kiểm: Công thức R² trong ảnh cần quan sát hình.



## A-026 — 2.3. Độ đo đánh giá hồi quy

Vị trí: P0079; Docs index 4843:5103. Loại: metrics.

> MAE và RMSE có đơn vị xe/giờ. MAE là sai số tuyệt đối trung bình, còn RMSE phạt nặng hơn các sai số lớn. R² không có đơn vị: nó so sai số của mô hình với sai số của cách luôn dự đoán ȳ, bằng 1 khi dự đoán hoàn hảo, bằng 0 khi ngang cách đó và âm khi kém hơn.

Cần kiểm: Hàm MAE/RMSE/R²,đơn vị xe/giờ,ý nghĩa so baseline constantmean.



## A-027 — 2.3. Độ đo đánh giá hồi quy

Vị trí: P0080; Docs index 5103:5337. Loại: metrics.

> MAE và RMSE có thể xếp hạng các mô hình khác nhau, nên báo cáo cả hai và nêu rõ metric dùng để chọn tham số. Các hàm đánh giá hiện tại cắt dự đoán âm về 0 trước khi tính điểm, nên mọi mô hình được so sánh phải dùng cùng quy tắc này.

Cần kiểm: Tấtcả scorehelper/OOF/validation có cắtprediction<0 về0 đồngnhất; primarymetricthựcdùng.



## A-028 — 2.4. Dữ liệu chuỗi thời gian, chia dữ liệu theo thời gian và data leakage

Vị trí: P0082; Docs index 5411:5629. Loại: training.

> Dữ liệu được sắp theo timestamp, nên phần huấn luyện luôn đứng trước phần đánh giá. Tuning dùng Time Series Split trên tập train. Imputation, encoder và scaler có học thống kê phải được fit trên fold-train tương ứng.

Cần kiểm: Splitthờigian,TimeSeriesSplit trêntrain,fitimputer/encoder/scaler từngfold.



## A-029 — 2.4. Dữ liệu chuỗi thời gian, chia dữ liệu theo thời gian và data leakage

Vị trí: P0083; Docs index 5629:5967. Loại: training.

> Theo tài liệu TimeSeriesSplit, các fold đánh giá chỉ phủ cùng một khoảng thời gian khi các mẫu cách đều. Dữ liệu ở đây thiếu giờ, nên các fold có cùng số hàng chưa chắc phủ cùng khoảng lịch. Vì vậy, khi diễn giải độ ổn định, cần ghi mốc thời gian và số mẫu của từng fold, và chỉ mô tả các fold là cửa sổ lịch bằng nhau nếu đã kiểm tra. [PAGE BREAK]

Cần kiểm: Foldmanifestn vàstart/end; tài liệuTimeSeriesSplit về equalspacing.



## A-030 — 3.1.1. Nguồn dữ liệu và phạm vi và quy mô

Vị trí: P0087; Docs index 6061:6402. Loại: data & preprocessing.

> Bộ Metro Interstate Traffic Volume do John Hogue công bố trên UCI năm 2019. Dữ liệu ghi lưu lượng theo giờ tại trạm ATR 301, I-94 hướng Tây, khu vực Minneapolis-St Paul, và phát hành theo CC BY 4.0. CSV của dự án có 48.204 dòng, 9 cột gồm 8 đầu vào và một biến mục tiêu; timestamp trải từ 02/10/2012 09:00 đến 30/09/2018 23:00. Nguồn: UCI.

Cần kiểm: UCIHogue2019/ATR301I94westbound/CCBY4 + CSVshape/datebounds.



## A-031 — 3.1.1. Nguồn dữ liệu và phạm vi và quy mô

Vị trí: P0088; Docs index 6402:6732. Loại: data & preprocessing.

> Các số kiểm tra riêng từ CSV: 40.575 timestamp duy nhất, 7.629 dòng vượt số timestamp duy nhất và 11.976 giờ không có quan sát trong lưới giờ từ đầu đến cuối. 7.629 là số dòng dư theo khóa thời gian, chưa chắc là số bản ghi trùng hoàn toàn. Số giờ thiếu tính trên timestamp không gắn timezone như trong file; chưa phân tích DST.

Cần kiểm: CSVunique40575,excess7629,missinghour11976,naive timestamp/DST chưa xử lý.



## A-032 — 3.2.1 Tổng quan và chất lượng dữ liệu

Vị trí: P0135; Docs index 8154:8377. Loại: data & preprocessing.

> Timestamp lặp không đồng nghĩa với dòng trùng hoàn toàn. Các dòng cùng giờ có lưu lượng nhất quán nhưng có thể khác nhãn thời tiết, như minh họa ở Bảng 3.3. Vì vậy, không được cộng lặp traffic_volume khi tổng hợp theo giờ.

Cần kiểm: groupbytimestamp y.nunique()==1,không sumtarget; rawrows ví dụ.



## A-033 — 3.2.1 Tổng quan và chất lượng dữ liệu

Vị trí: P0170; Docs index 9392:9634. Loại: data & preprocessing.

> Không có null không đồng nghĩa dữ liệu hoàn toàn sạch. Giờ vắng bản ghi ở mục 3.1 không được quy thành lưu lượng 0. Với mưa/tuyết, Q1 và Q3 đều bằng 0 nên IQR có thể gắn cờ cả các giá trị dương hợp lý. Các vấn đề trên được xử lý tại mục 3.3.

Cần kiểm: Targetgap không điền0; quantilesrain/snow Q1Q3=0; tiề nxửlýmục3.3 hiệnchưaviết.



## A-034 — 3.2.2. Phân bố lưu lượng giao thông

Vị trí: P0172; Docs index 9670:9891. Loại: data & preprocessing.

> Sau bước kiểm tra chất lượng dữ liệu, nhóm khảo sát phân bố của biến mục tiêu traffic_volume trên 40.575 giờ quan sát duy nhất. Mỗi timestamp chỉ được tính một lần; các thống kê dưới đây sử dụng toàn bộ dữ liệu theo giờ.

Cần kiểm: EDA_general dùng toàn40575uniquehour; phân biệt nguồn phân tích khámphá với trainingfeatures.



## A-035 — 3.2.2. Phân bố lưu lượng giao thông

Vị trí: P0196; Docs index 10277:10495. Loại: data & preprocessing.

> Trung bình thấp hơn trung vị khoảng 136,35 xe/giờ. Một nửa số giờ quan sát có lưu lượng từ 1.248,50 đến 4.952 xe/giờ; độ lệch chuẩn khoảng 1.984,77 xe/giờ cho thấy lưu lượng phân tán đáng kể quanh giá trị trung bình.[PAGE BREAK]

Cần kiểm: Tính3290.65−3427=-136.35,Q1/Q3/std đúngfullhourly.



## A-036 — 3.2.2. Phân bố lưu lượng giao thông

Vị trí: P0198; Docs index 10518:10630. Loại: figures.

> Hình 3.1 kết hợp histogram và boxplot để thể hiện tần suất quan sát, trung vị và khoảng phân bố của lưu lượng.[IMAGE kix.exjdsthkcy2o]

Cần kiểm: ẢnhHình3.1 có cảhistogramboxplot và nguồnfullhourly.



## A-037 — 3.2.2. Phân bố lưu lượng giao thông

Vị trí: P0199; Docs index 10630:10700. Loại: figures.

> Hình 3.1. Phân bố lưu lượng giao thông trên các giờ quan sát duy nhất

Cần kiểm: ChúthíchHình3.1 khớp dữliệu/ảnh,đơnvị,n.



## A-038 — 3.2.2. Phân bố lưu lượng giao thông

Vị trí: P0200; Docs index 10700:11029. Loại: figures.

> Histogram có nhiều vùng tập trung, không thể hiện một đỉnh duy nhất rõ rệt. Boxplot cho thấy khoảng giữa Q1 và Q3 khá rộng, phù hợp với mức phân tán trong Bảng 3.5. Phân bố tổng thể chưa cho biết các vùng lưu lượng này xuất hiện vào thời điểm nào; mục tiếp theo phân tích theo giờ, thứ và loại ngày để làm rõ mẫu hình thời gian.

Cần kiểm: Ảnhhistogram đa vùngtậptrung/boxplotIQR so với data.



## A-039 — 3.2.3. Lưu lượng theo thời gian

Vị trí: P0202; Docs index 11061:11224. Loại: data & preprocessing.

> Nhóm phân tích lưu lượng theo giờ, thứ và tháng trên toàn bộ 40.575 timestamp duy nhất. Các thống kê chỉ tính giờ có bản ghi, không gán lưu lượng 0 cho giờ thiếu.

Cần kiểm: Bảnggiờ/thứ/tháng trên40575uniquehours,khôngzero-fillgaps.



## A-040 — 3.2.3. Lưu lượng theo thời gian

Vị trí: P0206; Docs index 11353:11419. Loại: figures.

> Hình 3.2. Lưu lượng trung bình theo giờ, thứ trong tuần và tháng[PAGE BREAK]

Cần kiểm: Hình3.2đúng3biểuđồmean hour/weekday/month;đơnvị,n.



## A-041 — 3.2.3. Lưu lượng theo thời gian

Vị trí: P0239; Docs index 12010:12074. Loại: figures.

> Hình 3.3 lưu lượng trung bình theo tổ hợp thứ trong tuần và giờ

Cần kiểm: Hình3.3đúngthứ–giờ,khácweekday/weekend;labelđủ.



## A-042 — 3.2.3. Lưu lượng theo thời gian

Vị trí: P0240; Docs index 12074:12307. Loại: model comparison.

> Từ thứ Hai đến thứ Sáu, lưu lượng cao tập trung vào buổi sáng và chiều; cuối tuần tăng muộn hơn, tập trung quanh giữa ngày. Kết quả gợi ý xem xét đồng thời giờ, thứ và cờ cuối tuần; giá trị dự đoán cần kiểm chứng ở phần thực nghiệm.

Cần kiểm: Groupmeans/heatmapthứ–giờ; chỉ gợi ý tươngtác,không xem làđãchọnfeature.



## A-043 — 3.2.4. Mối liên  hệ giữa thời tiết và lưu lượng

Vị trí: P0243; Docs index 12401:12597. Loại: data & preprocessing.

> Bảng 3.7 tính sau khi đánh dấu nhiệt độ 0 K và điểm mưa 9.831,3 mm là thiếu, rồi gộp thời tiết theo giờ bằng median các giá trị phân biệt. n là số cặp quan sát hợp lệ của từng biến với lưu lượng.

Cần kiểm: temp0/rain9831.3->NaN; medianunique perhour trước corr; nvalidpairs.



## A-044 — 3.2.4. Mối liên  hệ giữa thời tiết và lưu lượng

Vị trí: P0265; Docs index 12867:13034. Loại: terminology.

> Nhiệt độ có tương quan dương yếu; mưa và tuyết có hệ số gần 0. Tương quan riêng lẻ thấp chưa loại trừ quan hệ phi tuyến hoặc giá trị bổ sung khi kết hợp với thời gian

Cần kiểm: Pearson/Spearman mô tả yếu khôngloạiphi tuyến; FE ablation kiểm íchlợithêm.



## A-045 — 3.2.4. Mối liên  hệ giữa thời tiết và lưu lượng

Vị trí: P0269; Docs index 13184:13235. Loại: figures.

> Hình 3.4. Lưu lượng trung bình theo nhãn thời tiết

Cần kiểm: Hình3.4đúngweather_main vsmeantraffic và samplecounts.



## A-046 — 3.2.4. Mối liên  hệ giữa thời tiết và lưu lượng

Vị trí: P0287; Docs index 13415:13645. Loại: data & preprocessing.

> Một giờ được tính một lần trong mỗi nhóm nhưng có thể mang nhiều nhãn; có 5.349 giờ như vậy. Clouds có trung bình cao nhất, còn Squall thấp nhất nhưng chỉ có 4 giờ. Nhóm Smoke cũng hiếm (20 giờ), nên cần thận trọng khi diễn giải.

Cần kiểm: Nhómweather multi-label5349hours;Cloudsmeanmax/Squallminn4/Smoken20.



## A-047 — 3.2.4. Mối liên  hệ giữa thời tiết và lưu lượng

Vị trí: P0288; Docs index 13645:13833. Loại: model comparison.

> Chênh lệch giữa các nhãn có thể gắn với giờ và mùa, không chứng minh nhân quả. Ích lợi dự đoán của thời tiết cần được kiểm chứng bằng đối chứng cùng mô hình và tập giờ ở phần thực nghiệm.

Cần kiểm: Weatherconfounding theo giờ/mùa; giátrịdựđoán qua matchedablation.



## A-048 — 3.5. Pipeline học máy

Vị trí: P0301; Docs index 14394:14505. Loại: process.

> Gợi ý: Chèn sơ đồ pipeline: dữ liệu → tiền xử lý → đặc trưng → chia tập → huấn luyện/tuning → đánh giá → demo.

Cần kiểm: Sơđồpipeline phân biệttransformdeterministic trướcsplit vàfitstatistics saufoldsplit; đây chỉ làgợiý,chưa phải kết quả.



## A-049 — 3.6.2. Kiểm soát data leakage và tính công bằng khi so sánh

Vị trí: P0308; Docs index 14754:14895. Loại: process.

> Gợi ý: Cách fit preprocessing chỉ trên train; không dùng test để chọn mô hình/tuning; các mô hình dùng cùng tập, cùng mốc chia, cùng metric.

Cần kiểm: Giao thứcchốngleakage/equalcohort vàtestuntouched; đây làyêucầutemplate.



## A-050 — 3.6.4. Độ đo và phương án tinh chỉnh siêu tham số

Vị trí: P0313; Docs index 14991:15109. Loại: hyperparameter.

> Gợi ý: Phương pháp (Grid/Random Search + CV theo thời gian), không gian tham số, chỉ số chọn mô hình trên validation.

Cần kiểm: CVsearchspace/ngânsách/seed/selectionmetric và rolevalidation; templatechưacókếtquả.



## A-051 — 3.6.5. Thiết kế thí nghiệm đối chứng đặc trưng

Vị trí: P0316; Docs index 15171:15296. Loại: model comparison.

> Gợi ý: Time, Time + Weather, Time + Weather + History: cùng thuật toán, cùng tập và mốc chia, để trả lời câu hỏi nghiên cứu.

Cần kiểm: A12/B27/C30 hoặc5FEconfigs cùngmodel/params/cohort/folds; templatechưacókếtquả.



## A-052 — 3.6.5. Thiết kế thí nghiệm đối chứng đặc trưng

Vị trí: P0318; Docs index 15311:15704. Loại: training.

> Dự đoán ngoài fold (Out-of-Fold — OOF) được tạo bằng phương pháp TimeSeriesSplit với ba fold. Ở mỗi fold, mô hình được huấn luyện trên dữ liệu quá khứ và dự đoán trên đoạn dữ liệu tiếp theo; các bước tiền xử lý có học thống kê cũng chỉ được fit trên phần huấn luyện tương ứng. Các dự đoán được ghép theo timestamp để đánh giá trên những quan sát chưa tham gia huấn luyện mô hình tạo ra chúng.

Cần kiểm: OOF3TimeSeriesSplit; fitpasttransform foldtrain,predictnext,align timestamp.



## A-053 — 3.6.5. Thiết kế thí nghiệm đối chứng đặc trưng

Vị trí: P0319; Docs index 15704:16009. Loại: training.

> Trong thí nghiệm ensemble, Random Forest và XGBoost sử dụng cùng cấu hình đặc trưng, bộ chia và các giờ chấm. Trọng số kết hợp được lựa chọn theo MAE trên dự đoán OOF thuộc tập train. Sau khi chọn trọng số, hai mô hình được huấn luyện lại trên toàn bộ tập train và ensemble được đánh giá trên validation.

Cần kiểm: RF+XGB cohort/folds/OOFweightselection/refitfulltrain/validation; cần phânbiệt20–21Nov vàfinal22NovthêmExtraTrees.



## A-054 — 3.6.5. Thiết kế thí nghiệm đối chứng đặc trưng

Vị trí: P0320; Docs index 16009:16147. Loại: metrics.

> Do OOF được sử dụng để lựa chọn trọng số, MAE OOF tại trọng số được chọn là điểm phục vụ lựa chọn, chưa phải đánh giá độc lập cuối cùng.

Cần kiểm: OOF dùng chọnweight làselectionscore,khôngđộc lập; tuningmodels trêncùngfold cũngtạooptimism.



## A-055 — 4.4. So sánh các mô hình trên tập test

Vị trí: P0332; Docs index 16544:16638. Loại: process.

> Gợi ý: Chỉ đánh giá test một lần cho mô hình đã chốt; so sánh công bằng cùng tập và tiêu chí.

Cần kiểm: Test-once làgợiýtươnglai; đối chiếutestevaluatedflag,khôngghi làđãtest.



## A-056 — 2.2. Các thuật toán sử dụng

Vị trí: P0044, P0045; Docs index 1992:2078. Loại: architecture.

> Linear Regression (LR)/ Ridge | Quan hệ tuyến tính, ngoài ra Ridge còn có phạt thêm L2

Cần kiểm: Kiểm từng ô của Table2 dòng2 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-057 — 2.2. Các thuật toán sử dụng

Vị trí: P0046, P0047; Docs index 2080:2134. Loại: architecture.

> Random Forest ̣(RF) | Trung bình dự đoán của nhiều cây

Cần kiểm: Kiểm từng ô của Table2 dòng3 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-058 — 2.2. Các thuật toán sử dụng

Vị trí: P0048, P0049; Docs index 2136:2197. Loại: architecture.

> Gradient Boosting | Bổ sung cây tuần tự để cải thiện hàm loss

Cần kiểm: Kiểm từng ô của Table2 dòng4 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-059 — 2.2. Các thuật toán sử dụng

Vị trí: P0050, P0051; Docs index 2199:2258. Loại: architecture.

> MLP | Nhiều tầng phi tuyến, nhạy với thang đo và tối ưu hóa

Cần kiểm: Kiểm từng ô của Table2 dòng5 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-060 — 2.2. Các thuật toán sử dụng

Vị trí: P0052, P0053; Docs index 2260:2315. Loại: architecture.

> XGBoost | Boosting  các cây theo cơ chế regularization

Cần kiểm: Kiểm từng ô của Table2 dòng6 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-061 — 3.1.2. Danh sách thuộc tính và biến mục tiêu

Vị trí: P0093, P0094, P0095; Docs index 6826:6961. Loại: data & preprocessing.

> holiday | Nhãn | Ngày lễ quốc gia Mỹ và ngày lễ khu vực (Minnesota State Fair). Chuỗi None là một nhãn hợp lệ, không phải giá trị thiếu.

Cần kiểm: Kiểm từng ô của Table3 dòng2 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-062 — 3.1.2. Danh sách thuộc tính và biến mục tiêu

Vị trí: P0096, P0097, P0098; Docs index 6963:7042. Loại: data & preprocessing.

> temp | Số thực, K | Nhiệt độ trung bình theo giờ; đổi sang °C khi tạo đặc trưng.

Cần kiểm: Kiểm từng ô của Table3 dòng3 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-063 — 3.1.2. Danh sách thuộc tính và biến mục tiêu

Vị trí: P0099, P0100, P0101; Docs index 7044:7111. Loại: data & preprocessing.

> rain_1h, snow_1h | Số thực, mm | Lượng mưa và lượng tuyết trong giờ.

Cần kiểm: Kiểm từng ô của Table3 dòng4 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-064 — 3.1.2. Danh sách thuộc tính và biến mục tiêu

Vị trí: P0102, P0103, P0104; Docs index 7113:7155. Loại: data & preprocessing.

> clouds_all | Số nguyên, % | Độ che phủ mây.

Cần kiểm: Kiểm từng ô của Table3 dòng5 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-065 — 3.1.2. Danh sách thuộc tính và biến mục tiêu

Vị trí: P0105, P0106, P0107; Docs index 7157:7218. Loại: data & preprocessing.

> weather_main | Nhãn văn bản | Mô tả thời tiết ngắn (nhóm lớn).

Cần kiểm: Kiểm từng ô của Table3 dòng6 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-066 — 3.1.2. Danh sách thuộc tính và biến mục tiêu

Vị trí: P0108, P0109, P0110; Docs index 7220:7298. Loại: data & preprocessing.

> weather_description | Nhãn văn bản | Mô tả thời tiết chi tiết hơn weather_main.

Cần kiểm: Kiểm từng ô của Table3 dòng7 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-067 — 3.1.2. Danh sách thuộc tính và biến mục tiêu

Vị trí: P0111, P0112, P0113; Docs index 7300:7364. Loại: data & preprocessing.

> date_time | Timestamp | Khóa thời gian; nguồn tạo đặc trưng lịch.

Cần kiểm: Kiểm từng ô của Table3 dòng8 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-068 — 3.1.2. Danh sách thuộc tính và biến mục tiêu

Vị trí: P0114, P0115, P0116; Docs index 7366:7416. Loại: data & preprocessing.

> traffic_volume | Số nguyên, xe/giờ | Biến mục tiêu.

Cần kiểm: Kiểm từng ô của Table3 dòng9 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-069 — 3.2.1 Tổng quan và chất lượng dữ liệu

Vị trí: P0125, P0126; Docs index 7865:7931. Loại: data & preprocessing.

> Giá trị Null,Giá trị null; chuỗi rỗng hoặc chỉ có khoảng trắng | 0

Cần kiểm: Kiểm từng ô của Table4 dòng2 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-070 — 3.2.1 Tổng quan và chất lượng dữ liệu

Vị trí: P0127, P0128; Docs index 7933:7994. Loại: data & preprocessing.

> Dòng trùng hoàn toàn, không tính lần xuất hiện đầu. | 17 dòng

Cần kiểm: Kiểm từng ô của Table4 dòng3 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-071 — 3.2.1 Tổng quan và chất lượng dữ liệu

Vị trí: P0129, P0130; Docs index 7996:8043. Loại: data & preprocessing.

> Timestamp xuất hiện nhiều lần | 5.445 timestamp

Cần kiểm: Kiểm từng ô của Table4 dòng4 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-072 — 3.2.1 Tổng quan và chất lượng dữ liệu

Vị trí: P0131, P0132; Docs index 8045:8096. Loại: data & preprocessing.

> Tổng số dòng thuộc các timestamp lăpk | 13.074 dòng

Cần kiểm: Kiểm từng ô của Table4 dòng5 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-073 — 3.2.1 Tổng quan và chất lượng dữ liệu

Vị trí: P0133, P0134; Docs index 8098:8153. Loại: data & preprocessing.

> Timestamp có nhiều giá trị Traffic_volume khác nhau | 0

Cần kiểm: Kiểm từng ô của Table4 dòng6 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-074 — 3.2.1 Tổng quan và chất lượng dữ liệu

Vị trí: P0141, P0142, P0143, P0144; Docs index 8500:8542. Loại: data & preprocessing.

> 10/10/2012 07:00 | Rain | light rain | 6.793

Cần kiểm: Kiểm từng ô của Table5 dòng2 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-075 — 3.2.1 Tổng quan và chất lượng dữ liệu

Vị trí: P0145, P0146, P0147, P0148; Docs index 8544:8602. Loại: data & preprocessing.

> 10/10/2012 07:00 | Drizzle | light intensity drizzle | 6.793

Cần kiểm: Kiểm từng ô của Table5 dòng3 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-076 — 3.2.1 Tổng quan và chất lượng dữ liệu

Vị trí: P0155, P0156, P0157; Docs index 8818:8934. Loại: data & preprocessing.

> Nhiệt độ bằng 0 K | 10 dòng tại 10 giờ quan sát. | Không phù hợp với điều kiện quan trắc ngoài trời; cần xử lý riêng.

Cần kiểm: Kiểm từng ô của Table6 dòng2 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-077 — 3.2.1 Tổng quan và chất lượng dữ liệu

Vị trí: P0158, P0159, P0160; Docs index 8936:9052. Loại: data & preprocessing.

> Lượng mưa cực lớn | 9.831,3 mm tại 11/07/2016 17:00. | Giá trị nghi vấn; không dùng IQR để loại mọi lượng mưa dương..

Cần kiểm: Kiểm từng ô của Table6 dòng3 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-078 — 3.2.1 Tổng quan và chất lượng dữ liệu

Vị trí: P0161, P0162, P0163; Docs index 9054:9159. Loại: data & preprocessing.

> Lưu lượng bằng 0 | 23/07/2016 lúc 18:00 và 23:00. | Chưa xác minh nguyên nhân; chưa đủ căn cứ tự động xoá.

Cần kiểm: Kiểm từng ô của Table6 dòng4 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-079 — 3.2.1 Tổng quan và chất lượng dữ liệu

Vị trí: P0164, P0165, P0166; Docs index 9161:9254. Loại: data & preprocessing.

> Khác cách viết nhãn | sky is clear và Sky is Clear. | Cùng nội dung nhưng khác chữ hoa/thường.

Cần kiểm: Kiểm từng ô của Table6 dòng5 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-080 — 3.2.1 Tổng quan và chất lượng dữ liệu

Vị trí: P0167, P0168, P0169; Docs index 9256:9391. Loại: data & preprocessing.

> Nhãn ngày lễ | Nhãn sự kiện thường ghi lúc 00:00. | Cần kiểm tra nhãn theo ngày; không suy mọi giờ có holiday = None đều là ngày thường.

Cần kiểm: Kiểm từng ô của Table6 dòng6 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-081 — 3.2.2. Phân bố lưu lượng giao thông

Vị trí: P0180, P0181, P0182, P0183; Docs index 10077:10123. Loại: data & preprocessing.

> Trung bình | 3.290,65 | Trung vị (Q2) | 3.427,00

Cần kiểm: Kiểm từng ô của Table7 dòng2 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-082 — 3.2.2. Phân bố lưu lượng giao thông

Vị trí: P0184, P0185, P0186, P0187; Docs index 10125:10188. Loại: data & preprocessing.

> Độ lệch chuẩn mẫu | 1.984,77 | Khoảng tứ phân vị (IQR) | 3.703,50

Cần kiểm: Kiểm từng ô của Table7 dòng3 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-083 — 3.2.2. Phân bố lưu lượng giao thông

Vị trí: P0188, P0189, P0190, P0191; Docs index 10190:10245. Loại: data & preprocessing.

> Phân vị 25% (Q1) | 1.248,50 | Phân vị 75% (Q3) | 4.952,00

Cần kiểm: Kiểm từng ô của Table7 dòng4 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-084 — 3.2.2. Phân bố lưu lượng giao thông

Vị trí: P0192, P0193, P0194, P0195; Docs index 10247:10276. Loại: data & preprocessing.

> Nhỏ nhất | 0 | Lớn nhất | 7.280

Cần kiểm: Kiểm từng ô của Table7 dòng5 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-085 — 3.2.3. Lưu lượng theo thời gian

Vị trí: P0212, P0213, P0214, P0215; Docs index 11546:11596. Loại: data & preprocessing.

> Giờ trong ngày — 16:00 | Cao nhất | 5.708,61 | 1.707

Cần kiểm: Kiểm từng ô của Table8 dòng2 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-086 — 3.2.3. Lưu lượng theo thời gian

Vị trí: P0216, P0217, P0218, P0219; Docs index 11598:11648. Loại: data & preprocessing.

> Giờ trong ngày — 03:00 | Thấp nhất | 373,21 | 1.669

Cần kiểm: Kiểm từng ô của Table8 dòng3 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-087 — 3.2.3. Lưu lượng theo thời gian

Vị trí: P0220, P0221, P0222, P0223; Docs index 11650:11702. Loại: data & preprocessing.

> Thứ trong tuần — Thứ Sáu | Cao nhất | 3.674,78 | 5.877

Cần kiểm: Kiểm từng ô của Table8 dòng4 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-088 — 3.2.3. Lưu lượng theo thời gian

Vị trí: P0224, P0225, P0226, P0227; Docs index 11704:11758. Loại: data & preprocessing.

> Thứ trong tuần — Chủ nhật | Thấp nhất | 2.426,25 | 5.812

Cần kiểm: Kiểm từng ô của Table8 dòng5 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-089 — 3.2.3. Lưu lượng theo thời gian

Vị trí: P0228, P0229, P0230, P0231; Docs index 11760:11813. Loại: data & preprocessing.

> Tháng trong năm — Tháng 8 | Cao nhất | 3.430,32 | 3.705

Cần kiểm: Kiểm từng ô của Table8 dòng6 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-090 — 3.2.3. Lưu lượng theo thời gian

Vị trí: P0232, P0233, P0234, P0235; Docs index 11815:11870. Loại: data & preprocessing.

> Tháng trong năm — Tháng 12 | Thấp nhất | 3.040,19 | 3.337

Cần kiểm: Kiểm từng ô của Table8 dòng7 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-091 — 3.2.4. Mối liên  hệ giữa thời tiết và lưu lượng

Vị trí: P0249, P0250, P0251, P0252; Docs index 12712:12745. Loại: data & preprocessing.

> Nhiệt độ | 0,1392 | 0,1401 | 40.565

Cần kiểm: Kiểm từng ô của Table9 dòng2 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-092 — 3.2.4. Mối liên  hệ giữa thời tiết và lưu lượng

Vị trí: P0253, P0254, P0255, P0256; Docs index 12747:12782. Loại: data & preprocessing.

> Lượng mưa | −0,0134 | 0,0043 | 40.574

Cần kiểm: Kiểm từng ô của Table9 dòng3 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-093 — 3.2.4. Mối liên  hệ giữa thời tiết và lưu lượng

Vị trí: P0257, P0258, P0259, P0260; Docs index 12784:12822. Loại: data & preprocessing.

> Lượng tuyết | −0,0021 | −0,0052 | 40.575

Cần kiểm: Kiểm từng ô của Table9 dòng4 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-094 — 3.2.4. Mối liên  hệ giữa thời tiết và lưu lượng

Vị trí: P0261, P0262, P0263, P0264; Docs index 12824:12866. Loại: data & preprocessing.

> Tỷ lệ mây che phủ | 0,0783 | 0,0729 | 40.575

Cần kiểm: Kiểm từng ô của Table9 dòng5 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-095 — 3.2.4. Mối liên  hệ giữa thời tiết và lưu lượng

Vị trí: P0275, P0276, P0277, P0278; Docs index 13334:13362. Loại: data & preprocessing.

> Clouds | 15.127 | Snow | 2.795

Cần kiểm: Kiểm từng ô của Table10 dòng2 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-096 — 3.2.4. Mối liên  hệ giữa thời tiết và lưu lượng

Vị trí: P0279, P0280, P0281, P0282; Docs index 13364:13389. Loại: data & preprocessing.

> Clear | 13.371 | Smoke | 20

Cần kiểm: Kiểm từng ô của Table10 dòng3 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.



## A-097 — 3.2.4. Mối liên  hệ giữa thời tiết và lưu lượng

Vị trí: P0283, P0284, P0285, P0286; Docs index 13391:13414. Loại: data & preprocessing.

> Rain | 5.563 | Squall | 4

Cần kiểm: Kiểm từng ô của Table10 dòng4 từ CSV/notebook saved output hoặc modelregistry tương ứng; giữ nguyên scope và đơn vị.


