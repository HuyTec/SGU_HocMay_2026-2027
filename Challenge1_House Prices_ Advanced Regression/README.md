# House Prices — Thí nghiệm dự đoán giá nhà

## Cấu trúc

```text
data/raw/                   Dữ liệu gốc và mô tả
notebooks/
  eda/                      Notebook khám phá dữ liệu
  preprocessing/            Notebook thử tiền xử lý
  feature/                  Notebook thử đặc trưng
  experiment/               Notebook mô hình và phân tích sai số
experiments/                Kết quả của mọi lần thí nghiệm
  YYYY-MM-DD_HH-MM-SS_V1_ten/
    notebook.ipynb          Bản chụp notebook của lần chạy
    log.xlsx                Thông tin và kết quả lần chạy
    figures/                Biểu đồ cần lưu, nếu có
    artifacts/              Các tệp kết quả khác, nếu có
```

Mọi lần EDA, tiền xử lý, tạo đặc trưng, đánh giá mô hình hoặc tuning đều có
thư mục riêng trong `experiments/`. Notebook làm việc nằm trong `notebooks/`;
bản chụp của lần chạy được lưu cùng kết quả. Tên thư mục gồm ngày giờ, phiên bản
và tên ngắn; không ghi đè kết quả cũ. Cây thư mục trên là quy ước cho các lần
chạy tiếp theo, không có nghĩa các thư mục thí nghiệm đã tồn tại.

## Các bước thực hiện một thí nghiệm

1. Ghi câu hỏi, giả thuyết, dữ liệu và mốc so sánh trong notebook.
2. Ghi cấu hình: cách xử lý, mô hình hoặc biểu đồ, cách chia dữ liệu, metric,
   tham số và seed nếu có.
3. Chạy từng bước; lưu kết quả, nhận xét và những lần lỗi hoặc chưa hoàn tất.
4. So sánh trên cùng dữ liệu và cách đánh giá khi phù hợp; ghi kết luận và giới hạn.
5. Lưu notebook và kết quả vào thư mục lần chạy kèm ngày giờ, phiên bản và mô tả.

Với cross-validation, các bước tiền xử lý có học từ dữ liệu phải được fit bên
trong từng fold. File `test.csv` không có nhãn để tính sai số.
Hiện hàm chưa tự tạo thư mục lần chạy hoặc chụp notebook; cần lưu các tệp đó thủ công.
