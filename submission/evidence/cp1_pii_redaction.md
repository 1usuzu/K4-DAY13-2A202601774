# CP1 — Bằng chứng PII đã được redact

Phụ trách: Thành viên B (Security Engineer) — PII scrubbing, regex patterns, kiểm chứng log.

Nguồn dữ liệu: `data/logs.jsonl` sinh lại từ đầu (log cũ đã xoá trước khi chạy), gồm 10 query trong
`data/sample_queries.jsonl` + 5 query PII chủ động + 1 request lỗi (`tool_fail`).

## 1. Kết quả validator

```
--- Lab Verification Results ---
Total log records analyzed: 35
Potential PII leaks detected: 0

+ [PASSED] PII scrubbing
```

Bộ detector của `scripts/validate_logs.py` chỉ chấm 4 loại: `email`, `phone_vn`, `cccd`, `credit_card`.
Passport và địa chỉ nằm ngoài phạm vi chấm nên được chứng minh riêng ở mục 2.

## 2. Log đã che PII theo từng loại

Trích từ `data/logs.jsonl` (event `request_received`):

| Loại PII | Input gửi vào | Giá trị trong log |
|---|---|---|
| email | `Email tôi là ngo.dat@vinuni.edu.vn, ...` | `Email tôi là [REDACTED_EMAIL], gửi hoá đơn giúp` |
| thẻ Visa + Amex | `Thẻ Visa 4111 1111 1111 1111 và thẻ Amex 3782 822463 10005` | `Thẻ Visa [REDACTED_CREDIT_CARD] và thẻ Amex [REDACTED_CREDIT_CARD_AMEX]` |
| hộ chiếu | `Hộ chiếu của tôi là C1234567, còn của vợ là HC7654321` | `Hộ chiếu của tôi là [REDACTED_PASSPORT_VN], còn của vợ là [REDACTED_PASSPORT_VN]` |
| địa chỉ VN | `Giao tới số nhà 25 đường Lê Lợi, phường 5, quận Bình Thạnh, thành phố Hồ Chí Minh` | `Giao tới [REDACTED_ADDRESS_STREET] [REDACTED_ADDRESS_STREET], [REDACTED_ADDRESS_...` |
| điện thoại + CCCD | `Gọi 0987654321 hoặc +84 912 345 678, CCCD 012345678912` | `Gọi [REDACTED_PHONE_VN] hoặc [REDACTED_PHONE_VN], CCCD [REDACTED_CCCD]` |

Tổng số marker `[REDACTED_*]` trong log: 10 record, đủ 6 loại pattern.

## 3. Redaction nằm ở tầng processor, không phụ thuộc call site

`scrub_event` được đăng ký trong `app/logging_config.py` **trước** `JsonlFileProcessor`, nên PII bị chặn
trước khi ghi file kể cả khi call site quên gọi `summarize_text()`.

Probe: log thẳng PII thô vào `payload` không qua `summarize_text`:

```python
log.info("raw_pii_probe", service="test",
         payload={"detail": "user ngo.dat@gmail.com card 4111111111111111 passport C1234567"})
```

Kết quả ghi ra file:

```json
{"service": "test", "payload": {"detail": "user [REDACTED_EMAIL] card [REDACTED_CREDIT_CARD] passport [REDACTED_PASSPORT_VN]"}, "event": "raw_pii_probe", "level": "info", "ts": "2026-08-11T08:09:31.289944Z"}
```

Điều này bịt lỗ ở `app/main.py` đường lỗi, nơi `payload={"detail": str(exc), ...}` truyền exception thô
không qua `summarize_text()`.

## 4. Kiểm tra false positive

Text kỹ thuật không bị redact nhầm (pattern địa chỉ neo bằng từ khoá + yêu cầu tên riêng viết hoa):

- `đường truyền bị chậm nên latency tăng` — giữ nguyên
- `tra cứu đường dẫn tài liệu ở docs/GUIDE.md` — giữ nguyên
- `quận huyện nào cũng áp dụng chính sách này` — giữ nguyên

## 5. Giới hạn đã biết

- Tên đường/phường viết thường (`tôi ở đường lê lợi`) sẽ lọt. Đây là đánh đổi có chủ đích để tránh
  redact nhầm từ "đường/phố" trong log kỹ thuật.
- Thứ tự pattern trong `PII_PATTERNS` là ngữ nghĩa: `address_admin` phải chạy trước `address_street`,
  nếu không từ khoá "phố" sẽ cắt `thành phố Hồ Chí Minh` thành `thành [REDACTED_ADDRESS_STREET]`.
- Điểm tổng `validate_logs.py` vẫn 30/100 vì correlation ID và enrichment thuộc vai khác, chưa hoàn thành.
  Hạng mục thuộc Thành viên B (PII scrubbing, 30 điểm) đã PASSED.
