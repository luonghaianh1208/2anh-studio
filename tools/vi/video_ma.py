#!/usr/bin/env python3
"""Dựng video giải thích từ video.md (kiểu Vox, hay kịch bản cũ viết tay / cắt dán): giọng đọc, cảnh vẽ bằng mã, phụ đề.

  python tools/vi/video_ma.py <thư_mục> [--plan-only] [--xem-truoc]

stdout đúng một dòng JSON. Hướng dẫn: docs/vi/tro-ly/video-giai-thich.md
"""

from __future__ import annotations

import argparse
import contextlib
import dataclasses
import importlib.util
import json
import os
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from thi_nghiem_parts import thu_vien  # noqa: E402
from video_ma_parts import anh, chup, ghep, giong, hinh, kho, kiem, lich, parse, thoi_luong, trang, vox  # noqa: E402
from video_parts import media  # noqa: E402

FIX_INPUT = "Viết video.md trong thư mục dự án (xem docs/vi/tro-ly/video-giai-thich.md) rồi chạy lại."
FIX_INTERNAL = "Lỗi ngoài dự kiến; dán nguyên thông báo này cho người bảo trì."
FIX_CHUP = "Chạy lại một lần; vẫn lỗi thì dán nguyên thông báo này cho người bảo trì."
FIX_CANH = "Rút gọn hoặc sửa nội dung cảnh đó theo thông báo."
FIX_NHAC = ("Sửa nhạc nền theo thông báo: dòng `nhac-nen` (tên file nằm trong nhac/) và `nguon-nhac` ở khối thông tin đầu "
            "video.md, hoặc bản ghi của file trong nhac/nguon.json; không cần nhạc nền thì xoá dòng `nhac-nen`.")
FIX_NGUON_NHAC = ("Rút gọn dòng nguồn nhạc: ghi `nguon-nhac:` ngắn hơn ở khối thông tin đầu video.md (tên bản · tác giả · "
                  "giấy phép), hoặc rút gọn title/creator của file trong nhac/nguon.json, rồi chạy lại.")
FIX_NGUON_DE = ("Rút gọn dòng `tai-lieu` hoặc chữ của cảnh cuối, hoặc ghi `nguon-nhac:` ngắn hơn ở khối thông tin đầu "
                "video.md, rồi chạy lại.")
FIX_PHAN = "Tách công thức thành nhiều phần bằng ` | ` (mỗi phần hiện liền một khối), hoặc rút gọn phần đó."
FIX_TAI_LIEU = "Rút gọn nội dung cảnh (chữ ở góc phải dưới) hoặc dòng `tai-lieu`, rồi chạy lại."
GIONG_TAM = 8.0


def log(text: str) -> None:
    print(text, file=sys.stderr, flush=True)


def emit(payload: dict) -> None:
    text = json.dumps(payload, ensure_ascii=False) + "\n"
    try:
        sys.stdout.write(text)
    except UnicodeEncodeError:
        sys.stdout.buffer.write(text.encode("utf-8", errors="replace"))
    sys.stdout.flush()


def co_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


def co_chromium() -> bool:
    root = os.environ.get("LOCALAPPDATA")
    if not root:
        return False
    base = Path(root) / "ms-playwright"
    if not (base.is_dir() and (any(base.glob("chromium-*")) or any(base.glob("chromium_headless_shell-*")))):
        return False
    return importlib.util.find_spec("playwright") is not None


def _mo_hinh(video: parse.Video, thu_muc: Path) -> dict:
    return {c.so: thu_vien.load(c.truong["mau"][0], thu_muc) for c in video.canh if c.loai == "thi-nghiem"}


def _nen(scene: parse.Scene, thu_muc: Path):
    """Nền của cảnh ke-chuyen cho trang: {kieu: 'mau', ten, hat} hoặc {kieu: 'anh', dataUrl, rong, cao, nguon, moHinh?}.
    Nền AI không có dòng nguồn trong cảnh (`nguon` None): dòng "tạo bằng AI" hiện cuối video."""
    nen = kiem.nen_goc(scene)
    if nen["kieu"] == "mau":
        # Hạt giống của nền mẫu là số cảnh gốc: `nhu-canh` dùng lại đúng hình của cảnh đó.
        return {"kieu": "mau", "ten": nen["ten"], "hat": scene.nen["canh"] if scene.nen["kieu"] == "nhu" else scene.so}
    ten = nen["file"] if nen["kieu"] == "file" else kiem.file_ai(thu_muc, nen["file"])
    a = anh.doc(thu_muc, ten, None)
    ra = {"kieu": "anh", "dataUrl": a["dataUrl"], "rong": a["rong"], "cao": a["cao"], "nguon": None if a.get("ai") else a["nguon"]}
    if a.get("ai"):
        ra["moHinh"] = a["moHinh"]
    return ra


def _nhan_vat_anh(scene: parse.Scene, thu_muc: Path, meta: dict):
    """Ảnh nhân vật AI của cảnh ({dataUrl, rong, cao, moHinh}), None khi không có nhân vật AI."""
    tu_the = parse.tu_the_cua(scene, meta)
    if not tu_the or not meta.get("nhan-vat", "").startswith("ve:"):
        return None
    a = anh.doc(thu_muc, kiem.file_ai(thu_muc, f"ai/tu-the-{tu_the}.png"), None)
    return {"dataUrl": a["dataUrl"], "rong": a["rong"], "cao": a["cao"], "moHinh": a["moHinh"]}


def _tai_nguyen(scene: parse.Scene, thu_muc: Path, meta: dict | None = None) -> dict:
    if scene.loai == "vox":
        return vox.tai_nguyen(scene, thu_muc)
    them = {}
    if scene.nen is not None:
        them["nen"] = _nen(scene, thu_muc)
    nv = _nhan_vat_anh(scene, thu_muc, meta or {})
    if nv:
        them["nhanVatAnh"] = nv
    return {**_tai_nguyen_cot(scene, thu_muc), **them}


def _tai_nguyen_cot(scene: parse.Scene, thu_muc: Path) -> dict:
    if scene.loai == "minh-hoa":
        hinhs = []
        for value in scene.truong["hinh"]:
            ten, nhan = hinh.tach_minh_hoa(value)
            hinhs.append({**hinh.doc(ten), "nhan": nhan})
        return {"hinh": None, "anh": None, "hinhs": hinhs}
    if "hinh" in scene.truong:
        return {"hinh": hinh.doc(scene.truong["hinh"][0]), "anh": None, "hinhs": []}
    if "anh" in scene.truong:
        nguon_tay = scene.truong.get("nguon", [None])[0]
        return {"hinh": None, "anh": anh.doc(thu_muc, scene.truong["anh"][0], nguon_tay), "hinhs": []}
    return {"hinh": None, "anh": None, "hinhs": []}


def _cac_du(video, cac_lich, models, thu_muc: Path, nhac=None) -> list:
    """`nhac`: nhạc nền (`kiem.doc_nhac`). Cảnh cuối mang các dòng nguồn cuối video: "Hình minh hoạ tạo bằng AI (…)"
    khi video có ảnh AI (nền, nhân vật hay trường `anh`), rồi nguồn nhạc."""
    cac_tn = [_tai_nguyen(c, thu_muc, video.meta) for c in video.canh]
    cac_du = [lich.du_lieu_canh(c, cl, models.get(c.so), {**tn, "meta": video.meta})
              for c, cl, tn in zip(video.canh, cac_lich, cac_tn)]
    # Mọi ảnh AI được ghi công: nền, nhân vật, và ảnh `ai/…` dùng ở trường `anh:` thường.
    mo_hinh = [a["moHinh"] for tn in cac_tn for a in (tn.get("nen"), tn.get("nhanVatAnh"), tn.get("anh"))
               if a and a.get("moHinh")]
    mo_hinh += [a["moHinh"] for scene, tn in zip(video.canh, cac_tn) if scene.loai == "vox"
                for a in (tn.get("anh") or {}).values() if a and a.get("moHinh")]
    dongs = ([lich.dong_ai(mo_hinh)] if mo_hinh else []) + ([nhac["nguon"]] if nhac is not None else [])
    if video.meta["phong-cach"] == "vox":
        dongs = []   # Vox không hiện nguồn nào trên hình: mọi nguồn ghi vào nguon.txt cạnh video
    if cac_du:
        lich.gan_dong_nguon(cac_du[-1], dongs)
    if video.meta.get("loat"):
        lich.gan_loat(cac_du, video.meta["loat"])
    return cac_du


def _trang(video, cac_lich, models, thu_muc: Path, nhac=None) -> list:
    return [trang.dung_trang(du, models.get(du["so"])) for du in _cac_du(video, cac_lich, models, thu_muc, nhac)]


_RE_CHONG = re.compile(r"^chong:(.+),(.+)$")
_RE_NGUON_NHIP = re.compile(r"^nguon-nhip-(\d+)$")
_RE_NHIP = re.compile(r"^nhip-(\d+)$")
FIX_NGUON_CANH = "Rút gọn dòng `nguon` của cảnh (tối đa 90 ký tự hiện)."
FIX_NGUON_NHIP = "Đổi ảnh có nguồn ngắn hơn, hoặc đổi sang ô rộng hơn."


def _kiem_tran_vox(canh, tran: list) -> None:
    for muc in tran:
        m = _RE_CHONG.match(muc)
        if m:
            raise kiem.CanhError(canh.so, f"hai vật {m.group(1)} và {m.group(2)} đè lên nhau quá nhiều.",
                                 "Đổi ô của một nhịp, đổi `bo-cuc` (ví dụ `chong` cho nhiều vật) hoặc bớt nhịp.")
        m = _RE_NGUON_NHIP.match(muc)
        if m:
            raise kiem.CanhError(canh.so, f"nguồn ảnh của nhịp {int(m.group(1)) + 1} quá dài, tràn khung.",
                                 FIX_NGUON_NHIP)
        m = _RE_NHIP.match(muc)
        if m:
            raise kiem.CanhError(canh.so, f"chữ của nhịp {int(m.group(1)) + 1} tràn ô.",
                                 "Rút gọn chữ của nhịp đó (ý dài để ở lời) hoặc đổi sang ô rộng hơn.")
        if muc == "nguon":
            raise kiem.CanhError(canh.so, "dòng nguồn (`nguon`) của cảnh tràn khung.", FIX_NGUON_CANH)
        if muc == "nhac-nguon":
            raise kiem.CanhError(canh.so, "dòng nguồn nhạc nền (hiện cuối video, cùng dòng hình AI nếu có) dài quá, tràn khung.",
                                 FIX_NGUON_NHAC)
        if muc:
            raise kiem.CanhError(canh.so, f"chữ ở mục `{muc}` tràn khung. Rút ngắn nội dung hoặc chia thành hai cảnh.")


def _kiem_tran_tat_ca(page, video, trang_html) -> None:
    for canh, html in zip(video.canh, trang_html):
        tran = chup.kiem_tran(page, html)
        if canh.loai == "vox":
            _kiem_tran_vox(canh, tran)
            continue
        phan = [muc[len("phan:"):] for muc in tran if muc.startswith("phan:")]
        if phan:
            raise kiem.CanhError(canh.so, f'phần công thức "{phan[0]}" quá dài cho khổ này', FIX_PHAN)
        if "tai-lieu" in tran:
            raise kiem.CanhError(canh.so, "dòng tài liệu (`tai-lieu`) đè lên chữ hoặc ảnh của cảnh.", FIX_TAI_LIEU)
        if "nhac-nguon-de" in tran:
            raise kiem.CanhError(canh.so, "dòng nguồn cuối video (hình AI, nhạc nền) đè lên dòng tài liệu hoặc chữ của cảnh.",
                                 FIX_NGUON_DE)
        noi_dung = [muc for muc in tran if muc != "nhac-nguon"]
        if noi_dung:
            raise kiem.CanhError(canh.so, f"chữ ở mục `{', '.join(noi_dung)}` tràn khung. Rút ngắn nội dung hoặc chia thành hai cảnh.")
        if tran:
            raise kiem.CanhError(canh.so, "dòng nguồn nhạc nền (hiện cuối video, cùng dòng hình AI nếu có) dài quá, tràn khung.",
                                 FIX_NGUON_NHAC)


@contextlib.contextmanager
def _loi_chup():
    try:
        yield
    except (media.MediaError, kiem.CanhError, OSError):
        raise
    except Exception as exc:  # noqa: BLE001
        raise media.MediaError("dung", f"Chụp khung hỏng: {type(exc).__name__}: {exc}", FIX_CHUP) from exc


def _giong_tam(video: parse.Video) -> list:
    """Giọng giả cho bố cục: 8 giây, hoặc tới mốc `tham-so` cuối của cảnh để thấy trạng thái cuối."""
    out = []
    for c in video.canh:
        moc = [float(v.split()[0]) for v in c.truong.get("tham-so", [])]
        giai = lich.GiongInfo(mp3=None, giay=GIONG_TAM, moc_cau=[], uoc_luong=True, nguon="may") if c.loai == "cau-hoi" else None
        out.append(lich.GiongInfo(mp3=None, giay=max([GIONG_TAM] + moc), moc_cau=[], uoc_luong=True, nguon="may", giai=giai))
    return out


def _lay_giong(c: parse.Scene, thu_muc_giong: Path, meta: dict) -> lich.GiongInfo:
    """Giọng của cảnh; cảnh câu hỏi thêm giọng lời giải (file riêng `canh-<số>-giai.mp3`)."""
    g = giong.lay_giong(c.so, c.loi, thu_muc_giong, meta["giong"], meta["toc-do"])
    if c.loai != "cau-hoi":
        return g
    giai = giong.lay_giong(c.so, c.truong["loi-giai"][0], thu_muc_giong, meta["giong"], meta["toc-do"], ten=f"canh-{c.so}-giai")
    return dataclasses.replace(g, giai=giai)


def _trang_tam(video: parse.Video, thu_muc: Path, models: dict, nhac=None) -> list:
    cac_lich, _ = lich.dung_lich(video.canh, _giong_tam(video), kiem_moc=False)
    return _trang(video, cac_lich, models, thu_muc, nhac)


def _xem_truoc(video: parse.Video, thu_muc: Path, warnings: list, nhac=None) -> dict:
    trang_html = _trang_tam(video, thu_muc, _mo_hinh(video, thu_muc), nhac)
    ra = thu_muc / "xem-truoc"
    shutil.rmtree(ra, ignore_errors=True)
    files = []
    with _loi_chup(), chup.trinh_duyet() as browser:
        page = chup.trang_moi(browser, kho.tu_meta(video.meta))
        _kiem_tran_tat_ca(page, video, trang_html)
        for canh, html in zip(video.canh, trang_html):
            chup.chup_cuoi(page, html, ra / f"canh-{canh.so}.png")
            if canh.loai == "vox":
                thoi_luong = page.evaluate("() => window.THI_VIDEO.thoiDiemCuoi()")
                page.evaluate("(t) => window.datThoiDiem(t)", thoi_luong / 2)
                giua = ra / f"canh-{canh.so}-giua.png"
                page.screenshot(path=str(giua), type="png")
                files.append(f"xem-truoc/canh-{canh.so}-giua.png")
            files.append(f"xem-truoc/canh-{canh.so}.png")
    return {"files": files, "so_canh": len(video.canh), "thoi_luong_giay": None,
            "phong_cach": video.meta["phong-cach"], "giong": None}


def _dung(video: parse.Video, thu_muc: Path, warnings: list, nhac=None) -> dict:
    """`nhac`: nhạc nền đã đọc ở bước kiểm (`kiem.doc_nhac`), để ffprobe chỉ đo nhạc một lần mỗi lượt."""
    if not co_ffmpeg():
        raise media.MediaError("ffmpeg", "Chưa có FFmpeg.", media.FIX_FFMPEG)
    if not co_chromium():
        raise media.MediaError("chromium", "Chưa cài Chromium hoặc playwright.", chup.FIX_CHROMIUM)
    models = _mo_hinh(video, thu_muc)
    k = kho.tu_meta(video.meta)
    with _loi_chup(), chup.trinh_duyet() as browser:
        _kiem_tran_tat_ca(chup.trang_moi(browser, k), video, _trang_tam(video, thu_muc, models, nhac))
    meta_giong = video.meta
    if video.meta["giong"] in giong.VIENEU_GIONG:
        if giong.co_vieneu():
            # Đọc mọi cảnh chưa có giọng trong một tiến trình VieNeu (mô hình chỉ nạp một lần).
            giong.tao_truoc_vieneu([(f"canh-{c.so}", c.loi) for c in video.canh], thu_muc / "giong",
                                   video.meta["giong"], video.meta["toc-do"])
        else:
            meta_giong = {**video.meta, "giong": "nu"}
            warnings.append("Máy không có VieNeu nên không dùng được giọng Thu Giang; đã dùng giọng nữ edge-tts. "
                            "Đặt biến môi trường VIENEU_PYTHON trỏ tới python của VieNeu để dùng giọng Thu Giang.")
    cac_giong = [_lay_giong(c, thu_muc / "giong", meta_giong) for c in video.canh]
    cac_lich, canh_bao = lich.dung_lich(video.canh, cac_giong)
    warnings.extend(canh_bao)
    if "thoi-luong" in video.meta:
        warnings[:] = [w for w in warnings if "mục tiêu `thoi-luong:" not in w]
        cb_that = thoi_luong.canh_bao(int(video.meta["thoi-luong"]), sum(cl.thoi_luong for cl in cac_lich),
                                       video.meta["toc-do"], False, meta_giong["giong"])
        if cb_that is not None:
            warnings.append(cb_that)
    cac_du = _cac_du(video, cac_lich, models, thu_muc, nhac)
    models_js = {so: m.js for so, m in models.items()}
    so_khung = [cl.so_khung for cl in cac_lich]
    lam = thu_muc / ".khung"
    shutil.rmtree(lam, ignore_errors=True)
    thu_muc_khung = lam / "anh"
    thu_muc_khung.mkdir(parents=True)
    try:
        so_tt = chup.so_tien_trinh()
        log(f"Chụp {sum(so_khung)} khung ({lich.FPS} khung/giây) bằng {len(chup.chia_dai(so_khung, so_tt))} tiến trình Chromium...")
        # Hiệu ứng âm thanh: sự kiện đọc từ chính trang của mỗi cảnh trong lượt chụp (một nguồn thời gian).
        co_am = video.meta["am-thanh"] == "co"
        with _loi_chup():
            ket = chup.chup_song_song(cac_du, models_js, so_khung, lich.FPS, thu_muc_khung, so_tt,
                                      thu_muc_su_kien=lam / "su-kien" if co_am else None, kho=k)
        su_kien = [ket.get(du["so"], []) for du in cac_du] if co_am and ket is not None else None
        log("Ghép video bằng FFmpeg...")
        files = ghep.ghep_video(thu_muc, cac_lich, cac_giong, video.meta["phu-de"], su_kien=su_kien, nhac=nhac, kho=k,
                                chu_de=video.meta["phong-cach"], canh_bao=warnings)
    finally:
        shutil.rmtree(lam, ignore_errors=True)
    if video.meta["phu-de"] != "file":
        (thu_muc / "phu-de.srt").unlink(missing_ok=True)
    if video.meta["phong-cach"] == "vox":
        (thu_muc / "nguon.txt").write_text(vox.nguon_van_ban(video, thu_muc, nhac), encoding="utf-8")
        files = files + ["nguon.txt"]
    nguon = {g.nguon for g in cac_giong} | {g.giai.nguon for g in cac_giong if g.giai is not None}
    return {"files": files, "so_canh": len(video.canh), "thoi_luong_giay": round(sum(cl.thoi_luong for cl in cac_lich), 2),
            "phong_cach": video.meta["phong-cach"], "giong": nguon.pop() if len(nguon) == 1 else "hon-hop"}


def chay(thu_muc: Path, plan_only: bool, xem_truoc: bool, warnings: list) -> dict:
    md = thu_muc / "video.md"
    if not thu_muc.is_dir() or not md.is_file():
        raise media.MediaError("input", f"Không thấy {md}.", FIX_INPUT)
    video = parse.parse(md.read_text(encoding="utf-8-sig"))
    nhac = kiem.doc_nhac(video, thu_muc)
    warnings.extend(kiem.kiem(video, thu_muc, doc_nhac_nen=False, chi_canh_bao=plan_only))
    warnings.extend(kiem.canh_bao_hinh_khop_loi(video))
    uoc = thoi_luong.uoc_tinh(video)
    if "thoi-luong" in video.meta:
        canh_bao = thoi_luong.canh_bao(int(video.meta["thoi-luong"]), uoc, video.meta["toc-do"], True,
                                       video.meta["giong"])
        if canh_bao is not None:
            warnings.append(canh_bao)
    if plan_only:
        return {"files": [], "so_canh": len(video.canh), "thoi_luong_giay": None,
                "phong_cach": video.meta["phong-cach"], "giong": None, "thoi_luong_uoc": round(uoc, 1)}
    if xem_truoc:
        if not co_chromium():
            raise media.MediaError("chromium", "Chưa cài Chromium hoặc playwright.", chup.FIX_CHROMIUM)
        return _xem_truoc(video, thu_muc, warnings, nhac)
    return _dung(video, thu_muc, warnings, nhac)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Dựng video giải thích từ video.md", add_help=False)
    ap.add_argument("thu_muc")
    ap.add_argument("--plan-only", action="store_true")
    ap.add_argument("--xem-truoc", action="store_true")
    try:
        args = ap.parse_args(argv)
    except SystemExit:
        emit({"ready": False, "files": [], "so_canh": 0, "thoi_luong_giay": None, "phong_cach": None, "giong": None, "warnings": [],
              "error": {"step": "input", "message": "Sai tham số dòng lệnh.", "fix": "Dùng: python tools/vi/video_ma.py <thư_mục> [--plan-only] [--xem-truoc]"}})
        return 1
    warnings: list = []
    base = {"ready": False, "files": [], "so_canh": 0, "thoi_luong_giay": None, "phong_cach": None, "giong": None,
            "thoi_luong_uoc": None}
    try:
        kq = chay(Path(args.thu_muc).resolve(), args.plan_only, args.xem_truoc, warnings)
        emit({**base, **kq, "ready": True, "warnings": warnings, "error": None})
        return 0
    except parse.ParseError as exc:
        error = {"step": "parse", "message": str(exc), "fix": "Sửa đúng dòng đó trong video.md rồi chạy lại."}
    except kiem.CanhError as exc:
        error = {"step": "canh", "message": str(exc), "fix": exc.fix or (FIX_NHAC if exc.so == 0 else FIX_CANH)}
    except media.MediaError as exc:
        error = {"step": exc.step, "message": str(exc), "fix": exc.fix}
    except OSError as exc:
        error = {"step": "write", "message": f"Không ghi được file: {exc}", "fix": "Đóng file đang mở và kiểm tra ổ đĩa rồi chạy lại."}
    except Exception as exc:  # noqa: BLE001
        error = {"step": "internal", "message": f"{type(exc).__name__}: {exc}", "fix": FIX_INTERNAL}
    emit({**base, "warnings": warnings, "error": error})
    return 1


if __name__ == "__main__":
    sys.exit(main())
