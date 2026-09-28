"""Ghép trang HTML cho một cảnh: phong cách + khung + file cảnh + dữ liệu. Mọi thứ nhúng trong trang."""

from __future__ import annotations

import json
from pathlib import Path

from . import kho as kho_py
from . import phong

RUNTIME = Path(__file__).resolve().parent / "runtime"
NGHIEM = Path(__file__).resolve().parents[1] / "thi_nghiem_parts" / "runtime"


def json_nhung(data) -> str:
    return json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")


def _doc(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def dung_trang(du: dict, model=None) -> str:
    # kho.js nạp đầu tiên (sau bảng ô bố cục nó đọc): mọi runtime khác đọc khổ và ô qua THI_KHO;
    # du["kho"] (kho.py) được đặt trước khi dựng cảnh.
    kho = du["kho"]
    scripts = [f"window.THI_O_BO_CUC = {json_nhung(kho_py.O)};\n", _doc(RUNTIME / "kho.js")]
    if du["loai"] == "thi-nghiem":
        scripts.append(_doc(NGHIEM / "khung.js"))
        scripts.append(model.js)
    # cat-dan.js (hàm thuần; chỉ chạm trang khi khung-video.js gọi ở cảnh cat-dan) nạp trước chuyen-canh.js.
    for ten in ("dong.js", "cat-dan.js", "nhan-vat.js", "chuyen-canh.js", "khung-loat.js", "khung-video.js", "nhan.js", "hinh.js", "ban-tay.js", "may-quay.js"):
        scripts.append(_doc(RUNTIME / ten))
    scripts.append(_doc(RUNTIME / "canh" / f"{du['loai']}.js"))
    scripts.append(f"window.DU_CANH = {json_nhung(du)};\nTHI_KHO.dat(window.DU_CANH.kho);\nTHI_VIDEO.khoiDong(window.DU_CANH);")
    # Phong cách: viet-tay.css là nền chung; cat-dan thêm font Be Vietnam Pro và lớp da cat-dan.css.
    chu_de = du.get("chuDe", {}).get("ten", "viet-tay")
    css_them = _doc(RUNTIME / "cat-dan.css") + "\n" if chu_de == "cat-dan" else ""
    body = "\n".join(f"<script>\n{s}\n</script>" for s in scripts)
    return ("<!doctype html>\n<html lang=\"vi\"><head><meta charset=\"utf-8\">"
            f"<style>\n:root {{ --rong: {kho['rong']}px; --cao: {kho['cao']}px; --day: {kho['day']}px; }}\n"
            f"{phong.font_css(chu_de)}\n{_doc(RUNTIME / 'viet-tay.css')}\n{css_them}</style></head>\n"
            f"<body><div id=\"khung\"></div>\n{body}\n</body></html>\n")
