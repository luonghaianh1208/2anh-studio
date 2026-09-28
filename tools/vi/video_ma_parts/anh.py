"""Ảnh thật trong anh/: đọc kích thước, nhúng data:, dựng dòng nguồn. Chỉ dùng thư viện chuẩn."""

from __future__ import annotations

import base64
import json
import re
import struct
import unicodedata
from pathlib import Path

DINH_DANG = (".jpg", ".jpeg", ".png", ".webp")
TOI_DA = 8 * 1024 * 1024
_MIME = {".jpg": "jpeg", ".jpeg": "jpeg", ".png": "png", ".webp": "webp"}
_SOF_MARKERS = (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF)
_URL_RE = re.compile(r"(?:https?://|www\.)[^\s)\]]*", re.IGNORECASE)
_NGOAC_RONG_RE = re.compile(r"\(\s*\)|\[\s*\]")


class AnhError(Exception):
    """Ảnh trong anh/ không đọc được, sai định dạng, quá lớn, hoặc chưa có nguồn."""


class NguonAiError(AnhError):
    """Ảnh AI chưa có (hoặc có sai) bản ghi nguồn trong anh/ai/nguon.json."""


AI = "ai/"
DONG_AI = "Hình minh hoạ tạo bằng AI ({})"
FIX_NGUON_AI = "chạy `python tools/vi/anh_ai.py <thư_mục> nhan`"


def _hop_le(ten_file: str) -> bool:
    """Tên file trần trong anh/, hoặc đúng một tiền tố `ai/` (ảnh AI vẽ, anh/ai/) trước tên file trần."""
    if ten_file.startswith(AI):
        ten_file = ten_file[len(AI):]
    if not ten_file or ".." in ten_file or "/" in ten_file or "\\" in ten_file:
        return False
    if re.match(r"^[a-zA-Z]:", ten_file):
        return False
    return True


def co_alpha(du_lieu: bytes, duoi: str) -> bool:
    """Ảnh có kênh trong suốt: PNG kiểu màu 4/6 (xám/RGB + alpha) hoặc có khối tRNS; WEBP VP8X cờ alpha hoặc VP8L.
    JPEG không bao giờ có."""
    if duoi == ".png":
        if len(du_lieu) < 26:
            return False
        if du_lieu[25] in (4, 6):
            return True
        i = 8
        while i + 8 <= len(du_lieu):
            dai, tag = struct.unpack(">I4s", du_lieu[i:i + 8])
            if tag == b"tRNS":
                return True
            if tag in (b"IDAT", b"IEND"):
                return False
            i += 12 + dai
        return False
    if duoi == ".webp":
        fourcc = du_lieu[12:16]
        return fourcc == b"VP8L" or (fourcc == b"VP8X" and len(du_lieu) > 20 and bool(du_lieu[20] & 0x10))
    return False


def _nguon_ai(thu_muc_du_an: Path, ten: str) -> dict:
    """Bản ghi của `ten` (tên trần trong anh/ai/) trong anh/ai/nguon.json (anh_ai.py ghi:
    [{file, cong_cu, mo_hinh, prompt, ngay, mo_ta?, canh?}]); thiếu file, thiếu bản ghi hay thiếu mô hình là AnhError.
    `moTa`, `canh`: mô tả đã vẽ và (nền) số cảnh vẽ cho; bản ghi cũ không có thì None."""
    manifest = Path(thu_muc_du_an) / "anh" / "ai" / "nguon.json"
    thieu = f"`anh/ai/{ten}` chưa có nguồn trong `anh/ai/nguon.json`: {FIX_NGUON_AI}"
    if not manifest.is_file():
        raise NguonAiError(thieu)
    try:
        du_lieu = json.loads(manifest.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise NguonAiError(f"không đọc được `anh/ai/nguon.json` ({exc}): {FIX_NGUON_AI}") from exc
    if not isinstance(du_lieu, list) or not all(isinstance(m, dict) for m in du_lieu):
        raise NguonAiError(f"`anh/ai/nguon.json` sai cấu trúc: cần danh sách [{{\"file\": ..., \"mo_hinh\": ...}}]; {FIX_NGUON_AI}")
    for muc in du_lieu:
        if unicodedata.normalize("NFC", str(muc.get("file", ""))) == unicodedata.normalize("NFC", ten):
            mo_hinh = _bo_dia_chi_web(muc.get("mo_hinh"))
            if not mo_hinh:
                raise NguonAiError(f"`anh/ai/nguon.json` thiếu `mo_hinh` của `{ten}`: {FIX_NGUON_AI}")
            mo_ta = muc.get("mo_ta")
            return {"moHinh": mo_hinh, "congCu": _bo_dia_chi_web(muc.get("cong_cu")),
                    "moTa": mo_ta if isinstance(mo_ta, str) else None,
                    "canh": muc.get("canh") if isinstance(muc.get("canh"), int) else None}
    raise NguonAiError(thieu)


def _kich_thuoc_png(du_lieu: bytes) -> tuple:
    rong, cao = struct.unpack(">II", du_lieu[16:24])
    return rong, cao


def _huong_exif(doan: bytes) -> int:
    """Thẻ Orientation (0x0112) trong IFD0 của một đoạn APP1 Exif; 1 khi không có hoặc hỏng."""
    if not doan.startswith(b"Exif\x00\x00") or len(doan) < 14:
        return 1
    tiff = doan[6:]
    thu_tu = {b"II": "<", b"MM": ">"}.get(tiff[:2])
    if thu_tu is None:
        return 1
    try:
        ifd = struct.unpack(thu_tu + "I", tiff[4:8])[0]
        so_the = struct.unpack(thu_tu + "H", tiff[ifd:ifd + 2])[0]
        for k in range(so_the):
            o = ifd + 2 + 12 * k
            the, kieu = struct.unpack(thu_tu + "HH", tiff[o:o + 4])
            if the == 0x0112 and kieu == 3:
                return struct.unpack(thu_tu + "H", tiff[o + 8:o + 10])[0]
    except struct.error:
        return 1
    return 1


def _kich_thuoc_jpeg(du_lieu: bytes) -> tuple:
    """Kích thước hiển thị: đổi rộng/cao khi thẻ Exif Orientation là 5–8 (Chromium xoay ảnh theo thẻ này)."""
    huong = 1
    i = 2
    n = len(du_lieu)
    while i + 3 < n:
        if du_lieu[i] != 0xFF:
            i += 1
            continue
        marker = du_lieu[i + 1]
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        if marker == 0xD9:
            break
        do_dai = struct.unpack(">H", du_lieu[i + 2:i + 4])[0]
        if marker == 0xE1 and huong == 1:
            huong = _huong_exif(du_lieu[i + 4:i + 2 + do_dai])
        if marker in _SOF_MARKERS:
            cao, rong = struct.unpack(">HH", du_lieu[i + 5:i + 9])
            return (cao, rong) if 5 <= huong <= 8 else (rong, cao)
        i += 2 + do_dai
    raise struct.error("không thấy đoạn SOF")


def _kich_thuoc_webp(du_lieu: bytes) -> tuple:
    fourcc = du_lieu[12:16]
    if fourcc == b"VP8X":
        rong = int.from_bytes(du_lieu[24:27], "little") + 1
        cao = int.from_bytes(du_lieu[27:30], "little") + 1
        return rong, cao
    if fourcc == b"VP8L":
        bits = int.from_bytes(du_lieu[21:25], "little")
        rong = (bits & 0x3FFF) + 1
        cao = ((bits >> 14) & 0x3FFF) + 1
        return rong, cao
    if fourcc == b"VP8 ":
        rong = struct.unpack("<H", du_lieu[26:28])[0] & 0x3FFF
        cao = struct.unpack("<H", du_lieu[28:30])[0] & 0x3FFF
        return rong, cao
    raise struct.error(f"khối WEBP lạ: {fourcc!r}")


def _kich_thuoc(duoi: str, du_lieu: bytes, ten_file: str) -> tuple:
    try:
        if duoi == ".png":
            return _kich_thuoc_png(du_lieu)
        if duoi in (".jpg", ".jpeg"):
            return _kich_thuoc_jpeg(du_lieu)
        return _kich_thuoc_webp(du_lieu)
    except (struct.error, IndexError) as exc:
        raise AnhError(f"không đọc được kích thước `anh/{ten_file}` (file hỏng?)") from exc


def _bo_dia_chi_web(chu) -> str:
    chu = _NGOAC_RONG_RE.sub("", _URL_RE.sub("", str(chu or "")))
    return " ".join(chu.split()).strip(" -–·,;:/")


def _nguon_tu_manifest(thu_muc_du_an: Path, ten_file: str) -> str:
    manifest = Path(thu_muc_du_an) / "anh" / "image_sources.json"
    if not manifest.is_file():
        return ""
    sai = '`anh/image_sources.json` sai cấu trúc: cần dạng {"items": [{"filename": ..., "author": ..., ...}]}'
    try:
        du_lieu = json.loads(manifest.read_text(encoding="utf-8-sig"))
    except OSError as exc:
        raise AnhError(f"không đọc được `anh/image_sources.json`: {exc}") from exc
    except ValueError as exc:
        raise AnhError(f"`anh/image_sources.json` không phải JSON hợp lệ ({exc})") from exc
    if not isinstance(du_lieu, dict) or not isinstance(du_lieu.get("items", []), list):
        raise AnhError(sai)
    cac_muc = du_lieu.get("items", [])
    if not all(isinstance(muc, dict) for muc in cac_muc):
        raise AnhError(sai + "; mỗi phần tử của `items` phải là một bản ghi {...}")
    for muc in cac_muc:
        if muc.get("filename") == ten_file:
            phan = [muc.get("author"), muc.get("license_name") or muc.get("license"), muc.get("provider")]
            phan = [p for p in (_bo_dia_chi_web(p) for p in phan) if p]
            if not phan:
                return ""
            return "Ảnh: " + " · ".join(phan)
    return ""


def _tim_theo_nfc(thu_muc_anh: Path, ten_file: str):
    """Tên có dấu có thể được lưu dạng NFD (chép từ máy Mac) trong khi video.md viết dạng NFC, hoặc ngược lại."""
    muon = unicodedata.normalize("NFC", ten_file)
    if not thu_muc_anh.is_dir():
        return None
    for p in thu_muc_anh.iterdir():
        if p.is_file() and unicodedata.normalize("NFC", p.name) == muon:
            return p
    return None


def doc(thu_muc_du_an: Path, ten_file: str, nguon_tay: str | None) -> dict:
    """Ảnh `anh/<ten_file>` nhúng data:. `ai/<file>`: ảnh AI vẽ trong anh/ai/, nguồn luôn lấy từ anh/ai/nguon.json
    (bỏ qua `nguon_tay`); kết quả có thêm `ai`, `moHinh`, `alpha` (có kênh trong suốt), `moTa` và `canhVe` (mô tả đã
    vẽ, số cảnh vẽ cho; None khi bản ghi không có)."""
    if not _hop_le(ten_file):
        raise AnhError(f"`{ten_file}` không hợp lệ: `anh` chỉ được là tên file nằm trong `anh/`, không phải đường dẫn.")
    la_ai = ten_file.startswith(AI)
    duoi = Path(ten_file).suffix.lower()
    if duoi not in DINH_DANG:
        raise AnhError(f"`{ten_file}` không phải định dạng ảnh cho phép ({', '.join(DINH_DANG)})")
    thu_muc_anh = (Path(thu_muc_du_an) / "anh" / ("ai" if la_ai else "")).resolve()
    ten = ten_file[len(AI):] if la_ai else ten_file
    duong_dan = (thu_muc_anh / ten).resolve()
    if not duong_dan.is_relative_to(thu_muc_anh):
        raise AnhError(f"`{ten_file}` không hợp lệ: `anh` chỉ được là tên file nằm trong `anh/`, không phải đường dẫn.")
    if not duong_dan.is_file():
        duong_dan = _tim_theo_nfc(thu_muc_anh, ten) or duong_dan
    if not duong_dan.is_file():
        raise AnhError(f"không có file `anh/{ten_file}`")
    kich_thuoc_byte = duong_dan.stat().st_size
    if kich_thuoc_byte > TOI_DA:
        raise AnhError(f"`anh/{ten_file}` nặng {kich_thuoc_byte} byte, tối đa {TOI_DA}")
    du_lieu = duong_dan.read_bytes()
    rong, cao = _kich_thuoc(duoi, du_lieu, ten_file)
    data_url = f"data:image/{_MIME[duoi]};base64," + base64.b64encode(du_lieu).decode("ascii")
    if la_ai:
        ai = _nguon_ai(thu_muc_du_an, ten)
        return {"dataUrl": data_url, "nguon": DONG_AI.format(ai["moHinh"]), "rong": rong, "cao": cao, "ai": True,
                "moHinh": ai["moHinh"], "alpha": co_alpha(du_lieu, duoi), "moTa": ai["moTa"], "canhVe": ai["canh"]}
    nguon = nguon_tay.strip() if nguon_tay else _nguon_tu_manifest(thu_muc_du_an, ten_file)
    if not nguon:
        raise AnhError(f"`anh/{ten_file}` chưa có nguồn: ghi `nguon:` trong cảnh, hoặc thêm bản ghi cho "
                        f"`{ten_file}` vào `anh/image_sources.json`")
    return {"dataUrl": data_url, "nguon": nguon, "rong": rong, "cao": cao}
