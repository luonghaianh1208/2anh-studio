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
    "phong-anh": ("chup-that", "minh-hoa"),
    "bang-mau": ("kem", "bao-cu", "dem", "tuoi"),
    "chuyen-canh": ("xen-ke", "xe-giay", "lia", "khong"),
}
# Khoá đầu của kiểu viết tay, không dùng ở Vox.
VOX_CAM = ("ban-tay", "nhan-vat", "mau-ao", "chu-dong", "may-quay")
CHUYEN_CANH = ("xe-giay", "lia", "khong")
# Chuyển cảnh xen kẽ (khoá đầu `chuyen-canh: xen-ke`, mặc định của Vox): cảnh chẵn/lẻ (kể từ Cảnh 2) luân phiên.
CHUYEN_XEN_KE = ("xe-giay", "lia")
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


def moc_nhip(nhips: list, moc_tu: list, dan_dau: float) -> list:
    """Mốc bắt đầu (giây trong cảnh) của từng nhịp, theo mốc từ (`lich.CanhLich.moc_tu`) của cụm từ nhịp đó khớp
    trong lời; `@dau` luôn ở `dan_dau`. Cụm không khớp được (giọng chưa có mốc từ, hay không khớp) nối tiếp nhịp
    trước, cách 0,6 giây."""
    khoa = [w["khoa"] for w in moc_tu]
    ra, vi_tri = [], 0
    for n in nhips:
        if n.cum == "@dau":
            ra.append(dan_dau)
            continue
        can = khoa_tu(n.cum)
        i = next((j for j in range(vi_tri, len(khoa) - len(can) + 1) if khoa[j:j + len(can)] == can), -1)
        if i < 0:
            ra.append((ra[-1] + 0.6) if ra else dan_dau)
            continue
        ra.append(moc_tu[i]["t"])
        vi_tri = i + len(can)
    return [max(dan_dau, t) for t in ra]


def _o_cac_nhip(scene, kho_ten: str) -> list:
    """Ô của từng nhịp theo thứ tự: nhịp ghi ô thì dùng đúng ô đó; không ghi thì ô đầu tiên của `BO_CUC[bo_cuc][kho]`
    (trừ `nen`) chưa có vật nào dùng, hết ô thì dùng lại ô cuối; bố cục `chong` không có ô, trả `"chong-<k>"`."""
    bo_cuc = scene.truong["bo-cuc"][0]
    o_hop_le = [o for o in BO_CUC[bo_cuc][kho_ten] if o != "nen"]
    da_dung: list = []
    chong_dem = 0
    ket = []
    for n in scene.nhip:
        if n.o is not None:
            ket.append(n.o)
            if n.o not in da_dung:
                da_dung.append(n.o)
            continue
        if bo_cuc == "chong":
            ket.append(f"chong-{chong_dem}")
            chong_dem += 1
            continue
        trong = [o for o in o_hop_le if o not in da_dung]
        o = trong[0] if trong else (ket[-1] if ket else (o_hop_le[0] if o_hop_le else None))
        ket.append(o)
        da_dung.append(o)
    return ket


def _nhip_du_lieu(n: Nhip, o: str, bat_dau: float) -> dict:
    d = {"batDau": bat_dau, "vat": n.vat, "o": o, "tuyChon": list(n.tuy_chon),
         "chu": None, "the": None, "anh": None, "so": None}
    if n.vat in ("chu", "nhan", "dau"):
        d["chu"] = hien(n.noi_dung)
    elif n.vat == "mui-ten":
        d["chu"] = n.noi_dung
    elif n.vat == "the":
        from .parse import tach_the
        nhan, gia_tri, chu_thich = tach_the(n.noi_dung)
        d["the"] = {"nhan": nhan, "giaTri": gia_tri, "chuThich": chu_thich}
    elif n.vat == "so":
        m = _SO_RE.search(n.noi_dung)
        raw = m.group(1)
        thap_phan = len(raw.split(".", 1)[1]) if "." in raw else 0
        d["so"] = {"giaTri": float(raw), "truoc": n.noi_dung[:m.start()], "sau": n.noi_dung[m.end():],
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

    dan_dau = _lich.DAN_DAU
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
        "nhip": nhip_du, "nguon": scene.truong.get("nguon", [None])[0], "co": {"chuyen": _chuyen_canh(scene, meta)},
        "nenTruoc": None, "dongNguon": [], "loat": None, "tu": list(cl.moc_tu),
    }


def kiem(video, thu_muc) -> list:
    """Kiểm cảnh Vox: mỗi nhịp `anh` phải có ảnh đã xử lý trong `anh/ai/vox.json` (Task 4); cảnh báo lời dài."""
    from . import kiem as _kiem

    duong_bang = Path(thu_muc) / "anh" / "ai" / "vox.json"
    try:
        bang = json.loads(duong_bang.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        bang = {}
    if not isinstance(bang, dict):
        bang = {}
    warnings: list = []
    for scene in video.canh:
        for n in scene.nhip:
            if n.vat != "anh":
                continue
            info = bang.get(f"{scene.so}-{n.chi_so}")
            file_ok = info is not None and (Path(thu_muc) / "anh" / info.get("file", "")).is_file()
            if not file_ok:
                raise _kiem.CanhError(scene.so, f"nhịp {n.chi_so + 1} chưa có ảnh đã xử lý.",
                                      "Chạy `python tools\\vi\\anh_vox.py <thư mục video>` để tạo và xử lý ảnh, "
                                      "rồi chạy lại.")
        if len(scene.loi) > _kiem.LOI_DAI:
            warnings.append(f"Cảnh {scene.so}: lời dài {len(scene.loi)} ký tự (quá {_kiem.LOI_DAI}); nên tách "
                            "thành hai cảnh.")
    return warnings


def tai_nguyen(scene, thu_muc) -> dict:
    """Ảnh của cảnh ({chi_số: {dataUrl, rong, cao, kieu, nguon, moHinh}}), đọc trực tiếp từ `anh/ai/vox.json` và các
    PNG đã xử lý trong `anh/ai/xu-ly/` (đã kiểm nguồn ở `anh_vox.py`; không qua `anh.doc`)."""
    from PIL import Image

    duong_bang = Path(thu_muc) / "anh" / "ai" / "vox.json"
    try:
        bang = json.loads(duong_bang.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        bang = {}
    if not isinstance(bang, dict):
        bang = {}
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
    return {"anh": ra}
