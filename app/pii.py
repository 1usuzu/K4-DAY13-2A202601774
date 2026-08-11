from __future__ import annotations

import hashlib
import re

# Thứ tự quan trọng: scrub_text áp dụng tuần tự, pattern chạy trước "ăn" text trước.
# Đặt pattern đặc thù (dài, có tiền tố) trước pattern chung chung.
PII_PATTERNS: dict[str, str] = {
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
    # Visa/Master/JCB 16 số và Amex 15 số (4-6-5)
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    "credit_card_amex": r"\b3[47]\d{2}[- ]?\d{6}[- ]?\d{5}\b",
    "phone_vn": r"(?<!\d)(?:\+84|0)(?:[ .-]?\d){9}(?!\d)",
    "cccd": r"\b\d{12}\b",
    # Hộ chiếu VN: 1-2 chữ in hoa + 7 chữ số, ví dụ C1234567 / HC1234567
    "passport_vn": r"\b[A-Z]{1,2}\d{7}\b",
    # Địa chỉ VN: neo bằng từ khoá để tránh nuốt nhầm text thường.
    # address_admin phải chạy TRƯỚC address_street, nếu không "thành phố X"
    # sẽ bị từ khoá "phố" của address_street cắt mất.
    "address_admin": (
        r"(?i:phường|quận|huyện|thị\s*trấn|tỉnh|thành\s*phố)\s+"
        r"(?:\d+|[A-ZÀ-Ỹ][\wÀ-ỹ]*(?:\s+[A-ZÀ-Ỹ][\wÀ-ỹ]*){0,2})"
    ),
    "address_street": (
        r"(?i:số\s*nhà|ngõ|hẻm|đường|phố)\s+"
        r"(?:\d+[\w/]*|[A-ZÀ-Ỹ][\wÀ-ỹ]*(?:\s+[A-ZÀ-Ỹ][\wÀ-ỹ]*){0,2})"
    ),
}


def scrub_text(text: str) -> str:
    safe = text
    for name, pattern in PII_PATTERNS.items():
        safe = re.sub(pattern, f"[REDACTED_{name.upper()}]", safe)
    return safe


def summarize_text(text: str, max_len: int = 80) -> str:
    safe = scrub_text(text).strip().replace("\n", " ")
    return safe[:max_len] + ("..." if len(safe) > max_len else "")


def hash_user_id(user_id: str) -> str:
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12]
