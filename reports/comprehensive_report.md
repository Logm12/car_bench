# Báo cáo tổng hợp kết quả phát triển Trợ lý ảo VinFast Vivi (CAR-bench)

Báo cáo này tổng hợp kết quả thực hiện của chuỗi 5 nhiệm vụ (tasks) trong quá trình phát triển tác nhân AI trợ lý ảo VinFast Vivi nhằm đạt mục tiêu: Hiểu ý định người dùng, quyết định hành động, phối hợp gọi hàm (function calling) và hỗ trợ các kịch bản trình diễn (demo scenarios).

---

## 1. Tổng quan tiến độ thực hiện

Dưới đây là bảng tổng hợp tiến độ và trạng thái hoàn thành của từng nhiệm vụ trong dự án:

| Nhiệm vụ | Nội dung trọng tâm | Trạng thái | Đầu ra chính |
| :--- | :--- | :--- | :--- |
| **Task 1** | Thiết lập môi trường, phân tích dữ liệu, định nghĩa ý định | Hoàn thành | `intent_definitions.py`, `task1_architecture_notes.md` |
| **Task 2** | Gợi ý prompt hệ thống, phân loại ý định, thiết kế trạng thái | Hoàn thành | `vivi_prompts.py`, `agent_state.py`, `test_agent_flow.py` |
| **Task 3** | Xây dựng đường ống xử lý, cơ chế phục hồi LLM | Hoàn thành | Tích hợp ý định động, bộ xử lý thử lại (backoff retry) |
| **Task 4** | Tích hợp gọi hàm, hội thoại đa lượt, tương thích Windows | Hoàn thành | Tuần tuần tự hóa trạng thái, vá lỗi tương thích Windows |
| **Task 5** | Nâng cao độ tin cậy, xử lý tình huống biên, nhật ký hệ thống | Hoàn thành | Sửa lỗi Pydantic, xử lý lỗi double-failure, dọn nhật ký |

---

## 2. Chi tiết kết quả thực hiện theo từng nhiệm vụ

### Task 1: Kiến trúc hệ thống, Thiết lập môi trường và Định nghĩa Intent
- **Kết quả đạt được:**
  - Thiết lập môi trường phát triển trên Windows thông qua việc sử dụng cơ chế Git **sparse-checkout** đối với thư mục `third_party/car-bench`. Giải pháp này giúp bỏ qua các tệp tin chứa dấu hai chấm (`:`) trong tên kết quả chạy thử nghiệm, khắc phục giới hạn của hệ thống tệp NTFS.
  - Cấu hình thành công các biến môi trường kết nối LLM thông qua LiteLLM (GPT-4o-mini đóng vai trò giả lập người dùng; dòng mô hình GLM-5.1 của NVIDIA NIM đóng vai trò tác nhân lý giải chính).
  - Phân tích tập dữ liệu `carbench-ijcai/car-benchmark-vv` và ánh xạ thành công danh mục **25 ý định (intents)** độc lập của trợ lý ảo Vivi trong [intent_definitions.py](file:///e:/VinAI/car-bench-ijcai/src/track_1_agent_under_test/intent_definitions.py).
  - Hoàn thiện tài liệu kiến trúc [task1_architecture_notes.md](file:///e:/VinAI/car-bench-ijcai/docs/task1_architecture_notes.md) mô tả luồng xử lý truy vấn hợp nhất.

### Task 2: Thiết kế Luồng Tác nhân, Chiến lược Gợi ý Prompt và Trạng thái Hội thoại
- **Kết quả đạt được:**
  - Xây dựng prompt hệ thống `VIVI_SYSTEM_PROMPT` trong [vivi_prompts.py](file:///e:/VinAI/car-bench-ijcai/src/track_1_agent_under_test/vivi_prompts.py) tuân thủ quy tắc Text-to-Speech (TTS): loại bỏ hoàn toàn các ký tự định dạng markdown, đồng nhất hệ đo lường mét và định dạng thời gian 24 giờ, tích hợp các ràng buộc an toàn (như liên kết mở tấm che nắng trước khi mở cửa sổ trời, cảnh báo hiệu suất năng lượng khi mở cửa sổ lúc bật điều hòa).
  - Triển khai bộ phân loại ý định based-on-few-shot xuất ra định dạng cấu trúc JSON kèm điểm số tin cậy.
  - Triển khai lớp `AgentState` quản lý trạng thái hội thoại, lưu trữ tạm các yêu cầu gọi hàm đang chờ xác nhận từ người dùng, hỗ trợ tuần tự hóa và giải tuần tự hóa trạng thái phiên làm việc.
  - Hoàn thiện bộ kiểm thử đơn vị trong [test_agent_flow.py](file:///e:/VinAI/car-bench-ijcai/tests/test_agent_flow.py).

### Task 3: Xây dựng Đường ống Xử lý Cơ bản (Query → Reasoning → Action Selection)
- **Kết quả đạt được:**
  - Tích hợp bộ phân loại ý định động vào trước giai đoạn lý giải chính, đảm bảo chèn đúng hướng dẫn hệ thống kèm theo ý định hiện tại của người dùng vào đầu lịch sử hội thoại.
  - Thiết lập vòng lặp thử lại tự động theo thuật toán số mũ (exponential backoff retry) tối đa 3 lần nhằm đối phó với các lỗi quá tải API (Rate Limit) ở tầng kết nối LLM.
  - Triển khai các cơ chế ép kiểu dữ liệu và kiểm tra cấu trúc dữ liệu trả về từ mô hình giả lập, bảo đảm an toàn dữ liệu và ghi nhận chính xác chi phí token sử dụng.
  - Vượt qua kịch bản kiểm thử tích hợp trong [test_agent_pipeline.py](file:///e:/VinAI/car-bench-ijcai/tests/test_agent_pipeline.py).

### Task 4: Tích hợp Gọi hàm và Hội thoại Đa lượt
- **Kết quả đạt được:**
  - Kết nối quản lý trạng thái `AgentState` với tiến trình thực thi thực tế để duy trì lịch sử hội thoại đa lượt của người dùng qua các phiên làm việc của tác nhân.
  - Triển khai cơ chế phân giải thông tin xác thực động, tự động chèn khóa `NVIDIA_API_KEY` và địa chỉ `NVIDIA_API_BASE` khi phát hiện lời gọi mô hình thuộc nhóm `z-ai` hoặc `nvidia` (ví dụ như mô hình đánh giá chính sách `policy_evaluator.py`).
  - Giải quyết toàn bộ các lỗi tương thích hệ điều hành Windows:
    - Chuẩn hóa đường dẫn Docker sử dụng phương thức `.as_posix()` trong `generate_compose.py`.
    - Thay thế cơ chế ngắt tiến trình nhóm `os.killpg` bằng gọi hàm `terminate()` và `kill()` của thư viện subprocess.
    - Ép mã hóa UTF-8 cho luồng xuất tiêu chuẩn và loại bỏ emoji hiển thị trong bảng điều khiển để tránh lỗi `UnicodeEncodeError`.
    - Bổ sung cấu hình đọc tệp tin `setup.py` dưới định dạng UTF-8.

### Task 5: Nâng cao Độ tin cậy, Xử lý Tình huống Biên, Kịch bản Đánh giá và Cải tiến Nhật ký
- **Kết quả đạt được:**
  - Khắc phục lỗi kiểm tra dữ liệu nghiêm ngặt của Pydantic (`ValidationError`) trong `fixed_context.py` do dữ liệu đầu vào của tập kiểm thử nằm ngoài phạm vi định nghĩa (ví dụ: dung lượng pin xe khởi tạo ở mức 80% trong khi ràng buộc yêu cầu tối thiểu là 90%).
  - Giải quyết lỗi xung đột trạng thái kết thúc (double-failure) trong `car_bench_evaluator.py` bằng việc chuyển giao quyền cập nhật trạng thái lỗi duy nhất về cho lớp quản lý `evaluator_executor.py`.
  - Chuẩn hóa các dấu ngoặc nhọn trong Loguru để dọn sạch lỗi định dạng hiển thị, tắt cảnh báo không cần thiết từ thư viện LiteLLM (`LITELLM_LOG=ERROR`).
  - Xác định và phân tích nguyên nhân cảnh báo thiếu tệp dữ liệu đường đi (`routes_metadata.jsonl`) và dữ liệu địa điểm (`pois.jsonl`) trong kho lưu trữ Hugging Face, kiểm chứng hoạt động ổn định của cơ chế dự phòng tự động.

---

## 3. Hạn chế và thách thức hiện tại

Mặc dù hệ thống đã hoạt động ổn định và vượt qua toàn bộ các kịch bản kiểm thử tích hợp, dự án vẫn tồn tại một số điểm hạn chế kỹ thuật:

1. **Độ trễ và chi phí phân loại ý định:** Bộ phân loại ý định few-shot hoạt động trên nền tảng đám mây (cloud-based LLM) làm tăng độ trễ phản hồi của hệ thống và tiêu tốn chi phí API cho các câu lệnh đơn giản của người dùng.
2. **Luồng xử lý tuyến tính:** Luồng tác nhân hiện tại được thiết kế theo dạng tuần tự đơn giản, chưa tối ưu hóa cho các hành động yêu cầu gọi nhiều hàm đồng thời (parallel tool calling) hoặc xử lý các chuỗi thao tác phức tạp liên kết giữa các thiết bị ngoại vi trên xe.
3. **Mất đồng bộ hệ thống phân tán:** Quản lý trạng thái hội thoại `AgentState` hiện đang lưu trữ trực tiếp trong bộ nhớ RAM cục bộ của tiến trình, chưa có cơ chế đồng bộ hóa hoặc giải phóng bộ nhớ khi số lượng phiên hội thoại tăng cao hoặc triển khai trên nhiều nút máy chủ.
4. **Bất đồng bộ dịch vụ đám mây:** Việc sử dụng hỗn hợp hai nhà cung cấp LLM khác nhau (OpenAI cho người dùng giả lập và NVIDIA NIM cho tác nhân lý giải) có thể dẫn đến sự chênh lệch thời gian phản hồi mạng và sự không đồng nhất về định dạng phản hồi.
5. **Hạn chế dữ liệu kiểm thử thực tế:** Sự thiếu hụt dữ liệu bản đồ đường đi và danh mục POI chi tiết từ tập dữ liệu Hugging Face gốc giới hạn khả năng đánh giá thực tế của các tính năng điều hướng nâng cao.

---

## 4. Kế hoạch hành động và cách khắc phục trong tương lai

Nhằm khắc phục các hạn chế trên và chuẩn bị cho giai đoạn vận hành thương mại, các giải pháp kỹ thuật sau đây được đề xuất:

1. **Huấn luyện mô hình phân loại cục bộ (Edge Intent Classifier):**
   - Triển khai và tinh chỉnh một mô hình học máy nhỏ gọn (như DistilBERT hoặc FastText) trực tiếp trên thiết bị đầu cuối của xe (Edge) để thực hiện phân loại 25 nhóm ý định.
   - Mục tiêu: Rút ngắn độ trễ phân loại xuống dưới 10 mili-giây và giảm 100% chi phí gọi API đám mây cho giai đoạn tiền xử lý.
2. **Nâng cấp sang kiến trúc đồ thị tác nhân (Agentic Graph):**
   - Tái cấu trúc đường ống xử lý sang dạng đồ thị trạng thái (ví dụ sử dụng thư viện LangGraph).
   - Cho phép tác nhân đưa ra quyết định gọi nhiều hàm song song trong một lượt hội thoại và tự động sửa lỗi hành động dựa trên phản hồi của xe.
3. **Quản lý trạng thái phiên phân tán:**
   - Tích hợp một cơ sở dữ liệu lưu trữ khóa-giá trị tốc độ cao (như Redis) để quản lý trạng thái phiên hội thoại đa lượt của tác nhân Vivi.
   - Bổ sung cơ chế tự động dọn dẹp trạng thái dựa trên thời gian thực (TTL) và thuật toán tóm tắt lịch sử hội thoại tự động để kiểm soát dung lượng cửa sổ ngữ cảnh đầu vào của LLM.
4. **Xây dựng lớp Gateway chuẩn hóa LLM (Model Gateway):**
   - Thiết lập một lớp trung gian trừu tượng hóa mô hình để chuyển đổi tất cả cấu trúc dữ liệu trả về từ các nhà cung cấp đám mây khác nhau về một định dạng chuẩn chung của hệ thống trước khi chuyển vào luồng nghiệp vụ.
5. **Tự động hóa sinh dữ liệu giả lập (Mock Data Generator):**
   - Xây dựng một module nội bộ tự động sinh dữ liệu giả lập hoàn chỉnh cho các tuyến đường và danh mục POI dựa trên tọa độ GPS giả lập của xe để phục vụ cho các bài kiểm thử cục bộ mà không phụ thuộc vào kho dữ liệu Hugging Face.
