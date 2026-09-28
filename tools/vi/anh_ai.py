#!/usr/bin/env python3
"""Lập kế hoạch và nhận ảnh AI cho video giải thích, dựng từ `video.md` (nền `ve:`, nhân vật `nhan-vat: ve:`).

  python tools/vi/anh_ai.py <thư_mục> ke-hoach
  python tools/vi/anh_ai.py <thư_mục> nhan [--cong-cu <tên>] [--mo-hinh <tên>]

stdout đúng một dòng JSON. Hướng dẫn: docs/vi/tro-ly/video-giai-thich.md
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from anh_ai_parts import cau_lenh, xu_ly  # noqa: E402
from video_ma_parts import parse  # noqa: E402

FIX_INPUT = "Viết video.md trong thư mục dự án (xem docs/vi/tro-ly/video-giai-thich.md) rồi chạy lại."
FIX_INTERNAL = "Lỗi ngoài dự kiến; dán nguyên thông báo này cho người bảo trì."
KE_HOACH_TEN = "ke-hoach.json"
KHONG_AI = "Video không dùng ảnh AI."
NGUON_TEN = "nguon.json"
NGUON_HONG = "nguon.hong.json"
CONG_CU_MAC_DINH = "công cụ vẽ của nền tảng"
MO_HINH_MAC_DINH = "AI"
FIX_KE_HOACH = "Chạy `python tools/vi/anh_ai.py <thư_mục> ke-hoach` trước, vẽ ảnh theo kế hoạch, rồi chạy lại `nhan`."

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


_LOAI_MUC = ("nen", "nhan-vat-mau", "tu-the")


def _muc_hop_le(muc) -> bool:
    return (isinstance(muc, dict) and isinstance(muc.get("file"), str) and muc["file"]
            and "/" not in muc["file"] and "\\" not in muc["file"] and ".." not in muc["file"]
            and muc.get("loai") in _LOAI_MUC and isinstance(muc.get("prompt"), str)
            and isinstance(muc.get("canh"), list) and all(isinstance(c, int) for c in muc["canh"])
            and (muc["loai"] != "nen" or bool(muc["canh"])))


def _doc_ke_hoach(thu_muc: Path) -> dict:
    duong_dan = thu_muc / "anh" / "ai" / KE_HOACH_TEN
    if not thu_muc.is_dir() or not duong_dan.is_file():
        raise xu_ly.XuLyError("input", f"Không thấy {duong_dan}.", FIX_KE_HOACH)
    try:
        ke_hoach = json.loads(duong_dan.read_text(encoding="utf-8-sig"))
        if ke_hoach["kho"] not in xu_ly.KHO_XUAT or not isinstance(ke_hoach["muc"], list):
            raise ValueError("sai cấu trúc")
    except (ValueError, KeyError, TypeError) as exc:
        raise xu_ly.XuLyError("input", f"`anh/ai/{KE_HOACH_TEN}` hỏng ({exc}).", FIX_KE_HOACH) from exc
    sai = [k + 1 for k, m in enumerate(ke_hoach["muc"]) if not _muc_hop_le(m)]
    if sai:
        raise xu_ly.XuLyError("input", f"`anh/ai/{KE_HOACH_TEN}` hỏng: mục thứ {', '.join(map(str, sai))} thiếu hoặc sai "
                              "`file`, `loai`, `canh` hay `prompt`.", FIX_KE_HOACH)
    return ke_hoach


def ten_dau_ra(muc: dict) -> str:
    """Tên file đầu ra trong anh/ai/: nền -> `nen-<số cảnh đầu tiên>.jpg`; nhân vật -> `<tên gốc>.png`."""
    if muc["loai"] == "nen":
        return f"nen-{muc['canh'][0]}.jpg"
    return Path(muc["file"]).stem + ".png"


def _ghi_nguon(thu_muc_ai: Path, moi: list, bo: set, warnings: list) -> None:
    """Ghi nguyên tử anh/ai/nguon.json: giữ bản ghi cũ của file khác, thay bản ghi cùng tên file, bỏ bản ghi của các
    file trong `bo` (lượt này hỏng, đầu ra cũ đã xoá). File cũ hỏng hoặc sai cấu trúc: cất sang `nguon.hong.json` và
    cảnh báo, không thay im lặng."""
    duong_dan = thu_muc_ai / NGUON_TEN
    cu: list = []
    if duong_dan.is_file():
        try:
            cu = json.loads(duong_dan.read_text(encoding="utf-8-sig"))
        except ValueError:
            cu = None
        if not isinstance(cu, list):
            os.replace(duong_dan, thu_muc_ai / NGUON_HONG)
            warnings.append(f"`anh/ai/{NGUON_TEN}` cũ hỏng hoặc sai cấu trúc (cần danh sách); đã cất sang "
                            f"`anh/ai/{NGUON_HONG}` và ghi lại nguồn của các ảnh nhận ở lượt này.")
            cu = []
    bo = bo | {m["file"] for m in moi}
    giu = [m for m in cu if not (isinstance(m, dict) and m.get("file") in bo)]
    tam = duong_dan.with_name(NGUON_TEN + ".tam")
    tam.write_text(json.dumps(giu + moi, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tam, duong_dan)


def chay_nhan(thu_muc: Path, warnings: list, cong_cu: str | None = None, mo_hinh: str | None = None,
              run=subprocess.run, which=shutil.which, hom_nay: str | None = None) -> dict:
    """Nhận mọi ảnh trong kế hoạch từ anh/ai/goc/: nền -> anh/ai/nen-<N>.jpg, nhân vật -> anh/ai/<tên>.png trong suốt;
    ghi nguồn vào anh/ai/nguon.json. File thiếu gộp một lỗi `thieu`; ảnh tách nền hỏng gộp một lỗi `tach-nen`.
    Khi một mục lỗi: vẫn ghi nguồn của các mục đã xong ở lượt này, và xoá đầu ra cũ của mục lỗi (để video_ma báo
    thiếu thay vì dùng nhầm ảnh cũ)."""
    ke_hoach = _doc_ke_hoach(thu_muc)
    thu_muc_ai = thu_muc / "anh" / "ai"
    thu_muc_goc = thu_muc_ai / "goc"
    cac_muc = ke_hoach["muc"]
    goc = {m["file"]: xu_ly.tim_goc(thu_muc_goc, m["file"]) for m in cac_muc}
    thieu = [f for f, p in goc.items() if p is None]
    if thieu:
        raise xu_ly.XuLyError("thieu", f"Thiếu {len(thieu)} ảnh trong `anh/ai/goc/`: "
                              + ", ".join(f"`goc/{f}`" for f in thieu) + ".", xu_ly.FIX_THIEU)
    if not cac_muc:
        warnings.append(KHONG_AI)
        return {"files": [], "so_anh": 0, "ke_hoach": f"anh/ai/{KE_HOACH_TEN}"}
    if which("ffmpeg") is None or which("ffprobe") is None:
        raise xu_ly.XuLyError("ffmpeg", "Máy chưa có FFmpeg (ffmpeg, ffprobe).", xu_ly.FIX_FFMPEG)
    ngay = hom_nay or datetime.date.today().isoformat()
    files, nguon, hong, loi_dung = [], [], [], None
    bo: set = set()
    for muc in cac_muc:
        ra = ten_dau_ra(muc)
        ten = f"goc/{goc[muc['file']].name}"
        try:
            if muc["loai"] == "nen":
                (w, h), _, thieu_diem = xu_ly.xu_ly_nen(goc[muc["file"]], thu_muc_ai / ra, ke_hoach["kho"], ten, run)
                if thieu_diem:
                    warnings.append(f"Ảnh nền cảnh {muc['canh'][0]} nhỏ hơn Full HD ({w}x{h}).")
            else:
                xu_ly.xu_ly_nhan_vat(goc[muc["file"]], thu_muc_ai / ra, ten, run)
        except xu_ly.XuLyError as exc:
            (thu_muc_ai / ra).unlink(missing_ok=True)
            bo.add(ra)
            if exc.step != "tach-nen":
                loi_dung = exc
                break
            hong.append(exc.message)
            continue
        files.append(f"anh/ai/{ra}")
        nguon.append({"file": ra, "cong_cu": cong_cu or CONG_CU_MAC_DINH, "mo_hinh": mo_hinh or MO_HINH_MAC_DINH,
                      "prompt": muc["prompt"], "ngay": ngay})
    _ghi_nguon(thu_muc_ai, nguon, bo, warnings)
    if loi_dung is not None:
        raise loi_dung
    if hong:
        raise xu_ly.XuLyError("tach-nen", f"Tách nền không sạch {len(hong)} ảnh nhân vật: " + " ".join(hong),
                              xu_ly.FIX_TACH_NEN)
    files.append(f"anh/ai/{NGUON_TEN}")
    return {"files": files, "so_anh": len(nguon), "ke_hoach": f"anh/ai/{KE_HOACH_TEN}"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Lập kế hoạch ảnh AI cho video giải thích", add_help=False)
    ap.add_argument("thu_muc")
    ap.add_argument("lenh", choices=("ke-hoach", "nhan"))
    ap.add_argument("--cong-cu")
    ap.add_argument("--mo-hinh")
    try:
        args = ap.parse_args(argv)
    except SystemExit:
        emit({"ready": False, "files": [], "so_anh": 0, "ke_hoach": None, "warnings": [],
              "error": {"step": "input", "message": "Sai tham số dòng lệnh.",
                        "fix": "Dùng: python tools/vi/anh_ai.py <thư_mục> ke-hoach|nhan "
                               "[--cong-cu <tên>] [--mo-hinh <tên>]"}})
        return 1
    warnings: list = []
    base = {"ready": False, "files": [], "so_anh": 0, "ke_hoach": None}
    try:
        thu_muc = Path(args.thu_muc).resolve()
        if args.lenh == "nhan":
            kq = chay_nhan(thu_muc, warnings, cong_cu=args.cong_cu, mo_hinh=args.mo_hinh)
        else:
            kq = chay_ke_hoach(thu_muc, warnings)
        emit({**base, **kq, "ready": True, "warnings": warnings, "error": None})
        return 0
    except parse.ParseError as exc:
        error = {"step": "parse", "message": str(exc), "fix": "Sửa đúng dòng đó trong video.md rồi chạy lại."}
    except (AnhAiError, xu_ly.XuLyError) as exc:
        error = {"step": exc.step, "message": exc.message, "fix": exc.fix}
    except OSError as exc:
        error = {"step": "write", "message": f"Không ghi được file: {exc}", "fix": "Đóng file đang mở và kiểm tra ổ đĩa rồi chạy lại."}
    except Exception as exc:  # noqa: BLE001
        error = {"step": "internal", "message": f"{type(exc).__name__}: {exc}", "fix": FIX_INTERNAL}
    emit({**base, "warnings": warnings, "error": error})
    return 1


if __name__ == "__main__":
    sys.exit(main())
