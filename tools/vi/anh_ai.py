#!/usr/bin/env python3
"""Lập kế hoạch (và xử lý) ảnh AI cho video giải thích, dựng từ `video.md` (nền `ve:`, nhân vật `nhan-vat: ve:`).

  python tools/vi/anh_ai.py <thư_mục> ke-hoach

stdout đúng một dòng JSON. Hướng dẫn: docs/vi/tro-ly/video-giai-thich.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from anh_ai_parts import cau_lenh  # noqa: E402
from video_ma_parts import parse  # noqa: E402

FIX_INPUT = "Viết video.md trong thư mục dự án (xem docs/vi/tro-ly/video-giai-thich.md) rồi chạy lại."
FIX_INTERNAL = "Lỗi ngoài dự kiến; dán nguyên thông báo này cho người bảo trì."
KE_HOACH_TEN = "ke-hoach.json"
KHONG_AI = "Video không dùng ảnh AI."

# Khổ khung -> kích thước Full HD xuất của nền; kích thước ảnh nhân vật (mẫu và mọi tư thế) cố định.
_KICH_THUOC_NEN = {"ngang": "1920x1080", "doc": "1080x1920"}
_KICH_THUOC_NHAN_VAT = "1024x1536"


class AnhAiError(Exception):
    def __init__(self, step: str, message: str, fix: str) -> None:
        super().__init__(message)
        self.step = step
        self.message = message
        self.fix = fix


def log(text: str) -> None:
    print(text, file=sys.stderr, flush=True)


def emit(payload: dict) -> None:
    text = json.dumps(payload, ensure_ascii=False) + "\n"
    try:
        sys.stdout.write(text)
    except UnicodeEncodeError:
        sys.stdout.buffer.write(text.encode("utf-8", errors="replace"))
    sys.stdout.flush()


def _mo_ta_nhan_vat(meta: dict) -> str | None:
    """Mô tả nhân vật (`nhan-vat: ve: <mô tả>`), None khi video không có nhân vật AI."""
    nv = meta.get("nhan-vat", "khong")
    if not nv.startswith("ve:"):
        return None
    return nv[len("ve:"):].strip()


def _canh_dung_nen_ai(canh: list, goc: int) -> list:
    """Số các cảnh dùng chung một nền AI vẽ gốc ở cảnh `goc`: chính cảnh `goc`, cùng mọi cảnh `nhu-canh` (trực tiếp
    hoặc bắc cầu) giải về `goc` (`parse.giai_nen` đã giải phẳng về đúng cảnh gốc)."""
    ra = [goc]
    for c in canh:
        if c.nen is not None and c.nen.get("kieu") == "nhu" and c.nen.get("canh") == goc:
            ra.append(c.so)
    return ra


def lap_ke_hoach(video: parse.Video) -> list:
    """Danh sách mục kế hoạch: nhân vật mẫu trước, các tư thế đã dùng (theo thứ tự `parse.TU_THE`), rồi các nền
    `ve:` theo số cảnh. `nhu-canh` dùng lại nền của cảnh khác nên không tạo mục riêng."""
    meta = video.meta
    kho = meta["kho"]
    phong_cach = meta["phong-cach"]
    muc: list = []

    mo_ta_nv = _mo_ta_nhan_vat(meta)
    if mo_ta_nv is not None:
        canh_nhan_vat = [c.so for c in video.canh if parse.tu_the_cua(c, meta) is not None]
        muc.append({
            "file": "nhan-vat-mau.png", "loai": "nhan-vat-mau",
            "prompt": cau_lenh.nhan_vat_mau(mo_ta_nv, phong_cach),
            "kich_thuoc": _KICH_THUOC_NHAN_VAT, "tham_chieu": None, "canh": canh_nhan_vat,
        })
        for ten in parse.TU_THE:
            canh_tu_the = [c.so for c in video.canh if parse.tu_the_cua(c, meta) == ten]
            if not canh_tu_the:
                continue
            muc.append({
                "file": f"tu-the-{ten}.png", "loai": "tu-the",
                "prompt": cau_lenh.tu_the(ten, mo_ta_nv, phong_cach),
                "kich_thuoc": _KICH_THUOC_NHAN_VAT, "tham_chieu": "goc/nhan-vat-mau.png", "canh": canh_tu_the,
            })

    for c in video.canh:
        if c.loai != "ke-chuyen" or c.nen is None or c.nen.get("kieu") != "ai":
            continue
        muc.append({
            "file": f"nen-{c.so}.png", "loai": "nen",
            "prompt": cau_lenh.nen(c.nen["mo_ta"], phong_cach, kho),
            "kich_thuoc": _KICH_THUOC_NEN[kho], "tham_chieu": None, "canh": _canh_dung_nen_ai(video.canh, c.so),
        })
    return muc


def chay_ke_hoach(thu_muc: Path, warnings: list) -> dict:
    md = thu_muc / "video.md"
    if not thu_muc.is_dir() or not md.is_file():
        raise AnhAiError("input", f"Không thấy {md}.", FIX_INPUT)
    video = parse.parse(md.read_text(encoding="utf-8-sig"))
    muc = lap_ke_hoach(video)
    if not muc:
        warnings.append(KHONG_AI)
    duong_dan = thu_muc / "anh" / "ai" / KE_HOACH_TEN
    duong_dan.parent.mkdir(parents=True, exist_ok=True)
    noi_dung = {"phong_cach": video.meta["phong-cach"], "kho": video.meta["kho"], "muc": muc}
    duong_dan.write_text(json.dumps(noi_dung, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    file_tuong_doi = "anh/ai/" + KE_HOACH_TEN
    return {"files": [file_tuong_doi], "so_anh": len(muc), "ke_hoach": file_tuong_doi}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Lập kế hoạch ảnh AI cho video giải thích", add_help=False)
    ap.add_argument("thu_muc")
    ap.add_argument("lenh", choices=("ke-hoach",))
    try:
        args = ap.parse_args(argv)
    except SystemExit:
        emit({"ready": False, "files": [], "so_anh": 0, "ke_hoach": None, "warnings": [],
              "error": {"step": "input", "message": "Sai tham số dòng lệnh.",
                        "fix": "Dùng: python tools/vi/anh_ai.py <thư_mục> ke-hoach"}})
        return 1
    warnings: list = []
    base = {"ready": False, "files": [], "so_anh": 0, "ke_hoach": None}
    try:
        kq = chay_ke_hoach(Path(args.thu_muc).resolve(), warnings)
        emit({**base, **kq, "ready": True, "warnings": warnings, "error": None})
        return 0
    except parse.ParseError as exc:
        error = {"step": "parse", "message": str(exc), "fix": "Sửa đúng dòng đó trong video.md rồi chạy lại."}
    except AnhAiError as exc:
        error = {"step": exc.step, "message": exc.message, "fix": exc.fix}
    except OSError as exc:
        error = {"step": "write", "message": f"Không ghi được file: {exc}", "fix": "Đóng file đang mở và kiểm tra ổ đĩa rồi chạy lại."}
    except Exception as exc:  # noqa: BLE001
        error = {"step": "internal", "message": f"{type(exc).__name__}: {exc}", "fix": FIX_INTERNAL}
    emit({**base, "warnings": warnings, "error": error})
    return 1


if __name__ == "__main__":
    sys.exit(main())
