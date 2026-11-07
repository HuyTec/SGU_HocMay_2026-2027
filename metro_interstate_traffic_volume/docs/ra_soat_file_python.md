# Rà soát các file Python khi tái cấu trúc

| File | Đánh dấu | Căn cứ |
| --- | --- | --- |
| [src/data.py](../src/data.py) | Ứng viên hợp nhất | Gộp giờ, chia tập và điền thời tiết trùng vai trò với `preprocessing.py`. V2–V4, notebook phân tích lỗi và demo vẫn gọi module này. |
| [src/preprocessing.py](../src/preprocessing.py) và [src/prepare_data.py](../src/prepare_data.py) | Luồng song song cần đối chiếu | `prepare_data.py` dùng `preprocessing.py` để tạo CSV xử lý. Notebook Ridge A/B/C đọc các CSV đó. |
| [src/features.py](../src/features.py) | Hợp nhất theo hàm | Có hai nhóm hàm tạo đặc trưng cho luồng xuất CSV và luồng V2–V4. Cả hai nhóm có nơi gọi. |
| `src/__pycache__/*.pyc` | File sinh tự động | Python tạo khi import. Đây là ứng viên bỏ theo dõi Git và thêm quy tắc ignore trong đợt dọn riêng. |

Qua các nơi gọi hiện tại, chưa có căn cứ để xóa nguyên một file `.py` trong các nhóm trên. Khi hợp nhất tiền xử lý, cần đối chiếu schema, mốc chia và cách học thống kê trong từng fold trước khi chuyển nơi gọi.
