#!/usr/bin/env python3
"""Lập danh sách ảnh và vẽ ảnh AI cho video `phong-cach: vox` qua API kiểu OpenAI (9router mặc định).

  python tools/vi/anh_vox.py <thư_mục> [--chi-ke-hoach] [--toi-da N]

stdout đúng một dòng JSON. Hướng dẫn: docs/vi/tro-ly/video-vox.md
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import sys
from dataclasses import asdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from anh_vox_parts import ke_hoach, nguon_ve  # noqa: E402
from video_ma_parts import parse  # noqa: E402

ERROR_STEPS = ("input", "parse", "cau-hinh", "mang", "nha-cung-cap", "tach-nen", "write", "internal")
KE_HOACH_TEN = "ke-hoach.json"
NGUON_TEN = "nguon.json"
NGUON_HONG = "nguon.hong.json"
TOI_DA_MAC_DINH = 20
SO_LUONG_SONG_SONG = 3
SO_LAN_THU_LAI = 3
FIX_INPUT = "Viết video.md trong thư mục dự án (xem docs/vi/tro-ly/video-vox.md) rồi chạy lại."
FIX_INTERNAL = "Lỗi ngoài dự kiến; dán nguyên thông báo này cho người bảo trì."
CONG_CU_NEN_TANG = "nen-tang"
MO_HINH_NEN_TANG = "không rõ"


class AnhVoxError(Exception):
    def __init__(self, step: str, message: str, fix: str) -> None:
        super().__init__(message)
        self.step = step
        self.message = message
        self.fix = fix


def log(text: str) -> None:
    print(text, file=sys.stderr, flush=True)


def _khoa_tho_de_an() -> str | None:
    """Khoá thô đọc trực tiếp từ môi trường/file cấu hình, chỉ để che trong thông báo lỗi — kể cả khi
    `doc_cau_hinh` không chạy tới hoặc chính nó từ chối khoá này."""
    khoa = os.environ.get("ANH_AI_KEY")
    if khoa:
        return khoa
    try:
        f = Path.home() / ".2anh-studio" / "anh-ai.json"
        if f.is_file():
            return json.loads(f.read_text(encoding="utf-8")).get("khoa")
    except (OSError, ValueError):
        return None
    return None


def _an_khoa_trong_loi(error: dict) -> dict:
    khoa = _khoa_tho_de_an()
    if not khoa:
        return error
    return {**error, "message": error["message"].replace(khoa, "***"), "fix": error["fix"].replace(khoa, "***")}


def emit(payload: dict) -> None:
    text = json.dumps(payload, ensure_ascii=False) + "\n"
    try:
        sys.stdout.write(text)
    except UnicodeEncodeError:
        sys.stdout.buffer.write(text.encode("utf-8", errors="replace"))
    sys.stdout.flush()


def _doc_video(thu_muc: Path) -> parse.Video:
    md = thu_muc / "video.md"
    if not thu_muc.is_dir() or not md.is_file():
        raise AnhVoxError("input", f"Không thấy {md}.", FIX_INPUT)
    video = parse.parse(md.read_text(encoding="utf-8-sig"))
    if video.meta["phong-cach"] != "vox":
        raise AnhVoxError("input", "anh_vox.py chỉ dùng cho video `phong-cach: vox`.",
                           "Dựng video này bằng `tools/vi/video_ma.py` thay vì `anh_vox.py`.")
    return video


def _ghi_ke_hoach(thu_muc: Path, ch: nguon_ve.CauHinh, ds: list) -> str:
    duong_dan = thu_muc / "anh" / "ai" / KE_HOACH_TEN
    duong_dan.parent.mkdir(parents=True, exist_ok=True)
    muc = []
    for m in ds:
        d = asdict(m)
        d["tuy_chon"] = list(m.tuy_chon)
        d["file_goc"] = str(ke_hoach.file_goc(Path("."), m).as_posix())
        muc.append(d)
    noi_dung = {"mo_hinh": ch.mo_hinh, "muc": muc}
    duong_dan.write_text(json.dumps(noi_dung, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return "anh/ai/" + KE_HOACH_TEN


def _doc_nguon(thu_muc_ai: Path, warnings: list) -> list:
    duong_dan = thu_muc_ai / NGUON_TEN
    if not duong_dan.is_file():
        return []
    try:
        nguon = json.loads(duong_dan.read_text(encoding="utf-8-sig"))
    except ValueError:
        nguon = None
    if not isinstance(nguon, list):
        os.replace(duong_dan, thu_muc_ai / NGUON_HONG)
        warnings.append(f"`anh/ai/{NGUON_TEN}` cũ hỏng hoặc sai cấu trúc (cần danh sách); đã cất sang "
                        f"`anh/ai/{NGUON_HONG}` và ghi lại nguồn của các ảnh vẽ ở lượt này.")
        return []
    return nguon


def _ghi_nguon(thu_muc_ai: Path, moi: list) -> None:
    duong_dan = thu_muc_ai / NGUON_TEN
    cu = {b["ma"]: b for b in (_doc_nguon(thu_muc_ai, []) or []) if isinstance(b, dict) and "ma" in b}
    for b in moi:
        cu[b["ma"]] = b
    tam = duong_dan.with_name(NGUON_TEN + ".tam")
    tam.write_text(json.dumps(list(cu.values()), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tam, duong_dan)


def _ve_mot_anh(ch: nguon_ve.CauHinh, m, chi_muc: int, tong: int) -> bytes:
    log(f"Vẽ ảnh {chi_muc}/{tong} (cảnh {m.canh})...")
    for lan in range(SO_LAN_THU_LAI):
        try:
            return nguon_ve.ve(ch, m.prompt, m.kich_thuoc)
        except nguon_ve.VeError as exc:
            if not exc.thu_lai or lan == SO_LAN_THU_LAI - 1:
                raise


def _luu_anh(data: bytes, duong_dan: Path) -> None:
    duong_dan.parent.mkdir(parents=True, exist_ok=True)
    chu_ki = data[:12]
    if chu_ki.startswith(b"\x89PNG"):
        duong_dan.write_bytes(data)
        return
    from PIL import Image
    import io
    im = Image.open(io.BytesIO(data))
    im.save(duong_dan, "PNG")


def chay(thu_muc: Path, chi_ke_hoach: bool, toi_da: int, warnings: list) -> dict:
    video = _doc_video(thu_muc)
    ds = ke_hoach.lap(video)
    ch = nguon_ve.doc_cau_hinh()
    ke_hoach_rel = _ghi_ke_hoach(thu_muc, ch, ds)

    if chi_ke_hoach:
        return {"files": [ke_hoach_rel], "so_anh": len(ds), "da_ve": 0, "dung_lai": 0, "ke_hoach": ke_hoach_rel}

    thu_muc_ai = thu_muc / "anh" / "ai"
    nguon_cu = {b["ma"]: b for b in _doc_nguon(thu_muc_ai, warnings) if isinstance(b, dict) and "ma" in b}

    can_ve = []
    dung_lai = 0
    nguon_moi: list = []
    for m in ds:
        if m.nguon != "ve":
            continue
        file_goc = ke_hoach.file_goc(thu_muc, m)
        if not file_goc.is_file():
            can_ve.append(m)
            continue
        ban_ghi = nguon_cu.get(m.ma)
        if ban_ghi is not None and ban_ghi.get("mo_hinh") == ch.mo_hinh:
            dung_lai += 1
            continue
        # Ảnh do nền tảng tự vẽ (chưa rõ mô hình): dùng lại bất kể `ANH_AI_MO_HINH` hiện tại là gì.
        if ban_ghi is not None and ban_ghi.get("cong_cu") == CONG_CU_NEN_TANG:
            dung_lai += 1
            warnings.append(f"ảnh ai/goc/{m.ma}.png do nền tảng vẽ, chưa rõ mô hình")
            continue
        if ban_ghi is None:
            dung_lai += 1
            ban_ghi_moi = {"file": f"ai/goc/{m.ma}.png", "cong_cu": CONG_CU_NEN_TANG,
                           "mo_hinh": MO_HINH_NEN_TANG, "prompt": m.prompt, "ngay": date.today().isoformat(), "ma": m.ma}
            nguon_moi.append(ban_ghi_moi)
            warnings.append(f"ảnh ai/goc/{m.ma}.png do nền tảng vẽ, chưa rõ mô hình")
            continue
        can_ve.append(m)

    if len(can_ve) > toi_da:
        raise AnhVoxError("input", f"Cần vẽ {len(can_ve)} ảnh, quá giới hạn {toi_da}",
                           "Bớt nhịp `anh: ve:` hoặc chạy lại với `--toi-da N`.")

    files = [str(ke_hoach.file_goc(thu_muc, m).relative_to(thu_muc).as_posix())
             for m in ds if m.nguon == "ve" and ke_hoach.file_goc(thu_muc, m).is_file()]
    da_ve = 0
    loi_dung = None
    if can_ve:
        tong = len(can_ve)
        da_huy = False
        with concurrent.futures.ThreadPoolExecutor(SO_LUONG_SONG_SONG) as pool:
            tuong_lai = {pool.submit(_ve_mot_anh, ch, m, i + 1, tong): m for i, m in enumerate(can_ve)}
            for f in concurrent.futures.as_completed(tuong_lai):
                m = tuong_lai[f]
                try:
                    data = f.result()
                except concurrent.futures.CancelledError:
                    continue
                except nguon_ve.VeError as exc:
                    if loi_dung is None:
                        loi_dung = exc
                    if not da_huy:
                        pool.shutdown(wait=False, cancel_futures=True)
                        da_huy = True
                    continue
                # Lưu và ghi nguồn ngay khi mỗi ảnh vẽ xong: ảnh đã trả tiền không mất nếu ảnh khác lỗi sau đó.
                file_goc = ke_hoach.file_goc(thu_muc, m)
                _luu_anh(data, file_goc)
                files.append(str(file_goc.relative_to(thu_muc).as_posix()))
                nguon_moi.append({"file": f"ai/goc/{m.ma}.png", "cong_cu": "api", "mo_hinh": ch.mo_hinh,
                                  "prompt": m.prompt, "ngay": date.today().isoformat(), "ma": m.ma})
                da_ve += 1

    if nguon_moi:
        _ghi_nguon(thu_muc_ai, nguon_moi)

    if loi_dung is not None:
        raise loi_dung

    return {"files": files, "so_anh": len(ds), "da_ve": da_ve, "dung_lai": dung_lai, "ke_hoach": ke_hoach_rel}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Lập danh sách và vẽ ảnh AI cho video Vox", add_help=False)
    ap.add_argument("thu_muc")
    ap.add_argument("--chi-ke-hoach", action="store_true")
    ap.add_argument("--toi-da", type=int, default=TOI_DA_MAC_DINH)
    base = {"ready": False, "files": [], "so_anh": 0, "da_ve": 0, "dung_lai": 0, "ke_hoach": None}
    try:
        args = ap.parse_args(argv)
    except SystemExit:
        emit({**base, "warnings": [],
              "error": {"step": "input", "message": "Sai tham số dòng lệnh.",
                        "fix": "Dùng: python tools/vi/anh_vox.py <thư_mục> [--chi-ke-hoach] [--toi-da N]"}})
        return 1
    warnings: list = []
    try:
        thu_muc = Path(args.thu_muc).resolve()
        kq = chay(thu_muc, args.chi_ke_hoach, args.toi_da, warnings)
        emit({**base, **kq, "ready": True, "warnings": warnings, "error": None})
        return 0
    except parse.ParseError as exc:
        error = {"step": "parse", "message": str(exc), "fix": "Sửa đúng dòng đó trong video.md rồi chạy lại."}
    except (AnhVoxError, nguon_ve.VeError) as exc:
        error = {"step": exc.step, "message": exc.message, "fix": exc.fix}
    except OSError as exc:
        error = {"step": "write", "message": f"Không ghi được file: {exc}", "fix": "Đóng file đang mở và kiểm tra ổ đĩa rồi chạy lại."}
    except Exception as exc:  # noqa: BLE001
        error = {"step": "internal", "message": f"{type(exc).__name__}: {exc}", "fix": FIX_INTERNAL}
    emit({**base, "warnings": warnings, "error": _an_khoa_trong_loi(error)})
    return 1


if __name__ == "__main__":
    sys.exit(main())
