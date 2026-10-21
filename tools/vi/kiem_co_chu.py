#!/usr/bin/env python3
"""Kiểm cỡ chữ của slide trình chiếu trước khi xuất PPTX: không chữ nào dưới 24pt, trừ dòng ghi nguồn và số trang
(từ 18pt). Đọc `svg_output/*.svg` của dự án, tính cỡ chữ thật của từng dòng (kể cả cỡ thừa hưởng từ `<svg>`, `<g>`),
đổi sang pt theo cách bộ xuất của upstream đổi (1px SVG = 9525 EMU = 0,75pt).

  python tools/vi/kiem_co_chu.py <thư_mục_dự_án> [--toi-thieu 24] [--noi-dung 28]

stdout đúng một dòng JSON: {ready, so_trang, loi, canh_bao, bo_qua, error}. `loi` khác rỗng thì `ready` là false.
Chỉ áp cho khổ trình chiếu 16:9 (1280×720) và 4:3 (1024×768); khổ khác (poster, story) ghi vào `bo_qua`.
Hướng dẫn: docs/vi/tro-ly/quy-trinh-hoi.md mục "Cỡ chữ".
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

PT_MOI_PX = 0.75          # 9525 EMU / 12700 EMU mỗi pt
TOI_THIEU = 24.0
NOI_DUNG = 28.0
PHU_TOI_THIEU = 18.0      # dòng ghi nguồn ảnh, số trang
KHO_TRINH_CHIEU = {(1280, 720), (1024, 768)}
NOI_DUNG_DAI = 40         # dòng từ chừng này ký tự trở lên coi là nội dung (nên từ 28pt)
SVG = "{http://www.w3.org/2000/svg}"
_SO_RE = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*(px)?\s*$")
_PHU_RE = re.compile(r"^\s*(nguồn|ảnh:|ảnh của|source|photo|©|\(c\)|cc by|cc0)", re.I)
_SO_TRANG_RE = re.compile(r"^\s*\d{1,3}\s*(/\s*\d{1,3})?\s*$")


def _co(el) -> float | None:
    """Cỡ chữ khai trên chính phần tử (thuộc tính hoặc style), đơn vị px SVG."""
    gia_tri = el.get("font-size")
    kieu = el.get("style") or ""
    m = re.search(r"font-size\s*:\s*([^;]+)", kieu)
    if m:
        gia_tri = m.group(1)
    if gia_tri is None:
        return None
    m = _SO_RE.match(gia_tri)
    return float(m.group(1)) if m else None


def _chu(el) -> str:
    return re.sub(r"\s+", " ", " ".join(x.strip() for x in el.itertext() if x.strip()))


def _cac_dong(goc):
    """(chữ, cỡ px nhỏ nhất của dòng) cho mỗi `<text>` ngoài `<defs>`; cỡ thừa hưởng theo cây."""
    def di(el, co_cha, trong_defs):
        ten = el.tag.replace(SVG, "")
        co = _co(el) or co_cha
        if ten == "defs":
            trong_defs = True
        if ten == "text" and not trong_defs:
            cac_co = [co] if (el.text or "").strip() else []
            for con in el.iter():
                if con is el:
                    continue
                co_con = _co(con) or co
                if (con.text or "").strip():
                    cac_co.append(co_con)
            cac_co = [c for c in cac_co if c is not None]
            chu = _chu(el)
            if chu and cac_co:
                yield chu, min(cac_co)
            return
        for con in el:
            yield from di(con, co, trong_defs)

    yield from di(goc, _co(goc) or 16.0, False)


def kiem_trang(duong: Path, toi_thieu: float, noi_dung: float) -> tuple:
    goc = ET.parse(duong).getroot()
    vb = [float(x) for x in (goc.get("viewBox") or "0 0 0 0").replace(",", " ").split()]
    kho = (round(vb[2]), round(vb[3])) if len(vb) == 4 else (0, 0)
    if kho not in KHO_TRINH_CHIEU:
        return None, [], []
    loi, canh_bao = [], []
    for chu, px in _cac_dong(goc):
        pt = round(px * PT_MOI_PX, 1)
        phu = bool(_PHU_RE.match(chu) or _SO_TRANG_RE.match(chu))
        san = PHU_TOI_THIEU if phu else toi_thieu
        tom = chu if len(chu) <= 50 else chu[:47] + "…"
        if pt < san - 0.05:
            loi.append({"trang": duong.name, "chu": tom, "pt": pt, "toi_thieu": san,
                        "px_can": round(san / PT_MOI_PX)})
        elif not phu and len(chu) >= NOI_DUNG_DAI and pt < noi_dung - 0.05:
            canh_bao.append({"trang": duong.name, "chu": tom, "pt": pt, "nen": noi_dung,
                             "px_can": round(noi_dung / PT_MOI_PX)})
    return kho, loi, canh_bao


def chay(thu_muc: Path, toi_thieu: float, noi_dung: float) -> dict:
    trang = sorted((thu_muc / "svg_output").glob("*.svg"))
    if not trang:
        raise FileNotFoundError(f"Không thấy trang SVG trong {thu_muc / 'svg_output'}.")
    loi, canh_bao, bo_qua = [], [], []
    for t in trang:
        kho, l, c = kiem_trang(t, toi_thieu, noi_dung)
        if kho is None:
            bo_qua.append(t.name)
            continue
        loi += l
        canh_bao += c
    return {"so_trang": len(trang), "loi": loi, "canh_bao": canh_bao, "bo_qua": bo_qua}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Kiểm cỡ chữ slide trình chiếu (tối thiểu 24pt)")
    ap.add_argument("thu_muc")
    ap.add_argument("--toi-thieu", type=float, default=TOI_THIEU)
    ap.add_argument("--noi-dung", type=float, default=NOI_DUNG)
    a = ap.parse_args(argv)
    try:
        kq = chay(Path(a.thu_muc), a.toi_thieu, a.noi_dung)
        out = {"ready": not kq["loi"], **kq, "error": None}
    except (OSError, ET.ParseError) as exc:
        out = {"ready": False, "so_trang": 0, "loi": [], "canh_bao": [], "bo_qua": [],
               "error": {"step": "input", "message": str(exc),
                         "fix": "Chạy trên thư mục dự án có svg_output/ chứa các trang SVG."}}
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False))
    return 0 if out["ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
