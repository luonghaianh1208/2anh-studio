# tools/vi/anh_vox_parts/ke_hoach.py
"""Danh sách ảnh của video Vox và tên file tất định (video_ma đọc lại cùng tên)."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

DUOI_PHONG = {
    "chup-that": "ảnh chụp thật, ánh sáng tự nhiên, chi tiết sắc nét",
    "minh-hoa": "tranh minh hoạ phẳng, nét gọn, màu tươi",
}
DUOI_CAT = "một vật duy nhất ở giữa, nền xanh lá thuần #00FF00 phẳng, không bóng đổ, không viền"
DUOI_CHUNG = "không có chữ, không có chữ cái, không có logo"
KHO_ANH = {"cat": "1024x1024", ("khung", "ngang"): "1536x1024", ("khung", "doc"): "1024x1536",
           ("phu", "ngang"): "1536x1024", ("phu", "doc"): "1024x1536"}


@dataclass
class Muc:
    ma: str
    canh: int
    chi_so: int
    kieu: str          # cat | khung | phu
    nguon: str         # ve | tim | file
    prompt: str        # ve: câu lệnh đầy đủ; tim: từ khoá; file: tên file
    kich_thuoc: str
    tuy_chon: tuple


def ma_anh(prompt: str, kich_thuoc: str) -> str:
    return hashlib.sha256(f"{prompt}\n{kich_thuoc}".encode("utf-8")).hexdigest()[:16]


def hat(m: Muc) -> int:
    return m.canh * 100 + m.chi_so


def _kieu(n, nguon: str) -> str:
    if n.o == "nen":
        return "phu"
    if nguon != "ve" or "khung" in n.tuy_chon:
        return "khung"   # ảnh thật và ảnh có sẵn luôn là khung (spec 4.6)
    return "cat"


def lap(video) -> list:
    kho = video.meta["kho"]
    ds = []
    for c in video.canh:
        for n in c.nhip or []:
            if n.vat != "anh":
                continue
            nd = n.noi_dung
            nguon = "ve" if nd.startswith("ve:") else ("tim" if nd.startswith("tim:") else "file")
            kieu = _kieu(n, nguon)
            kt = KHO_ANH["cat"] if kieu == "cat" else KHO_ANH[(kieu, kho)]
            if nguon == "ve":
                phan = [nd[3:].strip(), DUOI_PHONG[video.meta["phong-anh"]]]
                if kieu == "cat":
                    phan.append(DUOI_CAT)
                phan.append(DUOI_CHUNG)
                prompt = ", ".join(phan)
            else:
                prompt = nd[4:].strip() if nguon == "tim" else nd
            ma = ma_anh(prompt, kt) if nguon == "ve" else hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:10]
            ds.append(Muc(ma, c.so, n.chi_so, kieu, nguon, prompt, kt, n.tuy_chon))
    return ds


def file_goc(thu_muc: Path, m: Muc) -> Path:
    if m.nguon == "ve":
        return thu_muc / "anh" / "ai" / "goc" / f"{m.ma}.png"
    if m.nguon == "tim":
        return thu_muc / "anh" / f"tim-{m.ma}.jpg"
    return thu_muc / "anh" / m.prompt


def file_xu_ly(thu_muc: Path, m: Muc) -> Path:
    duoi = "".join(f"-{t}" for t in ("duotone", "halftone") if t in m.tuy_chon)
    return thu_muc / "anh" / "ai" / "xu-ly" / f"{m.ma}-{hat(m)}-{m.kieu}{duoi}.png"
