# Quy trình bắt buộc cho AI agent

Phạm vi: thư mục `metro_interstate_traffic_volume` và các thư mục con.

## Nhánh và pull request

- Trước khi thay đổi file của dự án, kiểm tra trạng thái Git, nhánh hiện tại và các thay đổi đang có.
- Không chỉnh sửa trực tiếp trên `main` hoặc nhánh mặc định. Khi đang ở một trong các nhánh đó, tạo và chuyển sang nhánh riêng cho công việc trước khi sửa. Mặc định đặt tên `codex/<mo-ta-ngan>` nếu người yêu cầu không chỉ định tên khác.
- Nếu đã ở nhánh riêng phù hợp với công việc, tiếp tục trên nhánh đó; không tự chuyển nhánh khi có nguy cơ làm mất hoặc trộn thay đổi chưa được lưu.
- Với mỗi công việc có thay đổi file, chuẩn bị thay đổi, kiểm tra phù hợp, commit trên nhánh riêng, đẩy nhánh và tạo pull request về nhánh mặc định để nhóm review. Có thể tạo draft pull request khi công việc cần review trước khi hoàn thiện.
- Không tự merge pull request hoặc đẩy thay đổi trực tiếp vào `main`. Giữ nguyên các thay đổi không liên quan của người khác và không đưa chúng vào commit hoặc pull request.
- Nếu thiếu quyền, không có remote, không thể tạo nhánh/pull request, hoặc thao tác có nguy cơ ảnh hưởng thay đổi có sẵn, dừng bước bị chặn, giữ nguyên công việc và báo rõ nguyên nhân. Không bỏ qua quy trình bằng cách sửa hay đẩy trực tiếp lên `main`.
- Tác vụ chỉ đọc, trả lời câu hỏi hoặc review không thay đổi file không cần tạo nhánh hay pull request.

## Dự án học máy

- Không tự chạy huấn luyện, tuning hoặc đánh giá tập test trừ khi người dùng yêu cầu hoặc công việc đã được ủy quyền cần các bước đó.
- Không xóa, đổi tên hoặc ghi đè dữ liệu, notebook, log và hiện vật sẵn có nếu chưa được yêu cầu. Ghi rõ thay đổi về dữ liệu, đặc trưng và đánh giá để nhóm review.
- Không đưa khóa mã hóa, secret hoặc nội dung giải mã cần bảo vệ vào pull request hay log.
