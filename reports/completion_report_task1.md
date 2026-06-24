# Báo cáo hoàn thành Task 1: Kiến trúc hệ thống, Thiết lập môi trường và Định nghĩa Intent cho Trợ lý ảo Vivi

Chúng tôi đã hoàn thành toàn bộ mục tiêu của Task 1 cho Tác nhân AI Trợ lý ảo VinFast Vivi (CAR-bench).

## 1. Kết quả đạt được

### A. Thiết lập môi trường phát triển trên Windows
- Sử dụng tính năng **sparse-checkout** của Git đối với thư mục `third_party/car-bench` để bỏ qua các thư mục hoặc tệp chứa ký tự không hợp lệ trên Windows (tránh lỗi xung đột đặt tên tệp chứa dấu hai chấm `:` trên hệ thống tệp NTFS).
- Thiết lập và cấu hình các biến môi trường phục vụ kết nối mô hình ngôn ngữ lớn (LLM) trong tệp `.env`:
  - Trỏ `AGENT_LLM` tới `gpt-4o-mini` cho các tác vụ mô phỏng người dùng.
  - Định cấu hình `NVIDIA_API_BASE` và `NVIDIA_MODEL` trỏ tới điểm cuối NVIDIA NIM (sử dụng dòng mô hình GLM-5.1) phục vụ cho tác nhân lý giải và đánh giá chính sách.

### B. Phân tích dữ liệu VinFast Vivi
- Thu thập và phân tích cấu trúc cấu hình tập dữ liệu `carbench-ijcai/car-benchmark-vv` từ Hugging Face bao gồm ba tập con:
  - `tasks_base` (59 nhiệm vụ huấn luyện / 59 nhiệm vụ kiểm thử)
  - `tasks_disambiguation` (37 nhiệm vụ huấn luyện / 29 nhiệm vụ kiểm thử)
  - `tasks_hallucination` (57 nhiệm vụ huấn luyện / 59 nhiệm vụ kiểm thử)
  - Xác định và ánh xạ thành công danh mục **25 ý định người dùng (intents) độc lập** tương ứng với các nhóm chức năng trên xe.

### C. Xây dựng module định nghĩa ý định
- Triển khai mã nguồn trong [intent_definitions.py](file:///e:/VinAI/car-bench-ijcai/src/track_1_agent_under_test/intent_definitions.py) bao gồm:
  - Khai báo lớp `ViviIntent` kế thừa từ `Enum` đại diện cho 25 ý định.
  - Xây dựng bộ mô tả chi tiết cho từng ý định để cung cấp thông tin ngữ cảnh cho bộ phân loại và tác nhân lý giải.

### D. Đặc tả kiến trúc hệ thống
- Tạo lập tài liệu [task1_architecture_notes.md](file:///e:/VinAI/car-bench-ijcai/docs/task1_architecture_notes.md) mô tả chi tiết:
  - Luồng xử lý truy vấn hợp nhất (Truy vấn → Phân loại → Lý giải → Thực thi hành động).
  - Các ràng buộc về mặt trạng thái hội thoại và ngữ cảnh xe.
  - Giao thức giải quyết nhập nhằng thông tin theo mức độ ưu tiên từ 0 đến 5 cùng các điều kiện kích hoạt cảnh báo an toàn.

## 2. Hạn chế hiện tại
- Do kiến trúc của mẫu dự án mẫu A2A thực hiện thay đổi động biến hệ thống `sys.path` trước khi tải các gói thư viện nội bộ, các công cụ kiểm tra mã nguồn tĩnh như Ruff báo lỗi cảnh báo `E402` (câu lệnh import không nằm ở đầu tệp).
- Việc chạy thử nghiệm trực tiếp trên Windows gặp nhiều khó khăn về mặt định dạng phân cách đường dẫn và mã hóa ký tự mặc định so với môi trường Linux tiêu chuẩn.

## 3. Hướng khắc phục trong tương lai
- Tái cấu trúc cấu trúc thư mục dự án và phương thức đóng gói, chuyển sang sử dụng cơ chế cài đặt editable thông qua công cụ quản lý gói `uv` để loại bỏ hoàn toàn việc chỉnh sửa `sys.path` động.
- Phát triển tập lệnh tự động hóa cài đặt môi trường độc lập với hệ điều hành (cross-platform bootstrap script) nhằm giảm thiểu thời gian cấu hình thủ công trên các thiết bị phát triển mới.
