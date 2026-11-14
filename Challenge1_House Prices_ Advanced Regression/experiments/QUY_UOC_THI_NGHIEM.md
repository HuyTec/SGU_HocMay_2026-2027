# Quy ước tổ chức thí nghiệm House Prices

Tham khảo cấu trúc dự án Iris: tách notebook theo giai đoạn, đặt tên thí nghiệm,
ghi cấu hình, đánh giá baseline, tuning và lưu kết quả. Điều chỉnh cho bài toán
hồi quy và ghi lại diễn biến thực nghiệm, không chỉ điểm tốt nhất.

## Cấu trúc

```text
data/raw/                         # Dữ liệu gốc
notebooks/
  eda/                            # Notebook khám phá dữ liệu
  preprocessing/                  # Thử nghiệm xử lý dữ liệu
  feature/                        # Thử nghiệm tạo/chọn đặc trưng
  experiment/                     # Notebook mô hình, phân tích lỗi, tuning
experiments/
  YYYY-MM-DD_HH-MM-SS_V1_ten/     # Mọi lần EDA, xử lý, feature, model; không ghi đè
    notebook.ipynb                # Bản chụp notebook đã lưu khi chạy
    log.xlsx                      # Tổng quan, Validation, Hyperparameters, Tuning CV
    figures/                      # Biểu đồ cần giữ, nếu có
    artifacts/                    # Mô hình hoặc tệp khác, nếu thực sự cần
```

Đây là quy ước cho những lần chạy tiếp theo; cấu trúc minh họa không khẳng định
rằng các thư mục hoặc tệp kết quả đó đã tồn tại. Notebook gốc vẫn được tiếp tục
chỉnh sửa trong `notebooks/`. Bản chụp phải được lưu sau khi notebook được lưu
và phản ánh đúng nội dung/output của lần chạy; ghi rõ nếu chỉ lưu mã hoặc chưa
chạy hết. Không tự gán ngày chạy cho kết quả cũ không rõ thời điểm.

## Mỗi thí nghiệm cần thể hiện

1. **Câu hỏi và giả thuyết:** muốn kiểm tra gì, mốc so sánh và thay đổi nào.
2. **Cấu hình:** dữ liệu, target, phép biến đổi, preprocessing, mô hình,
   tham số, seed, cách chia và metric. Ghi phiên bản dữ liệu/code khi có.
3. **Quá trình:** các bước đã chạy, kết quả từng fold hoặc từng cấu hình tuning;
   đánh dấu thử nghiệm lỗi, chưa chạy hoặc bỏ dở thay vì chỉ giữ kết quả tốt.
4. **Kết luận:** so sánh trên cùng fold và dữ liệu, nhận xét giới hạn và hướng
   tiếp theo. Điểm CV dùng chọn tham số không phải đánh giá độc lập cuối cùng.
5. **Lưu vết:** ngày giờ kèm múi giờ, phiên bản, mô tả, notebook và các kết quả
   đi cùng trong thư mục của lần chạy. Không lưu thông tin chưa được kiểm chứng.

Lệnh thực hiện chuyển sang type HTML từ nb

```Shell
jupyter nbconvert --to html `
  "notebooks/experiment/<tên file>.ipynb" `
  --output-dir "experiments/<tên folder thí nghiệm"
```
