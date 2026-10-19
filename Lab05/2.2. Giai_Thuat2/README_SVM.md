# 2.2. GIẢI THUẬT 2: SUPPORT VECTOR MACHINE (SVM)

Hoàn thành mục 2.2.1 đến 2.2.4 của Lab - Thuat toan phan lop.pdf (trang 7-13).

## Thứ tự đọc và chạy

1. [Ôn tập lý thuyết: đủ 7 câu hỏi và trả lời](2_2_1_On_tap_ly_thuyet_SVM.ipynb).
2. [Bài mẫu 1: Iris, scaling, chọn kernel và vector hỗ trợ](2_2_2_Bai_mau_1_Iris.ipynb).
3. [Bài mẫu 2: biểu diễn ảnh Digits và SVM nhận diện chữ số](2_2_2_Bai_mau_2_Digits.ipynb).
4. [Bài thực hành 1: SVM trên dữ liệu tiểu đường](2_2_3_Thuc_hanh_Tieu_duong.ipynb).
5. [Bài thực hành 2: SVM trên dữ liệu động vật](2_2_4_Thuc_hanh_Dong_vat.ipynb).

Chọn kernel **SGU HocMay (Anaconda ổn định)** và **Run All**. Tổng cộng 34 ô mã đã chạy thành công bằng kernel Jupyter; các bảng, biểu đồ và nhận xét đã lưu trong notebook. Cần numpy, pandas, matplotlib, scikit-learn. Không cần Graphviz cho phần SVM.

## Dữ liệu sử dụng

| Bài | Nguồn dữ liệu | Số mẫu |
|---|---|---:|
| Iris | data/Iris.csv, bỏ Id | 150 |
| Digits | sklearn.datasets.load_digits, ảnh 8×8 | 1.797 |
| Tiểu đường | data/diabetes_prediction_dataset.csv | 100.000 ban đầu; 96.146 sau bỏ trùng |
| Động vật | data/data.csv, nhãn Dangerous | 871 ban đầu; 841 sau làm sạch |

sample_submission.csv là mẫu kết quả, không có pixel ảnh, không dùng huấn luyện. Không điền hai nhãn Dangerous bị thiếu; loại khỏi dữ liệu có giám sát. Các thư mục bài của thành viên khác được giữ nguyên.

## Điều chỉnh so với đoạn minh họa trong PDF

- Iris là hoa diên vĩ. Lựa chọn kernel bằng CV trên train, giữ test độc lập.
- Mã ảnh của PDF dùng Digits 8×8, không phải MNIST 28×28. Tách từ chỉ số 1500 để không bỏ mất một mẫu.
- confusion_matrix và classification_report nhận y_true trước, y_pred sau.
- Fit scaler/imputer/encoder trong Pipeline của mỗi fold, tránh rò rỉ dữ liệu.
- Với gần 100.000 dòng, dùng LinearSVC để học toàn bộ train; các bài nhỏ minh họa SVC kernel phi tuyến.
- Dữ liệu động vật rất mất cân bằng: dùng balanced accuracy chọn tham số và phân tích riêng lớp No. Test 100% trên 4 mẫu No không phải cam kết tổng quát hóa.

## Kết quả của cấu hình chọn bằng CV

| Bài | Số mẫu test | Test accuracy | Test F1-macro |
|---|---:|---:|---:|
| Bai_mau_Iris | 30 | 0.9667 | 0.9666 |
| Bai_mau_Digits | 297 | 0.9529 | 0.9531 |
| SVM_TieuDuong | 19,230 | 0.8854 | 0.7555 |
| SVM_DongVat | 169 | 1.0000 | 1.0000 |

Các bài dùng tiêu chí chọn CV khác nhau theo mục tiêu; không so trực tiếp điểm CV giữa các bài. Với tiểu đường, ROC AUC chọn cấu hình trọng số lớp balanced; recall tăng nhưng precision/accuracy giảm so với baseline, đã giải thích trong notebook. Với động vật, xem thêm điểm CV và số lượng lớp No rất ít.

## Kết quả lưu ra file

Mỗi bài có thư mục riêng trong **ket_qua/**, gồm so_sanh_mo_hinh.csv, cv_results.csv, du_doan_test.csv và nhan_xet.md. Các chỉ số accuracy, balanced accuracy, F1 và ROC AUC đã được đối chiếu lại với dự đoán test lưu trong CSV.
