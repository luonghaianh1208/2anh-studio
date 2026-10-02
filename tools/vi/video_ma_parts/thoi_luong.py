"""Ước tính thời lượng video từ số từ của lời, và cảnh báo khi lệch `thoi-luong` (spec Vox mục 7)."""

from __future__ import annotations

import re

# Từ/giây của giọng edge-tts tiếng Việt; đo trên video 9 cảnh, 288 từ (105 giây tiếng) ở tốc độ vừa.
TOC_DO = {"cham": 2.4, "vua": 2.7, "nhanh": 3.1}
# Giọng VieNeu (`giong: thu-giang`) đọc nhanh hơn; số đo ở docs/vi/phat-trien/2026-10-01-video-vox-kiem-thu.md.
TOC_DO_VIENEU = {"cham": 4.0, "vua": 4.3, "nhanh": 4.7}
GIONG_VIENEU = ("thu-giang",)
# Đoạn dẫn đầu (lich.DAN_DAU 1,0 s) và đuôi mỗi cảnh, trung bình đo được.
MOI_CANH = 1.1
# Cảnh Vox: dẫn đầu 0,25 s và đuôi 0,3 s (lich.VOX_DAN_DAU, VOX_DUOI).
MOI_CANH_VOX = 0.55
# Giọng VieNeu đọc từng câu rồi nối, giữa hai câu trong một cảnh nghỉ 0,22 s (giong.VIENEU_NGHI).
NGHI_CAU_VIENEU = 0.22
VUOT, THIEU = 0.15, 0.25
_DAU = re.compile(r"==|\(\(|\)\)|__|\{\{|\}\}")
_CAU = re.compile(r"(?<=[.!?…])\s+")


def dem_tu(text: str) -> int:
    return len(re.sub(r"[^\w\s]", " ", _DAU.sub("", text)).split())


def toc(toc_do: str, giong: str = "nu") -> float:
    """Từ/giây của giọng `giong` ở tốc độ `toc_do`."""
    return (TOC_DO_VIENEU if giong in GIONG_VIENEU else TOC_DO)[toc_do]


def uoc_tinh(video) -> float:
    giong = video.meta.get("giong", "nu")
    tu = sum(dem_tu(c.loi) + sum(dem_tu(x) for x in c.truong.get("loi-giai", [])) for c in video.canh)
    cho = sum(int(c.truong.get("cho", ["5"])[0]) + 0.4 for c in video.canh if c.loai == "cau-hoi")
    moi = sum(MOI_CANH_VOX if c.loai == "vox" else MOI_CANH for c in video.canh)
    nghi = 0.0
    if giong in GIONG_VIENEU:
        nghi = NGHI_CAU_VIENEU * sum(max(0, len([x for x in _CAU.split(c.loi.strip()) if x.strip()]) - 1)
                                     for c in video.canh)
    return tu / toc(video.meta["toc-do"], giong) + moi + cho + nghi


def _chuc(x: float) -> int:
    return max(10, int(round(x / 10.0)) * 10)


def canh_bao(muc_tieu: int, giay: float, toc_do: str, uoc: bool, giong: str = "nu") -> str | None:
    if muc_tieu * (1 - THIEU) <= giay <= muc_tieu * (1 + VUOT):
        return None
    dong_tu = f"ước {giay:.0f} giây" if uoc else f"dài {giay:.0f} giây"
    so_tu = _chuc(abs(giay - muc_tieu) * toc(toc_do, giong))
    viec = f"bớt khoảng {so_tu} từ lời" if giay > muc_tieu else f"thêm khoảng {so_tu} từ lời"
    return (f"Video {dong_tu}, mục tiêu `thoi-luong: {muc_tieu}` giây: {viec} (hoặc bớt/thêm cảnh) "
            "rồi chạy lại trước khi dựng thật.")
