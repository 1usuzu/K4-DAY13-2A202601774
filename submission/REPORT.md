# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: B4-2 
- Repository URL: https://github.com/1usuzu/K4-DAY13-2A202601774.git
- Commit SHA cuối: fbd7afd1277c769af4eda7bc172c7432d6dc87cc
- Thành viên và vai trò:

Lê Thị Trúc Linh: Thành viên A

Ngô Lưu Quốc Đạt: Thành viên B 

Lưu Xuân Dũng: Thành viên C

Nguyễn Thị Huyền Trang: Thành viên D 

Nguyễn Phương Thuỳ: Thành viên E


## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 50/100 (Sau CP1)
- Tổng số traces: 11
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard: `scripts/dashboard.py` (Streamlit Local)

## 3. Logging và tracing

- Evidence correlation ID: `req-9401019f` (Có trong data/logs.jsonl)
- Evidence PII redaction: Số điện thoại/Email đã được thay bằng `[REDACTED]`
- Evidence trace waterfall: Lưu trong `submission/evidence/trace_waterfall.png`
- Giải thích một span đáng chú ý: Span `retrieve` (VectorDB) bị nghẽn 2.5s khi kích hoạt sự cố.

## 4. Prompt versioning

- Prompt name: `monitoring_system_prompt`
- Version/label baseline: `v1` (production)
- Version/label candidate: `v2` (candidate)
- Trace ID của mỗi version: Lưu trong `submission/evidence/trace_prompt.txt`
- Bằng chứng đổi label hoặc rollback: Lưu trong `submission/evidence/rollback.png`

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: Hợp lệ 6/6 panel
- Evidence dashboard: Lưu trong `submission/evidence/dashboard.png`
- SLO đã chọn và lý do: p99 Latency < 2000ms. Lý do: RAG thường tốn thời gian nhưng nếu > 2s người dùng sẽ đóng app.
- Alert rules và runbook: Cảnh báo qua webhook khi vượt SLO. Runbook có tại `docs/alerts.md`.

## 6. Điều tra challenge

- Challenge ID: day13-k4-observability-v1
- Triệu chứng từ metrics: Dashboard cảnh báo p99 Latency tăng vọt lên khoảng 10-13s cho các request thuộc tính năng `monitoring`.
- Trace ID liên quan: Trace cho span của tính năng RAG bị kéo dài bất thường (Ví dụ: từ Correlation ID `req-9401019f`).
- Log line/correlation ID liên quan: Correlation ID `req-9401019f`.
- Root cause: Incident `rag_slow` gây ra việc dừng (sleep) 2.5 giây giả lập trong hàm `retrieve()` của file `app/mock_rag.py`. Việc này cộng với tải concurrency 5 làm nghẽn toàn bộ hệ thống API khiến thời gian kéo lên 13 giây.
- Fix action: Bỏ dòng `time.sleep(2.5)` trong khối kiểm tra sự cố `rag_slow` tại `app/mock_rag.py`.
- Preventive measure: Đặt timeout (VD: 1.5s) cho mọi lời gọi RAG/VectorDB. Nếu quá hạn tự động ngắt và dùng cache hoặc trả về fallback. Thiết lập thêm alert riêng cho Span RAG thay vì chỉ alert toàn cục.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| A (Linh) | CP1 Middleware, gán Correlation ID | Tham chiếu Git Log | Hiểu cách gán ID cho Request |
| B (Đạt) | CP1 PII Scrubbing | Tham chiếu Git Log | Biết cách dùng regex che dữ liệu nhạy cảm |
| C (Dũng) | CP1/CP2 Metrics, Dashboard | Tham chiếu Git Log | Định nghĩa metric spec 6 nhóm |
| D (Trang) | CP2 SLO, Alerts Runbook | Tham chiếu Git Log | Lên ngưỡng cảnh báo Alert |
| E (Thùy) | QA, Trace RAG, Dẫn dắt CP3, Báo cáo | fbd7afd127 | Nối Traces -> Logs để điều tra Root Cause |
