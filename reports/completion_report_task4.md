# Báo cáo hoàn thành Task 4: Tích hợp Gọi hàm và Hội thoại Đa lượt

Chúng tôi đã hoàn thành toàn bộ mục tiêu của Task 4 bao gồm việc tích hợp đường ống tác nhân với module gọi hàm nghiệp vụ của xe, đồng thời hoàn thiện cơ chế hội thoại đa lượt và các chỉnh sửa tương thích trên hệ điều hành Windows.

## 1. Kết quả đạt được

### A. Tích hợp gọi hàm và duy trì trạng thái đa lượt
- Đồng bộ hóa lớp quản lý trạng thái `AgentState` vào tiến trình thực thi chính của tác nhân (`car_bench_agent.py`), cho phép lưu giữ thông tin phiên làm việc, các biến xác nhận và ngữ cảnh của người dùng qua nhiều lượt trao đổi liên tiếp.
- Triển khai cơ chế phân giải khóa truy cập động ngay trước khi thực hiện gọi hàm LiteLLM: hệ thống sẽ tự động chèn các tham số `NVIDIA_API_KEY` và `NVIDIA_API_BASE` khi nhận diện mô hình đích thuộc nhóm `z-ai` hoặc `nvidia`.

### B. Định tuyến mô hình đánh giá độc lập
- Cấu hình lại cơ chế sinh phản hồi đánh giá trong tệp `policy_evaluator.py` để tự động nhận dạng và chuyển tiếp yêu cầu đến nền tảng NVIDIA NIM (sử dụng GLM-5.1), tách biệt hoàn toàn với mô hình giả lập người dùng chạy trên OpenAI GPT-4o-mini, loại bỏ sự phụ thuộc vào các API không ổn định khác.

### C. Khắc phục lỗi tương thích trên hệ điều hành Windows
- **Đường dẫn tệp tin:** Chuyển đổi định dạng dấu phân cách đường dẫn ngược `\` thành dấu xuôi `/` thông qua phương thức `.as_posix()` trong `generate_compose.py` để tương thích hoàn toàn với hệ thống Docker và môi trường ảo hóa.
- **Quản lý tiến trình:** Giải quyết lỗi thiếu thuộc tính `os.killpg` trên Windows bằng việc bổ sung điều kiện kiểm tra sự tồn tại của hàm và chuyển sang sử dụng phương thức `terminate()` và `kill()` của thư viện subprocess đối với các tiến trình chạy nền.
- **Mã hóa ký tự:** 
  - Khắc phục lỗi mã hóa phông chữ console (`UnicodeEncodeError` gây ra bởi các ký tự emoji) bằng cách thiết lập lại luồng đầu ra tiêu chuẩn sang định dạng UTF-8 (`sys.stdout.reconfigure(encoding='utf-8')`) và loại bỏ các emoji trực quan trong mã nguồn kiểm thử của CAR-bench (thay thế bằng chuỗi ASCII `[PASS]` và `[FAIL]`).
  - Thiết lập thuộc tính mã hóa đầu vào `encoding="utf-8"` khi đọc tệp `README.md` trong `setup.py` để ngăn ngừa lỗi biên dịch gói trên Windows.

### D. Kết quả kiểm thử
- Hệ thống đã vượt qua toàn bộ 49 bài kiểm thử đơn vị và tích hợp trong dự án mà không ghi nhận bất kỳ lỗi ngoại lệ nào. Mã nguồn tuân thủ hoàn toàn các chỉ dẫn kiểm tra tĩnh của Ruff.

## 2. Hạn chế hiện tại
- Việc vận hành đồng thời hai dịch vụ đám mây khác nhau (OpenAI và NVIDIA) làm gia tăng nguy cơ bất đồng bộ do chênh lệch về thời gian phản hồi mạng và sự không đồng nhất hoàn toàn trong cấu trúc dữ liệu trả về từ các API.
- Cơ chế hội thoại đa lượt hiện tại lưu trữ trạng thái trực tiếp trong bộ nhớ cục bộ, chưa hỗ trợ khả năng đồng bộ hóa hoặc phân tán nếu hệ thống được triển khai trên cụm máy chủ chịu tải cao.

## 3. Hướng khắc phục trong tương lai
- Phát triển một lớp trung gian trừu tượng hóa mô hình (Model Gateway/Abstraction Layer) để chuẩn hóa cấu trúc dữ liệu trả về từ bất kỳ nhà cung cấp dịch vụ LLM nào trước khi chuyển dữ liệu vào luồng nghiệp vụ của tác nhân.
- Tích hợp một cơ chế lưu trữ trạng thái ngoài có tính năng phân tán (chẳng hạn như Redis hoặc cơ sở dữ liệu NoSQL) để quản lý phiên hội thoại đa lượt của trợ lý ảo Vivi, tăng tính sẵn sàng và khả năng mở rộng của hệ thống.
