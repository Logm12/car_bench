# Báo cáo hoàn thành Task 2: Thiết kế Luồng Tác nhân, Chiến lược Gợi ý Prompt và Trạng thái Hội thoại

Chúng tôi đã hoàn thành toàn bộ mục tiêu của Task 2 liên quan đến việc xây dựng luồng hội thoại của tác nhân, áp dụng chiến lược gợi ý prompt tối ưu và thiết kế cấu trúc trạng thái.

## 1. Kết quả đạt được

### A. Chiến lược gợi ý prompt tương thích Text-to-Speech (TTS)
- Xây dựng hệ thống prompt `VIVI_SYSTEM_PROMPT` trong tệp `vivi_prompts.py` tuân thủ nghiêm ngặt các quy tắc chuyển đổi văn bản thành giọng nói để phản hồi trên xe:
  - Loại bỏ hoàn toàn các định dạng hiển thị trực quan (như định dạng markdown, in đậm, danh sách liệt kê dạng dấu chấm hoặc chữ số).
  - Áp dụng thống nhất hệ đo lường mét (khoảng cách bằng mét/kilômét, nhiệt độ bằng độ C) và định dạng thời gian 24 giờ.
  - Tích hợp các ràng buộc an toàn vật lý của xe: kiểm tra trạng thái tấm che nắng trước khi mở cửa sổ trời, đưa ra cảnh báo hiệu suất năng lượng nếu cửa sổ mở quá 25% khi đang bật điều hòa, và tự động điều chỉnh quạt gió/hướng gió khi kích hoạt sấy kính chắn gió.
- Phát triển bộ phân loại ý định `INTENT_CLASSIFICATION_SYSTEM_PROMPT` áp dụng phương pháp gợi ý few-shot, cho phép trích xuất phân loại ý định của người dùng thành một trong 25 lớp `ViviIntent` kèm theo điểm tin cậy dưới dạng cấu trúc JSON.

### B. Quản lý trạng thái hội thoại
- Triển khai lớp `AgentState` trong tệp `agent_state.py` để theo dõi ngữ cảnh hội thoại, lưu trữ tạm thời các yêu cầu gọi hàm đang chờ xác nhận từ phía người dùng (ví dụ: các hành động mở cửa sổ trời hoặc sấy kính) và ghi nhận danh sách lựa chọn của người dùng trong các tình huống giải quyết nhập nhằng thông tin.
- Hỗ trợ các phương thức tuần tự hóa `serialize` và giải tuần tự hóa `deserialize` dưới dạng từ điển Python, làm cơ sở cho việc lưu trữ trạng thái bền vững giữa các phiên làm việc của tác nhân.

### C. Kiểm thử và xác minh
- Xây dựng bộ kiểm thử đơn vị trong tệp `tests/test_agent_flow.py` nhằm xác thực:
  - Sự tuân thủ luật định dạng TTS của prompt hệ thống.
  - Tính chính xác về cấu trúc đầu ra của bộ phân loại ý định.
  - Độ tin cậy trong quá trình tuần tự hóa trạng thái hội thoại.
- Kết quả chạy thử nghiệm nội bộ hoàn thành thành công và mã nguồn đạt chứng nhận kiểm tra tĩnh từ công cụ Ruff.

## 2. Hạn chế hiện tại
- Việc phân loại ý định dựa trên mô hình ngôn ngữ lớn (LLM) thông qua cơ chế few-shot sinh ra độ trễ truy vấn tương đối cao và tăng chi phí vận hành đối với các câu lệnh đơn giản, lặp đi lặp lại.
- Trạng thái hội thoại `AgentState` chưa hỗ trợ cơ chế giải phóng bộ nhớ tự động hoặc nén lịch sử phiên làm việc khi số lượt trao đổi đa lượt kéo dài, dễ dẫn đến hiện tượng tràn cửa sổ ngữ cảnh của mô hình lý giải.

## 3. Hướng khắc phục trong tương lai
- Nghiên cứu huấn luyện hoặc tinh chỉnh (fine-tune) một mô hình phân loại cục bộ có kích thước nhỏ (ví dụ như kiến trúc DistilBERT hoặc FastText) chuyên biệt cho 25 lớp ý định của Vivi để xử lý phân loại cục bộ trực tiếp trên biên với độ trễ tối thiểu (dưới 10 mili-giây).
- Bổ sung cơ chế dọn dẹp trạng thái dựa trên thời gian thực (Time-To-Live - TTL) và giải thuật tóm tắt ngữ cảnh tự động cho `AgentState` để tối ưu hóa dung lượng đầu vào gửi tới LLM lý giải.
