# tools/vi/video_ma_parts/vox.py
"""Cảnh kiểu Vox: nhịp gắn cụm từ trong lời, bố cục và ô. Ngữ pháp ở docs/vi/tro-ly/nhip-vox.md."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

# Khoá đầu chỉ có ở Vox; giá trị đầu tiên là mặc định.
VOX_META_CHOICES = {
    "phong-anh": ("chup-that", "minh-hoa"),
    "bang-mau": ("kem", "bao-cu", "dem", "tuoi"),
    "chuyen-canh": ("xen-ke", "xe-giay", "lia", "khong"),
}
# Khoá đầu của kiểu viết tay, không dùng ở Vox.
VOX_CAM = ("ban-tay", "nhan-vat", "mau-ao", "chu-dong", "may-quay")
CHUYEN_CANH = ("xe-giay", "lia", "khong")
THOI_LUONG = (15, 600)
NHIP_TOI_DA = 6
CHU_TOI_DA = 2
CHONG_TOI_DA = 5
NGUON_DAI = 90
# bố cục -> {khổ: các ô}; `None` (không ghi ô) được phép với mọi bố cục.
BO_CUC = {
    "mot": {"ngang": ("giua", "tren", "duoi"), "doc": ("giua", "tren", "duoi")},
    "hai-ben": {"ngang": ("trai", "phai", "giua"), "doc": ("tren", "duoi", "giua")},
    "dan-hang": {"ngang": ("1", "2", "3", "4"), "doc": ("1", "2", "3", "4")},
    "chong": {"ngang": (), "doc": ()},
    "toan-canh": {"ngang": ("nen", "giua", "duoi"), "doc": ("nen", "giua", "duoi")},
}
# vật -> giới hạn ký tự hiện (None: không đếm)
VAT = {"anh": None, "the": None, "chu": 40, "nhan": 30, "dau": 16, "mui-ten": None, "so": 24}
GIOI_HAN_THE = (24, 16, 60)
ANH_MO_TA = 300
TUY_CHON = ("khung", "duotone", "halftone", "xa", "gan")
_SO_RE = re.compile(r"\{\{(-?\d+(?:\.\d+)?)\}\}")
_NHAN_RE = re.compile(r"==|\(\(|\)\)|__")


@dataclass
class Nhip:
    cum: str
    vat: str
    noi_dung: str
    o: str | None
    tuy_chon: tuple
    dong: int
    chi_so: int


def khoa_tu(text: str) -> list:
    """Từ đã chuẩn hoá để so cụm với lời: NFC, chữ thường, bỏ dấu câu (giữ dấu thanh) — như lich.khoa_so_khop."""
    s = unicodedata.normalize("NFC", text).lower()
    return re.sub(r"[^\w\s]", " ", s).split()


def tim_cum(tokens: list, cum: str, tu_vi_tri: int) -> int:
    can = khoa_tu(cum)
    if not can:
        return -1
    for i in range(max(tu_vi_tri, 0), len(tokens) - len(can) + 1):
        if tokens[i:i + len(can)] == can:
            return i
    return -1


def hien(chu: str) -> str:
    """Chữ hiện ra: bỏ dấu nhấn, số chạy hiện bằng con số."""
    return _SO_RE.sub(lambda m: m.group(1).replace(".", ","), _NHAN_RE.sub("", chu))


def _loi(no: int, message: str):
    from .parse import ParseError  # tránh vòng import
    return ParseError(no, message)


def doc_nhip(value: str, no: int, chi_so: int) -> Nhip:
    phan = [p.strip() for p in value.split(" | ")]
    if len(phan) < 2 or not phan[0]:
        raise _loi(no, "`nhip` phải có dạng `<cụm từ trong lời> | <vật>: <nội dung> | <ô> | <tuỳ chọn>`, "
                       "ví dụ `nhip: để mai tính | anh: ve: nhân viên nhún vai | trai`.")
    cum, vat_noi = phan[0], phan[1]
    m = re.match(r"^([a-z-]+):\s*(.*)$", vat_noi)
    if m is None or m.group(1) not in VAT:
        raise _loi(no, f"Vật của nhịp phải là một trong: {', '.join(VAT)} (dạng `vat: nội dung`).")
    vat, noi_dung = m.group(1), m.group(2).strip()
    # Với `the`, chính nội dung chứa " | ": gộp lại 3 phần sau vật.
    du = phan[2:]
    if vat == "the":
        the = [noi_dung] + du
        cat = 3 if len(the) >= 3 and the[2] not in TUY_CHON and not _la_o(the[2]) else 2
        noi_dung, du = " | ".join(the[:cat]), the[cat:]
    o = du[0] if du and du[0] and not set(du[0].split()) <= set(TUY_CHON) else None
    tuy = tuple((du[1] if o is not None and len(du) > 1 else (du[0] if o is None and du else "")).split())
    for t in tuy:
        if t not in TUY_CHON:
            raise _loi(no, f"Tuỳ chọn `{t}` không có; tuỳ chọn của nhịp: {', '.join(TUY_CHON)}.")
    _kiem_noi_dung(vat, noi_dung, no)
    return Nhip(cum=cum, vat=vat, noi_dung=noi_dung, o=o, tuy_chon=tuy, dong=no, chi_so=chi_so)


def _la_o(chu: str) -> bool:
    return any(chu in o for b in BO_CUC.values() for o in b.values())


def _kiem_noi_dung(vat: str, nd: str, no: int) -> None:
    if not nd:
        raise _loi(no, f"Nhịp `{vat}` chưa có nội dung.")
    if vat == "anh":
        if nd.startswith("ve:"):
            mo_ta = nd[3:].strip()
            if not mo_ta or len(mo_ta) > ANH_MO_TA:
                raise _loi(no, f"`anh: ve:` cần mô tả từ 1 đến {ANH_MO_TA} ký tự.")
        elif nd.startswith("tim:"):
            if not nd[4:].strip():
                raise _loi(no, "`anh: tim:` cần từ khoá tiếng Anh để tìm ảnh thật.")
        elif not nd.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            raise _loi(no, "`anh` là `ve: <mô tả>`, `tim: <từ khoá tiếng Anh>` hoặc tên file ảnh trong `anh/`.")
        return
    if vat == "the":
        p = [x.strip() for x in nd.split(" | ")]
        if len(p) not in (2, 3) or not p[0] or not p[1]:
            raise _loi(no, "`the` phải có dạng `<nhãn> | <giá trị> | <chú thích>` (chú thích bỏ trống được).")
        for chu, toi_da, ten in zip(p, GIOI_HAN_THE, ("nhãn", "giá trị", "chú thích")):
            if len(hien(chu)) > toi_da:
                raise _loi(no, f"{ten} của `the` dài {len(hien(chu))} ký tự, tối đa {toi_da}.")
        return
    if vat == "mui-ten":
        if not re.match(r"^\S+\s*->\s*\S+$", nd):
            raise _loi(no, "`mui-ten` phải có dạng `<ô> -> <ô>`, ví dụ `trai -> phai`.")
        return
    if vat == "so" and not _SO_RE.search(nd):
        raise _loi(no, "`so` cần một số chạy `{{…}}`, ví dụ `{{85}}% người được hỏi`.")
    toi_da = VAT[vat]
    if toi_da is not None and len(hien(nd)) > toi_da:
        raise _loi(no, f"Chữ của `{vat}` dài {len(hien(nd))} ký tự, tối đa {toi_da}. Rút gọn chữ; ý dài để ở lời.")


def kiem_canh(scene, kho: str) -> None:
    """Kiểm nhịp của một cảnh Vox đã đọc (bố cục, ô, cụm từ, thứ tự). Raise ParseError."""
    bo_cuc = scene.truong["bo-cuc"][0]
    no_bc = scene.dong_truong["bo-cuc"][0]
    if bo_cuc not in BO_CUC:
        raise _loi(no_bc, f"`bo-cuc` phải là một trong: {', '.join(BO_CUC)}.")
    o_hop_le = BO_CUC[bo_cuc][kho]
    tokens = khoa_tu(scene.loi)
    vi_tri = 0
    so_chu = 0
    for n in scene.nhip:
        if n.o is not None:
            if bo_cuc == "chong":
                raise _loi(n.dong, "Bố cục `chong` tự xếp các vật; bỏ ô ở nhịp này.")
            if n.o not in o_hop_le:
                raise _loi(n.dong, f"Ô `{n.o}` không có ở bố cục `{bo_cuc}` khổ {kho}; ô đúng: {', '.join(o_hop_le)}.")
        if n.o == "nen" and n.vat != "anh":
            raise _loi(n.dong, "Ô `nen` chỉ dành cho ảnh phủ kín khung (`anh`).")
        if n.vat == "chu":
            so_chu += 1
            if so_chu > CHU_TOI_DA:
                raise _loi(n.dong, f"Mỗi cảnh tối đa {CHU_TOI_DA} dòng `chu`; ý còn lại để ở lời hoặc tách cảnh.")
        if n.cum == "@dau":
            continue
        i = tim_cum(tokens, n.cum, vi_tri)
        if i < 0:
            co_truoc = tim_cum(tokens, n.cum, 0) >= 0
            if co_truoc:
                raise _loi(n.dong, f"Cụm \"{n.cum}\" nằm trước cụm của nhịp trước trong lời; viết các nhịp theo đúng "
                                   "thứ tự lời đọc.")
            raise _loi(n.dong, f"Cụm \"{n.cum}\" không có trong lời của Cảnh {scene.so}: \"{scene.loi}\". "
                               "Chép đúng vài từ liền nhau trong lời.")
        vi_tri = i + len(khoa_tu(n.cum))
    if bo_cuc == "chong" and len(scene.nhip) > CHONG_TOI_DA:
        raise _loi(scene.nhip[CHONG_TOI_DA].dong, f"Bố cục `chong` tối đa {CHONG_TOI_DA} vật.")
