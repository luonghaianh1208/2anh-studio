"""Hiệu ứng âm thanh tự tạo: mẫu WAV từ công thức cố định bằng FFmpeg (không file ngoài, không bản quyền, xác định),
và lệnh trộn các mẫu vào tiếng cảnh theo sự kiện `THI_VIDEO.suKien()` của trang. Chỉ dùng thư viện chuẩn."""

from __future__ import annotations

import array
import math
import subprocess
import sys
import wave
from pathlib import Path

from video_parts import media

TAN_SO = 44100
LOAI = ("chuyen", "but", "ting", "nhan", "tictac", "dung", "vut", "pop", "bup", "dem", "ding")
# Công thức (filtergraph nguồn, ra nhãn [o]) và độ dài (giây) của từng mẫu. Nhiễu có hạt cố định nên xác định.
CONG_THUC = {
    # Bút: nhiễu trắng lọc thông dải quanh 3 kHz, điều biên 11 Hz và 3 Hz (nét sột soạt). Dài đúng 1 s, số chu kì
    # điều biên nguyên nên lặp nối không vấp.
    "but": ("anoisesrc=d=1:c=white:r=44100:a=0.5:seed=4242,bandpass=f=3000:width_type=q:w=0.9,highpass=f=900,"
            "tremolo=f=11:d=0.55,tremolo=f=3:d=0.3[o]", 1.0),
    # Ting: sine 1318 Hz (Mi 6) tắt dần, thêm hoạ âm bậc hai.
    "ting": ("aevalsrc='0.7*sin(2*PI*1318*t)*exp(-7*t)+0.25*sin(2*PI*2636*t)*exp(-11*t)':s=44100:d=0.7,"
             "afade=t=in:d=0.004,afade=t=out:st=0.6:d=0.1[o]", 0.7),
    # Chuyển cảnh: nhiễu hồng, dải thấp nhạt dần trong khi dải cao mạnh dần (nghe như quét tần lên), vào/ra êm.
    "chuyen": ("anoisesrc=d=0.6:c=pink:r=44100:a=0.6:seed=777,asplit[a][b];"
               "[a]bandpass=f=500:width_type=q:w=1,afade=t=out:d=0.6[l];"
               "[b]bandpass=f=3000:width_type=q:w=1,afade=t=in:d=0.6[h];"
               "[l][h]amix=inputs=2:normalize=0,afade=t=in:d=0.15,afade=t=out:st=0.35:d=0.25[o]", 0.6),
    # Tích tắc: tiếng gõ gỗ ngắn (hai sine tắt rất nhanh).
    "tictac": ("aevalsrc='0.8*sin(2*PI*1900*t)*exp(-70*t)+0.4*sin(2*PI*950*t)*exp(-45*t)':s=44100:d=0.12,"
               "afade=t=in:d=0.002,afade=t=out:st=0.1:d=0.02[o]", 0.12),
    # Đúng: chuông hai nốt đi lên (Đô 6 rồi Son 6).
    "dung": ("aevalsrc='0.5*sin(2*PI*1047*t)*exp(-5*t)+0.5*gte(t,0.13)*sin(2*PI*1568*(t-0.13))*exp(-4*(t-0.13))':s=44100:d=0.9,"
             "afade=t=in:d=0.004,afade=t=out:st=0.75:d=0.15[o]", 0.9),
    # Nhấn: sine quét lên 500 → 1100 Hz trong 0,3 s, bao hình sin (vào/ra bằng 0).
    "nhan": ("aevalsrc='0.6*sin(2*PI*(500*t+1000*t*t))*sin(PI*t/0.3)':s=44100:d=0.3[o]", 0.3),
    # Video ngắn (ngan.js gán theo loại vật):
    # Vút: nhiễu hồng lọc dải quanh 1,8 kHz, to dần rồi nhỏ dần (gió lướt khi vật trượt vào).
    "vut": ("anoisesrc=d=0.4:c=pink:r=44100:a=0.6:seed=31,bandpass=f=1800:width_type=q:w=0.7,"
            "afade=t=in:d=0.16,afade=t=out:st=0.18:d=0.22[o]", 0.4),
    # Pop: sine quét xuống nhanh 900 Hz, tắt rất nhanh (bong bóng, biểu tượng bật ra).
    "pop": ("aevalsrc='0.8*sin(2*PI*(900*t-1500*t*t))*exp(-30*t)':s=44100:d=0.15,"
            "afade=t=in:d=0.003,afade=t=out:st=0.12:d=0.03[o]", 0.15),
    # Bụp: như pop nhưng trầm và mềm (nhân vật đổi tư thế).
    "bup": ("aevalsrc='0.7*sin(2*PI*(420*t-300*t*t))*exp(-18*t)':s=44100:d=0.2,"
            "afade=t=in:d=0.004,afade=t=out:st=0.16:d=0.04[o]", 0.2),
    # Đếm: chuỗi tiếng tích cách 70 ms trong 0,75 s (số chạy, chấm sáng dần).
    "dem": ("aevalsrc='0.6*sin(2*PI*2200*t)*exp(-90*mod(t,0.07))*lt(t,0.75)':s=44100:d=0.8,"
            "afade=t=in:d=0.003,afade=t=out:st=0.74:d=0.06[o]", 0.8),
    # Ding: chuông thông báo hai nốt Son 6 → Đô 7.
    "ding": ("aevalsrc='0.5*sin(2*PI*1568*t)*exp(-6*t)+0.5*gte(t,0.09)*sin(2*PI*2093*(t-0.09))*exp(-6*(t-0.09))':s=44100:d=0.7,"
             "afade=t=in:d=0.004,afade=t=out:st=0.6:d=0.1[o]", 0.7),
}
DAI_MAU = {loai: dai for loai, (_, dai) in CONG_THUC.items()}
# Đỉnh của từng mẫu sau chuẩn hoá (tuyến tính). Bút kéo dài nên nhỏ hơn 6 dB.
DINH_MAU = {"but": 0.25, "ting": 0.5, "chuyen": 0.5, "tictac": 0.5, "dung": 0.5, "nhan": 0.5,
            "vut": 0.4, "pop": 0.5, "bup": 0.45, "dem": 0.35, "ding": 0.5}
# Kênh hiệu ứng qua bộ giới hạn đỉnh 0,5 (−6,02 dBFS) rồi hạ để đỉnh thấp hơn đỉnh giọng DUOI_GIONG_DB.
GIOI_HAN = 0.5
DINH_BUS_DB = 20 * math.log10(GIOI_HAN)
DUOI_GIONG_DB = 20.0
# Sàn −80 dBFS chỉ chạm tới khi giọng gần như im lặng (cảnh im lặng đo được −120): giọng rất nhỏ (−45 dBFS) vẫn có
# hiệu ứng thấp hơn đủ DUOI_GIONG_DB.
MUC_THAP_NHAT, MUC_CAO_NHAT = -80.0, -20.0
BUT_VAO, BUT_RA = 0.03, 0.06


def dinh_db(wav: Path) -> float:
    """Đỉnh (dBFS) của file WAV PCM 16 bit; im lặng hoàn toàn là −120."""
    with wave.open(str(wav)) as w:
        if w.getsampwidth() != 2:
            raise ValueError(f"{wav}: cần PCM 16 bit")
        mau = array.array("h", w.readframes(w.getnframes()))
    if sys.byteorder == "big":
        mau.byteswap()
    dinh = max(max(mau, default=0), -min(mau, default=0))
    return 20 * math.log10(dinh / 32768) if dinh else -120.0


def _chuan_hoa(tho: Path, ra: Path, dinh: float) -> None:
    """Đưa đỉnh của mẫu về đúng `dinh` (tuyến tính), ghi WAV mono 16 bit."""
    with wave.open(str(tho)) as w:
        tan_so = w.getframerate()
        mau = array.array("h", w.readframes(w.getnframes()))
    if sys.byteorder == "big":
        mau.byteswap()
    lon = max(max(mau, default=0), -min(mau, default=0)) or 1
    k = dinh * 32767 / lon
    ket = array.array("h", (int(round(x * k)) for x in mau))
    if sys.byteorder == "big":
        ket.byteswap()
    with wave.open(str(ra), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(tan_so)
        w.writeframes(ket.tobytes())


def _chay(cmd: list, run) -> None:
    try:
        proc = run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise media.MediaError("ffmpeg", f"Không chạy được FFmpeg: {exc}", media.FIX_FFMPEG) from exc
    if proc.returncode != 0:
        loi = (proc.stderr or "").strip()[-400:]
        raise media.MediaError("dung", f"FFmpeg lỗi khi tạo tiếng hiệu ứng (mã {proc.returncode}): {loi}",
                               "Báo nội dung lỗi cho người bảo trì.")


def tao_mau(thu_muc: Path, run=subprocess.run) -> dict:
    """Tạo (một lần) `<thu_muc>/<loai>.wav` cho mọi loại hiệu ứng; mẫu đã có thì dùng lại."""
    thu_muc = Path(thu_muc)
    thu_muc.mkdir(parents=True, exist_ok=True)
    ket = {}
    for loai in LOAI:
        ra = thu_muc / f"{loai}.wav"
        if not ra.is_file():
            tho = thu_muc / f"{loai}.tho.wav"
            do_thi, dai = CONG_THUC[loai]
            _chay(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-filter_complex", do_thi, "-map", "[o]",
                   "-t", f"{dai:.3f}", "-ar", str(TAN_SO), "-ac", "1", "-c:a", "pcm_s16le", str(tho)], run)
            _chuan_hoa(tho, ra, DINH_MAU[loai])
            tho.unlink()
        ket[loai] = ra
    return ket


def _ms(t: float) -> int:
    return int(round(t * 1000))


def lenh_tron(wav_giong: Path, su_kien: list, mau: dict, wav_ra: Path, thoi_luong: float, dinh_giong_db: float = -3.0) -> list:
    """Lệnh FFmpeg trộn hiệu ứng vào tiếng cảnh `wav_giong` (đã có nhiễu nền, dài đúng `thoi_luong`).

    Mỗi sự kiện: mẫu của loại đó trễ `t` giây (`adelay`); bút lặp rồi cắt đúng `dai`. Các hiệu ứng cộng lại, qua bộ
    giới hạn đỉnh, rồi hạ để đỉnh thấp hơn đỉnh giọng `dinh_giong_db` đúng DUOI_GIONG_DB. Ra: dài đúng `thoi_luong`.
    """
    dung = [loai for loai in LOAI if any(e["loai"] == loai for e in su_kien)]
    vao = ["-i", str(wav_giong)]
    loc = ""
    nhan = []
    for i, loai in enumerate(dung, start=1):
        vao += ["-i", str(mau[loai])]
        cac = [e for e in su_kien if e["loai"] == loai]
        ten = [f"{loai}{k}" for k in range(len(cac))]
        if len(cac) > 1:
            loc += f"[{i}:a]asplit={len(cac)}" + "".join(f"[{t}]" for t in ten) + ";"
        else:
            loc += f"[{i}:a]anull[{ten[0]}];"
        for e, t in zip(cac, ten):
            chuoi = []
            if loai == "but":
                dai = float(e["dai"])
                vao_ = min(BUT_VAO, dai / 3)
                ra_ = min(BUT_RA, dai / 3)
                chuoi += [f"aloop=loop=-1:size={int(TAN_SO * DAI_MAU['but'])}", f"atrim=duration={dai:.3f}",
                          f"afade=t=in:d={vao_:.3f}", f"afade=t=out:st={dai - ra_:.3f}:d={ra_:.3f}"]
            else:
                con = thoi_luong - float(e["t"])
                if con < DAI_MAU[loai]:
                    # Mẫu dài quá cuối cảnh: cắt và tắt dần 30 ms để không có tiếng tách ở ranh cảnh.
                    ra_ = min(0.03, con / 2)
                    chuoi += [f"atrim=duration={con:.3f}", f"afade=t=out:st={con - ra_:.3f}:d={ra_:.3f}"]
            chuoi.append(f"adelay={_ms(float(e['t']))}:all=1")
            loc += f"[{t}]" + ",".join(chuoi) + f"[e_{t}];"
            nhan.append(f"[e_{t}]")
    muc = min(MUC_CAO_NHAT, max(MUC_THAP_NHAT, dinh_giong_db - DUOI_GIONG_DB))
    loc += ("".join(nhan) + f"amix=inputs={len(nhan)}:duration=longest:normalize=0,"
            f"alimiter=limit={GIOI_HAN}:level=0:latency=1,volume={muc - DINH_BUS_DB:.2f}dB[hu];"
            "[0:a][hu]amix=inputs=2:duration=first:normalize=0[a]")
    return [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *vao, "-filter_complex", loc, "-map", "[a]",
        "-t", f"{thoi_luong:.3f}", "-ar", str(TAN_SO), "-ac", "1", "-c:a", "pcm_s16le", str(wav_ra),
    ]
