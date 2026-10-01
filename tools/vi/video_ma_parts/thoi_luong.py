# tools/vi/video_ma_parts/thoi_luong.py
"""Ước tính thời lượng video từ số từ của lời, và cảnh báo khi lệch `thoi-luong` (spec Vox mục 7)."""

from __future__ import annotations

import re

# Từ/giây của giọng edge-tts tiếng Việt; đo trên video 9 cảnh, 288 từ (105 giây tiếng) ở tốc độ vừa.
TOC_DO = {"cham": 2.4, "vua": 2.7, "nhanh": 3.1}
# Đoạn dẫn đầu (lich.DAN_DAU 1,0 s) và đuôi mỗi cảnh, trung bình đo được.
MOI_CANH = 1.1
VUOT, THIEU = 0.15, 0.25
_DAU = re.compile(r"==|\(\(|\)\)|__|\{\{|\}\}")


def dem_tu(text: str) -> int:
    return len(re.sub(r"[^\w\s]", " ", _DAU.sub("", text)).split())


def uoc_tinh(video) -> float:
    toc = TOC_DO[video.meta["toc-do"]]
    tu = sum(dem_tu(c.loi) + sum(dem_tu(x) for x in c.truong.get("loi-giai", [])) for c in video.canh)
    cho = sum(int(c.truong.get("cho", ["5"])[0]) + 0.4 for c in video.canh if c.loai == "cau-hoi")
    return tu / toc + MOI_CANH * len(video.canh) + cho


def _chuc(x: float) -> int:
    return max(10, int(round(x / 10.0)) * 10)


def canh_bao(muc_tieu: int, giay: float, toc_do: str, uoc: bool) -> str | None:
    if muc_tieu * (1 - THIEU) <= giay <= muc_tieu * (1 + VUOT):
        return None
    dong_tu = f"ước {giay:.0f} giây" if uoc else f"dài {giay:.0f} giây"
    so_tu = _chuc(abs(giay - muc_tieu) * TOC_DO[toc_do])
    viec = f"bớt khoảng {so_tu} từ lời" if giay > muc_tieu else f"thêm khoảng {so_tu} từ lời"
    return (f"Video {dong_tu}, mục tiêu `thoi-luong: {muc_tieu}` giây: {viec} (hoặc bớt/thêm cảnh) "
            "rồi chạy lại trước khi dựng thật.")
