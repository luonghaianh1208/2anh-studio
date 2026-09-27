"""Ghép trang HTML cho một cảnh: phong cách + khung + file cảnh + dữ liệu. Mọi thứ nhúng trong trang."""

from __future__ import annotations

import json
from pathlib import Path

from . import phong

RUNTIME = Path(__file__).resolve().parent / "runtime"
NGHIEM = Path(__file__).resolve().parents[1] / "thi_nghiem_parts" / "runtime"


def json_nhung(data) -> str:
    return json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")


def _doc(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def dung_trang(du: dict, model=None) -> str:
    # kho.js nạp đầu tiên: mọi runtime khác đọc khổ qua THI_KHO; du["kho"] (kho.py) được đặt trước khi dựng cảnh.
    kho = du["kho"]
    scripts = [_doc(RUNTIME / "kho.js")]
    if du["loai"] == "thi-nghiem":
        scripts.append(_doc(NGHIEM / "khung.js"))
        scripts.append(model.js)
    for ten in ("dong.js", "chuyen-canh.js", "khung-video.js", "nhan.js", "hinh.js", "ban-tay.js", "may-quay.js"):
        scripts.append(_doc(RUNTIME / ten))
    scripts.append(_doc(RUNTIME / "canh" / f"{du['loai']}.js"))
    scripts.append(f"window.DU_CANH = {json_nhung(du)};\nTHI_KHO.dat(window.DU_CANH.kho);\nTHI_VIDEO.khoiDong(window.DU_CANH);")
    body = "\n".join(f"<script>\n{s}\n</script>" for s in scripts)
    return ("<!doctype html>\n<html lang=\"vi\"><head><meta charset=\"utf-8\">"
            f"<style>\n:root {{ --rong: {kho['rong']}px; --cao: {kho['cao']}px; }}\n"
            f"{phong.font_css()}\n{_doc(RUNTIME / 'viet-tay.css')}\n</style></head>\n"
            f"<body><div id=\"khung\"></div>\n{body}\n</body></html>\n")
