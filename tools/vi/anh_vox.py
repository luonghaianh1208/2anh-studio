#!/usr/bin/env python3
"""Lập danh sách ảnh và vẽ ảnh AI cho video `phong-cach: vox` qua API kiểu OpenAI (9router mặc định), tìm ảnh thật
(`tim:`), rồi tính trước ảnh đã xử lý (cắt nền viền giấy xé, khung mép xé, duotone, halftone) vào `anh/ai/xu-ly/` và
bảng `anh/ai/vox.json` cho video_ma.

  python tools/vi/anh_vox.py <thư_mục> [--chi-ke-hoach] [--toi-da N] [--cong-cu <tên>] [--mo-hinh <tên>]

stdout đúng một dòng JSON. Hướng dẫn: docs/vi/tro-ly/video-giai-thich.md
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import subprocess
import sys
from dataclasses import asdict, replace
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from anh_vox_parts import ke_hoach, nguon_ve, xu_ly  # noqa: E402
from video_ma_parts import anh, parse  # noqa: E402

ERROR_STEPS = ("input", "parse", "cau-hinh", "mang", "nha-cung-cap", "tach-nen", "write", "internal")
KE_HOACH_TEN = "ke-hoach.json"
NGUON_TEN = "nguon.json"
NGUON_HONG = "nguon.hong.json"
VOX_TEN = "vox.json"   # bảng duy nhất video_ma đọc: "<cảnh>-<nhịp>" -> file đã xử lý, kiểu cuối, nguồn
CAU_VE_LAI = "nền xanh lá #00FF00 tuyệt đối đồng màu, không gradient, không bóng"
FIX_NGUON_THAT = ("Xoá ảnh đó trong `anh/` rồi chạy lại để tìm ảnh khác, hoặc thêm bản ghi nguồn của ảnh vào "
                  "`anh/image_sources.json`.")
TOI_DA_MAC_DINH = 30
SO_LUONG_SONG_SONG = 3
SO_LAN_THU_LAI = 3
FIX_INPUT = "Viết video.md trong thư mục dự án (xem docs/vi/tro-ly/video-giai-thich.md) rồi chạy lại."
FIX_INTERNAL = "Lỗi ngoài dự kiến; dán nguyên thông báo này cho người bảo trì."
CONG_CU_API = "api"
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
            tep = json.loads(f.read_text(encoding="utf-8"))
            khoa = tep.get("khoa") if isinstance(tep, dict) else None
            return khoa if isinstance(khoa, str) and khoa else None
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


def _ghi_ke_hoach(thu_muc: Path, mo_hinh: str | None, ds: list) -> str:
    duong_dan = thu_muc / "anh" / "ai" / KE_HOACH_TEN
    duong_dan.parent.mkdir(parents=True, exist_ok=True)
    muc = []
    for m in ds:
        d = asdict(m)
        d["tuy_chon"] = list(m.tuy_chon)
        d["file_goc"] = str(ke_hoach.file_goc(Path("."), m).as_posix())
        muc.append(d)
    noi_dung = {"mo_hinh": mo_hinh, "muc": muc}
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
    """Lưu ảnh nguồn vẽ trả về thành PNG. Dữ liệu không đọc được thành ảnh là lỗi `nha-cung-cap`, không phải `write`."""
    import io

    from PIL import Image
    try:
        with Image.open(io.BytesIO(data)) as im:
            im.load()
            la_png = im.format == "PNG"
            if not la_png:
                im = im.copy()
    except (OSError, ValueError, Image.DecompressionBombError):
        raise nguon_ve.VeError("nha-cung-cap", nguon_ve.KHONG_PHAI_ANH, nguon_ve.FIX_NCC) from None
    duong_dan.parent.mkdir(parents=True, exist_ok=True)
    if la_png:
        duong_dan.write_bytes(data)
    else:
        im.save(duong_dan, "PNG")


def _nen_tang_ve(ban_ghi) -> bool:
    """Bản ghi nguồn của ảnh nền tảng tự vẽ (mọi `cong_cu` khác `api`): không vẽ lại bằng API dù mô hình khác."""
    return ban_ghi is not None and ban_ghi.get("cong_cu") != CONG_CU_API


def chay(thu_muc: Path, chi_ke_hoach: bool, toi_da: int, warnings: list, cong_cu: str | None = None,
         mo_hinh: str | None = None) -> dict:
    """`cong_cu`, `mo_hinh`: công cụ và mô hình nền tảng đã dùng vẽ ảnh có sẵn trong `anh/ai/goc/` (`--cong-cu`,
    `--mo-hinh`); ghi vào nguồn của ảnh mới và điền vào bản ghi "không rõ" cũ của cùng ảnh."""
    video = _doc_video(thu_muc)
    ds = ke_hoach.lap(video)

    if chi_ke_hoach:
        # Lập kế hoạch không cần cấu hình nguồn vẽ: file cấu hình hỏng không chặn bước này.
        try:
            mo_hinh_ch = nguon_ve.doc_cau_hinh().mo_hinh
        except nguon_ve.VeError:
            mo_hinh_ch = None
        ke_hoach_rel = _ghi_ke_hoach(thu_muc, mo_hinh_ch, ds)
        return {"files": [ke_hoach_rel], "so_anh": len(ds), "da_ve": 0, "dung_lai": 0, "ke_hoach": ke_hoach_rel}

    ch = nguon_ve.doc_cau_hinh()
    ke_hoach_rel = _ghi_ke_hoach(thu_muc, ch.mo_hinh, ds)
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
        if ban_ghi is not None and ban_ghi.get("cong_cu") == CONG_CU_API and ban_ghi.get("mo_hinh") == ch.mo_hinh:
            dung_lai += 1
            continue
        if ban_ghi is not None and not _nen_tang_ve(ban_ghi):
            can_ve.append(m)   # vẽ bằng API với mô hình khác: vẽ lại
            continue
        # Ảnh có sẵn do nền tảng tự vẽ: dùng lại bất kể `ANH_AI_MO_HINH`; ghi (hay điền) công cụ và mô hình đã nêu.
        dung_lai += 1
        if ban_ghi is None or (mo_hinh and ban_ghi.get("mo_hinh") == MO_HINH_NEN_TANG):
            nguon_moi.append({"file": f"ai/goc/{m.ma}.png",
                              "cong_cu": cong_cu or (ban_ghi or {}).get("cong_cu") or CONG_CU_NEN_TANG,
                              "mo_hinh": mo_hinh or MO_HINH_NEN_TANG, "prompt": m.prompt,
                              "ngay": (ban_ghi or {}).get("ngay") or date.today().isoformat(), "ma": m.ma})
        if not mo_hinh and (ban_ghi is None or ban_ghi.get("mo_hinh") == MO_HINH_NEN_TANG):
            warnings.append(f"ảnh ai/goc/{m.ma}.png do nền tảng vẽ, chưa rõ mô hình (thêm `--mo-hinh \"<tên>\"`)")

    if len(can_ve) > toi_da:
        raise AnhVoxError("input", f"Cần vẽ {len(can_ve)} ảnh, quá giới hạn {toi_da}",
                           "Bớt nhịp `anh: ve:` hoặc chạy lại với `--toi-da N`.")

    if nguon_moi:   # nguồn của ảnh nền tảng vẽ: ghi ngay, trước khi vẽ gì
        _ghi_nguon(thu_muc_ai, nguon_moi)
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
                file_goc = ke_hoach.file_goc(thu_muc, m)
                try:
                    # Lưu và ghi nguồn ngay khi mỗi ảnh vẽ xong: ảnh đã trả tiền không mất nếu ảnh khác lỗi sau đó.
                    _luu_anh(f.result(), file_goc)
                except concurrent.futures.CancelledError:
                    continue
                except nguon_ve.VeError as exc:   # lỗi vẽ, hoặc nguồn vẽ trả dữ liệu không phải ảnh
                    if loi_dung is None:
                        loi_dung = exc
                    if not da_huy:
                        pool.shutdown(wait=False, cancel_futures=True)
                        da_huy = True
                    continue
                files.append(str(file_goc.relative_to(thu_muc).as_posix()))
                # Ghi nguồn ngay sau mỗi ảnh (ghi file tạm rồi đổi tên): lượt chạy bị ngắt giữa chừng không làm ảnh
                # API đã vẽ bị ghi nhầm là "do nền tảng vẽ" ở lượt sau.
                _ghi_nguon(thu_muc_ai, [{"file": f"ai/goc/{m.ma}.png", "cong_cu": CONG_CU_API, "mo_hinh": ch.mo_hinh,
                                         "prompt": m.prompt, "ngay": date.today().isoformat(), "ma": m.ma}])
                da_ve += 1

    if loi_dung is not None:
        raise loi_dung

    for m in ds:
        if m.nguon == "tim":
            _tai_anh_that(thu_muc, m, video.meta["kho"])

    nguon_ve_ = {b["ma"]: b for b in _doc_nguon(thu_muc_ai, []) if isinstance(b, dict) and "ma" in b}
    bang = {}
    for m in ds:
        khoa = ke_hoach.khoa(m)
        ma_ke_hoach = m.ma   # mã trước khi vẽ lại: video_ma so với kế hoạch lập lại từ video.md để nhận ra ảnh cũ
        if m.kieu == "cat" and m.nguon == "ve" and not xu_ly.alpha_sach(xu_ly.tach_nen(ke_hoach.file_goc(thu_muc, m))):
            # Ảnh do nền tảng vẽ: không có API để vẽ lại, chuyển thẳng sang khung (xu_ly_muc ghi cảnh báo).
            if not _nen_tang_ve(nguon_ve_.get(m.ma)):
                try:
                    m, ve_moi = _ve_lai(thu_muc, ch, m, nguon_ve_)
                    da_ve += ve_moi
                    files.append(str(ke_hoach.file_goc(thu_muc, m).relative_to(thu_muc).as_posix()))
                except nguon_ve.VeError as exc:
                    loi = _an_khoa_trong_loi({"message": exc.message, "fix": ""})["message"]
                    warnings.append(f"Cảnh {m.canh}, nhịp {m.chi_so + 1}: không vẽ lại được ảnh tách nền chưa sạch "
                                    f"({exc.step}: {loi}).")
        mo_hinh = nguon = None
        if m.nguon == "ve":
            mo_hinh = (nguon_ve_.get(m.ma) or {}).get("mo_hinh") or ch.mo_hinh
        else:
            nguon = _nguon_anh_that(thu_muc, m)
        warnings.extend(xu_ly.xu_ly_muc(thu_muc, m, kho=video.meta["kho"], bang_mau=video.meta["bang-mau"]))
        file_xl = ke_hoach.file_xu_ly(thu_muc, m)
        files.append(str(file_xl.relative_to(thu_muc).as_posix()))
        bang[khoa] = {"file": str(file_xl.relative_to(thu_muc / "anh").as_posix()), "kieu": m.kieu, "ma": m.ma,
                      "ma_ke_hoach": ma_ke_hoach, "tuy_chon": list(m.tuy_chon), "loai_nguon": m.nguon,
                      "mo_hinh": mo_hinh, "nguon": nguon}
    duong_bang = thu_muc_ai / VOX_TEN
    duong_bang.parent.mkdir(parents=True, exist_ok=True)
    tam = duong_bang.with_name(VOX_TEN + ".tam")
    tam.write_text(json.dumps(bang, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    os.replace(tam, duong_bang)
    files.append("anh/ai/" + VOX_TEN)

    return {"files": list(dict.fromkeys(files)), "so_anh": len(ds), "da_ve": da_ve, "dung_lai": dung_lai, "ke_hoach": ke_hoach_rel}


def _ve_lai(thu_muc: Path, ch: nguon_ve.CauHinh, m, nguon_ve_: dict) -> tuple:
    """Ảnh cắt nền tách chưa sạch: vẽ lại đúng một lần với câu lệnh chặt hơn (mã băm mới, ghi nguon.json). Ảnh vẽ lại
    đã có (lượt trước, cùng mô hình hoặc do nền tảng vẽ) thì dùng lại. Trả (mục mới, số ảnh vừa vẽ)."""
    prompt = f"{m.prompt}, {CAU_VE_LAI}"
    m2 = replace(m, prompt=prompt, ma=ke_hoach.ma_anh(prompt, m.kich_thuoc))
    goc = ke_hoach.file_goc(thu_muc, m2)
    ban_ghi = nguon_ve_.get(m2.ma)
    if goc.is_file() and ban_ghi is not None and (ban_ghi.get("mo_hinh") == ch.mo_hinh or _nen_tang_ve(ban_ghi)):
        return m2, 0
    log(f"Ảnh cảnh {m.canh} tách nền chưa sạch, vẽ lại một lần với nền xanh chặt hơn...")
    _luu_anh(_ve_mot_anh(ch, m2, 1, 1), goc)
    ban_ghi = {"file": f"ai/goc/{m2.ma}.png", "cong_cu": CONG_CU_API, "mo_hinh": ch.mo_hinh, "prompt": prompt,
               "ngay": date.today().isoformat(), "ma": m2.ma}
    _ghi_nguon(thu_muc / "anh" / "ai", [ban_ghi])
    nguon_ve_[m2.ma] = ban_ghi
    return m2, 1


def _tai_anh_that(thu_muc: Path, m, kho: str) -> None:
    """`anh: tim:` -> chạy image_search.py của skill (chỉ chạy, không sửa) vào `anh/`; đã có file thì bỏ qua."""
    dich = ke_hoach.file_goc(thu_muc, m)
    if dich.is_file():
        return
    script = Path(__file__).resolve().parents[2] / "skills" / "ppt-master" / "scripts" / "image_search.py"
    cmd = [sys.executable, str(script), m.prompt, "--filename", dich.name,
           "--orientation", "landscape" if kho == "ngang" else "portrait", "-o", str(dich.parent)]
    log(f"Tìm ảnh thật \"{m.prompt}\" (cảnh {m.canh})...")
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
        hong = proc.returncode != 0
    except (OSError, subprocess.TimeoutExpired):
        hong = True
    if hong or not dich.is_file():
        raise nguon_ve.VeError("mang", f"Không tìm được ảnh thật cho \"{m.prompt}\" (cảnh {m.canh}).",
                               "Đổi từ khoá `tim:` (tiếng Anh, cụ thể hơn) hoặc dùng `anh: ve:`.")


def _nguon_anh_that(thu_muc: Path, m) -> str | None:
    """Dòng nguồn ảnh thật/ảnh có sẵn từ `anh/image_sources.json` (cùng cách video_ma đọc). Ảnh `tim:` bắt buộc có."""
    ten = ke_hoach.file_goc(thu_muc, m).name
    try:
        nguon = anh._nguon_tu_manifest(thu_muc, ten)
    except anh.AnhError as exc:
        if m.nguon != "tim":
            return None
        raise nguon_ve.VeError("nha-cung-cap", f"Ảnh thật chưa có nguồn: {exc}.", FIX_NGUON_THAT) from None
    if not nguon and m.nguon == "tim":
        raise nguon_ve.VeError("nha-cung-cap", f"Ảnh thật chưa có nguồn: `anh/{ten}` không có bản ghi trong "
                                               "`anh/image_sources.json`.", FIX_NGUON_THAT)
    return nguon or None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Lập danh sách và vẽ ảnh AI cho video Vox", add_help=False)
    ap.add_argument("thu_muc")
    ap.add_argument("--chi-ke-hoach", action="store_true")
    ap.add_argument("--toi-da", type=int, default=TOI_DA_MAC_DINH)
    ap.add_argument("--cong-cu")
    ap.add_argument("--mo-hinh")
    base = {"ready": False, "files": [], "so_anh": 0, "da_ve": 0, "dung_lai": 0, "ke_hoach": None}
    try:
        args = ap.parse_args(argv)
    except SystemExit:
        emit({**base, "warnings": [],
              "error": {"step": "input", "message": "Sai tham số dòng lệnh.",
                        "fix": "Dùng: python tools/vi/anh_vox.py <thư_mục> [--chi-ke-hoach] [--toi-da N] "
                               "[--cong-cu <tên>] [--mo-hinh <tên>]"}})
        return 1
    warnings: list = []
    try:
        thu_muc = Path(args.thu_muc).resolve()
        kq = chay(thu_muc, args.chi_ke_hoach, args.toi_da, warnings, cong_cu=(args.cong_cu or "").strip() or None,
                  mo_hinh=(args.mo_hinh or "").strip() or None)
        emit({**base, **kq, "ready": True, "warnings": warnings, "error": None})
        return 0
    except parse.ParseError as exc:
        error = {"step": "parse", "message": str(exc), "fix": "Sửa đúng dòng đó trong video.md rồi chạy lại."}
    except (AnhVoxError, nguon_ve.VeError, xu_ly.XuLyError) as exc:
        error = {"step": exc.step, "message": exc.message, "fix": exc.fix}
    except OSError as exc:
        error = {"step": "write", "message": f"Không ghi được file: {exc}", "fix": "Đóng file đang mở và kiểm tra ổ đĩa rồi chạy lại."}
    except Exception as exc:  # noqa: BLE001
        error = {"step": "internal", "message": f"{type(exc).__name__}: {exc}", "fix": FIX_INTERNAL}
    emit({**base, "warnings": warnings, "error": _an_khoa_trong_loi(error)})
    return 1


if __name__ == "__main__":
    sys.exit(main())
