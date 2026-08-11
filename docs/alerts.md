# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: High_Latency_P95
- Severity: critical
- SLI/SLO liên quan: latency_p95_ms (SLO: latency_p95 <= 3000ms)
- Điều kiện và thời gian duy trì: latency_p95 > 3000ms liên tục trong 1 phút.
- Ảnh hưởng tới người dùng: Người dùng nhận thấy hệ thống phản hồi cực kỳ chậm, thời gian chờ phản hồi chat bị kéo dài.
- Ba bước kiểm tra đầu tiên:
  1. **Kiểm tra Dashboard**: Xác định xem latency tăng vọt trên toàn hệ thống hay chỉ ở một số feature cụ thể (ví dụ: `monitoring` hoặc `qa`).
  2. **Mở Langfuse Tracing**: Tìm trace có latency cao bất thường trong khung giờ xảy ra sự cố, xem waterfall chart để tìm span bị chậm nhất (RAG `retrieve` hay LLM `generation`).
  3. **Truy vết Logs**: Lọc file `data/logs.jsonl` theo `correlation_id` của trace bị chậm để lấy dữ liệu log chi tiết về input/output và tài liệu tìm kiếm.
- Mitigation tạm thời:
  - Nếu do span RAG (`retrieve` bị chậm do incident `rag_slow`): Tạm thời tắt incident giả lập hoặc kiểm tra kết nối với vector database.
  - Nếu do span LLM: Kiểm tra trạng thái nhà cung cấp API LLM hoặc tối ưu lại độ dài của prompt/documents.
- Owner: team-sre

## Alert 2

- Tên: High_Error_Rate
- Severity: critical
- SLI/SLO liên quan: error_rate_pct (SLO: error_rate_pct <= 2%)
- Điều kiện và thời gian duy trì: error_rate_pct > 2% liên tục trong 1 phút.
- Ảnh hưởng tới người dùng: Người dùng liên tục nhận lỗi HTTP 500 khi chat, không thể nhận câu trả lời từ hệ thống.
- Ba bước kiểm tra đầu tiên:
  1. **Kiểm tra Dashboard**: Quan sát panel "Error rate and breakdown" để biết loại lỗi xảy ra là gì (ví dụ: `RuntimeError`).
  2. **Mở Langfuse Tracing**: Tìm kiếm các trace có trạng thái lỗi (error = true), xem thông tin traceback hoặc message lỗi ở span gặp sự cố.
  3. **Lọc Logs**: Tìm các log có event `request_failed` trong `data/logs.jsonl` để lấy `correlation_id` và xác định lỗi cụ thể xuất phát từ phần nào (RAG hay LLM).
- Mitigation tạm thời:
  - Nếu do vector store bị lỗi kết nối (`tool_fail`): Tắt incident giả lập hoặc chuyển sang cơ chế fallback (không sử dụng RAG hoặc dùng local search).
  - Nếu do lỗi API LLM: Kiểm tra key, quota hoặc chuyển hướng qua LLM backup.
- Owner: team-sre

## Alert 3

- Tên: Cost_Budget_Exceeded
- Severity: warning
- SLI/SLO liên quan: daily_cost_usd (SLO: daily_cost_usd <= 2.5)
- Điều kiện và thời gian duy trì: Tổng cost_usd vượt quá 2.5 USD trong cửa sổ 60 phút.
- Ảnh hưởng tới người dùng: Không ảnh hưởng trực tiếp đến người dùng, nhưng đe dọa ngân sách vận hành của hệ thống.
- Ba bước kiểm tra đầu tiên:
  1. **Kiểm tra Dashboard**: Xem panel "Cost over time" và "Input and output tokens" để đối chiếu xem lượng token tiêu thụ tăng vọt từ thời điểm nào.
  2. **Mở Langfuse Tracing**: Sắp xếp các trace theo chi phí giảm dần, kiểm tra metadata xem prompt version nào đang được sử dụng và model LLM nào đang tốn nhiều chi phí nhất.
  3. **So sánh Logs**: Đối chiếu logs của event `response_sent` để kiểm tra xem `tokens_out` của LLM generator có tăng đột biến bất thường không (ví dụ do incident `cost_spike`).
- Mitigation tạm thời:
  - Nếu do phiên bản prompt mới quá dài: Thực hiện rollback prompt trên Langfuse về phiên bản baseline cũ hơn.
  - Nếu do lượng traffic spam từ một user: Áp dụng Rate Limiting chặn IP hoặc user_id đó.
  - Nếu do incident giả lập: Tắt incident `cost_spike`.
- Owner: team-sre
