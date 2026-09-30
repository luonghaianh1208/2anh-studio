#!/usr/bin/env sh
# Cài đặt 2Anh Studio (bản Việt mở rộng của PPT Master) trên macOS/Linux.
set -eu

REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
PY=${PYTHON:-python3}

if ! command -v "$PY" >/dev/null 2>&1; then
  echo "[LỖI] Không tìm thấy $PY. Cài Python 3.10+ rồi chạy lại." >&2
  exit 1
fi
if ! "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
  echo "[LỖI] Cần Python 3.10 trở lên." >&2
  exit 1
fi

"$PY" -m pip install -r "$REPO_ROOT/requirements.txt"
"$PY" -m pip install -r "$REPO_ROOT/tools/vi/requirements-vi.txt" || echo "[CẢNH BÁO] Chưa cài được python-docx (thư viện soạn đề). Tạo slide vẫn dùng bình thường; khi cần soạn đề, chạy: $PY -m pip install -r tools/vi/requirements-vi.txt" >&2

if [ ! -f "$REPO_ROOT/.env" ]; then
  cp "$REPO_ROOT/.env.example" "$REPO_ROOT/.env"
  echo "[OK] Đã tạo .env từ .env.example"
fi

exec "$PY" "$REPO_ROOT/tools/vi/doctor.py"
