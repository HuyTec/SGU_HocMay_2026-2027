# Metro C30 · UCI-first interactive presentation

Ứng dụng bảo vệ đồ án: dữ liệu gốc → xử lý → C30 → dự đoán → sai số → giới hạn.
UCI là nguồn chính; MnDOT/OpenWeather là nghiên cứu mở rộng ở tab 6.

## Chạy từ gốc dự án

```powershell
& app/.venv/Scripts/python.exe -m pip install -r app/requirements.txt
& app/.venv/Scripts/python.exe -m streamlit run app/app.py --server.address 127.0.0.1 --server.port 8502 --browser.gatherUsageStats false
```

Mở http://127.0.0.1:8502/. Để kiểm tra:

```powershell
& app/.venv/Scripts/python.exe -X utf8 -m unittest discover -s app/tests -v
```

## Sáu tab

1. **Tổng quan**: bài toán, nguồn UCI, model/trọng số thật, metric test từ file có hash,
   split và pipeline trực quan. Metric được tính lại từ file predictions để đối chiếu;
   không chạy lại test hoặc chọn lại mô hình.
2. **Dữ liệu & tiền xử lý**: sáu bước có Quay lại/Tiếp theo/Đặt lại/progress.
   Ví dụ gộp timestamp và ngoại lệ gọi code preprocessing thật rồi đối chiếu bảng chuẩn.
   Chỉ xem 8 dòng đầu mặc định; có mục xem/tải toàn bộ 48.204 dòng.
3. **Lịch sử & C30**: giờ test hợp lệ mặc định; timeline169 ô, highlight lag24/lag168
   hoặc mean[t−24,t), cần18 quan sát; vector30 cột float32 từ prepare_features gốc.
4. **Kết quả dự đoán**: Stored mặc định, đọc đúng dòng từ test_predictions.csv.
   Live chỉ hiện khi model/hash/đầu vào hợp lệ, gọi đúng một giờ và đối chiếu stored.
   Dự đoán thành phần thật chỉ hiển thị sau live; không bịa số thành phần cho stored.
5. **Sai số**: khoảng ngày, metric của đúng scope saved-test, actual/prediction và error
   chung timestamp được khoanh; nhóm giờ/ngày thường/cuối tuần/cao điểm có n;
   top10 lỗi trong khoảng và feature inspector. Không gộp validation.
6. **Giới hạn & mở rộng**: mở dữ liệu ngoài khi yêu cầu; flow chuẩn giờ/ghép/validation,
   counts và tỷ lệ; giữ hai giả định CST/Chicago và giờ DST mơ hồ; so traffic/weather.
   Ngoài vẫn khóa inference. Fixture nhân tạo chỉ nằm trong mục nâng cao.

## Animation, state và khả năng tiếp cận

**Tab 4 · Chạy và giải thích từng bước:** chọn chế độ này rồi bấm **Xem kết quả
dự đoán**. App thực hiện predict thật cho đúng một giờ, ghi thời gian từng model
và đối chiếu stored, sau đó cho replay sáu bước: nhận đầu vào → tạo C30 → kiểm tra
schema → dự đoán từng model → nhân trọng số/cộng/clip → mở actual và sai số.
Các nút Quay lại/Tiếp theo/Phát lại điều khiển phần giải thích; animation Plotly có
Phát/Dừng độc lập, không giả vờ kéo chậm model. Đổi giờ/chế độ xóa trace cũ.

Mở **Xem sâu bên trong mô hình** để chọn cây RF/ExtraTrees và xem các nút/ngưỡng/
hướng đi/giá trị lá thật. Một cây không phải dự đoán cả rừng. Bấm **Tính đường dự
đoán qua các vòng boosting** để xem prefix XGBoost từ vòng1 đến vòng cuối; không
train lại, không phải loss curve, không nhân learning rate lần nữa.
Module `src/demo/calculation.py` chỉ thu trace inference và giải mã estimator đã lưu.

Plotly frames chạy trong trình duyệt khi người dùng bấm Phát; có Dừng và slider thủ công.
Có lựa chọn Giảm chuyển động. Không sleep, timer hoặc tự rerun cả app cho animation.
Streamlit fragments giới hạn rerun ở phần tương tác. Timestamp tab3/4 dùng chung sidebar;
đổi timestamp/mode/token sẽ xóa kết quả dự đoán cũ. Error inspection có vùng chọn riêng.
Xanh=được dùng; cam=cần chú ý; đỏ=không hợp lệ/sai số cần xem; xám=ngoài bước hiện tại.
Màu luôn có nhãn/hover hoặc chú thích.

## Kiến trúc và tính đúng đắn

- app.py: entrypoint.
- src/demo/uci_app.py: UI sáu tab, cache/state/fragments, lỗi từng thành phần.
- src/demo/presentation.py: views học tập, gọi preprocessing/features/inference chung;
  metric chỉ tóm tắt predictions đã lưu trong scope.
- src/demo/presentation_charts.py: Plotly/HTML highlight, không fit/biến đổi pipeline.
- service.py/weather.py/charts.py: giữ logic contract, guard, ghép và biểu đồ nguồn ngoài.
- predict.py và src/features.py/src/preprocessing.py: owning pipeline, không đổi trong refactor.

Cần giữ final_model.joblib đúng hash (file bị gitignore); không tự retrain khi thiếu file.
Thiếu artifact: stored/metrics vẫn dùng được, live không xuất hiện. Thiếu raw hoặc nguồn
ngoài chỉ làm phần tương ứng báo thiếu, không chặn toàn bộ demo.
Mô hình, dữ liệu gốc và output test không bị ghi đè. Một module openweather_adapter.py
mô phỏng lịch liên bang còn trong repo nhưng không được UI mới gọi để mở khóa ngoài.

Đọc [audit/kế hoạch](docs/uci_first_plan.md), [kịch bản10–15 phút](docs/uci_first_demo.md),
[nghiệm thu](docs/uci_first_verification.md). Các biên bản cũ trong docs là lịch sử;
những hướng dẫn đặt MnDOT ở tab2 hoặc fixture làm luồng chính đã được thay bằng bố cục này.
