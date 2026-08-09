# Chuẩn bị môi trường

## Yêu cầu

- Python 3.11 trở lên.
- Git.
- Tài khoản Langfuse nếu muốn ghi nhận trace chính thức.

## 1. Tạo virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

## 2. Cấu hình Langfuse

Điền vào `.env` nếu Lab Coach yêu cầu dùng Langfuse:

```dotenv
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=https://cloud.langfuse.com
```

Không commit `.env`. Nếu chưa có key, bạn vẫn có thể chạy API, log, metrics và public tests tại local.

## 3. Kiểm tra cài đặt

Terminal 1:

```bash
uvicorn app.main:app --reload --env-file .env
```

Terminal 2:

```bash
python scripts/load_test.py
python scripts/validate_logs.py
python -m pytest -q
```

API mặc định chạy tại `http://127.0.0.1:8000`; health check ở `/health`, metrics ở `/metrics`.

## Lỗi thường gặp

- `ModuleNotFoundError`: kiểm tra virtual environment đã được activate và chạy lại `pip install -r requirements.txt`.
- Không có `data/logs.jsonl`: bảo đảm API đang chạy trước khi chạy load test.
- Không thấy trace: kiểm tra ba biến `LANGFUSE_*`, sau đó khởi động lại API.
- Challenge chưa chạy: chờ Lab Coach release `config/challenge.json`.
