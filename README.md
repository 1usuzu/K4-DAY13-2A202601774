# Day 13 — Observability cho hệ thống AI

Trong lab 4 giờ này, bạn sẽ biến một API AI chạy được nhưng khó quan sát thành một hệ thống có thể theo dõi, phát hiện sự cố và giải thích nguyên nhân bằng bằng chứng.

## Sau lab, bạn làm được gì?

- Ghi log JSON có cấu trúc và correlation ID xuyên suốt một request.
- Loại bỏ PII trước khi dữ liệu được ghi vào log.
- Theo dõi latency, error, token, cost và quality proxy.
- Đọc metrics → mở trace → dùng log để chứng minh root cause.
- Thiết kế dashboard, SLO, alert và runbook cơ bản.
- Viết báo cáo incident có trace ID hoặc log cụ thể làm bằng chứng.

## Bạn cần hoàn thành

1. Hoàn thiện các khối `TODO` trong `app/` và `config/`.
2. Tạo tối thiểu 10 traces có metadata trên Langfuse.
3. Tạo dashboard đủ 6 nhóm chỉ số trong `docs/dashboard-spec.md`.
4. Điều tra challenge chính thức sau khi Lab Coach release `config/challenge.json`.
5. Hoàn thiện `submission/REPORT.md` và lưu bằng chứng trong `submission/evidence/`.

## 15 phút đầu

1. Làm theo [SETUP.md](SETUP.md).
2. Chạy API: `uvicorn app.main:app --reload --env-file .env`.
3. Ở terminal khác, chạy: `python scripts/load_test.py`.
4. Mở `data/logs.jsonl` và ghi lại những trường còn thiếu.
5. Chạy `python scripts/validate_logs.py` để lấy baseline.

## Practice và challenge chính thức

- Practice luôn dùng được: `python scripts/inject_incident.py --scenario rag_slow`.
- Challenge chính thức chỉ chạy sau khi có `config/challenge.json`.
- Khi được release, chạy:

```bash
python scripts/inject_incident.py
python scripts/load_test.py --challenge --concurrency 5
```

Nếu file chưa được release, script sẽ dừng và yêu cầu chờ Lab Coach. Không tự tạo hoặc sửa `config/challenge.json`.

## Cấu trúc repo

```text
app/          API, agent, logging, metrics, tracing và PII
config/       log schema, SLO, alert và challenge được release
data/         dữ liệu practice và log sinh ra khi chạy
docs/         hướng dẫn, dashboard spec và biểu mẫu bằng chứng
scripts/      load test, inject incident và kiểm tra log
tests/        public tests
submission/   báo cáo và evidence phải nộp
```

## Tài liệu cần đọc

- [CHECKPOINTS.md](CHECKPOINTS.md): tiến độ và đầu ra từng mốc.
- [RULES.md](RULES.md): quy định của bài lab.
- [SUBMISSION.md](SUBMISSION.md): cấu trúc bài nộp.
- [RUBRIC.md](RUBRIC.md): cách chấm tối đa 100 điểm.
- [docs/GUIDE.md](docs/GUIDE.md): gợi ý khi bị kẹt.

## Lưu ý

- App dùng fake LLM nên phần practice không cần API key trả phí.
- Không có Langfuse key, app vẫn chạy nhưng bạn không có bằng chứng trace để lấy trọn điểm.
- `validate_logs.py` chỉ là kiểm tra kỹ thuật nhanh, không phải điểm cuối cùng.
- Không commit `.env`, API key, `.venv/` hoặc log chứa dữ liệu nhạy cảm.
