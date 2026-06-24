# Báo cáo hoàn thành Task 3: Xây dựng Đường ống Xử lý Cơ bản của Tác nhân

Chúng tôi đã hoàn thành việc thiết lập đường ống xử lý truy vấn cơ bản (Pipeline) cho trợ lý ảo Vivi, liên kết các giai đoạn nhận dạng ý định, lý giải ngữ cảnh và lựa chọn hành động.

## 1. Kết quả đạt được

### A. Tích hợp bộ phân loại ý định động
- Kết nối thành công bộ phân loại ý định `ViviIntent` vào luồng xử lý chính của tác nhân. Truy vấn đầu vào của người dùng sẽ được phân tích ý định trước khi chuyển tới mô hình lý giải để đưa ra quyết định hành động tiếp theo.
- Triển khai cơ chế chèn prompt hệ thống động. Trạng thái ý định hiện tại (`Active User Intent`) được liên kết trực tiếp vào vị trí khởi đầu của lịch sử hội thoại, giúp mô hình ngôn ngữ lớn duy trì sự tập trung vào ngữ cảnh hành động tương ứng.

### B. Khả năng phục hồi và xử lý lỗi kết nối LLM
- Thiết lập cơ chế thử lại tự động theo thuật toán số mũ (exponential backoff retry) bao bọc xung quanh lời gọi API của LiteLLM. Hệ thống tự động tạm dừng và thực hiện gửi lại yêu cầu tối đa 3 lần khi đối mặt với các lỗi quá tải hoặc giới hạn tần suất gọi từ nhà cung cấp dịch vụ (Rate Limit).

### C. Chuẩn hóa và làm sạch dữ liệu đầu ra
- Xây dựng các hàm kiểm tra kiểu dữ liệu và ép kiểu dữ liệu từ điển chặt chẽ đối với các tham số đầu vào của công cụ (tool arguments) nhằm ngăn ngừa lỗi đổ vỡ hệ thống khi nhận được dữ liệu không hợp lệ hoặc bị khuyết thiếu cấu trúc từ mô hình giả lập.
- Thiết lập cơ chế trích xuất các thông số vận hành (như số lượng token tiêu thụ, chi phí cuộc gọi tương ứng) đồng bộ với giao diện kiểm thử của CAR-bench.

### D. Xác thực hệ thống
- Xây dựng kịch bản kiểm thử tích hợp đường ống tác nhân trong tệp `tests/test_agent_pipeline.py` sử dụng kỹ thuật giả lập phản hồi kết nối (`AsyncMock`). Bộ thử nghiệm hoàn thành tốt đẹp với thời gian phản hồi nhanh và vượt qua các tiêu chuẩn kiểm tra mã nguồn tĩnh của Ruff.

## 2. Hạn chế hiện tại
- Luồng xử lý tác nhân được thiết kế theo dạng tuyến tính tuần tự (Query → Reasoning → Action), chưa hỗ trợ cơ chế gọi đồng thời nhiều hàm song song (parallel tool calling) hoặc xử lý các chuỗi phụ thuộc phức tạp giữa các thiết bị ngoại vi trong xe.
- Cơ chế thử lại tự động mới chỉ giới hạn ở tầng kết nối LLM chính, chưa bao phủ các điểm kết nối dịch vụ ngoài hoặc các lỗi phát sinh trực tiếp trong quá trình thực thi công cụ phần cứng của bên thứ ba.

## 3. Hướng khắc phục trong tương lai
- Phát triển và nâng cấp đường ống xử lý sang mô hình đồ thị trạng thái tác nhân (Agentic Graph), cho phép hệ thống rẽ nhánh lý giải linh hoạt và hỗ trợ gọi hàm song song từ mô hình để tối ưu hóa thời gian phản hồi.
- Xây dựng một module quản lý độ tin cậy và xử lý ngoại lệ tập trung (Resilience Manager) áp dụng chung cho cả cuộc gọi mô hình và tiến trình thực thi công cụ nghiệp vụ ngoại vi.
