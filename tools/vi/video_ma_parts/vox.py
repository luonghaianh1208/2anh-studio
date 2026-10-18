# tools/vi/video_ma_parts/vox.py
"""Cảnh kiểu Vox: nhịp gắn cụm từ trong lời, bố cục và ô. Ngữ pháp ở docs/vi/tro-ly/nhip-vox.md."""

from __future__ import annotations

import base64
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

# Khoá đầu chỉ có ở Vox; giá trị đầu tiên là mặc định.
VOX_META_CHOICES = {
    # `cat-dan`: tranh cắt dán kiểu tạp chí cổ (mặc định, giống video mẫu Vox).
    # `ban-ve`: bản vẽ kỹ thuật nét trắng trên giấy xanh (Toán, Vật lí, Công nghệ); đi cùng `bang-mau: ban-ve`.
    "phong-anh": ("cat-dan", "chup-that", "minh-hoa", "ban-ve"),
    # Nền AI riêng cho từng cảnh (anh_vox.py); `khong`: nền giấy vẽ bằng mã (máy không có nguồn vẽ ảnh).
    "nen-canh": ("ve", "khong"),
    "bang-mau": ("kem", "bao-cu", "dem", "tuoi", "ban-ve"),
    "chuyen-canh": ("xen-ke", "xe-giay", "lia", "khong"),
}
# Khoá đầu tự do chỉ có ở Vox: nhân vật chính cố định, mô tả ≤ NHAN_VAT_CHINH_DAI ký tự; mô tả `ve:` gọi bằng `@nhan-vat`.
VOX_META_FREE = ("nhan-vat-chinh",)
NHAN_VAT_CHINH_DAI = 300
DAU_NHAN_VAT = "@nhan-vat"
# Khoá đầu của kiểu viết tay, không dùng ở Vox.
VOX_CAM = ("ban-tay", "nhan-vat", "mau-ao", "chu-dong", "may-quay")
CHUYEN_CANH = ("xe-giay", "lia", "khong")
# Chuyển cảnh xen kẽ (khoá đầu `chuyen-canh: xen-ke`, mặc định của Vox): cảnh chẵn/lẻ (kể từ Cảnh 2) luân phiên.
CHUYEN_XEN_KE = ("xe-giay", "lia")
THOI_LUONG = (10, 600)
# Giọng mặc định của Vox: "Thu Giang" (VieNeu); máy không có VieNeu thì video_ma lùi về giọng `nu` của edge-tts.
GIONG_MAC_DINH = "thu-giang"
# Vật đầu tiên của cảnh (không tính nền) phải hiện trong mấy từ đầu của lời, nếu không cảnh mở bằng nền trống.
MO_CANH_TU = 3
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
    # Dựng cảnh nhiều lớp (kiểu giấy cắt có chiều sâu): mỗi ảnh một vai, chữ ở `tren`/`giua`.
    "dung-canh": {"ngang": ("hau-canh", "chinh", "phu", "phu-2", "tien-canh", "tren", "giua"),
                  "doc": ("hau-canh", "chinh", "phu", "phu-2", "tien-canh", "tren", "giua")},
}
# Ô ảnh của `dung-canh` theo vai, xếp từ xa tới gần; ô chữ của nó.
VAI_DUNG_CANH = ("hau-canh", "phu-2", "phu", "chinh", "tien-canh")
O_CHU_DUNG_CANH = ("tren", "giua")
# vật -> giới hạn ký tự hiện (None: không đếm)
VAT = {"anh": None, "the": None, "chu": 40, "nhan": 30, "dau": 16, "mui-ten": None, "so": 24,
       "cot": None, "chu-trinh": None, "moc": None, "thap": None}
GIOI_HAN_THE = (24, 16, 60)
ANH_MO_TA = 300
# `dung`: con dấu màu xanh (ĐÚNG), đối với con dấu đỏ mặc định (SAI) trong mạch "hiểu sai → hiểu đúng".
TUY_CHON = ("khung", "duotone", "halftone", "xa", "gan", "dung")
# Vật nhiều mục (các mục cách nhau bằng `;`): số mục (tối thiểu, tối đa) và giới hạn ký tự từng phần.
DANH_SACH = {"cot": (2, 5), "chu-trinh": (3, 6), "moc": (2, 5), "thap": (3, 5)}
COT_NHAN, COT_DON_VI = 14, 6
CHU_TRINH_BUOC = 16
MOC_MOC, MOC_NHAN = 10, 20
THAP_TANG = 24
# Nhịp im (`giu: <giây>` của cảnh): giữ hình đứng im sau lời để nhấn ý.
GIU = (0.5, 3.0)
_COT_RE = re.compile(r"^(.+?)\s*=\s*(-?\d+(?:[.,]\d+)?)\s*(.*)$")
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
    s = _NHAN_RE.sub(" ", s.replace("**", " "))   # dấu nhấn (`__` là ký tự chữ với \w) không thuộc cụm từ
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


def doc_nhip(value: str, no: int, chi_so: int, ngan: bool = False) -> Nhip:
    """`ngan`: nhịp của video ngắn — vật và tuỳ chọn theo ngan.py, nội dung vật mới kiểm ở ngan.kiem_canh."""
    from . import ngan as _ngan

    vat_hop_le = _ngan.VAT if ngan else VAT
    tuy_hop_le = TUY_CHON + _ngan.TUY_CHON if ngan else TUY_CHON
    phan = [p.strip() for p in value.split(" | ")]
    if len(phan) < 2 or not phan[0]:
        raise _loi(no, "`nhip` phải có dạng `<cụm từ trong lời> | <vật>: <nội dung> | <ô> | <tuỳ chọn>`, "
                       "ví dụ `nhip: để mai tính | anh: ve: nhân viên nhún vai | trai`.")
    cum, vat_noi = phan[0], phan[1]
    m = re.match(r"^([a-z-]+):\s*(.*)$", vat_noi)
    if m is None or m.group(1) not in vat_hop_le:
        raise _loi(no, f"Vật của nhịp phải là một trong: {', '.join(vat_hop_le)} (dạng `vat: nội dung`).")
    vat, noi_dung = m.group(1), m.group(2).strip()
    # Với `the`, chính nội dung chứa " | ": gộp lại 3 phần sau vật.
    du = phan[2:]
    if vat == "the":
        the = [noi_dung] + du
        cat = 3 if len(the) >= 3 and the[2] not in tuy_hop_le and not _la_o(the[2]) else 2
        noi_dung, du = " | ".join(the[:cat]), the[cat:]
    if ngan and vat in _ngan.VAT_MOI:
        # Nội dung các vật mới có ` | ` bên trong (thong-bao, truoc-sau, trich-dan…): tách ô/tuỳ chọn ở cuối (tối đa
        # hai phần), phần còn lại gộp về nội dung.
        duoi: list = []
        while du and len(duoi) < 2 and (du[-1] in _ngan.O or (du[-1] and set(du[-1].split()) <= set(tuy_hop_le))):
            duoi.insert(0, du.pop())
        if du:
            noi_dung = " | ".join([noi_dung] + du)
        du = duoi
    o = du[0] if du and du[0] and not set(du[0].split()) <= set(tuy_hop_le) else None
    if len(du) > (2 if o is not None else 1):
        raise _loi(no, "Tuỳ chọn viết chung một phần, cách nhau bằng khoảng trắng, ví dụ `| phai | khung duotone`.")
    tuy = tuple((du[1] if o is not None and len(du) > 1 else (du[0] if o is None and du else "")).split())
    for t in tuy:
        if t not in tuy_hop_le:
            raise _loi(no, f"Tuỳ chọn `{t}` không có; tuỳ chọn của nhịp: {', '.join(tuy_hop_le)}.")
    if not (ngan and vat in _ngan.VAT_MOI):
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
    if vat in DANH_SACH:
        tach_danh_sach(vat, nd, no)
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


def tach_danh_sach(vat: str, nd: str, no: int = 0) -> list:
    """Các mục của `cot`, `chu-trinh`, `moc`, `thap` (cách nhau bằng `;`); kiểm số mục và độ dài. Trả danh sách dict
    cho trang: cot {nhan, giaTri, thapPhan, donVi}; moc {moc, nhan}; chu-trinh và thap {nhan}."""
    muc = [x.strip() for x in nd.split(";")]
    it, nhieu = DANH_SACH[vat]
    if any(not x for x in muc) or not it <= len(muc) <= nhieu:
        mau = {"cot": "`cot: 2020 = 12; 2022 = 30; 2024 = 45%`", "chu-trinh": "`chu-trinh: Bốc hơi; Ngưng tụ; Mưa`",
               "moc": "`moc: 1945: Độc lập; 1975: Thống nhất`", "thap": "`thap: Tự thể hiện; Tôn trọng; An toàn`"}[vat]
        raise _loi(no, f"`{vat}` cần từ {it} đến {nhieu} mục cách nhau bằng `;`, ví dụ {mau}.")
    ra = []
    for x in muc:
        if vat == "cot":
            m = _COT_RE.match(x)
            if m is None:
                raise _loi(no, f"Mục `{x}` của `cot` phải có dạng `<nhãn> = <số><đơn vị>`, ví dụ `2024 = 45%`.")
            nhan, so, don_vi = m.group(1).strip(), m.group(2).replace(",", "."), m.group(3).strip()
            if len(nhan) > COT_NHAN or len(don_vi) > COT_DON_VI:
                raise _loi(no, f"Mục `{x}` của `cot`: nhãn tối đa {COT_NHAN} ký tự, đơn vị tối đa {COT_DON_VI}.")
            if float(so) < 0:
                raise _loi(no, f"Mục `{x}` của `cot`: cột không vẽ được số âm.")
            tp = len(so.split(".", 1)[1]) if "." in so else 0
            ra.append({"nhan": nhan, "giaTri": float(so), "thapPhan": tp, "donVi": don_vi})
        elif vat == "moc":
            moc, _, nhan = x.partition(":")
            moc, nhan = moc.strip(), nhan.strip()
            if not moc or not nhan or len(moc) > MOC_MOC or len(nhan) > MOC_NHAN:
                raise _loi(no, f"Mục `{x}` của `moc` phải có dạng `<mốc>: <nhãn>`, mốc tối đa {MOC_MOC} ký tự, "
                               f"nhãn tối đa {MOC_NHAN}.")
            ra.append({"moc": moc, "nhan": nhan})
        else:
            toi_da = CHU_TRINH_BUOC if vat == "chu-trinh" else THAP_TANG
            if len(x) > toi_da:
                raise _loi(no, f"Mục `{x}` của `{vat}` dài {len(x)} ký tự, tối đa {toi_da}.")
            ra.append({"nhan": x})
    return ra


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
        if n.vat == "mui-ten":
            if not o_hop_le:
                raise _loi(n.dong, f"Bố cục `{bo_cuc}` không có ô nên không dùng `mui-ten`; đổi bố cục hoặc bỏ nhịp này.")
            for dau_mui in (x.strip() for x in n.noi_dung.split("->")):
                if dau_mui not in o_hop_le:
                    raise _loi(n.dong, f"Đầu mũi tên `{dau_mui}` không phải ô của bố cục `{bo_cuc}` khổ {kho}; "
                                       f"ô đúng: {', '.join(o_hop_le)}.")
        if "dung" in n.tuy_chon and n.vat != "dau":
            raise _loi(n.dong, "Tuỳ chọn `dung` (dấu xanh) chỉ dùng cho `dau`.")
        if bo_cuc == "dung-canh":
            if n.o is None and n.vat != "mui-ten":
                raise _loi(n.dong, "Bố cục `dung-canh` cần ghi rõ ô của từng nhịp: ảnh ở `hau-canh`, `chinh`, `phu`, "
                                   "`phu-2`, `tien-canh`; chữ ở `tren` hoặc `giua`.")
            if n.vat == "mui-ten":
                raise _loi(n.dong, "Bố cục `dung-canh` không dùng `mui-ten`.")
            if n.vat == "anh" and n.o not in VAI_DUNG_CANH:
                raise _loi(n.dong, f"Ảnh của `dung-canh` đặt ở một vai: {', '.join(VAI_DUNG_CANH)}.")
            if n.vat != "anh" and n.o not in O_CHU_DUNG_CANH:
                raise _loi(n.dong, f"`{n.vat}` của `dung-canh` đặt ở `tren` hoặc `giua`; các ô vai chỉ dành cho ảnh.")
            if n.vat == "anh" and n.o != "hau-canh" and "khung" in n.tuy_chon:
                raise _loi(n.dong, "Nhân vật và tiền cảnh của `dung-canh` là ảnh cắt rời, không dùng `khung`.")
        if n.vat in DANH_SACH and bo_cuc == "chong":
            raise _loi(n.dong, f"`{n.vat}` cần một ô rộng; dùng bố cục `mot`, `hai-ben` hoặc `toan-canh`, không dùng `chong`.")
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
    if bo_cuc == "dung-canh":
        vai = [n.o for n in scene.nhip if n.vat == "anh"]
        trung = sorted({o for o in vai if vai.count(o) > 1})
        if trung:
            n0 = next(n for n in scene.nhip if n.vat == "anh" and n.o == trung[0])
            raise _loi(n0.dong, f"Vai `{trung[0]}` của `dung-canh` chỉ có một ảnh; thêm người thì dùng `phu-2`.")
        if "chinh" not in vai and "hau-canh" not in vai:
            raise _loi(scene.dong_truong["bo-cuc"][0], "Cảnh `dung-canh` cần ít nhất ảnh `hau-canh` hoặc nhân vật `chinh`.")
    if bo_cuc == "chong" and len(scene.nhip) > CHONG_TOI_DA:
        raise _loi(scene.nhip[CHONG_TOI_DA].dong, f"Bố cục `chong` tối đa {CHONG_TOI_DA} vật.")


def moc_nhip(nhips: list, moc_tu: list, dan_dau: float) -> list:
    """Mốc bắt đầu (giây trong cảnh) của từng nhịp, theo mốc từ (`lich.CanhLich.moc_tu`) của cụm từ nhịp đó khớp
    trong lời; `@dau` luôn ở `dan_dau`. Cụm không khớp được (giọng chưa có mốc từ, hay không khớp) nối tiếp nhịp
    trước, cách đúng 0,6 giây (không rải theo vị trí từ).

    `moc_tu[i]["khoa"]` (`lich.khoa_so_khop`) chỉ bỏ dấu câu, không tách từ ghép bằng dấu câu dính liền thành
    nhiều token (`"85,5%"`, `"chu-kì"` vẫn là một mục); cụm của nhịp (`vox.khoa_tu`) thì tách "," "-" "%"… thành
    khoảng trắng rồi `split()`. Để so đúng, khai triển từng mục `moc_tu` qua `khoa_tu` thành các token con (bỏ mục
    rỗng, ví dụ một dấu gạch ngang đứng riêng), giữ chỉ số từ nguồn để lấy lại đúng giờ `t` của mục đó."""
    khoa, nguon = [], []
    for idx, w in enumerate(moc_tu):
        for tok in khoa_tu(w["chu"]):
            khoa.append(tok)
            nguon.append(idx)
    ra, vi_tri = [], 0
    for n in nhips:
        if n.cum == "@dau":
            ra.append(dan_dau)
            continue
        can = khoa_tu(n.cum)
        i = (next((j for j in range(vi_tri, len(khoa) - len(can) + 1) if khoa[j:j + len(can)] == can), -1)
             if can else -1)
        if i < 0:
            ra.append((ra[-1] + 0.6) if ra else dan_dau)
            continue
        ra.append(moc_tu[nguon[i]]["t"])
        vi_tri = i + len(can)
    return [max(dan_dau, t) for t in ra]


def _o_cac_nhip(scene, kho_ten: str) -> list:
    """Ô của từng nhịp theo thứ tự: nhịp ghi ô thì dùng đúng ô đó; `mui-ten` không ghi ô thì `None` (vẽ trên cả
    khung, không chiếm ô nào); không ghi thì ô đầu tiên của `BO_CUC[bo_cuc][kho]`
    (trừ `nen`) chưa có vật nào dùng (kể cả ô ghi tường minh ở một nhịp *sau* trong cùng cảnh — tránh đè lên ô mà
    nhịp sau sẽ nhận), hết ô thì dùng ô cuối của bố cục (không bao giờ là `nen`: `nen` chỉ dành cho ảnh ghi tường
    minh); bố cục `chong` không có ô, trả `"chong-<k>"`."""
    bo_cuc = scene.truong["bo-cuc"][0]
    o_hop_le = [o for o in BO_CUC[bo_cuc][kho_ten] if o != "nen"]
    # Tiền nạp mọi ô đã ghi tường minh ở bất kỳ nhịp nào của cảnh (kể cả nhịp đứng sau), để nhịp tự chọn ô không
    # bao giờ đè lên ô một nhịp khác sẽ dùng.
    da_dung: list = []
    for n in scene.nhip:
        if n.o is not None and n.o not in da_dung:
            da_dung.append(n.o)
    chong_dem = 0
    ket = []
    for n in scene.nhip:
        if n.o is not None:
            ket.append(n.o)
            continue
        if n.vat == "mui-ten":
            ket.append(None)   # mũi tên vẽ trên cả khung, không chiếm ô
            continue
        if bo_cuc == "chong":
            ket.append(f"chong-{chong_dem}")
            chong_dem += 1
            continue
        trong = [o for o in o_hop_le if o not in da_dung]
        o = trong[0] if trong else (o_hop_le[-1] if o_hop_le else None)
        ket.append(o)
        if o not in da_dung:
            da_dung.append(o)
    return ket


def _nhip_du_lieu(n: Nhip, o: str, bat_dau: float) -> dict:
    d = {"batDau": bat_dau, "vat": n.vat, "o": o, "tuyChon": list(n.tuy_chon),
         "chu": None, "the": None, "anh": None, "so": None, "ds": None}
    if n.vat in ("chu", "nhan", "dau"):
        d["chu"] = hien(n.noi_dung)
    elif n.vat == "mui-ten":
        d["chu"] = n.noi_dung
    elif n.vat == "the":
        from .parse import tach_the
        nhan, gia_tri, chu_thich = tach_the(n.noi_dung)
        d["the"] = {"nhan": nhan, "giaTri": gia_tri, "chuThich": chu_thich}
    elif n.vat in DANH_SACH:
        d["ds"] = tach_danh_sach(n.vat, n.noi_dung)
    elif n.vat == "so":
        m = _SO_RE.search(n.noi_dung)
        raw = m.group(1)
        thap_phan = len(raw.split(".", 1)[1]) if "." in raw else 0
        d["so"] = {"giaTri": float(raw), "truoc": hien(n.noi_dung[:m.start()]), "sau": hien(n.noi_dung[m.end():]),
                   "thapPhan": thap_phan}
    return d


def _chuyen_canh(scene, meta: dict):
    """Kiểu chuyển cảnh vào cảnh này (spec §3–5): trường `chuyen` của cảnh (`khong` -> None); không có thì theo
    khoá đầu `chuyen-canh` (`xen-ke` luân phiên hai kiểu, `khong` -> None); Cảnh 1 luôn None."""
    if scene.so <= 1:
        return None
    kieu = scene.truong.get("chuyen", [None])[0]
    if kieu == "khong":
        return None
    if kieu:
        return kieu
    kieu_meta = meta.get("chuyen-canh", "xen-ke")
    if kieu_meta == "xen-ke":
        return CHUYEN_XEN_KE[(scene.so - 2) % len(CHUYEN_XEN_KE)]
    return None if kieu_meta == "khong" else kieu_meta


def du_lieu_canh(scene, cl, tai_nguyen: dict, meta: dict) -> dict:
    """Dữ liệu trang của một cảnh Vox (Hợp đồng dùng chung, global.md)."""
    from . import kho as _kho, phong as _phong
    from . import lich as _lich

    dan_dau = getattr(cl, "dan_dau", _lich.DAN_DAU)
    kho_ten = meta.get("kho", "ngang")
    anh_tn = tai_nguyen.get("anh") or {}
    cac_o = _o_cac_nhip(scene, kho_ten)
    cac_bat_dau = moc_nhip(scene.nhip, cl.moc_tu, dan_dau)
    nhip_du = []
    for n, o, bat_dau in zip(scene.nhip, cac_o, cac_bat_dau):
        d = _nhip_du_lieu(n, o, bat_dau)
        if n.vat == "anh":
            d["anh"] = anh_tn.get(n.chi_so)
        nhip_du.append(d)
    return {
        "so": scene.so, "loai": "vox", "thoiLuong": cl.thoi_luong, "danDau": dan_dau,
        "kho": _kho.tu_meta(meta).du_lieu(), "chuDe": _phong.chu_de("vox"),
        "boCuc": scene.truong["bo-cuc"][0], "hat": scene.so, "bangMau": meta.get("bang-mau", "kem"),
        # `nguon` (nguồn số liệu) không hiện trên hình: video_ma ghi vào nguon.txt cạnh video.
        "nhip": nhip_du, "nguon": None, "nen": tai_nguyen.get("nen"), "co": {"chuyen": _chuyen_canh(scene, meta)},
        "nenTruoc": None, "dongNguon": [], "loat": None, "tu": list(cl.moc_tu),
    }


# Tuỳ chọn đổi chính ảnh đã xử lý (`xa`, `gan` chỉ đổi lớp, không làm ảnh cũ).
TUY_CHON_ANH = ("khung", "duotone", "halftone")
FIX_ANH = "Chạy `python tools\\vi\\anh_vox.py <thư mục video>` để tạo và xử lý ảnh, rồi chạy lại."


def _doc_bang(thu_muc) -> dict:
    duong_bang = Path(thu_muc) / "anh" / "ai" / "vox.json"
    try:
        bang = json.loads(duong_bang.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return {}
    return bang if isinstance(bang, dict) else {}


def _con_moi(info: dict, m) -> bool:
    """Bản ghi `vox.json` còn khớp mục kế hoạch `m` (anh_vox_parts.ke_hoach.Muc) lập từ video.md hiện tại: cùng mã
    kế hoạch (mô tả, khổ, phong ảnh), cùng loại nguồn, cùng tuỳ chọn ảnh, cùng kiểu (ảnh `cat` đã tự chuyển sang
    `khung` vẫn khớp)."""
    if m is None:
        return False
    tuy = info.get("tuy_chon")
    if not isinstance(tuy, list):
        return False
    return (info.get("ma_ke_hoach") == m.ma and info.get("loai_nguon") == m.nguon
            and sorted(t for t in tuy if t in TUY_CHON_ANH) == sorted(t for t in m.tuy_chon if t in TUY_CHON_ANH)
            and (info.get("kieu") == m.kieu or (m.kieu == "cat" and info.get("kieu") == "khung")))


def kiem(video, thu_muc, chi_canh_bao: bool = False) -> list:
    """Kiểm cảnh Vox: mỗi nhịp `anh` phải có ảnh đã xử lý trong `anh/ai/vox.json`, còn khớp video.md hiện tại;
    cảnh báo lời dài. `chi_canh_bao` (`--plan-only`): thiếu ảnh hay ảnh cũ chỉ là cảnh báo, để ước thời lượng được
    trước khi chạy `anh_vox.py`."""
    from anh_vox_parts import ke_hoach as _ke_hoach

    from . import kiem as _kiem

    bang = _doc_bang(thu_muc)
    ke = {(m.canh, m.chi_so): m for m in _ke_hoach.lap(video)}
    warnings: list = []
    for scene in video.canh:
        m_nen = ke.get((scene.so, _ke_hoach.CHI_SO_NEN))
        if m_nen is not None:
            info = bang.get(f"{scene.so}-nen")
            file_ok = isinstance(info, dict) and (Path(thu_muc) / "anh" / str(info.get("file", ""))).is_file()
            if not file_ok or not _con_moi(info, m_nen):
                thieu = "chưa có nền AI" if not file_ok else "nền AI đã cũ so với video.md"
                if chi_canh_bao:
                    warnings.append(f"Cảnh {scene.so}: {thieu}; chạy anh_vox.py trước --xem-truoc.")
                else:
                    raise _kiem.CanhError(scene.so, f"{thieu}.", FIX_ANH + " Máy không có nguồn vẽ ảnh thì ghi "
                                          "`nen-canh: khong` vào khối thông tin.")
        dau = [n for n in scene.nhip if n.cum != "@dau"]
        if len(dau) == len(scene.nhip) and dau and tim_cum(khoa_tu(scene.loi), dau[0].cum, 0) > MO_CANH_TU:
            warnings.append(f"Cảnh {scene.so}: vật đầu tiên hiện muộn (cụm \"{dau[0].cum}\" nằm sau từ thứ {MO_CANH_TU} "
                            "của lời), cảnh sẽ mở bằng nền trống; thêm một nhịp `@dau` (nhãn tiêu đề hoặc hình chính).")
        for n in scene.nhip:
            if n.vat != "anh":
                continue
            info = bang.get(f"{scene.so}-{n.chi_so}")
            file_ok = isinstance(info, dict) and (Path(thu_muc) / "anh" / str(info.get("file", ""))).is_file()
            if not file_ok:
                if chi_canh_bao:
                    warnings.append(f"Cảnh {scene.so}: nhịp {n.chi_so + 1} chưa có ảnh; chạy anh_vox.py trước --xem-truoc.")
                    continue
                raise _kiem.CanhError(scene.so, f"nhịp {n.chi_so + 1} chưa có ảnh đã xử lý.", FIX_ANH)
            if not _con_moi(info, ke.get((scene.so, n.chi_so))):
                if chi_canh_bao:
                    warnings.append(f"Cảnh {scene.so}: ảnh của nhịp {n.chi_so + 1} đã cũ so với video.md; chạy lại "
                                    "anh_vox.py trước --xem-truoc.")
                    continue
                raise _kiem.CanhError(scene.so, f"ảnh của nhịp {n.chi_so + 1} (cảnh {scene.so}) đã cũ so với video.md; "
                                                "chạy lại anh_vox.py.", FIX_ANH)
        if len(scene.loi) > _kiem.LOI_DAI:
            warnings.append(f"Cảnh {scene.so}: lời dài {len(scene.loi)} ký tự (quá {_kiem.LOI_DAI}); nên tách "
                            "thành hai cảnh.")
    return warnings


def tai_nguyen(scene, thu_muc) -> dict:
    """Ảnh của cảnh ({chi_số: {dataUrl, rong, cao, kieu, nguon, moHinh}}), đọc trực tiếp từ `anh/ai/vox.json` và các
    PNG đã xử lý trong `anh/ai/xu-ly/` (đã kiểm nguồn ở `anh_vox.py`; không qua `anh.doc`)."""
    from PIL import Image

    bang = _doc_bang(thu_muc)
    ra: dict = {}
    for n in scene.nhip:
        if n.vat != "anh":
            continue
        info = bang.get(f"{scene.so}-{n.chi_so}")
        if not info:
            continue
        duong_anh = Path(thu_muc) / "anh" / info["file"]
        data = duong_anh.read_bytes()
        with Image.open(duong_anh) as im:
            rong, cao = im.size
        ra[n.chi_so] = {
            "dataUrl": "data:image/png;base64," + base64.b64encode(data).decode("ascii"),
            "rong": rong, "cao": cao, "kieu": info.get("kieu"),
            "nguon": info.get("nguon"), "moHinh": info.get("mo_hinh"),
        }
    nen = None
    info = bang.get(f"{scene.so}-nen")
    if isinstance(info, dict) and info.get("file"):
        duong_nen = Path(thu_muc) / "anh" / info["file"]
        if duong_nen.is_file():
            with Image.open(duong_nen) as im:
                rong, cao = im.size
            kieu_tep = "jpeg" if duong_nen.suffix.lower() in (".jpg", ".jpeg") else "png"
            nen = {"dataUrl": f"data:image/{kieu_tep};base64," + base64.b64encode(duong_nen.read_bytes()).decode("ascii"),
                   "rong": rong, "cao": cao, "moHinh": info.get("mo_hinh")}
    return {"anh": ra, "nen": nen}


def nguon_van_ban(video, thu_muc, nhac=None) -> str:
    """Nội dung `nguon.txt` cạnh video: Vox không hiện nguồn nào trên hình, nên mô hình AI, nguồn ảnh thật (giấy phép
    CC BY bắt buộc ghi công), nguồn số liệu từng cảnh và nguồn nhạc nền ghi ở đây."""
    bang = _doc_bang(thu_muc)
    dong = [f"Nguồn của video «{video.meta['tieu-de']}»", ""]
    mo_hinh = sorted({str(i["mo_hinh"]) for i in bang.values() if isinstance(i, dict) and i.get("mo_hinh")})
    if mo_hinh:
        dong += [f"Hình minh hoạ tạo bằng AI: {', '.join(mo_hinh)}", ""]
    anh_that = []
    for scene in video.canh:
        for n in scene.nhip or []:
            info = bang.get(f"{scene.so}-{n.chi_so}")
            if n.vat == "anh" and isinstance(info, dict) and info.get("nguon"):
                anh_that.append(f"- Cảnh {scene.so}: {info['nguon']}")
    if anh_that:
        dong += ["Ảnh thật:"] + anh_that + [""]
    so_lieu = [f"- Cảnh {s.so}: {s.truong['nguon'][0]}" for s in video.canh if s.truong.get("nguon")]
    if so_lieu:
        dong += ["Số liệu:"] + so_lieu + [""]
    if nhac is not None and nhac.get("nguon"):
        dong += [f"Nhạc nền: {nhac['nguon']}", ""]
    return "\n".join(dong).rstrip() + "\n"
