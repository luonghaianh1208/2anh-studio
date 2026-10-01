# tools/vi/anh_vox_parts/nguon_ve.py
"""Gọi API tạo ảnh kiểu OpenAI (9router mặc định). Khoá không bao giờ đi vào thông báo lỗi."""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

URL_MAC_DINH = "http://localhost:20128/v1"
MO_HINH_MAC_DINH = "ag/gemini-3.1-flash-image"
FIX_KHOA = ("Đặt khoá API của 9router: `setx ANH_AI_KEY \"<khoá>\"` (lấy ở trang quản trị 9router) rồi mở lại cửa sổ "
            "lệnh; hoặc dùng `anh: tim:` (ảnh thật), hoặc thay ảnh bằng `chu`, `the`.")
FIX_MANG = "Kiểm tra 9router đang chạy (`9router` mở ở cổng 20128) hoặc địa chỉ `ANH_AI_URL`, rồi chạy lại."
FIX_NCC = "Đọc thông báo của nhà cung cấp: hết hạn mức thì chờ hoặc đổi `ANH_AI_MO_HINH`; câu lệnh bị từ chối thì sửa mô tả `ve:`."


class VeError(Exception):
    """`thu_lai`: lỗi tạm (mạng, 5xx) — anh_vox thử lại tối đa 2 lần trước khi báo."""

    def __init__(self, step: str, message: str, fix: str, thu_lai: bool = False) -> None:
        super().__init__(message)
        self.step, self.message, self.fix, self.thu_lai = step, message, fix, thu_lai


@dataclass
class CauHinh:
    url: str
    khoa: str | None
    mo_hinh: str


def doc_cau_hinh(env=os.environ, home: Path | None = None) -> CauHinh:
    tep = {}
    f = (home or Path.home()) / ".2anh-studio" / "anh-ai.json"
    if f.is_file():
        try:
            tep = json.loads(f.read_text(encoding="utf-8"))
        except ValueError as exc:
            raise VeError("cau-hinh", f"File cấu hình {f} hỏng: {exc}", "Sửa hoặc xoá file đó rồi chạy lại.") from None
    return CauHinh(url=(env.get("ANH_AI_URL") or tep.get("url") or URL_MAC_DINH).rstrip("/"),
                   khoa=env.get("ANH_AI_KEY") or tep.get("khoa"),
                   mo_hinh=env.get("ANH_AI_MO_HINH") or tep.get("mo_hinh") or MO_HINH_MAC_DINH)


def _an(chu: str, khoa: str | None) -> str:
    return chu.replace(khoa, "***") if khoa else chu


def ve(ch: CauHinh, prompt: str, kich_thuoc: str, timeout: float = 120, mo=urllib.request.urlopen) -> bytes:
    than = json.dumps({"model": ch.mo_hinh, "prompt": prompt, "size": kich_thuoc, "n": 1}).encode("utf-8")
    dau = {"Content-Type": "application/json"}
    if ch.khoa:
        dau["Authorization"] = f"Bearer {ch.khoa}"
    req = urllib.request.Request(f"{ch.url}/images/generations", data=than, headers=dau)
    try:
        with mo(req, timeout=timeout) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as exc:
        chu = exc.read()[:500].decode("utf-8", "replace")
        if exc.code == 401:
            raise VeError("cau-hinh", _an(f"Nguồn vẽ từ chối khoá (401): {chu}", ch.khoa), FIX_KHOA) from None
        raise VeError("nha-cung-cap", _an(f"Nguồn vẽ báo lỗi {exc.code}: {chu}", ch.khoa), FIX_NCC,
                      thu_lai=exc.code >= 500) from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise VeError("mang", _an(f"Không gọi được {ch.url}: {exc}", ch.khoa), FIX_MANG, thu_lai=True) from None
    try:
        muc = data["data"][0]
    except (KeyError, IndexError, TypeError):
        raise VeError("nha-cung-cap", _an(f"Nguồn vẽ không trả ảnh: {str(data)[:300]}", ch.khoa), FIX_NCC) from None
    if muc.get("b64_json"):
        return base64.b64decode(muc["b64_json"])
    if muc.get("url"):
        try:
            with mo(urllib.request.Request(muc["url"]), timeout=timeout) as r:
                return r.read()
        except (urllib.error.URLError, OSError) as exc:
            raise VeError("mang", f"Không tải được ảnh từ địa chỉ nguồn vẽ trả về: {exc}", FIX_MANG) from None
    raise VeError("nha-cung-cap", "Nguồn vẽ trả kết quả không có ảnh.", FIX_NCC)
