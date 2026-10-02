"""Giọng đọc từng cảnh: file thầy cô đặt sẵn, giọng máy edge-tts, hoặc bản tạo lần trước còn dùng được."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable

from video_parts import media

from .lich import GiongInfo, tach_cau
from .lich import khoa_so_khop as _chuan_hoa

VOICES = {"nu": "vi-VN-HoaiMyNeural", "nam": "vi-VN-NamMinhNeural"}
RATES = {"cham": "-10%", "vua": "+0%", "nhanh": "+15%"}
FIX_GIONG = "Có mạng rồi chạy lại, hoặc đặt sẵn file giọng giong/canh-<số>.mp3 cho từng cảnh."
FIX_EDGE = "Cài edge-tts bằng: python -m pip install -r requirements.txt (ở thư mục gốc repo)."
FIX_FILE = "Xoá hoặc thay file giọng đó rồi chạy lại."
# Giọng VieNeu (đọc trên máy, không cần mạng): khoá `giong` -> tên giọng trong VieNeu. Python của môi trường VieNeu
# lấy từ biến môi trường VIENEU_PYTHON, không đặt thì thử đường dẫn mặc định.
VIENEU_GIONG = {"thu-giang": "Thu Giang"}
VIENEU_PYTHON_MAC_DINH = r"E:\vieneu-tts\Scripts\python.exe"
VIENEU_TEMPO = {"cham": 0.92, "vua": 1.0, "nhanh": 1.1}
VIENEU_NGHI = 0.22   # giây nghỉ giữa hai câu trong một cảnh
VIENEU_SCRIPT = Path(__file__).resolve().parent / "vieneu_doc.py"
FIX_VIENEU = ("Kiểm tra VieNeu chạy được (biến môi trường VIENEU_PYTHON trỏ tới python của môi trường VieNeu), hoặc "
              "ghi `giong: nu` để dùng giọng edge-tts.")
_MARKUP_RE = re.compile(r"\*\*|~|\^|==|\(\(|\)\)|__|\{\{|\}\}")
_TOI_DA_SU_KIEN = 6
_TOI_DA_TU = 3


def bam(loi: str, voice: str, rate: str) -> str:
    return hashlib.sha256(f"{voice}|{rate}|{loi}".encode("utf-8")).hexdigest()[:16]


def _khop_tai(chuan_tu: list, chuan_su_kien: list, i: int, j: int):
    """Thử khớp từ `i` của kịch bản với sự kiện `j` trở đi: 1-1, 1 từ trải trên
    nhiều sự kiện (số đọc từng chữ số, viết tắt), hoặc nhiều từ gộp vào 1 sự kiện."""
    if i >= len(chuan_tu) or j >= len(chuan_su_kien):
        return None
    if chuan_tu[i] == chuan_su_kien[j]:
        return i + 1, j + 1
    acc = ""
    for k in range(1, _TOI_DA_SU_KIEN + 1):
        if j + k > len(chuan_su_kien):
            break
        acc += chuan_su_kien[j + k - 1]
        if acc == chuan_tu[i]:
            return i + 1, j + k
        if not chuan_tu[i].startswith(acc):
            break
    acc = ""
    for m in range(1, _TOI_DA_TU + 1):
        if i + m > len(chuan_tu):
            break
        acc += chuan_tu[i + m - 1]
        if acc == chuan_su_kien[j]:
            return i + m, j + 1
        if not chuan_su_kien[j].startswith(acc):
            break
    return None


def can_chinh_tu(chuan_tu: list, chuan_su_kien: list) -> tuple:
    """Khớp từng token kịch bản (đã chuẩn hoá) với sự kiện WordBoundary (đã chuẩn hoá) — lõi dùng chung
    cho mốc đầu câu (`_can_chinh_moc_cau`) và mốc từng từ hiển thị (karaoke, giữ nguyên dấu câu/chữ hoa
    của kịch bản). Trả `(idx_su_kien, i, j)`: `idx_su_kien[k]` là chỉ số sự kiện khớp với token thứ `k`
    (`None` nếu token đó bị gộp vào sự kiện của token liền trước, hoặc không khớp được); `i`, `j` là vị
    trí dừng lại (để đánh giá độ tin cậy: còn dư bao nhiêu token/sự kiện)."""
    idx_su_kien: list = [None] * len(chuan_tu)
    i = j = 0
    while i < len(chuan_tu) and j < len(chuan_su_kien):
        ket = _khop_tai(chuan_tu, chuan_su_kien, i, j)
        if ket is not None:
            idx_su_kien[i] = j
            i, j = ket
            continue
        tim = None
        for dj in range(1, _TOI_DA_SU_KIEN + 1):
            if _khop_tai(chuan_tu, chuan_su_kien, i, j + dj) is not None:
                tim = ("su_kien", dj)
                break
        if tim is None:
            for di in range(1, _TOI_DA_TU + 1):
                if _khop_tai(chuan_tu, chuan_su_kien, i + di, j) is not None:
                    tim = ("tu", di)
                    break
        if tim is None:
            i += 1
            continue
        if tim[0] == "su_kien":
            j += tim[1]
        else:
            i += tim[1]
    return idx_su_kien, i, j


def _can_chinh_moc_cau(cau: list, tu: list):
    """Ghép mốc đầu mỗi câu bằng cách so khớp chữ (kịch bản) với sự kiện WordBoundary.
    Trả `None` khi không đủ tin cậy (từ đầu một câu không khớp được, hoặc số sự kiện đã dùng
    lệch quá xa tổng số sự kiện) — không bao giờ trả mốc sai một cách âm thầm."""
    tokens: list = []
    dau_cau: list = []
    for c in cau:
        dau_cau.append(len(tokens))
        tokens.extend(c.split())
    if not tokens or not tu:
        return None

    chuan_tu = [_chuan_hoa(w) for w in tokens]
    chuan_su_kien = [_chuan_hoa(e["chu"]) for e in tu]
    idx_su_kien, _i, j = can_chinh_tu(chuan_tu, chuan_su_kien)

    if any(idx_su_kien[p] is None for p in dau_cau):
        return None
    if abs(len(tu) - j) > max(3, round(len(tu) * 0.1)):
        return None
    return [tu[idx_su_kien[p]]["t"] for p in dau_cau]


def _moc_cau_theo_tu(text: str, tu: list) -> list:
    """Mốc câu = thời điểm của từ đầu mỗi câu, so khớp chữ với danh sách sự kiện.
    Không so khớp được chắc chắn thì trả về [] để `lich.dung_lich` tự ước lượng
    lại theo số ký tự (và nêu cảnh báo), thay vì âm thầm trả mốc sai."""
    cau = tach_cau(text)
    if not cau:
        return []
    moc = _can_chinh_moc_cau(cau, tu)
    return moc if moc is not None else []


async def _tong_hop(text: str, voice: str, rate: str, out_path: Path) -> dict:
    import edge_tts

    tu: list = []
    with open(out_path, "wb") as f:
        communicate = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                tu.append({
                    "t": round(chunk["offset"] / 1e7, 3),
                    "d": round(chunk["duration"] / 1e7, 3),
                    "chu": chunk["text"],
                })
    return {"cau": _moc_cau_theo_tu(text, tu), "tu": tu}


def tong_hop_edge(text: str, voice: str, rate: str, out_path: Path) -> dict:
    try:
        import edge_tts  # noqa: F401
    except ImportError as exc:
        raise media.MediaError("giong", "Chưa cài edge-tts.", FIX_EDGE) from exc
    try:
        return asyncio.run(_tong_hop(text, voice, rate, out_path))
    except Exception as exc:
        raise media.MediaError("giong", f"Không tạo được giọng đọc (thường do mất mạng): {exc}", FIX_GIONG) from exc


def vieneu_python() -> Path | None:
    duong = Path(os.environ.get("VIENEU_PYTHON") or VIENEU_PYTHON_MAC_DINH)
    return duong if duong.is_file() else None


def co_vieneu() -> bool:
    return vieneu_python() is not None


def _moc_tu_theo_cau(cau: list, moc: list, dai: list) -> list:
    """Mốc từng từ trong mỗi câu, chia theo số ký tự trên đúng thời lượng tiếng của câu đó (VieNeu không trả mốc từ)."""
    tu = []
    for c, t0, d in zip(cau, moc, dai):
        cac = c.split()
        tong = sum(len(w) for w in cac) or 1
        qua = 0
        for w in cac:
            a = t0 + qua / tong * d
            qua += len(w)
            tu.append({"t": round(a, 3), "d": round(len(w) / tong * d, 3), "chu": w})
    return tu


def _vieneu_chay(viec: list, voice: str, toc_do: str, run=subprocess.run) -> list:
    """`viec`: [(lời đã bỏ dấu nhấn, file mp3 đích)]. Đọc tất cả trong một tiến trình VieNeu (nạp mô hình một lần),
    đổi sang mp3. Trả [{"cau": mốc câu, "tu": mốc từ}] theo thứ tự `viec`."""
    py = vieneu_python()
    if py is None:
        raise media.MediaError("giong", "Không thấy Python của VieNeu.", FIX_VIENEU)
    if not viec:
        return []
    tempo = VIENEU_TEMPO[toc_do]
    tam = Path(viec[0][1]).parent
    tam.mkdir(parents=True, exist_ok=True)
    cac_cau = [tach_cau(loi) or [loi] for loi, _ in viec]
    wavs = [Path(str(dich) + ".vieneu.wav") for _, dich in viec]
    viec_json = tam / "vieneu-viec.json"
    viec_json.write_text(json.dumps({"giong": voice.split(":", 1)[1], "nghi": VIENEU_NGHI,
                                     "viec": [{"cau": c, "ra": str(w)} for c, w in zip(cac_cau, wavs)]},
                                    ensure_ascii=False), encoding="utf-8")
    try:
        try:
            proc = run([str(py), str(VIENEU_SCRIPT), str(viec_json)], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=3600)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise media.MediaError("giong", f"Không chạy được VieNeu: {exc}", FIX_VIENEU) from exc
        dong = [d for d in (proc.stdout or "").splitlines() if d.startswith("{")]
        if proc.returncode != 0 or not dong:
            raise media.MediaError("giong", f"VieNeu lỗi: {(proc.stderr or '').strip()[-300:]}", FIX_VIENEU)
        ket_qua = json.loads(dong[-1])["ket_qua"]
        ra = []
        for (loi, dich), cau, wav, kq in zip(viec, cac_cau, wavs, ket_qua):
            loc = ["-af", f"atempo={tempo}"] if tempo != 1.0 else []
            cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(wav), *loc,
                   "-ar", "44100", "-ac", "1", "-b:a", "128k", "-f", "mp3", str(dich)]
            try:
                p2 = run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise media.MediaError("ffmpeg", f"Không chạy được FFmpeg: {exc}", media.FIX_FFMPEG) from exc
            if p2.returncode != 0:
                raise media.MediaError("giong", f"Không đổi được giọng VieNeu sang mp3: {(p2.stderr or '').strip()[-200:]}",
                                       FIX_VIENEU)
            moc = [round(m / tempo, 3) for m in kq["moc"]]
            dai = [d / tempo for d in kq["dai"]]
            ra.append({"cau": moc, "tu": _moc_tu_theo_cau(cau, moc, dai)})
        return ra
    finally:
        viec_json.unlink(missing_ok=True)
        for w in wavs:
            w.unlink(missing_ok=True)


def tong_hop_vieneu(text: str, voice: str, rate: str, out_path: Path) -> dict:
    """Đọc một lời bằng VieNeu (`rate` là khoá `toc-do`)."""
    return _vieneu_chay([(text, out_path)], voice, rate)[0]


def tao_truoc_vieneu(cac_loi: list, thu_muc: Path, giong: str, toc_do: str) -> int:
    """`cac_loi`: [(tên file không đuôi, lời)]. Đọc trong MỘT tiến trình mọi lời chưa có giọng VieNeu hợp lệ (mô hình
    chỉ nạp một lần), ghi mp3 và sổ giọng như `lay_giong`. File người dùng đặt sẵn không bị đụng. Trả số lời đã đọc."""
    voice = "vieneu:" + VIENEU_GIONG[giong]
    can = []
    for ten, loi in cac_loi:
        mp3, so_giong = thu_muc / f"{ten}.mp3", thu_muc / f"{ten}.json"
        doc = _MARKUP_RE.sub("", loi)
        ma_bam = bam(doc, voice, toc_do)
        if mp3.is_file():
            ghi = _so_giong(so_giong)
            if not ghi or (ghi.get("kich_thuoc"), ghi.get("sha256")) != _dau_van_tay(mp3) or ghi.get("bam") == ma_bam:
                continue
        can.append((doc, mp3, so_giong, ma_bam))
    if not can:
        return 0
    print(f"Đọc {len(can)} lời bằng giọng {VIENEU_GIONG[giong]} (VieNeu)...", file=sys.stderr, flush=True)
    tam = [(doc, mp3.with_name(mp3.name + ".tmp")) for doc, mp3, _s, _m in can]
    try:
        ket = _vieneu_chay(tam, voice, toc_do)
        for (doc, mp3, so_giong, ma_bam), (_d, t), kq in zip(can, tam, ket):
            kich_thuoc, sha = _dau_van_tay(t)
            so_giong.write_text(json.dumps({"bam": ma_bam, "moc": kq["cau"], "tu": kq["tu"], "kich_thuoc": kich_thuoc,
                                            "sha256": sha}, ensure_ascii=False), encoding="utf-8")
            os.replace(t, mp3)
    finally:
        for _d, t in tam:
            t.unlink(missing_ok=True)
    return len(can)


def _giay(mp3: Path, do_dai: Callable) -> float:
    if not mp3.is_file() or mp3.stat().st_size == 0:
        raise media.MediaError("giong", f"{mp3.name} rỗng hoặc không có.", FIX_FILE)
    try:
        return float(do_dai(mp3))
    except media.MediaError as exc:
        if str(exc).startswith("ffprobe lỗi"):
            raise media.MediaError("giong", f"{mp3.name} không đọc được (file hỏng?).", FIX_FILE) from exc
        raise


def _so_giong(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _dau_van_tay(path: Path) -> tuple:
    return path.stat().st_size, hashlib.sha256(path.read_bytes()).hexdigest()


def _loi_file(exc: media.MediaError, mp3: Path) -> media.MediaError:
    """Lỗi tổng hợp giọng nêu đúng file giọng (cảnh câu hỏi có hai file: câu hỏi và lời giải)."""
    fix = f"Có mạng rồi chạy lại, hoặc đặt sẵn file giọng giong/{mp3.name}." if exc.fix == FIX_GIONG else exc.fix
    return media.MediaError(exc.step, f"{mp3.name}: {exc.message}", fix)


def lay_giong(so: int, loi: str, thu_muc: Path, giong: str, toc_do: str,
              tong_hop: Callable = tong_hop_edge, do_dai: Callable = media.probe_duration,
              ten: str | None = None) -> GiongInfo:
    """Giọng của một lời. `ten` là tên file không đuôi (mặc định `canh-<số>`; lời giải của cảnh câu hỏi dùng
    `canh-<số>-giai`); file thầy cô đặt sẵn với tên đó được dùng và không bao giờ bị ghi đè."""
    ten = ten or f"canh-{so}"
    mp3 = thu_muc / f"{ten}.mp3"
    so_giong = thu_muc / f"{ten}.json"
    if giong in VIENEU_GIONG:
        voice, rate = "vieneu:" + VIENEU_GIONG[giong], toc_do
        if tong_hop is tong_hop_edge:
            tong_hop = tong_hop_vieneu
    else:
        voice, rate = VOICES[giong], RATES[toc_do]
    doc = _MARKUP_RE.sub("", loi)
    ma_bam = bam(doc, voice, rate)
    if mp3.is_file():
        ghi = _so_giong(so_giong)
        if not ghi or (ghi.get("kich_thuoc"), ghi.get("sha256")) != _dau_van_tay(mp3):
            return GiongInfo(mp3=mp3, giay=_giay(mp3, do_dai), moc_cau=[], uoc_luong=True, nguon="co-san",
                              moc_tu=[], uoc_luong_tu=True)
        if ghi.get("bam") == ma_bam:
            moc = [float(m) for m in ghi.get("moc", [])]
            tu_ghi = ghi.get("tu")
            moc_tu = list(tu_ghi) if isinstance(tu_ghi, list) else []
            return GiongInfo(mp3=mp3, giay=_giay(mp3, do_dai), moc_cau=moc, uoc_luong=not moc, nguon="may",
                              moc_tu=moc_tu, uoc_luong_tu=not moc_tu)
    thu_muc.mkdir(parents=True, exist_ok=True)
    tam = mp3.with_name(mp3.name + ".tmp")
    so_giong_cu = so_giong.read_bytes() if so_giong.is_file() else None
    try:
        try:
            ket_qua = tong_hop(doc, voice, rate, tam)
        except media.MediaError as exc:
            if exc.step != "giong":
                raise
            raise _loi_file(exc, mp3) from exc
        if isinstance(ket_qua, dict):
            moc, tu = list(ket_qua.get("cau", [])), list(ket_qua.get("tu", []))
        else:
            moc, tu = list(ket_qua), []
        kich_thuoc, sha = _dau_van_tay(tam)
        so_giong.write_text(json.dumps({"bam": ma_bam, "moc": moc, "tu": tu, "kich_thuoc": kich_thuoc, "sha256": sha},
                                       ensure_ascii=False), encoding="utf-8")
        os.replace(tam, mp3)
    except BaseException:
        tam.unlink(missing_ok=True)
        if so_giong_cu is None:
            so_giong.unlink(missing_ok=True)
        else:
            so_giong.write_bytes(so_giong_cu)
        raise
    return GiongInfo(mp3=mp3, giay=_giay(mp3, do_dai), moc_cau=list(moc), uoc_luong=not moc, nguon="may",
                      moc_tu=list(tu), uoc_luong_tu=not tu)
