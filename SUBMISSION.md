# Hướng dẫn nộp bài

## Nội dung bắt buộc

- Source đã hoàn thiện trong `app/`, `config/`, `scripts/` và `tests/`.
- `submission/REPORT.md` đã điền đầy đủ.
- Evidence đặt trong `submission/evidence/`:
  - kết quả `validate_logs.py`;
  - danh sách tối thiểu 10 traces;
  - một trace waterfall;
  - log có correlation ID;
  - bằng chứng PII đã được redact;
  - dashboard đủ 6 nhóm chỉ số;
  - bằng chứng điều tra challenge.

## Không được nộp

- `.env`, API key hoặc secret.
- `.venv/`, cache, dependency đã cài.
- Log có PII chưa được che.
- Source hoặc ảnh lấy từ sample solution của đội khác.
- File `config/challenge.json` đã bị tự ý sửa.

## Kiểm tra trước khi nộp

```bash
python -m pytest -q
python scripts/validate_logs.py
git status --short
```

Sau đó push repo bài làm và nộp URL repository cùng commit SHA cuối trên hệ thống Codelabs. Nếu Lab Coach quy định cách đặt tên repo, ưu tiên quy định được công bố trong lớp.

Bài thiếu `submission/REPORT.md`, không clone được, lộ secret hoặc sai loại URL được xem là chưa hợp lệ và cần nộp lại.
