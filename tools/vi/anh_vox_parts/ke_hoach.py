"""Danh sách ảnh của video Vox và tên file tất định (video_ma đọc lại cùng tên)."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

DUOI_PHONG = {
    # Kiểu video mẫu Vox: tranh cắt dán hỗn hợp, giấy cũ, tranh khắc, tông trầm.
    "cat-dan": ("tranh cắt dán hỗn hợp kiểu tạp chí cổ, ghép từ ảnh in chấm lưới và tranh khắc, giấy cũ ngả màu, "
                "mép giấy xé, tông đỏ trầm, xanh than, vàng đất và kem"),
    "chup-that": "ảnh chụp thật, ánh sáng tự nhiên, chi tiết sắc nét",
    "minh-hoa": "tranh minh hoạ phẳng, nét gọn, màu tươi",
}
DUOI_CAT = "cả cụm nằm gọn ở giữa, tách rời khỏi nền, nền xanh lá thuần #00FF00 phẳng, không bóng đổ, không viền"
DUOI_NEN = ("nền phủ kín khung làm phông cho video, các mảng giấy xé và hình mờ nằm ở rìa và các góc, "
            "chừa vùng giấy sáng ít chi tiết ở giữa và bên trái để đặt chữ, không có nhân vật lớn ở giữa")
DUOI_CHUNG = "không có chữ, không có chữ cái, không có logo"
KHO_ANH = {"cat": "1024x1024", ("khung", "ngang"): "1536x1024", ("khung", "doc"): "1024x1536",
           ("phu", "ngang"): "1536x1024", ("phu", "doc"): "1024x1536",
           ("nen", "ngang"): "1536x1024", ("nen", "doc"): "1024x1536"}
# Nền AI của cảnh không thuộc nhịp nào: chỉ số nhịp quy ước -1, khoá trong vox.json là "<cảnh>-nen".
CHI_SO_NEN = -1
LOI_TRONG_NEN = 160


@dataclass
class Muc:
    ma: str
    canh: int
    chi_so: int
    kieu: str          # cat | khung | phu | nen
    nguon: str         # ve | tim | file
    prompt: str        # ve: câu lệnh đầy đủ; tim: từ khoá; file: tên file
    kich_thuoc: str
    tuy_chon: tuple


def ma_anh(prompt: str, kich_thuoc: str) -> str:
    return hashlib.sha256(f"{prompt}\n{kich_thuoc}".encode("utf-8")).hexdigest()[:16]


def hat(m: Muc) -> int:
    return m.canh * 100 + (99 if m.kieu == "nen" else m.chi_so)


def khoa(m: Muc) -> str:
    """Khoá của mục trong `anh/ai/vox.json`."""
    return f"{m.canh}-nen" if m.kieu == "nen" else f"{m.canh}-{m.chi_so}"


def _kieu(n, nguon: str) -> str:
    if n.o == "nen":
        return "phu"
    if nguon != "ve" or "khung" in n.tuy_chon:
        return "khung"   # ảnh thật và ảnh có sẵn luôn là khung (spec 4.6)
    return "cat"


def _nen_canh(video, c) -> Muc:
    """Nền AI của cảnh: theo trường `nen` của cảnh, không ghi thì lập từ tên video và lời của cảnh."""
    mo_ta = c.truong.get("nen", [""])[0].strip()
    if mo_ta.startswith("ve:"):
        mo_ta = mo_ta[3:].strip()
    if not mo_ta:
        mo_ta = f"phông nền cho video «{video.meta['tieu-de']}», gợi ý nội dung: {c.loi[:LOI_TRONG_NEN]}"
    kt = KHO_ANH[("nen", video.meta["kho"])]
    prompt = ", ".join([mo_ta, DUOI_PHONG[video.meta["phong-anh"]], DUOI_NEN, DUOI_CHUNG])
    return Muc(ma_anh(prompt, kt), c.so, CHI_SO_NEN, "nen", "ve", prompt, kt, ())


def lap(video) -> list:
    kho = video.meta["kho"]
    ve_nen = video.meta.get("nen-canh", "ve") == "ve"
    ds = []
    for c in video.canh:
        co_phu = False
        for n in c.nhip or []:
            if n.vat != "anh":
                continue
            nd = n.noi_dung
            nguon = "ve" if nd.startswith("ve:") else ("tim" if nd.startswith("tim:") else "file")
            kieu = _kieu(n, nguon)
            co_phu = co_phu or kieu == "phu"
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
        # Cảnh đã có ảnh phủ kín khung (`toan-canh`, ô `nen`) thì không cần nền AI riêng.
        if ve_nen and not co_phu and c.nhip is not None:
            ds.append(_nen_canh(video, c))
    return ds


def file_goc(thu_muc: Path, m: Muc) -> Path:
    if m.nguon == "ve":
        return thu_muc / "anh" / "ai" / "goc" / f"{m.ma}.png"
    if m.nguon == "tim":
        return thu_muc / "anh" / f"tim-{m.ma}.jpg"
    return thu_muc / "anh" / m.prompt


def file_xu_ly(thu_muc: Path, m: Muc) -> Path:
    if m.kieu == "nen":   # nền phủ khung: JPEG cho nhẹ trang
        return thu_muc / "anh" / "ai" / "xu-ly" / f"{m.ma}-{hat(m)}-nen.jpg"
    duoi = "".join(f"-{t}" for t in ("duotone", "halftone") if t in m.tuy_chon)
    return thu_muc / "anh" / "ai" / "xu-ly" / f"{m.ma}-{hat(m)}-{m.kieu}{duoi}.png"
