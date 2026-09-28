"""Nhận ảnh AI đã vẽ (`anh/ai/goc/`): nền cắt phủ về khổ xuất (JPEG), nhân vật tách nền xanh, kiểm alpha, cắt sát
(PNG trong suốt). Mọi xử lý ảnh bằng FFmpeg; Python chỉ đọc kênh alpha thô để đo."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

DUOI_GOC = (".png", ".jpg", ".jpeg", ".webp")
KHO_XUAT = {"ngang": (1920, 1080), "doc": (1080, 1920)}
TOI_DA = 8 * 1024 * 1024
# Chất lượng JPEG của nền: -q:v 3, tăng dần (giảm chất lượng) tới khi file dưới 8 MB.
CHAT_LUONG = (3, 5, 8, 12, 18, 25, 31)
LOC_TACH = "format=rgba,colorkey=0x00FF00:0.30:0.08,despill=type=green"
GOC_O = 8                 # cạnh ô vuông mỗi góc khi kiểm
GOC_ALPHA_TOI_DA = 10     # alpha trung bình mỗi góc phải dưới mức này
NGUONG_DUC = 128          # điểm "đục" khi đếm tỉ lệ
NGUONG_CAT = 32           # điểm tính vào hộp cắt sát (bỏ nhiễu rất mờ)
DUC_TOI_THIEU, DUC_TOI_DA = 0.05, 0.70
CANH_NHAN_VAT_TOI_DA = 1536  # cạnh dài nhất của ảnh nhân vật sau khi cắt (chỉ thu nhỏ, không phóng to)
_TEN_GOC = ("trái trên", "phải trên", "trái dưới", "phải dưới")

FIX_FFMPEG = "Cài FFmpeg theo mục \"Công cụ tuỳ chọn\" của docs/vi/cai-dat-bang-ai.md rồi chạy lại."
FIX_ANH_HONG = ("FFmpeg không đọc được ảnh đó (file hỏng hoặc không phải ảnh): lưu lại hoặc vẽ lại ảnh rồi chạy lại; "
                "vẫn lỗi thì cài lại FFmpeg theo docs/vi/cai-dat-bang-ai.md.")
FIX_THIEU = ("Vẽ các ảnh còn thiếu theo `anh/ai/ke-hoach.json` (đúng tên file; đuôi .png, .jpg, .jpeg hoặc .webp đều được), "
             "lưu vào `anh/ai/goc/`, rồi chạy lại. Nền tảng không có công cụ vẽ thì đổi sang `nen: mau/...` và "
             "`nhan-vat: nguoi-que`.")
FIX_TACH_NEN = ("Vẽ lại ảnh đó trên nền xanh lá thuần #00FF00 phủ kín cả ảnh (không bóng, không viền, không dải tối), "
                "nhân vật không có màu xanh lá và không chạm mép ảnh, rồi chạy lại.")


class XuLyError(Exception):
    def __init__(self, step: str, message: str, fix: str) -> None:
        super().__init__(message)
        self.step = step
        self.message = message
        self.fix = fix


def tim_goc(thu_muc_goc: Path, ten: str):
    """File gốc của mục `ten` trong `anh/ai/goc/`: đúng đuôi kế hoạch trước, rồi các đuôi ảnh khác; None khi không có."""
    goc = Path(ten).stem
    duoi = Path(ten).suffix.lower()
    for d in (duoi,) + tuple(x for x in DUOI_GOC if x != duoi):
        p = Path(thu_muc_goc) / f"{goc}{d}"
        if p.is_file():
            return p
    return None


def _chay(cmd: list, run, ten: str, nhi_phan: bool = False):
    kieu = {} if nhi_phan else {"text": True, "encoding": "utf-8", "errors": "replace"}
    try:
        proc = run(cmd, capture_output=True, timeout=600, **kieu)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise XuLyError("ffmpeg", f"Không chạy được {cmd[0]}: {exc}", FIX_FFMPEG) from exc
    if proc.returncode != 0:
        loi = proc.stderr or ""
        if isinstance(loi, bytes):
            loi = loi.decode("utf-8", errors="replace")
        raise XuLyError("ffmpeg", f"{cmd[0]} lỗi khi xử lý `{ten}` (mã {proc.returncode}): {loi.strip()[-300:]}",
                        FIX_ANH_HONG)
    return proc


def kich_thuoc(duong_dan: Path, run, ten: str) -> tuple:
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
           "-of", "csv=s=x:p=0", str(duong_dan)]
    ra = (_chay(cmd, run, ten).stdout or "").strip().splitlines()
    try:
        w, h = (int(x) for x in ra[0].split("x")[:2])
    except (IndexError, ValueError) as exc:
        raise XuLyError("ffmpeg", f"Không đọc được kích thước `{ten}`.", FIX_ANH_HONG) from exc
    return w, h


def loc_nen(w: int, h: int, rong: int, cao: int) -> tuple:
    """(bộ lọc, (rộng, cao) đầu ra, thiếu điểm ảnh). Ảnh đủ lớn: co giữ tỉ lệ để phủ khổ xuất rồi cắt giữa. Ảnh nhỏ
    hơn: không phóng to, chỉ cắt giữa vùng lớn nhất đúng tỉ lệ khổ (video_ma vẫn phủ kín khi hiển thị)."""
    if w >= rong and h >= cao:
        return (f"scale={rong}:{cao}:force_original_aspect_ratio=increase:flags=lanczos,crop={rong}:{cao}",
                (rong, cao), False)
    cw = min(w, round(h * rong / cao))
    ch = min(h, round(cw * cao / rong))
    cw, ch = cw - cw % 2, ch - ch % 2
    return f"crop={cw}:{ch}", (cw, ch), True


def do_alpha(raw: bytes, w: int, h: int) -> dict:
    """Đo kênh alpha thô (một byte một điểm, theo hàng): alpha trung bình bốn góc GOC_O×GOC_O (trái trên, phải trên,
    trái dưới, phải dưới), tỉ lệ điểm đục (> NGUONG_DUC), hộp (x, y, w, h) bao các điểm > NGUONG_CAT (None khi rỗng)."""
    o = min(GOC_O, w, h)
    goc = []
    for x0, y0 in ((0, 0), (w - o, 0), (0, h - o), (w - o, h - o)):
        tong = sum(sum(raw[(y0 + y) * w + x0:(y0 + y) * w + x0 + o]) for y in range(o))
        goc.append(tong / (o * o))
    duc = bytes(1 if i > NGUONG_DUC else 0 for i in range(256))
    cat = bytes(1 if i > NGUONG_CAT else 0 for i in range(256))
    ti_le = raw.translate(duc).count(1) / (w * h)
    x_min, x_max, y_min, y_max = w, -1, h, -1
    for y in range(h):
        hang = raw[y * w:(y + 1) * w].translate(cat)
        dau = hang.find(1)
        if dau < 0:
            continue
        x_min, x_max = min(x_min, dau), max(x_max, hang.rfind(1))
        y_min = min(y_min, y)
        y_max = y
    hop = None if x_max < 0 else (x_min, y_min, x_max - x_min + 1, y_max - y_min + 1)
    return {"goc": goc, "duc": ti_le, "hop": hop}


def mau_goc(rgba: bytes, w: int, h: int) -> list:
    """Màu trung bình (r, g, b) của bốn góc GOC_O×GOC_O trong ảnh RGBA thô, cùng thứ tự `_TEN_GOC`."""
    o = min(GOC_O, w, h)
    ra = []
    for x0, y0 in ((0, 0), (w - o, 0), (0, h - o), (w - o, h - o)):
        tong = [0, 0, 0]
        for y in range(o):
            hang = rgba[((y0 + y) * w + x0) * 4:((y0 + y) * w + x0 + o) * 4]
            for k in range(3):
                tong[k] += sum(hang[k::4])
        ra.append(tuple(round(t / (o * o)) for t in tong))
    return ra


def _la_xanh_la(mau: tuple) -> bool:
    r, g, b = mau
    return g >= 100 and g > r + 30 and g > b + 30


def kiem_alpha(do: dict, mau: list | None = None):
    """Lý do tách nền không đạt, None khi đạt. `mau`: màu trung bình bốn góc của ảnh gốc (`mau_goc`) để nói rõ vì sao
    góc còn đục: nền xanh lá nhưng không thuần #00FF00, hay bóng/viền/màu khác ở góc."""
    con_duc = []
    for k, (ten, a) in enumerate(zip(_TEN_GOC, do["goc"])):
        if a < GOC_ALPHA_TOI_DA:
            continue
        if mau is None:
            con_duc.append(f"góc {ten} còn đục (alpha trung bình {a:.0f})")
            continue
        ma = "#{:02X}{:02X}{:02X}".format(*mau[k])
        if _la_xanh_la(mau[k]):
            con_duc.append(f"góc {ten} còn đục: nền không phải xanh thuần #00FF00 (đo được {ma})")
        else:
            con_duc.append(f"góc {ten} còn đục: còn bóng hoặc viền ở góc (đo được {ma})")
    if con_duc:
        return "; ".join(con_duc)
    if do["duc"] < DUC_TOI_THIEU:
        return f"phần đục quá ít ({do['duc']:.0%}, cần ít nhất {DUC_TOI_THIEU:.0%}): nhân vật bị tách mất hoặc quá nhỏ"
    if do["duc"] > DUC_TOI_DA:
        return f"phần đục quá nhiều ({do['duc']:.0%}, tối đa {DUC_TOI_DA:.0%}): nền chưa được tách hoặc nhân vật quá to"
    return None


def _ghi(cmd: list, run, ten: str, tam: Path) -> None:
    """Chạy lệnh ghi ảnh ra `tam`; lỗi thì xoá file tạm dở dang."""
    try:
        _chay(cmd, run, ten)
    except XuLyError:
        tam.unlink(missing_ok=True)
        raise


def _thay(tam: Path, dich: Path) -> None:
    try:
        os.replace(tam, dich)
    except OSError:
        tam.unlink(missing_ok=True)
        raise


def xu_ly_nen(goc: Path, dich: Path, kho: str, ten: str, run) -> tuple:
    """Nền -> `dich` (.jpg). Trả (rộng, cao) đầu ra và cờ thiếu điểm ảnh."""
    w, h = kich_thuoc(goc, run, ten)
    rong, cao = KHO_XUAT[kho]
    loc, ra, thieu = loc_nen(w, h, rong, cao)
    tam = dich.with_name(dich.stem + ".tam" + dich.suffix)
    for q in CHAT_LUONG:
        _ghi(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(goc), "-vf", loc, "-frames:v", "1",
              "-pix_fmt", "yuvj420p", "-q:v", str(q), str(tam)], run, ten, tam)
        if tam.stat().st_size <= TOI_DA:
            break
    _thay(tam, dich)
    return (w, h), ra, thieu


def _doc_tho(goc: Path, loc: str, pix_fmt: str, byte_moi_diem: int, w: int, h: int, run, ten: str) -> bytes:
    raw = _chay(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(goc), "-vf", loc, "-frames:v", "1",
                 "-f", "rawvideo", "-pix_fmt", pix_fmt, "pipe:1"], run, ten, nhi_phan=True).stdout
    if len(raw) != w * h * byte_moi_diem:
        raise XuLyError("ffmpeg", f"Dữ liệu điểm ảnh của `{ten}` có {len(raw)} byte, cần {w * h * byte_moi_diem}.",
                        FIX_ANH_HONG)
    return bytes(raw)


def co_nho(cw: int, ch: int, he_so: float = 1.0) -> tuple:
    """Kích thước sau khi thu cạnh dài về tối đa CANH_NHAN_VAT_TOI_DA (nhân thêm `he_so` khi phải nén dưới 8 MB);
    không bao giờ phóng to."""
    ti_le = min(1.0, CANH_NHAN_VAT_TOI_DA / max(cw, ch)) * he_so
    return max(1, round(cw * ti_le)), max(1, round(ch * ti_le))


def xu_ly_nhan_vat(goc: Path, dich: Path, ten: str, run) -> None:
    """Nhân vật -> `dich` (.png RGBA): tách nền xanh (bỏ qua khi ảnh gốc đã trong suốt ở bốn góc), kiểm alpha, cắt sát
    theo hộp alpha, thu cạnh dài về tối đa 1536 px và dưới 8 MB. Không đạt: XuLyError tach-nen."""
    w, h = kich_thuoc(goc, run, ten)
    rgba = _doc_tho(goc, "format=rgba", "rgba", 4, w, h, run, ten)
    alpha_goc = rgba[3::4]
    if all(a < GOC_ALPHA_TOI_DA for a in do_alpha(alpha_goc, w, h)["goc"]):
        loc, raw = "format=rgba", alpha_goc  # ảnh đã trong suốt sẵn (vd. GPT Image): giữ nguyên alpha
    else:
        loc = LOC_TACH
        raw = _doc_tho(goc, LOC_TACH + ",alphaextract", "gray", 1, w, h, run, ten)
    do = do_alpha(raw, w, h)
    ly_do = kiem_alpha(do, mau_goc(rgba, w, h))
    if ly_do:
        raise XuLyError("tach-nen", f"`{ten}`: {ly_do}.", FIX_TACH_NEN)
    x, y, cw, ch = do["hop"]
    tam = dich.with_name(dich.stem + ".tam" + dich.suffix)
    for he_so in (1.0, 0.8, 0.64, 0.5, 0.4, 0.3):
        nw, nh = co_nho(cw, ch, he_so)
        thu = f",scale={nw}:{nh}:flags=lanczos" if (nw, nh) != (cw, ch) else ""
        _ghi(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(goc),
              "-vf", f"{loc},crop={cw}:{ch}:{x}:{y}{thu}", "-frames:v", "1", "-pix_fmt", "rgba", str(tam)], run, ten, tam)
        if tam.stat().st_size <= TOI_DA:
            break
    _thay(tam, dich)
