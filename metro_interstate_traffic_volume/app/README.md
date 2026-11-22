# Metro C30 · Streamlit

Chạy từ thư mục gốc `metro_interstate_traffic_volume`:

```powershell
python -m pip install -r app/requirements.txt
python -m streamlit run app/app.py --server.address 127.0.0.1
```

Môi trường kiểm tra riêng đã được tạo tại `app/.venv`:

```powershell
app/.venv/Scripts/python.exe -m streamlit run app/app.py --server.address 127.0.0.1
app/.venv/Scripts/python.exe -X utf8 -m unittest discover -s app/tests -v
app/.venv/Scripts/python.exe -X utf8 -m app.src.demo.audit_cli
```

Sáu tab: Tổng quan → Dữ liệu → Giờ & history → Mô hình & dự đoán → Đánh giá → Hướng dẫn.
Đoạn kịch bản bổ sung không cung cấp tên sáu tab ban đầu; các tên này bám theo chức năng đã nêu.

## Cấu trúc tích hợp

- `app.py`: UI, cache theo hash file và trạng thái phiên.
- `src/demo/service.py`: audit, kiểm tra chất lượng, inference, scoring; không phụ thuộc Streamlit.
- `src/demo/charts.py`: biểu đồ chồng hai nguồn, chênh lệch, phân phối/mẫu giờ và sai số đã có.
- `src/demo/audit_cli.py`: tái tạo bảng kiểm tra từ file thật, không chạy dự đoán.
- `tests/`: kiểm tra leakage, timestamp, history, clipping, scoring và thay đổi widget.
- `docs/`: hợp đồng dữ liệu, bảng kiểm tra, ví dụ và phạm vi xác minh.

Import từ root dự án: `from app.src.demo import service`. Lớp dịch vụ gọi `predict.prepare_features`,
`predict.predict_hours` và `src.features.add_history_features`. Không có công thức C30 riêng.
Không gọi hàm huấn luyện hoặc quy trình test UCI. Không thay đổi artifact, dữ liệu UCI hoặc output test.

## Trạng thái

MnDOT có traffic nhưng chưa đủ hợp đồng weather/time/holiday, vì vậy khóa dự đoán và đánh giá ngoài.
Không xuất `hourly_demo.csv` giả tương thích. Weather UTC và traffic wall time được xem riêng, không tự ghép.
Chế độ **Tổng hợp · kiểm tra kỹ thuật** dùng dữ liệu nhân tạo xác định trước để kiểm tra phần mềm;
không phải dữ liệu MnDOT, không phải điểm test UCI hay bằng chứng về chất lượng mô hình.

Tab 2 bấm **Lập biểu đồ đối chiếu nguồn**: xem hai đường UCI–MnDOT trên phần giao,
chênh lệch hai nguồn, bảng dữ liệu mới/cũ, phân phối dùng chung bin và mẫu giờ theo thứ.
Timeline tách 6.533 giờ chung, 19 giờ MnDOT bổ sung trong giai đoạn UCI và 1.608 giờ sau UCI;
chỉ 80,06% toàn bộ MnDOT giao timestamp với UCI. Cửa sổ đường traffic mặc định đi qua ranh giới cuối UCI.
Tab 5 bấm **Xem biểu đồ sai số UCI đã lưu**: histogram residual, MAE theo ngày và giờ,
đọc từ dự đoán test đã lưu sau khi kiểm tra hash. Sau khi đánh giá fixture cũng có cùng bộ biểu đồ,
ghi rõ dữ liệu tổng hợp. Không có biểu đồ sai số MnDOT giả khi còn khóa inference.
Tab 6 kèm [nguồn chính thức và bằng chứng tin cậy](docs/demo_sources.md), phân biệt uy tín nguồn với tính tương thích dữ liệu.

Xem [hợp đồng](docs/demo_data_contract.md), [bảng audit](docs/demo_audit.md),
[ví dụ và xác minh](docs/demo_examples.md). Artifact bị `.gitignore` bỏ qua;
khi chuyển máy phải cung cấp đúng file cuối và hash trong biên bản đã lưu, không tự fit lại.

Để mở MnDOT về sau: xác minh từng blocker bằng tài liệu nguồn, tạo adapter chuẩn hóa và provenance,
thêm kiểm tra hợp đồng, rồi nối adapter vào service/UI. Không thêm checkbox “bỏ qua tương thích”.
