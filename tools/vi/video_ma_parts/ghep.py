"""Ghép khung hình + tiếng + phụ đề thành video.mp4 bằng FFmpeg. Thư mục dự án chỉ được truyền dưới dạng cwd và đường dẫn tuyệt đối."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from video_parts import media, srt

from . import am_thanh, karaoke
from .chup import DUOI_KHUNG, FIX_DUNG, ten_khung
from .giong import _MARKUP_RE  # cùng bộ dấu giọng đọc bỏ đi: ** ~ ^ == (( )) __ {{ }}
from .lich import DAN_DAU, FPS, doan_loi
from .phong import FONT as ITIM_FONT, TEN as ITIM_TEN

BIEN_DO_NHIEU = 0.002
HAT_NHIEU = 1234
STYLE = f"FontName={ITIM_TEN},FontSize=16,Outline=1.5,Shadow=0,Spacing=0.5,MarginV=22"
FONTS_REL = ".khung/fonts"
KHUNG_DAU = f".khung/anh/{ten_khung(0)}"
# Nhạc nền: vào/ra dần, mức nền, và bộ nén hạ nhạc khi tiếng chính (giọng) vượt ngưỡng.
NHAC_VAO_RA = 1.5
NHAC_DB = -24
NHAC_NEN = "threshold=0.02:ratio=8:attack=20:release=400"


def cues_phu_de(cac_lich: list) -> list:
    cues = []
    so = 0
    for cl in cac_lich:
        for cac_cau, moc_cau, het_giong, _tu in doan_loi(cl):
            het = cl.bat_dau + het_giong
            for k, cau in enumerate(cac_cau):
                start = cl.bat_dau + moc_cau[k]
                end = cl.bat_dau + moc_cau[k + 1] if k + 1 < len(cac_cau) else het
                so += 1
                cues.append(srt.Cue(index=so, start=start, end=max(end, start + 0.1), text=_MARKUP_RE.sub("", cau)))
    return cues


def _giong_tre(vao: int, tre: float, thoi_luong: float, ra: str) -> str:
    return (f"[{vao}:a]aresample=44100,aformat=channel_layouts=mono,adelay={int(round(tre * 1000))}:all=1,"
            f"apad=whole_dur={thoi_luong:.3f}[{ra}];")


def lenh_am_canh(mp3: Path, wav: Path, thoi_luong: float, giai: tuple | None = None) -> list:
    """Tiếng một cảnh: giọng từ giây DAN_DAU, trộn nhiễu nền. `giai` = (mp3 lời giải, giây bắt đầu trong cảnh) của
    cảnh câu hỏi: giọng lời giải trộn thêm ở đúng lúc hiện đáp án."""
    # Lớp nhiễu hồng rất nhỏ: loa Bluetooth/HDMI tự tắt khi gặp im lặng tuyệt đối và nuốt âm đầu câu sau.
    nhieu = f"anoisesrc=d={thoi_luong:.3f}:c=pink:r=44100:a={BIEN_DO_NHIEU}:seed={HAT_NHIEU}"
    vao = ["-i", str(mp3)]
    loc = _giong_tre(0, DAN_DAU, thoi_luong, "g")
    nhan = "[g]"
    if giai is not None:
        vao += ["-i", str(giai[0])]
        loc += _giong_tre(1, giai[1], thoi_luong, "h")
        nhan += "[h]"
    so_n = len(vao) // 2
    loc += (f"[{so_n}:a]aformat=channel_layouts=mono[n];"
            f"{nhan}[n]amix=inputs={so_n + 1}:duration=first:normalize=0[a]")
    return [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *vao,
        "-f", "lavfi", "-i", nhieu, "-filter_complex", loc, "-map", "[a]",
        "-t", f"{thoi_luong:.3f}", "-ar", "44100", "-ac", "1", "-c:a", "pcm_s16le", str(wav),
    ]


def lenh_nhac(danh_sach_am: Path, nhac: Path, wav_ra: Path, tong: float) -> list:
    """Tiếng chính (nối các cảnh) trộn nhạc nền: nhạc lặp vô hạn rồi cắt đúng `tong` giây, vào/ra 1,5 s (video ngắn
    thì nửa video), −24 dB, hạ thêm bằng `sidechaincompress` lấy tiếng chính làm tín hiệu điều khiển."""
    mo = min(NHAC_VAO_RA, tong / 2)
    loc = ("[0:a]aresample=44100,aformat=channel_layouts=mono,asplit=2[chinh][dk];"
           f"[1:a]aresample=44100,aformat=channel_layouts=mono,atrim=duration={tong:.3f},asetpts=N/SR/TB,"
           f"afade=t=in:d={mo:.3f},afade=t=out:st={tong - mo:.3f}:d={mo:.3f},volume={NHAC_DB}dB[nen];"
           f"[nen][dk]sidechaincompress={NHAC_NEN}[ha];"
           "[chinh][ha]amix=inputs=2:duration=first:normalize=0[a]")
    return [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(danh_sach_am), "-stream_loop", "-1", "-i", str(nhac),
        "-filter_complex", loc, "-map", "[a]", "-t", f"{tong:.3f}", "-ar", "44100", "-ac", "1", "-c:a", "pcm_s16le",
        str(wav_ra),
    ]


def lenh_video(danh_sach_am: Path, out_mp4: Path, fps: int, phu_de_tuong_doi) -> list:
    """`danh_sach_am`: danh sách nối tiếng các cảnh (.txt), hoặc một file tiếng đã trộn nhạc (.wav)."""
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-framerate", str(fps), "-i", f".khung/anh/f%06d.{DUOI_KHUNG}",
    ]
    if Path(danh_sach_am).suffix.lower() == ".txt":
        cmd += ["-f", "concat", "-safe", "0"]
    cmd += ["-i", str(danh_sach_am)]
    if phu_de_tuong_doi:
        if str(phu_de_tuong_doi).endswith(".ass"):
            cmd += ["-vf", f"subtitles={phu_de_tuong_doi}:fontsdir={FONTS_REL}"]
        else:
            cmd += ["-vf", f"subtitles={phu_de_tuong_doi}:fontsdir={FONTS_REL}:force_style='{STYLE}'"]
    cmd += ["-r", str(fps), "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out_mp4)]
    return cmd


def _kiem_khung(thu_muc: Path, kho, run) -> None:
    """Khung đầu tiên phải đúng kích thước xuất của khổ: ghép không co giãn nên sai là lỗi chụp."""
    anh = thu_muc / KHUNG_DAU
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
           "-of", "csv=s=x:p=0", str(anh)]
    try:
        proc = run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60, cwd=thu_muc)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise media.MediaError("ffmpeg", f"Không chạy được ffprobe: {exc}", media.FIX_FFMPEG) from exc
    mong = f"{kho.rong_xuat}x{kho.cao_xuat}"
    co = (proc.stdout or "").strip() if proc.returncode == 0 else ""
    if co != mong:
        raise media.MediaError("dung", f"Khung hình chụp ra {co or 'không đọc được'}, cần {mong} (khổ {kho.ten}, "
                                       f"{kho.do_phan_giai}).", FIX_DUNG)


def _chay(cmd: list, run, cwd: Path) -> None:
    try:
        proc = run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=7200, cwd=cwd)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise media.MediaError("ffmpeg", f"Không chạy được FFmpeg: {exc}", media.FIX_FFMPEG) from exc
    if proc.returncode != 0:
        loi = (proc.stderr or "").strip()[-400:]
        raise media.MediaError("dung", f"FFmpeg lỗi (mã {proc.returncode}): {loi}", "Báo nội dung lỗi cho người bảo trì.")


def ghep_video(thu_muc: Path, cac_lich: list, cac_giong: list, phu_de: str, fps: int = FPS, run=subprocess.run,
               su_kien: list | None = None, nhac: dict | None = None, kho=None) -> list:
    """`su_kien`: sự kiện âm thanh của từng cảnh (cùng thứ tự `cac_lich`) để trộn hiệu ứng; None là không có hiệu ứng.
    `nhac`: kết quả `nhac.doc` (nhạc nền trộn sau khi nối tiếng các cảnh); None là không có nhạc.
    `kho` (kho.Kho): kiểm kích thước khung chụp và đặt khung phụ đề karaoke theo điểm CSS; None là khổ ngang cũ."""
    kich_ass = {}
    if kho is not None:
        _kiem_khung(thu_muc, kho, run)
        kich_ass = {"rong": kho.rong, "cao": kho.cao}  # PlayRes theo điểm CSS; libass tự co theo khung video
    lam = thu_muc / ".khung"
    wavs = []
    mau = None
    for k, (cl, giong) in enumerate(zip(cac_lich, cac_giong)):
        wav = lam / f"am-{cl.so}.wav"
        giai = (giong.giai.mp3, cl.bat_dau_giai) if giong.giai is not None and cl.bat_dau_giai is not None else None
        cac = su_kien[k] if su_kien is not None else []
        if not cac:
            _chay(lenh_am_canh(giong.mp3, wav, cl.thoi_luong, giai), run, thu_muc)
        else:
            # Tiếng cảnh = giọng (có nhiễu nền) trộn hiệu ứng, mức hiệu ứng theo đỉnh giọng của chính cảnh.
            wav_giong = lam / f"am-{cl.so}-giong.wav"
            _chay(lenh_am_canh(giong.mp3, wav_giong, cl.thoi_luong, giai), run, thu_muc)
            if mau is None:
                mau = am_thanh.tao_mau(lam / "am", run=run)
            _chay(am_thanh.lenh_tron(wav_giong, cac, mau, wav, cl.thoi_luong, dinh_giong_db=am_thanh.dinh_db(wav_giong)),
                  run, thu_muc)
        wavs.append(wav)
    danh_sach = lam / "am.txt"
    danh_sach.write_text(media.build_audio_concat_text(wavs), encoding="utf-8")
    am = danh_sach
    if nhac is not None:
        am = lam / "am-nhac.wav"
        tong = round(sum(cl.thoi_luong for cl in cac_lich), 3)
        _chay(lenh_nhac(danh_sach, Path(nhac["duong_dan"]), am, tong), run, thu_muc)
    cac_cue = cues_phu_de(cac_lich)
    cues = srt.render_srt(cac_cue)
    files = ["video.mp4"]
    burn = None
    if phu_de == "hinh":
        thoat = [srt.Cue(index=c.index, start=c.start, end=c.end, text=c.text.replace("\\", "⧵").replace("{", "\\{").replace("}", "\\}"))
                 for c in cac_cue]
        (lam / "phu-de.srt").write_text(srt.render_srt(thoat), encoding="utf-8")
        fonts_dir = lam / "fonts"
        fonts_dir.mkdir(exist_ok=True)
        shutil.copy2(ITIM_FONT, fonts_dir / ITIM_FONT.name)
        burn = ".khung/phu-de.srt"
    elif phu_de == "karaoke":
        (lam / "phu-de.ass").write_text(karaoke.tao_ass(cac_lich, **kich_ass), encoding="utf-8")
        fonts_dir = lam / "fonts"
        fonts_dir.mkdir(exist_ok=True)
        shutil.copy2(ITIM_FONT, fonts_dir / ITIM_FONT.name)
        burn = ".khung/phu-de.ass"
    elif phu_de == "file":
        (thu_muc / "phu-de.srt").write_text(cues, encoding="utf-8")
        files.append("phu-de.srt")
    tam = lam / "video.mp4"
    _chay(lenh_video(am, tam, fps, burn), run, thu_muc)
    try:
        os.replace(tam, thu_muc / "video.mp4")
    except PermissionError as exc:
        raise media.MediaError("write", "Không ghi được video.mp4 (đang mở ở nơi khác).",
                               "Đóng video.mp4 nếu đang mở trong trình phát rồi chạy lại.") from exc
    return files
