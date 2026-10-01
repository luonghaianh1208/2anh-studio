"""Biểu tượng nét tabler-outline: chuẩn tên, đọc phần tử vẽ, gợi ý khi sai. Chỉ dùng thư viện chuẩn."""

from __future__ import annotations

import difflib
import re
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

THU_MUC = Path(__file__).resolve().parents[3] / "skills" / "ppt-master" / "templates" / "icons" / "tabler-outline"
# Bảng tra khái niệm tiếng Việt -> tên biểu tượng: một nguồn duy nhất, đọc thẳng từ tài liệu cho AI.
BANG_TRA = Path(__file__).resolve().parents[3] / "docs" / "vi" / "tham-khao" / "canh-video.md"
BANG_TRA_TEN = "docs/vi/tham-khao/canh-video.md"

NHAN_TOI_DA = 30
_TIEN_TO = "tabler-outline/"
_DUOI = ".svg"
_KHUNG_D = "M0 0h24v24H0z"
_TE_HINH = ("path", "circle", "rect", "line", "polyline", "polygon", "ellipse")
_SVG_NS = "{http://www.w3.org/2000/svg}"
_SO_GOI_Y = 5
_NGUONG_GOI_Y = 0.5
_MARKUP_RE = re.compile(r"\*\*|~|\^")
_DONG_BANG_RE = re.compile(r"^\| ([^|]+?) \| ([^|]+?) \| `([^`]+)` \|$", re.M)
_NGUONG_VIET = 0.75


class HinhError(Exception):
    """Tên biểu tượng không có trong thư viện, hoặc dòng `hinh` sai định dạng `tên | nhãn`."""


def chuan_ten(s: str) -> str:
    ten = s.strip()
    if ten.lower().startswith(_TIEN_TO):
        ten = ten[len(_TIEN_TO):]
    if ten.lower().endswith(_DUOI):
        ten = ten[: -len(_DUOI)]
    return ten.strip().lower()


def _danh_sach() -> list:
    """Tên để gợi ý theo tiếng Anh; bỏ biểu tượng thương hiệu `brand-*` (không bao giờ là hình bài học)."""
    return sorted(p.stem for p in THU_MUC.glob("*.svg") if not p.stem.startswith("brand-"))


def _bo_dau(s: str) -> str:
    s = s.replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def _khoa(s: str) -> str:
    return " ".join(_bo_dau(s).lower().replace("-", " ").split())


def bang_tra() -> list:
    """Các dòng (khái niệm, tên) của mục "Bảng tra biểu tượng" trong canh-video.md; thiếu file thì rỗng."""
    try:
        van_ban = BANG_TRA.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    phan = van_ban.split("## Bảng tra biểu tượng", 1)
    if len(phan) < 2:
        return []
    return [(khai_niem.strip(), ten.strip()) for _mon, khai_niem, ten in _DONG_BANG_RE.findall(phan[1])]


def _goi_y_viet(ten: str) -> list:
    """Khớp tên (bỏ dấu) với cột khái niệm tiếng Việt: trùng hẳn, rồi chứa nhau, rồi gần giống, rồi chung một từ."""
    khoa = _khoa(ten)
    if not khoa:
        return []
    tu = {t for t in khoa.split() if len(t) >= 3}
    dau = khoa.split()[0]
    bac: dict = {}
    for thu_tu, (khai_niem, ten_hinh) in enumerate(bang_tra()):
        for cum in (_khoa(c) for c in khai_niem.split(",")):
            if not cum:
                continue
            if cum == khoa:
                b = 0
            elif khoa in cum or cum in khoa:
                b = 1
            elif difflib.SequenceMatcher(None, khoa, cum).ratio() >= _NGUONG_VIET:
                b = 2
            elif tu & set(cum.split()):
                b = 3 if dau in cum.split() else 4  # chung từ đầu (danh từ chính) xếp trước
            else:
                continue
            bac[ten_hinh] = min(bac.get(ten_hinh, (9, 0)), (b, thu_tu))
    return sorted(bac, key=lambda t: bac[t])


def goi_y(ten: str) -> list:
    """Tối đa 5 tên: theo bảng tra tiếng Việt trước, rồi tên tiếng Anh gần đúng (không có `brand-*`)."""
    viet = [t for t in _goi_y_viet(ten) if not t.startswith("brand-")]
    anh = difflib.get_close_matches(_bo_dau(chuan_ten(ten)), _danh_sach(), n=_SO_GOI_Y, cutoff=_NGUONG_GOI_Y)
    # Tên một từ không dấu thường là tên tiếng Anh gõ sai: xếp gợi ý tiếng Anh trước.
    mot_tu_khong_dau = ten.strip().isascii() and not any(c in ten for c in " -_")
    kq = []
    for t in (anh + viet if mot_tu_khong_dau else viet + anh):
        if t not in kq:
            kq.append(t)
    return kq[:_SO_GOI_Y]


def _hop_le(chuan: str) -> bool:
    if not chuan or ".." in chuan or "/" in chuan or "\\" in chuan:
        return False
    if re.match(r"^[a-zA-Z]:", chuan):
        return False
    return True


def tach_minh_hoa(value: str) -> tuple:
    if "|" not in value:
        raise HinhError(f"dòng `hinh` phải có dạng `tên | nhãn`; thiếu dấu `|` trong `{value}`")
    ten, nhan = value.split("|", 1)
    ten, nhan = ten.strip(), nhan.strip()
    if not nhan:
        raise HinhError(f"dòng `hinh` phải có dạng `tên | nhãn`; thiếu nhãn trong `{value}`")
    so_ky_tu = len(_MARKUP_RE.sub("", nhan))
    if so_ky_tu > NHAN_TOI_DA:
        raise HinhError(f"nhãn hình `{nhan}` dài {so_ky_tu} ký tự, tối đa {NHAN_TOI_DA}")
    return ten, nhan


def doc(ten: str) -> dict:
    chuan = chuan_ten(ten)
    thong_bao_sai = f"`{ten}` không hợp lệ: `hinh` chỉ được là tên biểu tượng tabler-outline, không phải đường dẫn."
    if not _hop_le(chuan):
        raise HinhError(thong_bao_sai)
    goc = THU_MUC.resolve()
    duong_dan = (THU_MUC / f"{chuan}.svg").resolve()
    if not duong_dan.is_relative_to(goc):
        raise HinhError(thong_bao_sai)
    if not duong_dan.is_file():
        cac_goi_y = goi_y(ten)
        thong_bao = (f"không có biểu tượng `{ten}` trong thư viện tabler-outline. Tên biểu tượng là tiếng Anh: tra mục "
                     f"\"Bảng tra biểu tượng\" trong {BANG_TRA_TEN}")
        if cac_goi_y:
            thong_bao += ". Có thể bạn muốn: " + ", ".join(cac_goi_y)
        raise HinhError(thong_bao)
    root = ET.fromstring(duong_dan.read_text(encoding="utf-8"))
    phan_tu = []
    for el in root:
        the = el.tag.removeprefix(_SVG_NS)
        if the not in _TE_HINH:
            continue
        thuoc_tinh = dict(el.attrib)
        if thuoc_tinh.get("stroke") == "none":
            continue
        if the == "path" and thuoc_tinh.get("d") == _KHUNG_D:
            continue
        phan_tu.append({"the": the, "thuocTinh": thuoc_tinh})
    return {"ten": chuan, "viewBox": root.attrib.get("viewBox", "0 0 24 24"), "phanTu": phan_tu}
