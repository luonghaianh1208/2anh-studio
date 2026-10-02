# tools/vi/anh_vox_parts/nguon_ve.py
"""Gọi API tạo ảnh kiểu OpenAI (9router mặc định). Khoá không bao giờ đi vào thông báo lỗi."""

from __future__ import annotations

import base64
import binascii
import json
import os
import threading
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

URL_MAC_DINH = "http://localhost:20128/v1"
MO_HINH_MAC_DINH = "ag/gemini-3.1-flash-image"
FIX_KHOA = ("Đặt khoá API của 9router: `setx ANH_AI_KEY \"<khoá>\"` (lấy ở trang quản trị 9router) rồi mở lại cửa sổ "
            "lệnh; hoặc dùng `anh: tim:` (ảnh thật), hoặc thay ảnh bằng `chu`, `the`.")
FIX_MANG = "Kiểm tra 9router đang chạy (`9router` mở ở cổng 20128) hoặc địa chỉ `ANH_AI_URL`, rồi chạy lại."
HAN_CHOT = 180   # giây, hạn tổng của một lần vẽ (kể cả tải ảnh `url`)
KHONG_PHAI_ANH ="Nguồn vẽ trả dữ liệu không phải ảnh."
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
        if not isinstance(tep, dict) or any(k in tep and not isinstance(tep[k], str) for k in ("url", "khoa", "mo_hinh")):
            raise VeError("cau-hinh", f"File cấu hình {f} sai dạng: cần một đối tượng JSON, `url`, `khoa`, `mo_hinh` "
                                      "đều là chuỗi.", "Sửa hoặc xoá file đó rồi chạy lại.")
    khoa_tho = env.get("ANH_AI_KEY") or tep.get("khoa")
    khoa = None
    if khoa_tho:
        khoa_sach = khoa_tho.strip()
        if khoa_sach != khoa_tho or any(not c.isprintable() for c in khoa_sach):
            raise VeError("cau-hinh", "Khoá API (ANH_AI_KEY hoặc anh-ai.json) có ký tự xuống dòng hoặc ký tự lạ.",
                          FIX_KHOA)
        khoa = khoa_sach or None
    return CauHinh(url=(env.get("ANH_AI_URL") or tep.get("url") or URL_MAC_DINH).rstrip("/"),
                   khoa=khoa,
                   mo_hinh=env.get("ANH_AI_MO_HINH") or tep.get("mo_hinh") or MO_HINH_MAC_DINH)


def _an(chu: str, khoa: str | None) -> str:
    return chu.replace(khoa, "***") if khoa else chu


def _trich(data, khoa: str | None) -> str:
    """Đoạn ngắn của câu trả lời để đưa vào thông báo: bỏ mọi chuỗi ảnh base64, che khoá, tối đa 300 ký tự."""
    def bo_anh(x):
        if isinstance(x, dict):
            return {k: ("…" if k == "b64_json" and v else bo_anh(v)) for k, v in x.items()}
        if isinstance(x, list):
            return [bo_anh(v) for v in x]
        return x
    return _an(json.dumps(bo_anh(data), ensure_ascii=False), khoa)[:300]


def ve(ch: CauHinh, prompt: str, kich_thuoc: str, timeout: float = 120, mo=urllib.request.urlopen) -> bytes:
    """Vẽ một ảnh, có hạn tổng `HAN_CHOT` giây: `timeout` của urllib chỉ tính từng lần đọc socket, nên máy chủ giữ kết
    nối mà nhỏ giọt dữ liệu thì không bao giờ hết giờ. Yêu cầu chạy ở luồng nền (daemon); quá hạn thì bỏ luồng đó và
    báo lỗi `mang` tạm thời (anh_vox thử lại)."""
    han = HAN_CHOT
    kq: dict = {}

    def chay():
        try:
            kq["anh"] = _ve(ch, prompt, kich_thuoc, timeout, mo)
        except BaseException as exc:  # noqa: BLE001 — chuyển nguyên lỗi về luồng gọi
            kq["loi"] = exc

    luong = threading.Thread(target=chay, name="ve-anh", daemon=True)
    luong.start()
    luong.join(han)
    if luong.is_alive():
        raise VeError("mang", f"Nguồn vẽ không trả ảnh sau {han:g} giây.", FIX_MANG, thu_lai=True)
    if "loi" in kq:
        raise kq["loi"]
    return kq["anh"]


def _ve(ch: CauHinh, prompt: str, kich_thuoc: str, timeout: float, mo) -> bytes:
    than = json.dumps({"model": ch.mo_hinh, "prompt": prompt, "size": kich_thuoc, "n": 1}).encode("utf-8")
    dau = {"Content-Type": "application/json"}
    if ch.khoa:
        dau["Authorization"] = f"Bearer {ch.khoa}"
    req = urllib.request.Request(f"{ch.url}/images/generations", data=than, headers=dau)
    try:
        with mo(req, timeout=timeout) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as exc:
        chu = _an(exc.read().decode("utf-8", "replace"), ch.khoa)[:500]
        if exc.code == 401:
            raise VeError("cau-hinh", f"Nguồn vẽ từ chối khoá (401): {chu}", FIX_KHOA) from None
        raise VeError("nha-cung-cap", f"Nguồn vẽ báo lỗi {exc.code}: {chu}", FIX_NCC,
                      thu_lai=exc.code >= 500) from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise VeError("mang", _an(f"Không gọi được {ch.url}: {exc}", ch.khoa), FIX_MANG, thu_lai=True) from None
    try:
        muc = data["data"][0]
    except (KeyError, IndexError, TypeError):
        raise VeError("nha-cung-cap", f"Nguồn vẽ không trả ảnh: {_trich(data, ch.khoa)}", FIX_NCC) from None
    if not isinstance(muc, dict):
        muc = {}
    if muc.get("b64_json"):
        try:
            return base64.b64decode(muc["b64_json"])
        except (binascii.Error, ValueError, TypeError):
            raise VeError("nha-cung-cap", KHONG_PHAI_ANH, FIX_NCC) from None
    if muc.get("url"):
        try:
            with mo(urllib.request.Request(muc["url"]), timeout=timeout) as r:
                return r.read()
        except (urllib.error.URLError, OSError) as exc:
            raise VeError("mang", f"Không tải được ảnh từ địa chỉ nguồn vẽ trả về: {exc}", FIX_MANG) from None
    # Nguồn vẽ thỉnh thoảng trả 200 mà không có ảnh (gặp thật với 9router): coi là lỗi tạm, thử lại.
    raise VeError("nha-cung-cap", f"Nguồn vẽ trả kết quả không có ảnh: {_trich(data, ch.khoa)}", FIX_NCC, thu_lai=True)
