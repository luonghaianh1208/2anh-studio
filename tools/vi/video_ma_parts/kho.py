"""Khổ khung hình: một nguồn cho kích thước trang, chụp, phụ đề và ghép. Chỉ dùng thư viện chuẩn.

Bố cục tính theo điểm CSS (ngang 1280×720, dọc 720×1280); Chromium chụp với `device_scale_factor = ti_le`
nên khung xuất là 1920×1080 / 1080×1920 ở 1080, và giữ nguyên điểm CSS ở 720.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

# tên khổ -> (rộng, cao, đáy vùng nội dung = mép trên vùng phụ đề), điểm CSS
CAC_KHO = {"ngang": (1280, 720, 620), "doc": (720, 1280, 1080)}
TI_LE = {1080: 1.5, 720: 1.0}

# Ô bố cục {khổ: {tên ô: {x, y, w, h}}}, điểm CSS. Một nguồn cho trang (runtime/kho.js, qua trang.py) và Python.
O = json.loads((Path(__file__).resolve().parent / "runtime" / "o-bo-cuc.json").read_text(encoding="utf-8"))


def o(ten_kho: str, ten_o: str) -> dict:
    """Ô `ten_o` của khổ `ten_kho` (bản sao); khổ chưa có bảng riêng dùng bảng ngang, như runtime/kho.js."""
    bang = O.get(ten_kho, O["ngang"])
    if ten_o not in bang:
        raise ValueError(f"Ô bố cục `{ten_o}` không có ở khổ {ten_kho}.")
    return dict(bang[ten_o])


@dataclass(frozen=True)
class Kho:
    ten: str
    do_phan_giai: int

    def __post_init__(self) -> None:
        if self.ten not in CAC_KHO:
            raise ValueError(f"Khổ `{self.ten}` không có; chọn một trong: {', '.join(CAC_KHO)}.")
        if self.do_phan_giai not in TI_LE:
            raise ValueError(f"Độ phân giải `{self.do_phan_giai}` không có; chọn một trong: {', '.join(map(str, TI_LE))}.")

    @property
    def rong(self) -> int:
        return CAC_KHO[self.ten][0]

    @property
    def cao(self) -> int:
        return CAC_KHO[self.ten][1]

    @property
    def day(self) -> int:
        return CAC_KHO[self.ten][2]

    @property
    def ti_le(self) -> float:
        return TI_LE[self.do_phan_giai]

    @property
    def rong_xuat(self) -> int:
        return round(self.rong * self.ti_le)

    @property
    def cao_xuat(self) -> int:
        return round(self.cao * self.ti_le)

    @property
    def tam(self) -> tuple:
        """Điểm máy quay đưa mục đang nhìn về: giữa bề ngang, nửa chiều cao vùng nội dung."""
        return (self.rong / 2, self.day * 0.5)

    def du_lieu(self) -> dict:
        """`du["kho"]` cho trang (runtime/kho.js)."""
        tam_x, tam_y = self.tam
        return {"ten": self.ten, "rong": self.rong, "cao": self.cao, "day": self.day, "tamX": tam_x, "tamY": tam_y}


def tu_meta(meta: dict) -> Kho:
    """Khổ theo khoá đầu `kho` và `do-phan-giai` (thiếu thì ngang, 1080)."""
    return Kho(meta.get("kho", "ngang"), int(meta.get("do-phan-giai", "1080")))
