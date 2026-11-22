# Đề xuất sửa và bổ sung báo cáo

Các đoạn dưới đây là bản để duyệt, chưa được ghi vào Google Docs. Vị trí Pxxxx tham chiếu bản chụp báo cáo ngày 22/11/2026 trong `agent_a/report_snapshot.txt`; không phải số trang. Các con số được làm tròn từ CSV/JSON đã lưu, không chạy lại mô hình. Khi dán, bỏ các dòng hướng dẫn và bằng chứng của người rà soát.

## 4. Danh sách đề xuất sửa đổi chi tiết

**[SỬA-001] | Mức độ: Trung bình | Loại: THIẾU**

- **Vị trí:** 1.1, P0026.
- **Nội dung hiện tại:** “Mỗi năm, một tài xế ở Mỹ mất trung 49 giờ vì tắc đường”.
- **Vấn đề:** Thiếu nguồn, năm khảo sát và phạm vi của con số; dữ liệu I-94 không tự chứng minh thống kê này.
- **Bằng chứng:** A-001; [UCI, phần Dataset Information](https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume) chỉ mô tả bộ dữ liệu, không cung cấp số giờ ùn tắc này.
- **Nội dung thay thế đề xuất:**

> Lưu lượng giao thông thay đổi theo giờ trong ngày và loại ngày. Đề tài sử dụng dữ liệu tại trạm ATR 301 trên đường I-94 hướng Tây để khảo sát các mẫu hình này và xây dựng mô hình dự đoán lưu lượng theo giờ. Kết quả được giới hạn trong phạm vi trạm và giai đoạn quan sát của bộ dữ liệu.

- **Cần cập nhật kèm theo:** Tài liệu tham khảo; phần mở đầu slide nếu đang dùng con số 49 giờ.
- **Độ tin cậy:** Cao về việc thiếu nguồn; chưa xác minh con số 49 giờ đúng hay sai.

**[SỬA-002] | Mức độ: Cao | Loại: THIẾU**

- **Vị trí:** 1.2, P0028–P0034; chèn 1.3 trước P0035.
- **Nội dung hiện tại:** “Đánh giá ảnh hưởng của thời tiết đến lưu lượng”; “Xây dựng và so sánh các mô hình dự báo lưu lượng”.
- **Vấn đề:** Mục có tên câu hỏi nghiên cứu nhưng mới liệt kê mục tiêu; chưa định nghĩa thời điểm dự đoán và điều kiện có history. Số mục nhảy từ 1.2 sang 1.4.
- **Bằng chứng:** A-002–A-007 ↔ B-012–B-017; `src/features.py:270`; `notebooks/features/README.md:17`.
- **Nội dung thay thế đề xuất:**

> Nhóm xây dựng mô hình hồi quy dự đoán `traffic_volume`, đơn vị xe/giờ, tại trạm ATR 301 trên I-94 hướng Tây. Ba câu hỏi nghiên cứu gồm: (RQ1) Lưu lượng thay đổi theo giờ, thứ, ngày lễ và điều kiện thời tiết như thế nào? (RQ2) Khi giữ cùng mô hình và các giờ chấm, bổ sung thời tiết và lịch sử lưu lượng làm thay đổi MAE bao nhiêu? (RQ3) Phương án mô hình nào phù hợp nhất trong phạm vi đã thử, và sai số tập trung ở những điều kiện nào?
>
> **1.3. Phạm vi và kịch bản dự đoán**
>
> Với cấu hình C30, đánh giá được thực hiện tuần tự theo giờ. Tại giờ cần dự đoán, mô hình sử dụng lưu lượng đã quan sát ở những giờ trước và giả định thông tin thời tiết cùng giờ đã sẵn có. Đây là điều kiện của thực nghiệm; khả năng nhận dữ liệu thời tiết đúng thời điểm khi triển khai chưa được kiểm chứng. Kết quả C30 áp dụng cho các giờ đủ history theo quy tắc của dự án. Các phân tích mối liên hệ trong EDA không được diễn giải thành tác động nhân quả.

- **Cần cập nhật kèm theo:** 3.4, 3.6, 4.9, 5.2; mục lục và slide phạm vi.
- **Độ tin cậy:** Cao.

**[SỬA-003] | Mức độ: Trung bình | Loại: LỆCH**

- **Vị trí:** 2.2, P0062 và P0066; bổ sung ExtraTrees sau phần RF.
- **Nội dung hiện tại:** “Sai số out-of-bag (OOB) cho ước lượng đánh giá mà không cần tập validation riêng”; “khái quát tốt hơn”.
- **Vấn đề:** Đây là mô tả lý thuyết, chưa phải tuyên bố dự án dùng OOB. Tuy nhiên cách viết dễ làm lẫn với giao thức theo thời gian; learning rate nhỏ cũng không bảo đảm khái quát tốt hơn trong mọi trường hợp. Thiếu ExtraTrees là thành phần mô hình đã chốt.
- **Bằng chứng:** A-013, A-015 ↔ B-017, B-021, B-033; `notebooks/validation/outputs/final_C30/selected_model.json:129`; [tài liệu ensemble của scikit-learn](https://scikit-learn.org/stable/modules/ensemble.html).
- **Nội dung thay thế đề xuất:**

> Random Forest hồi quy lấy trung bình dự đoán của nhiều cây. OOB là một cách đánh giá có thể dùng với bootstrap, nhưng trong dự án này mô hình được lựa chọn bằng CV theo thời gian và validation. Với Gradient Boosting, learning rate điều chỉnh mức đóng góp của từng cây; giá trị phù hợp được chọn bằng thực nghiệm.
>
> ExtraTrees cũng kết hợp nhiều cây, đồng thời tăng tính ngẫu nhiên khi chọn ngưỡng chia. Cấu hình ExtraTrees được chọn trong dự án dùng toàn bộ mẫu huấn luyện cho mỗi cây (`bootstrap=False`). Nhóm thử bổ sung mô hình này vào ensemble RF/XGBoost để kiểm tra khả năng giảm sai số trên cùng các giờ chấm.

- **Cần cập nhật kèm theo:** Bảng thuật toán 2.2; bảng tham số 4.1; 3.6 và 5.1.
- **Độ tin cậy:** Cao; không kết luận đoạn cũ đã báo cáo chạy OOB.

**[SỬA-004] | Mức độ: Cao | Loại: THIẾU**

- **Vị trí:** 3.3.1–3.3.3, P0291–P0296.
- **Nội dung hiện tại:** “[Nhóm bổ sung]”; “chỉ fit trên tập train”.
- **Vấn đề:** Chưa phân biệt làm sạch cố định với điền thiếu có học thống kê; thiếu chính sách gộp nhiều bản ghi cùng giờ.
- **Bằng chứng:** B-004–B-011, B-022; `src/preprocessing.py:8`, `src/preprocessing.py:42`, `src/preprocessing.py:65`, `src/preprocessing.py:151`; `src/feature_experiments.py:141`; `src/model.py:128`.
- **Nội dung thay thế đề xuất:**

> **3.3.1. Giá trị thiếu, timestamp trùng và định dạng**
>
> CSV được đọc với `keep_default_na=False` để giữ chuỗi `None` của `holiday`. Nhóm kiểm tra tính nhất quán của mục tiêu rồi giữ một giá trị `traffic_volume` cho mỗi timestamp, không cộng lưu lượng của các dòng cùng giờ. Số đo thời tiết được gộp bằng median của các giá trị phân biệt; nhãn được bỏ khoảng trắng, chuyển về chữ thường và hợp các nhãn duy nhất. Nhãn ngày lễ được áp dụng cho các giờ cùng ngày có sự kiện trong CSV, chưa bổ sung lịch lễ ngoài.
>
> **3.3.2. Ngoại lệ và nhiễu**
>
> Nhóm đánh dấu 10 giá trị nhiệt độ 0 K và điểm `rain_1h=9831.3` tại 11/07/2016 17:00 là thiếu. Các giờ có lưu lượng bằng 0 được giữ vì chưa xác minh nguyên nhân. Không bổ sung mục tiêu cho các giờ vắng bản ghi. Kết quả làm sạch là `hourly_unfilled.csv`, gồm 40.575 giờ và 10 cột; còn 10 giá trị nhiệt độ và một giá trị mưa thiếu.
>
> **3.3.3. Encoding, điền thiếu và scaling**
>
> Điền thiếu được thực hiện trong từng fold. Nhiệt độ thiếu ưu tiên quan sát gốc trước đó trong tối đa sáu giờ, sau đó dùng median theo tháng–giờ, cuối cùng là median toàn phần huấn luyện tương ứng. Mưa thiếu dùng median của phần huấn luyện. Không điền median cho lag và không nội suy mục tiêu. Các cờ thời tiết được tạo theo từng nhãn, cho phép nhiều nhãn cùng xuất hiện trong một giờ. Ridge dùng one-hot cho `weekday_hour` và `month`, đồng thời chuẩn hóa các cột số còn lại; MLP chuẩn hóa đầu vào và mục tiêu. Encoder và scaler chỉ được fit trên fold-train.

- **Cần cập nhật kèm theo:** 3.4–3.6, sơ đồ pipeline, phụ lục hướng dẫn chạy.
- **Độ tin cậy:** Cao.

**[SỬA-005] | Mức độ: Cao | Loại: THIẾU**

- **Vị trí:** 3.4, P0298–P0299.
- **Nội dung hiện tại:** “History (lag, rolling) nếu dùng”.
- **Vấn đề:** History đã được dùng và là điều kiện quan trọng của mô hình cuối; cần công thức và số cột chính xác.
- **Bằng chứng:** B-012–B-014, B-019; `src/features.py:212`, `src/features.py:223`, `src/features.py:279`, `src/features.py:283`.
- **Nội dung thay thế đề xuất:**

> Nhóm sử dụng ba cấu hình tích lũy. A12 gồm `hour`, `day_of_week`, `month`, `is_weekend`, `is_rush_hour`, `is_holiday` và sáu cột sin/cos của giờ, thứ, tháng. B27 bổ sung `temp_c`, `rain_1h`, `snow_1h`, `clouds_all` và 11 cờ `weather_main`. C30 bổ sung `lag_24h`, `lag_168h`, `mean_24h`.
>
> Hai lag được tra bằng timestamp đúng tại t−24 giờ và t−168 giờ. `mean_24h` là trung bình trên khoảng [t−24 giờ, t), yêu cầu ít nhất 18 giờ quan sát; giờ đang dự đoán không tham gia. Các giờ thiếu một trong ba giá trị history bị loại khỏi cohort đối chứng chung. Vì dữ liệu có giờ thiếu, dịch theo số hàng không tương đương với tra theo giờ thực.
>
> Ngoài A12, B27 và C30, phần FE có hai phương án trung gian: A12 cộng bốn biến thời tiết dạng số (16 cột), và A12 cộng 11 cờ thời tiết (23 cột). Cả năm phương án dùng cùng RF cố định để đánh giá đóng góp của nhóm đặc trưng. Thí nghiệm này chưa tách riêng đóng góp của từng cột.

- **Cần cập nhật kèm theo:** 3.6.5, 4.8; bảng đặc trưng và tên cấu hình trên slide.
- **Độ tin cậy:** Cao.

**[SỬA-006] | Mức độ: Cao | Loại: THIẾU**

- **Vị trí:** 3.5 và 3.6.1–3.6.2, P0301–P0309.
- **Nội dung hiện tại:** “dữ liệu → tiền xử lý → đặc trưng → chia tập → huấn luyện/tuning → đánh giá → demo”; “[Nhóm bổ sung]”.
- **Vấn đề:** Sơ đồ gợi ý chưa biểu diễn ranh giới học thống kê, cohort chung và bước test còn chờ.
- **Bằng chứng:** B-007–B-018, B-036; `src/feature_experiments.py:85`; `notebooks/features/outputs/e4bc1e064317af8c/fold_manifest.csv:2`; `notebooks/validation/outputs/final_C30/selected_model.json:194`.
- **Nội dung thay thế đề xuất:**

> Pipeline gồm: CSV gốc → kiểm tra và gộp theo giờ → `hourly_unfilled.csv` → chia theo thời gian → tạo đặc trưng theo thông tin sẵn có → FE và tuning trong train → đối chiếu validation → khóa cấu hình. Bước tiếp theo là refit trên train + validation rồi đánh giá test một lần cho mô hình đã khóa; bước này chưa hoàn thành tại thời điểm báo cáo.
>
> Dữ liệu được chia theo thứ tự các giờ quan sát, với 28.402 giờ train (đến 10/05/2017 04:00), 6.086 giờ validation (10/05/2017 05:00 đến 19/01/2018 14:00) và 6.087 giờ test (19/01/2018 15:00 đến 30/09/2018 23:00). Tỷ lệ 70/15/15 tính theo số mẫu, không phải độ dài lịch.
>
> Để so sánh công bằng với C30, FE và tuning dùng chung 22.503 giờ train đủ history cho cả A12 và B27. Ba fold có lần lượt 5.628, 11.253 và 16.878 mẫu fit; mỗi fold chấm 5.625 mẫu, tổng cộng 16.875 dự đoán OOF. Các đoạn chấm phủ 16.931, 10.163 và 5.867 giờ lịch nên không được xem là ba cửa sổ lịch bằng nhau. Validation C30 giữ 6.050 giờ đủ history. Điền thiếu, encoding và scaling có học thống kê chỉ dùng phần huấn luyện tương ứng.

- **Cần cập nhật kèm theo:** Sơ đồ 3.5, bảng fold, mọi bảng n ở Chương 4, hạn chế 5.2.
- **Độ tin cậy:** Cao.

**[SỬA-007] | Mức độ: Cao | Loại: THIẾU**

- **Vị trí:** 3.6.3–3.6.5, P0311–P0317.
- **Nội dung hiện tại:** “không gian tham số, chỉ số chọn mô hình trên validation”; “[Nhóm bổ sung]”.
- **Vấn đề:** Gợi ý chưa nêu cách tuning thực tế. Tham số được chọn bằng mean fold MAE trong train; cần tách FE, tuning và lựa chọn trên validation.
- **Bằng chứng:** A-008, A-050–A-051 ↔ B-019–B-026; `src/tuning_cv.py:22`, `src/tuning_cv.py:56`, `src/tuning_cv.py:83`; `src/model.py:19`.
- **Nội dung thay thế đề xuất:**

> Hai baseline gồm trung bình lưu lượng theo thứ–giờ của phần train tương ứng, với trung bình toàn train làm giá trị dự phòng, và seasonal naive dùng `lag_168h`. Chúng được chấm trên cùng các timestamp với mô hình.
>
> FE cố định Random Forest với 400 cây, `max_depth=12`, `min_samples_leaf=5`, `max_features=1.0`, `random_state=42`. Chỉ nhóm đặc trưng thay đổi giữa năm phương án.
>
> Tuning đánh giá Ridge, Random Forest, Gradient Boosting, MLP và XGBoost trên A12, B27, C30. Mỗi cặp mô hình–cấu hình có sáu ứng viên được lấy bằng `ParameterSampler`, seed 42, dùng cùng ba fold và cohort của FE. Tổng ngân sách là 270 lượt fit. Tham số được chọn theo MAE trung bình fold, sau đó RMSE trung bình fold và thứ tự ứng viên nếu cần phá hòa. Không gian tìm kiếm và danh sách ứng viên được lưu cùng giao thức; bảng tham số chi tiết đặt ở phụ lục. Validation và test không tham gia bước tuning CV này.

- **Cần cập nhật kèm theo:** 4.3, 4.8; phụ lục search space và ứng viên. Dùng kết quả tuning sau sửa sampler, không chép bảng RF cũ bằng điểm FE.
- **Độ tin cậy:** Cao.

**[SỬA-008] | Mức độ: Cao | Loại: LỆCH**

- **Vị trí:** Sau 3.6.5, P0318–P0320; nên tách thành 3.6.6 “OOF và ensemble”.
- **Nội dung hiện tại:** “Trong thí nghiệm ensemble, Random Forest và XGBoost sử dụng cùng cấu hình đặc trưng”; “hai mô hình được huấn luyện lại trên toàn bộ tập train”.
- **Vấn đề:** Mô tả phù hợp nhánh hai mô hình nhưng chưa bao quát phương án ExtraTrees cuối; “toàn bộ train” cần nói rõ cohort 22.503 giờ.
- **Bằng chứng:** A-052–A-054 ↔ B-027–B-036; `experiments/21-11-2026_Huy_C30_OOF/outputs/selected_weights.json:52`; `experiments/22-11-2026_Huy_C30_MAE_Diversity/outputs/selected_option.json:2`; `notebooks/validation/outputs/final_C30/selected_model.json:40`.
- **Nội dung thay thế đề xuất:**

> Dự đoán OOF được tạo bằng ba fold theo thời gian trong train. Mỗi dự đoán do mô hình chỉ học từ phần quá khứ của fold tạo ra; các bước tiền xử lý có học thống kê cũng chỉ fit trên phần đó. Các dự đoán được ghép theo timestamp để chọn phương án kết hợp. Điểm OOF được dùng để lựa chọn nên chưa phải ước lượng đánh giá độc lập sau lựa chọn.
>
> Ngày 20/11, nhóm đối chiếu hai bộ tham số RF/XGBoost trên cùng C30 và giữ ensemble 50/50 làm đối chứng. Ngày 21/11, lựa chọn bằng OOF cho tỷ trọng RF/XGBoost 60/40 nhưng không cải thiện MAE validation so với 50/50. Ngày 22/11, nhóm thử năm cấu hình mô hình bổ sung với ba tỷ trọng kết hợp cho mỗi cấu hình, tổng cộng 16 phương án OOF khi tính cả đối chứng. OOF chọn ExtraTrees chiếm 50% và ensemble RF/XGBoost cũ chiếm 50%, tương đương RF 25%, XGBoost 25%, ExtraTrees 50%.
>
> Các thành phần được fit trên cohort 22.503 giờ train để chấm 6.050 giờ validation đủ history. Nhóm chốt phương án ba mô hình sau khi đối chiếu kết quả. Validation đã được xem trong nhiều vòng phát triển, do đó kết quả được xem là thăm dò. Đặc tả đã khóa chưa phải mô hình được refit trên train + validation, và chưa có điểm test của phương án cuối.

- **Cần cập nhật kèm theo:** 2.2, 4.3–4.6, 5.1–5.2, sơ đồ pipeline và slide kết luận.
- **Độ tin cậy:** Cao; không gọi đoạn cũ sai cho chính thí nghiệm hai thành phần.

**[SỬA-009] | Mức độ: Trung bình | Loại: THIẾU**

- **Vị trí:** 4.1, P0324–P0325.
- **Nội dung hiện tại:** “Phiên bản Python/thư viện, seed, phần cứng, liên kết mã và log”.
- **Vấn đề:** Chưa có môi trường của lượt chạy; `requirements.txt` khác manifest về NumPy nên không dùng nó thay cho lịch sử runtime.
- **Bằng chứng:** B-031–B-033, B-037–B-038; `notebooks/validation/outputs/final_C30/selected_model.json:176`; `requirements.txt:4`.
- **Nội dung thay thế đề xuất:**

> Manifest của mô hình chốt ghi NumPy 2.5.3, pandas 3.0.6, scikit-learn 1.9.1 và XGBoost 3.4.1. Các mô hình thành phần dùng `random_state=42`, `n_jobs=4`. File `requirements.txt` hiện ghi NumPy 2.5.4; vì vậy phiên bản tái lập cần được đối chiếu theo manifest của từng lượt. Thông tin CPU, RAM và thời gian huấn luyện chưa được tổng hợp đủ để báo cáo.

- **Cần cập nhật kèm theo:** Phụ lục A và bảng cấu hình; chỉ thêm phiên bản Python khi có nguồn runtime tương ứng, không suy từ tên kernel notebook.
- **Độ tin cậy:** Cao cho phiên bản thư viện được ghi, chưa xác minh phần cứng và thời gian chạy.

**[SỬA-010] | Mức độ: Cao | Loại: THIẾU**

- **Vị trí:** 4.2–4.3, P0327–P0330.
- **Nội dung hiện tại:** “[Nhóm bổ sung]”; “Tham số tối ưu, kết quả trên validation”.
- **Vấn đề:** Chưa có kết quả đã chạy; dễ gộp điểm CV và validation thành cùng bảng xếp hạng.
- **Bằng chứng:** B-021–B-025, B-027, B-034; `notebooks/tuning/outputs/comparison_summary.csv:12`; `notebooks/validation/outputs/final_C30/validation_comparison.csv:8`.
- **Nội dung thay thế đề xuất:**

> Trên 16.875 dự đoán OOF thuộc train, C30 có MAE trung bình fold lần lượt là 231,0395 với Random Forest; 235,9835 với XGBoost; 255,9309 với Gradient Boosting; 261,9641 với Ridge; và 277,1134 với MLP. Đây là kết quả tuning hiện lưu sau khi sửa cách lấy mẫu ứng viên RF. Mức 247,9260 thuộc RF cố định ở bước FE, không phải điểm RF tốt nhất của lượt tuning hiện tại.
>
> Các tham số dùng trong mạch validation từ 20/11 được ghi riêng theo `run_config.json` của từng thí nghiệm. Bộ tham số tái dựng từ Claude là một nhánh đối chiếu, không được mô tả là đầu ra trực tiếp của lượt tuning chung. Trên cùng 6.050 giờ validation C30, baseline trung bình thứ–giờ đạt MAE 291,7388, RMSE 503,2185, R² 0,934378; seasonal naive đạt MAE 330,1775, RMSE 635,0735, R² 0,895484. Bảng chọn phương án validation được trình bày riêng ở mục tiếp theo.

- **Cần cập nhật kèm theo:** Bảng CV phải có SD và n từng fold; bảng validation có n=6.050 và mốc lịch; phụ lục lưu đường dẫn run.
- **Độ tin cậy:** Cao về kết quả lưu; nguồn tham số Claude ban đầu chưa xác minh độc lập.

**[SỬA-011] | Mức độ: Cao | Loại: THIẾU**

- **Vị trí:** 4.4, P0331–P0352, gồm bảng trống.
- **Nội dung hiện tại:** “4.4. So sánh các mô hình trên tập test”; “Chỉ đánh giá test một lần cho mô hình đã chốt”.
- **Vấn đề:** Đây là khung kế hoạch, chưa phải điểm test đã công bố. Kết quả hiện có là validation; không điền các số 190–198 vào bảng mang tên test.
- **Bằng chứng:** A-055 ↔ B-030, B-034–B-036; `notebooks/validation/outputs/final_C30/validation_comparison.csv:2`; `notebooks/validation/outputs/final_C30/selected_model.json:195`.
- **Nội dung thay thế đề xuất:**

> **4.4. Đối chiếu validation và trạng thái đánh giá test**
>
> Các phương án dưới đây sử dụng cùng C30, cohort train và 6.050 giờ validation đủ history. Ensemble RF 25% + XGBoost 25% + ExtraTrees 50% có MAE thấp nhất trong bảng: 190,1900 xe/giờ; RMSE 313,5266 xe/giờ; R² 0,974527. So với RF/XGBoost 50/50, MAE giảm 3,6203 và RMSE giảm 2,5582 xe/giờ. R² không phải tỷ lệ số giờ được dự đoán đúng.
>
> Đến thời điểm khóa báo cáo, cấu hình đã được chốt nhưng chưa refit trên train + validation và chưa đánh giá test cho mô hình cuối. Vì vậy bảng này chỉ phản ánh validation; kết quả test sẽ được bổ sung sau bước đánh giá cuối theo cấu hình đã khóa.

Chèn bảng validation cùng cohort ở mục 2 của bản rà soát; nguồn duy nhất là `validation_comparison.csv`. Để trống kết quả test cho đến khi có log thật.

- **Cần cập nhật kèm theo:** Tên bảng, 5.1, tóm tắt, slide kết quả; nếu giữ mục test riêng thì thêm 4.4.2 “Chưa thực hiện”.
- **Độ tin cậy:** Cao; không kết luận toàn bộ lịch sử dự án chưa từng xem test.

**[SỬA-012] | Mức độ: Cao | Loại: THIẾU**

- **Vị trí:** 4.5 và 5.2, P0354–P0355, P0372–P0373.
- **Nội dung hiện tại:** “So sánh train–validation–test”; “[Nhóm bổ sung]”.
- **Vấn đề:** Chưa có đánh giá test cuối hoặc learning curve tương ứng để chẩn đoán overfitting; thiếu hạn chế do lặp lại validation và chọn trên OOF.
- **Bằng chứng:** B-015, B-017–B-018, B-029, B-035–B-036; `notebooks/validation/outputs/final_C30/paired_bootstrap.csv:2`; `notebooks/validation/outputs/final_C30/selected_model.json:193`.
- **Nội dung thay thế đề xuất:**

> Kết quả hiện tại được giới hạn bởi ba fold theo thời gian, một seed và ngân sách tìm kiếm nhỏ. Các fold có cùng số mẫu chấm nhưng độ dài lịch khác nhau. Cohort đủ history loại những giờ mà A12 hoặc B27 vẫn có thể dự đoán, nên kết luận đối chứng áp dụng cho cohort này.
>
> OOF được dùng để chọn tham số hoặc phương án kết hợp, còn validation đã được xem nhiều lần trong quá trình phát triển. So với ensemble 50/50, bootstrap theo ngày cho chênh lệch MAE của phương án chốt có khoảng 95% từ 1,6303 đến 5,7975 xe/giờ. So với ExtraTrees đơn, khoảng tương ứng chứa 0, từ −0,9887 đến 2,9426 xe/giờ. Các khoảng này có tính thăm dò và không thay thế đánh giá độc lập trên test. Chưa đủ bằng chứng để kết luận mức cải thiện so với ExtraTrees đơn ổn định trên dữ liệu tương lai.
>
> Thời tiết cùng giờ được giả định sẵn có; nhãn ngày lễ chỉ lấy từ CSV; chưa phân tích DST. EDA tổng quan đã sử dụng toàn bộ dữ liệu để mô tả, vì vậy cần phân biệt việc chưa chấm test của mô hình cuối với việc chưa từng xem bất kỳ thông tin nào từ giai đoạn test. Chưa có đủ kết quả để kết luận overfitting chỉ từ chênh lệch giữa điểm CV và validation.

- **Cần cập nhật kèm theo:** 3.6.2, 4.4, 5.1 và mọi kết luận “tốt nhất”.
- **Độ tin cậy:** Cao cho giới hạn thiết kế; không tuyên bố kiểm định độc lập.

**[SỬA-013] | Mức độ: Cao | Loại: THIẾU**

- **Vị trí:** 4.8, P0362–P0363.
- **Nội dung hiện tại:** “[Nhóm bổ sung]”.
- **Vấn đề:** Thiếu kết quả trả lời đóng góp nhóm đặc trưng; mô hình C30 thắng không tự chứng minh thời tiết hữu ích hoặc vô ích.
- **Bằng chứng:** B-019–B-020, B-025; `notebooks/features/outputs/e4bc1e064317af8c/feature_comparison.csv:2`; `notebooks/tuning/outputs/paired_block_bootstrap.csv:3`.
- **Nội dung thay thế đề xuất:**

> Với cùng RF cố định, ba fold và 16.875 giờ chấm, MAE trung bình fold của A12 là 288,3182; thêm thời tiết dạng số là 291,5528; thêm cờ thời tiết là 290,0372; B27 là 290,7253; C30 là 247,9260 xe/giờ. C30 tốt nhất trong năm nhóm đã thử, trong khi B27 chưa cải thiện A12 ở cấu hình RF cố định này.
>
> Sau tuning, RF A12 và B27 có MAE lần lượt 288,1823 và 286,8227. Chênh lệch 1,3595 xe/giờ có khoảng bootstrap theo khối bảy ngày từ −3,8586 đến 7,1612 nên chưa tách được chiều cải thiện trong phân tích có điều kiện này. C30 đạt 231,0395 với RF. Kết quả ủng hộ giá trị của nhóm history trong phạm vi thực nghiệm, nhưng chưa tách đóng góp của từng lag và chưa cho phép kết luận chung rằng thời tiết không có ích.

- **Cần cập nhật kèm theo:** 1.2, 4.9, 5.1; không gộp năm validation lịch sử vào bảng FE đồng nhất này.
- **Độ tin cậy:** Cao; các khoảng từ OOF đã dùng chọn tham số, không phải kiểm định độc lập.

**[SỬA-014] | Mức độ: Cao | Loại: THIẾU**

- **Vị trí:** 5.1, P0370; thêm bảng tham số tại 4.1 hoặc phụ lục A.
- **Nội dung hiện tại:** “[Nhóm bổ sung]”.
- **Vấn đề:** Chưa ghi mô hình đã chốt, trạng thái artifact và kết quả có thể tái lập.
- **Bằng chứng:** B-030–B-037; `notebooks/validation/outputs/final_C30/selected_components.csv:2`; `notebooks/validation/outputs/final_C30/selected_model.json:194`.
- **Nội dung thay thế đề xuất:**

> Nhóm chốt cấu hình C30 với dự đoán bằng 0,25 lần Random Forest, cộng 0,25 lần XGBoost và 0,50 lần ExtraTrees. Trên 6.050 giờ validation đủ history, phương án đạt MAE 190,1900 xe/giờ, RMSE 313,5266 xe/giờ và R² 0,974527. Đây là phương án có MAE thấp nhất trong bảng validation cùng cohort hiện lưu. Kết luận còn giới hạn bởi việc validation đã được sử dụng trong nhiều vòng phát triển. File `selected_model.json` ghi cấu hình đã khóa; bước refit trên train + validation và đánh giá test cuối chưa hoàn thành.

| Thành phần  | Tỷ trọng | Tham số chính đã khóa                                                                                                                                                                   |
| ------------- | ---------: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Random Forest |       0,25 | `n_estimators=100`, `max_depth=None`, `min_samples_leaf=2`, `max_features=0.33`, `bootstrap=True`                                                                                  |
| XGBoost       |       0,25 | `n_estimators=400`, `max_depth=6`, `learning_rate=0.03`, `subsample=0.7`, `colsample_bytree=0.8`, `min_child_weight=1`, `objective='reg:squarederror'`, `tree_method='hist'` |
| ExtraTrees    |       0,50 | `n_estimators=200`, `max_depth=None`, `min_samples_leaf=2`, `max_features=0.8`, `bootstrap=False`                                                                                  |

> Các thành phần dùng seed 42, `n_jobs=4`. Dự đoán thành phần và dự đoán cuối được cắt phần âm về 0. Việc đã thử loss MAE trong nhánh bổ sung không có nghĩa các thành phần cuối đều được fit bằng loss MAE.

- **Cần cập nhật kèm theo:** 2.2, 3.6.6, 4.4, slide và phụ lục hướng dẫn; không gọi JSON đặc tả là checkpoint đã fit.
- **Độ tin cậy:** Cao.

**[SỬA-015] | Mức độ: Trung bình | Loại: THIẾU**

- **Vị trí:** 5.3 và phụ lục A, P0375, P0381–P0382.
- **Nội dung hiện tại:** “[Nhóm bổ sung]”; “hướng dẫn cài đặt và tái lập kết quả”.
- **Vấn đề:** Demo chưa có code chạy và một số liên kết README không tồn tại ở snapshot repo hiện tại; chưa được báo cáo là đã triển khai.
- **Bằng chứng:** B-036, B-039–B-040; `app/demo_time_weather.py:1`; `docs/report_review/2026-11-22/agent_b/read_only_checks.json:106`; proposal P0088 trong `context/ML_Project_Proposal.txt`.
- **Nội dung thay thế đề xuất:**

> Công việc tiếp theo là hoàn tất refit và đánh giá test theo cấu hình đã khóa, lưu mô hình cùng quy tắc tiền xử lý và thứ tự đặc trưng, rồi xây dựng demo. File demo hiện mới chứa phần chú thích nên chưa có sản phẩm inference hoạt động. Phạm vi demo cần được chốt: Time + Weather theo đề cương, hoặc C30 với đầu vào history bổ sung. Danh mục notebook và hướng dẫn chạy sẽ được kiểm tra lại theo các file thực sự có trong bản bàn giao.

- **Cần cập nhật kèm theo:** Phụ lục mã nguồn, README, slide tiến độ; sửa đường dẫn là công việc riêng, chưa thực hiện trong đợt rà soát này.
- **Độ tin cậy:** Cao về hiện trạng file; lựa chọn phạm vi demo cần nhóm quyết định.

**[SỬA-016] | Mức độ: Thấp | Loại: LỆCH**

- **Vị trí:** 3.2.1 và các bảng EDA, P0122/P0125/P0131/P0136/P0139/P0160/P0211/P0272/P0274.
- **Nội dung hiện tại:** “timestamp lăpk”; “timestamo”; “weather _description”; “Giờ”; “dương..”.
- **Vấn đề:** Lỗi gõ và tên cột không nhất quán; “Giờ” ở cột đếm mẫu dễ bị hiểu là giờ trong ngày.
- **Bằng chứng:** A-I014, A-I028 trong `agent_a/issues.json`; A-072, A-074, A-085, A-095; các đoạn gốc tương ứng trong `agent_a/report_snapshot.txt`.
- **Nội dung thay thế đề xuất:** Dùng lần lượt các ô/caption hoàn chỉnh sau tại đúng vị trí: “Bảng 3.2. Kết quả kiểm tra giá trị thiếu và timestamp lặp”; “Giá trị null, chuỗi rỗng hoặc chỉ có khoảng trắng”; “Tổng số dòng thuộc các timestamp lặp”; “Bảng 3.3. Hai bản ghi cùng timestamp nhưng khác nhãn thời tiết”; “weather_description”; “Giá trị nghi vấn; không dùng IQR để loại mọi lượng mưa dương.” Đổi tiêu đề cột đếm mẫu thành “n (giờ quan sát)”.
- **Cần cập nhật kèm theo:** Danh mục bảng; tên cột trong slide, giữ nguyên mọi số liệu.
- **Độ tin cậy:** Cao.

**[SỬA-017] | Mức độ: Trung bình | Loại: THIẾU**

- **Vị trí:** Caption Hình 3.1–3.4, P0199/P0206/P0239/P0269; 1.5, P0036.
- **Nội dung hiện tại:** “Hình 3.4. Lưu lượng trung bình theo nhãn thời tiết”; “1.5. Bố cục báo cáo” chưa có nội dung.
- **Vấn đề:** Hình chưa gắn đủ phạm vi và nguồn tái lập; thiếu đoạn giới thiệu bố cục.
- **Bằng chứng:** A-036–A-045 ↔ B-041–B-044, X-008; `notebooks/eda/EDA_general.ipynb:8650`, `notebooks/eda/EDA_general.ipynb:9589`; bản chụp P0036.
- **Nội dung thay thế đề xuất:**

> Hình 3.1. Phân bố lưu lượng trên 40.575 giờ quan sát duy nhất. Nguồn: `notebooks/eda/EDA_general.ipynb`, toàn bộ giai đoạn dữ liệu.
>
> Hình 3.2. Lưu lượng trung bình theo giờ, thứ và tháng trên 40.575 giờ quan sát duy nhất; số mẫu các nhóm nổi bật ở Bảng 3.6. Nguồn: `notebooks/eda/EDA_general.ipynb`.
>
> Hình 3.3. Lưu lượng trung bình theo cặp thứ–giờ trên toàn bộ giai đoạn dữ liệu, chỉ tính các giờ có quan sát. Nguồn: `notebooks/eda/EDA_general.ipynb`.
>
> Hình 3.4. Lưu lượng trung bình theo từng nhãn thời tiết; một giờ có thể thuộc nhiều nhóm. Số mẫu các nhóm được ghi ở Bảng 3.8 và bảng đầy đủ trong notebook nguồn. Nguồn: `notebooks/eda/EDA_general.ipynb`, toàn bộ giai đoạn dữ liệu.
>
> Báo cáo gồm năm chương. Chương 1 giới thiệu bài toán và câu hỏi nghiên cứu. Chương 2 trình bày thuật toán, độ đo và nguyên tắc đánh giá theo thời gian. Chương 3 mô tả dữ liệu, tiền xử lý, đặc trưng và thiết kế thực nghiệm. Chương 4 trình bày các kết quả đã lưu, đối chứng và giới hạn diễn giải. Chương 5 tổng hợp mô hình được lựa chọn và công việc còn lại.

- **Cần cập nhật kèm theo:** Danh mục hình, mục lục; bản bàn giao cần giữ notebook và hình nguồn thực sự tồn tại.
- **Độ tin cậy:** Cao; chưa kiểm tra bố cục toàn trang sau khi dán.

## 5. Nội dung nên bổ sung (➕ THIẾU)

Các mục dưới đây bổ sung phần chưa có mà không tạo thêm thí nghiệm.

### 5.1. Bảng fold tại cuối mục 3.6.1

| Fold | Fit đến        | Đoạn chấm                            |  n fit | n chấm | Độ dài lịch đoạn chấm (giờ) |
| ---- | ---------------- | --------------------------------------- | -----: | ------: | ----------------------------------: |
| 1    | 05/08/2013 19:00 | 05/08/2013 20:00 đến 12/07/2015 06:00 |  5.628 |   5.625 |                              16.931 |
| 2    | 12/07/2015 06:00 | 12/07/2015 07:00 đến 07/09/2016 17:00 | 11.253 |   5.625 |                              10.163 |
| 3    | 07/09/2016 17:00 | 07/09/2016 18:00 đến 10/05/2017 04:00 | 16.878 |   5.625 |                               5.867 |

Phần fit của cả ba fold bắt đầu tại 09/10/2012 09:00. Nguồn: B-017–B-018, `notebooks/features/outputs/e4bc1e064317af8c/fold_manifest.csv:2`–`:4`. Tổng n chấm là 16.875.

### 5.2. Phạm vi của EDA trước mục 3.2.2

> EDA tổng quan mô tả toàn bộ 40.575 giờ quan sát, còn các notebook EDA_A, EDA_B, EDA_C phục vụ khảo sát trên train. Hai phạm vi có thể cho số trung bình khác nhau. Kết quả mô tả toàn bộ dữ liệu không được dùng làm điểm đánh giá độc lập cho mô hình; các tham số có học thống kê của FE và tuning vẫn được fit trong phần train tương ứng.

Nguồn: A-034, A-039 ↔ B-016, B-041–B-042; `notebooks/eda/README.md:5`, `src/feature_experiments.py:141`. Không tự gọi việc EDA toàn dữ liệu là bằng chứng một mô hình cụ thể đã rò rỉ; cần truy vết quyết định phát sinh từ EDA.

### 5.3. Phân tích sai số tại 4.6

> Mạch thí nghiệm ngày 21/11 phân tích sai số của RF/XGBoost nhằm tìm hướng bổ sung mô hình. Phân tích này thuộc ensemble hai thành phần. Mô hình cuối có thêm ExtraTrees nên cần ghi rõ phiên bản mô hình trên từng hình và bảng sai số. Khi chưa có bảng phân nhóm của mô hình cuối, nhóm chưa kết luận riêng về mức sai số của nó trên ngày lễ, thời tiết hiếm hoặc các giờ sau khoảng trống dữ liệu.

Nguồn: B-028–B-030; `experiments/21-11-2026_Huy_C30_OOF/outputs/assessment.md:1`; `experiments/22-11-2026_Huy_C30_MAE_Diversity/outputs/assessment.md:1`. Đây là đoạn mô tả giới hạn; không gán số liệu của mô hình cũ sang mô hình cuối.

### 5.4. Trả lời câu hỏi nghiên cứu tại 4.9

> RQ1: EDA ghi nhận khác biệt lưu lượng theo giờ và loại ngày; các mối liên hệ thời tiết được mô tả có kèm số mẫu. Chênh lệch này chưa chứng minh quan hệ nhân quả. Phần so sánh ngày lễ cùng thứ–giờ cần bổ sung từ notebook train với đúng số mẫu.
>
> RQ2: Trên cohort đối chứng chung, C30 có MAE thấp nhất trong FE dùng RF cố định. Bổ sung thời tiết chưa cải thiện ở lượt RF cố định; sau tuning RF, mức cải thiện B27 so với A12 còn nhỏ và khoảng bootstrap có điều kiện chứa 0. Kết quả chưa cho phép khẳng định lợi ích của thời tiết ổn định trong mọi cấu hình.
>
> RQ3: Phương án đã chốt là RF 25% + XGBoost 25% + ExtraTrees 50%, có MAE validation thấp nhất trong bảng cùng cohort hiện lưu. Kết quả phân tích sai số cần phân biệt ensemble hai thành phần với mô hình cuối; đánh giá test cuối chưa có.

Nguồn: A-042, A-044, A-047 ↔ B-020, B-025, B-028, B-034–B-036; `notebooks/tuning/outputs/paired_block_bootstrap.csv:3`. Chỉ dán phần ngày lễ khi đã kiểm bảng `matched_holidays`, không tự điền số từ EDA toàn CSV.

### 5.5. Nghiên cứu liên quan, tài liệu tham khảo và diễn giải mô hình

- **1.4 (P0035):** Chèn trước một đoạn xác định nguồn dữ liệu: “Metro Interstate Traffic Volume được Hogue công bố trên UCI năm 2019. Đây là bộ dữ liệu của đề tài; phần nghiên cứu liên quan cần trình bày riêng các công trình dùng dữ liệu giao thông và chỉ so sánh chỉ số khi giao thức đánh giá tương thích.” Nguồn: [UCI](https://archive.ics.uci.edu/dataset/492/metro+interstate+traffic+volume), A-030. Chưa chọn và kiểm chứng một paper thực nghiệm cụ thể, nên chưa viết bảng so sánh thành tích với paper.
- **Tài liệu tham khảo (P0378):** Thay ví dụ bằng “Hogue, J. (2019). Metro Interstate Traffic Volume [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5X60B.” Thêm tài liệu chính thức của scikit-learn/XGBoost cho lý thuyết và giao thức, rồi thống nhất kiểu trích dẫn.
- **4.7 (P0361):** Nếu chưa có artifact diễn giải của mô hình chốt, dùng: “Nhóm chưa tổng hợp phân tích độ quan trọng đặc trưng cho ensemble cuối. Kết quả đối chứng nhóm đặc trưng ở mục 4.8 cung cấp bằng chứng về hiệu quả dự đoán trong giao thức đã thử, chưa phải ước lượng tác động nhân quả của từng biến.” Căn cứ: B-020 và B-030; tính đầy đủ của SHAP/permutation importance cho mô hình cuối còn CHƯA XÁC MINH.
- **Thông tin đầu báo cáo và phụ lục C:** Điền giảng viên, lớp, đóng góp và nguồn AI theo xác nhận của nhóm. P0008/P0010/P0018/P0391–P0405 vẫn là chỗ trống. Không suy tên tác giả từ người chạy notebook hay người tạo file.

### 5.6. Cách sắp xếp mạch thực nghiệm

Chương 3 trình bày phương pháp theo thứ tự tiền xử lý → đặc trưng → giao thức FE/CV → OOF/ensemble. Chương 4 trình bày bằng chứng theo FE → tuning → đối chiếu tham số ngày 20/11 → thử trọng số ngày 21/11 → ExtraTrees ngày 22/11 → chốt validation. Các thí nghiệm lịch sử trước 20/11 đặt trong phụ lục với giao thức riêng, không biến thành năm bước chọn mô hình cuối.

Căn cứ: `notebooks/validation/README.md:5`, `notebooks/validation/README.md:27`; B-016–B-030. README chỉ chứng minh cách phân loại dự kiến; các notebook được liên kết nhưng vắng mặt phải được đánh dấu chưa có trong bản bàn giao (B-040).

## 6. Việc cần xác nhận hoặc thu thập thêm

1. **Con số 49 giờ:** cần nguồn gốc, năm và phạm vi; nếu không có, dùng SỬA-001.
2. **28 equation node gốc:** API không trả nội dung ký hiệu. Năm ảnh công thức đã xem không thay thế việc kiểm các equation native. Cần xuất PDF từ Docs để đối chiếu ký hiệu, chỉ số, dấu tổng và quy ước loss. Không suy công thức sai vì API trống.
3. **Phần cứng, runtime Python, thời gian fit và convergence MLP:** cần log đúng lượt; `requirements.txt` hoặc tên kernel không đủ chứng minh. Không ghi thời gian huấn luyện hay số tham số NN khi chưa có.
4. **Tham số Claude gốc:** repo có cấu hình tái dựng và kết quả, chưa đủ chứng minh nguồn `summary_row.json` ban đầu. Giữ cách gọi “bộ tham số tái dựng” khi chưa nhận được nguồn.
5. **Ngày lễ cùng thứ–giờ và phân tích sai số cuối:** kiểm output đúng notebook/cohort; không chép số từ model cũ. Feature importance/SHAP của mô hình cuối chưa xác minh đủ.
6. **Artifact và demo:** xác nhận phạm vi demo B27 hay C30; sửa các liên kết bàn giao thiếu trong một công việc riêng. Đợt rà soát này không tạo lại notebook và không fit/test.

Các lệnh dưới đây chỉ đọc thông tin để chuẩn bị bằng chứng, không huấn luyện lại:

```powershell
# Chạy trong thư mục repo; rg giới hạn dòng dài để tránh in base64 notebook.
Get-Content notebooks/validation/outputs/final_C30/selected_model.json
Get-Content notebooks/tuning/outputs/comparison_summary.csv
rg -n --max-columns 220 --max-columns-preview 'matched_holidays|holiday|bootstrap|n_iter_|ConvergenceWarning' notebooks/eda/eda_A.ipynb src/eda/helpers.py notebooks/tuning
rg -n --max-columns 220 --max-columns-preview 'python|versions|runtime|elapsed|duration' experiments/22-11-2026_Huy_C30_MAE_Diversity/outputs
Get-FileHash data/preprocessed/hourly_unfilled.csv -Algorithm SHA256
Test-Path src/validation_main.py
Test-Path notebooks/validation/validation_final_C30.ipynb
```

Để xác định môi trường **đang mở** có thể chạy `python --version` và `python -m pip freeze`; kết quả này chỉ mô tả môi trường hiện tại, không thay cho log của lượt cũ. Chưa cung cấp lệnh test cuối vì cần entry point refit/eval được kiểm tra và thống nhất trước; không chạy đại một notebook lịch sử lên test.
