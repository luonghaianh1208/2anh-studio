# tools/vi/anh_vox_parts/xu_ly.py
"""Xử lý ảnh Vox (tính trước, không tính lại mỗi khung): tách nền xanh, viền giấy xé + bóng đổ cho ảnh cắt nền,
khung mép xé cho ảnh khung, cắt phủ, duotone và in chấm (halftone). Pillow + numpy; FFmpeg chỉ cho bước tách nền."""

from __future__ import annotations

import math
import os
import random
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

from anh_ai_parts.xu_ly import LOC_TACH
from anh_vox_parts import ke_hoach

GIAY = (247, 242, 230)        # màu giấy của viền và khung
MUC_IN = (34, 30, 28)         # màu mực chấm halftone khi không có duotone
MAU_DUOTONE = {"kem": ((38, 52, 94), (244, 236, 214)), "bao-cu": ((60, 48, 40), (236, 226, 204)),
               "dem": ((16, 22, 40), (120, 180, 220)), "tuoi": ((120, 30, 60), (255, 214, 120))}
CANH_TOI_DA = 1400            # cạnh dài nhất của ảnh đã xử lý
CANH_VAT_TOI_DA = 1100        # vật cắt nền trước khi thêm viền và lề bóng
GOC = 16                      # cạnh ô góc khi kiểm alpha
DO_DUC_BONG = 0.35

FIX_FFMPEG = "Cài FFmpeg theo mục \"Công cụ tuỳ chọn\" của docs/vi/cai-dat-bang-ai.md rồi chạy lại."
FIX_ANH_HONG = "File ảnh hỏng hoặc không phải ảnh: xoá file đó (ảnh vẽ sẽ được vẽ lại) hoặc thay ảnh khác rồi chạy lại."


class XuLyError(Exception):
    def __init__(self, step: str, message: str, fix: str) -> None:
        super().__init__(message)
        self.step = step
        self.message = message
        self.fix = fix


# ---------------------------------------------------------------- tách nền

def tach_nen(goc: Path, run=subprocess.run) -> Image.Image:
    """Tách nền xanh bằng bộ lọc FFmpeg của anh_ai (`LOC_TACH`), rồi dọn thêm bằng numpy: điểm xanh lá đậm (nền xanh
    không thuần, bóng đổ trên nền xanh) thành trong suốt, và gỡ ánh xanh mà không làm lệch màu vàng."""
    goc = Path(goc)
    try:
        with Image.open(goc) as im:
            san = ImageOps.exif_transpose(im).convert("RGBA")
    except OSError as exc:
        raise XuLyError("tach-nen", f"Không đọc được ảnh `{goc.name}`: {exc}", FIX_ANH_HONG) from None
    if alpha_sach(san):
        return san   # ảnh đã trong suốt sẵn (vd. GPT Image): giữ nguyên alpha
    with tempfile.TemporaryDirectory() as tmp:
        ra = Path(tmp) / "tach.png"
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(goc), "-vf", LOC_TACH, "-frames:v", "1", str(ra)]
        try:
            proc = run(cmd, capture_output=True, timeout=600)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise XuLyError("tach-nen", f"Không chạy được FFmpeg: {exc}", FIX_FFMPEG) from None
        if proc.returncode != 0 or not ra.is_file():
            loi = proc.stderr or b""
            if isinstance(loi, bytes):
                loi = loi.decode("utf-8", errors="replace")
            raise XuLyError("tach-nen", f"FFmpeg không tách nền được `{goc.name}` (mã {proc.returncode}): "
                                        f"{loi.strip()[-300:]}", FIX_ANH_HONG)
        with Image.open(ra) as im:
            a = np.array(im.convert("RGBA"), dtype=np.int16)
    o = np.asarray(san.convert("RGB")).astype(np.int16)
    if o.shape[:2] == a.shape[:2]:
        # Chỉ lấy alpha của FFmpeg; màu lấy từ ảnh GỐC vì despill của FFmpeg làm lệch màu vàng sang cam và làm xám
        # bóng đổ. Đo sắc xanh trên ảnh gốc: nền xanh đậm, nền loang và bóng đổ trên nền xanh có G trội hẳn R, B (kể
        # cả khi tối) -> trong suốt; vùng chuyển mờ dần.
        og, omx = o[..., 1].astype(np.float32), np.maximum(o[..., 0], o[..., 2]).astype(np.float32)
        troi = (og - omx) / np.maximum(og, 1.0)
        giu = np.clip((0.5 - troi) / 0.2, 0.0, 1.0)
        a[..., :3] = o
        a[..., 3] = np.minimum(a[..., 3], np.rint(255 * giu)).astype(np.int16)
    # Gỡ ánh xanh ở mép, liên tục theo màu: G không vượt ngưỡng nằm giữa trung bình (R + B) / 2
    # (màu gần trung tính -> hết ám xanh) và max(R, B) (R, B chênh nhiều như vàng, cam, xanh ngọc -> giữ sắc).
    # Despill trung bình của FFmpeg làm vàng ngả cam nên không dùng màu của nó.
    # Chỉ sửa theo độ trong suốt (điểm đục hẳn giữ đúng màu: ô liu, bạc hà, xanh ngọc), cộng dải mép 2 điểm ảnh sát
    # vùng trong suốt — nơi quầng xanh còn sót dù alpha đã 255.
    r, g, b = (a[..., k].astype(np.float32) for k in range(3))
    w = np.clip(np.abs(r - b) / 60.0, 0.0, 1.0)
    nguong = (r + b) / 2 + w * np.abs(r - b) / 2
    trong = 1.0 - a[..., 3].astype(np.float32) / 255.0
    trong[_gian(a[..., 3] < 128, 2) & (a[..., 3] >= 128)] = 1.0
    a[..., 1] = np.rint(g - trong * np.maximum(0.0, g - nguong)).astype(np.int16)
    return Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")


def alpha_sach(im: Image.Image) -> bool:
    """Bốn góc GOC×GOC gần như trong suốt và phần đục hẳn chiếm 5–90% diện tích."""
    al = np.asarray(im.convert("RGBA"))[..., 3]
    h, w = al.shape
    o = min(GOC, w, h)
    for y0, x0 in ((0, 0), (0, w - o), (h - o, 0), (h - o, w - o)):
        if al[y0:y0 + o, x0:x0 + o].mean() >= 10:
            return False
    duc = float((al == 255).mean())
    return 0.05 <= duc <= 0.90


# ---------------------------------------------------------------- hình học

def cat_phu(im: Image.Image, ti_le: float) -> Image.Image:
    """Cắt giữa về tỉ lệ rộng/cao `ti_le`, không phóng."""
    w, h = im.size
    if w / h > ti_le:
        nw = max(1, round(h * ti_le))
        x = (w - nw) // 2
        return im.crop((x, 0, x + nw, h))
    nh = max(1, round(w / ti_le))
    y = (h - nh) // 2
    return im.crop((0, y, w, y + nh))


def _thu_nho(im: Image.Image, canh: int) -> Image.Image:
    w, h = im.size
    if max(w, h) <= canh:
        return im
    k = canh / max(w, h)
    return im.resize((max(1, round(w * k)), max(1, round(h * k))), Image.LANCZOS)


def _gian1(m: np.ndarray, vuong: bool) -> np.ndarray:
    o = m.copy()
    o[1:, :] |= m[:-1, :]
    o[:-1, :] |= m[1:, :]
    o[:, 1:] |= m[:, :-1]
    o[:, :-1] |= m[:, 1:]
    if vuong:
        o[1:, 1:] |= m[:-1, :-1]
        o[1:, :-1] |= m[:-1, 1:]
        o[:-1, 1:] |= m[1:, :-1]
        o[:-1, :-1] |= m[1:, 1:]
    return o


def _gian(m: np.ndarray, buoc: int) -> np.ndarray:
    for i in range(buoc):
        m = _gian1(m, i % 2 == 1)
    return m


def _khoang_cach(m: np.ndarray, toi_da: int) -> np.ndarray:
    """Khoảng cách (điểm ảnh, xấp xỉ bát giác) từ mỗi điểm tới mặt nạ `m`, chặn ở `toi_da + 1`. Giãn lần lượt chữ thập
    rồi ô vuông nên gần với khoảng cách Euclid mà không cần scipy."""
    d = np.full(m.shape, toi_da + 1, np.int16)
    d[m] = 0
    cur = m
    for k in range(1, toi_da + 1):
        moi = _gian1(cur, k % 2 == 0)
        d[moi & ~cur] = k
        cur = moi
    return d


def _nhieu_vong(rng: random.Random, so_moc: int, bien_do: float, goc: np.ndarray) -> np.ndarray:
    """Nhiễu giá trị 1D tuần hoàn theo góc: `so_moc` mốc ngẫu nhiên, nội suy tuyến tính."""
    moc = [rng.uniform(-bien_do, bien_do) for _ in range(so_moc)]
    xp = np.linspace(-math.pi, math.pi, so_moc + 1)
    return np.interp(goc, xp, moc + moc[:1])


def _thot_giay(shape, hat: int, bien_do: int = 6) -> np.ndarray:
    """Thớ giấy: nhiễu ±bien_do, kéo dài theo chiều ngang cho giống sợi giấy."""
    nrng = np.random.default_rng(random.Random(hat).getrandbits(32))
    h, w = shape
    tho = nrng.integers(-bien_do, bien_do + 1, size=(h, max(1, w // 3 + 1))).astype(np.float32)
    tho = np.repeat(tho, 3, axis=1)[:, :w]
    tho += nrng.integers(-2, 3, size=(h, w))
    return tho


def _to_giay(mask_l: Image.Image, hat: int) -> Image.Image:
    """Lớp giấy RGBA có thớ, alpha theo `mask_l`."""
    w, h = mask_l.size
    tho = _thot_giay((h, w), hat)
    rgb = np.clip(np.array(GIAY, np.float32)[None, None, :] + tho[..., None], 0, 255).astype(np.uint8)
    lop = Image.fromarray(rgb, "RGB").convert("RGBA")
    lop.putalpha(mask_l)
    return lop


def _bong(alpha_l: Image.Image, dx: int, dy: int, mo: float) -> Image.Image:
    """Bóng đổ: alpha làm mờ Gauss, độ đục DO_DUC_BONG, lệch (dx, dy)."""
    a = alpha_l.filter(ImageFilter.GaussianBlur(mo)).point(lambda v: round(v * DO_DUC_BONG))
    lech = Image.new("L", alpha_l.size, 0)
    lech.paste(a, (dx, dy))
    bong = Image.new("RGBA", alpha_l.size, (24, 18, 12, 0))
    bong.putalpha(lech)
    return bong


def _lap_lo(mask: np.ndarray) -> np.ndarray:
    """Lấp các lỗ kín trong mặt nạ (vd. quai cốc): loang từ góc ngoài, phần không loang tới là bên trong."""
    # .copy(): ảnh dựng từ fromarray dùng chung bộ nhớ với mảng, floodfill ghi vào đó không có tác dụng.
    nen = Image.fromarray(np.where(mask, 255, 0).astype(np.uint8), "L").copy()
    ImageDraw.floodfill(nen, (0, 0), 128)
    return np.asarray(nen) != 128


def vien_xe(im_rgba: Image.Image, hat: int) -> Image.Image:
    """Vật đã tách nền -> vật trên mảnh giấy xé trắng ngà (mép răng cưa theo `hat`, thớ giấy, lỗ kín được lấp),
    bóng đổ mềm, lề trong suốt đều bốn phía để bóng không bị cắt."""
    vat = im_rgba.convert("RGBA")
    w, h = vat.size
    r = max(8, round(0.035 * max(w, h)))
    xa_nhat = math.ceil(1.6 * r)                        # viền dày nhất có thể
    lech_bong = (max(1, round(0.3 * r)), max(1, round(0.6 * r)))
    mo_bong = 0.5 * r
    pad = xa_nhat + lech_bong[1] + math.ceil(3 * mo_bong) + 2
    W, H = w + 2 * pad, h + 2 * pad
    nen = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nen.paste(vat, (pad, pad))
    al = np.asarray(nen)[..., 3]
    m = al > 128

    d = _khoang_cach(m, xa_nhat)
    ys, xs = np.nonzero(m)
    cy, cx = (ys.mean(), xs.mean()) if len(ys) else (H / 2, W / 2)
    yy, xx = np.mgrid[0:H, 0:W]
    goc = np.arctan2(yy - cy, xx - cx)
    rng = random.Random(hat)
    nhieu = (_nhieu_vong(rng, 64, 0.45, goc)          # mép lượn to
             + _nhieu_vong(rng, 220, 0.14, goc)       # răng xé
             + _nhieu_vong(rng, 700, 0.07, goc))      # sợi giấy
    gioi = r * (1 + np.clip(nhieu, -0.3, 0.6))
    vien = _lap_lo((d <= gioi) | m)

    cung = Image.fromarray(np.where(vien, 255, 0).astype(np.uint8), "L")
    # Khử răng cưa ra phía ngoài, giữ trong viền đục hẳn.
    mem = Image.fromarray(np.maximum(np.asarray(cung), np.asarray(cung.filter(ImageFilter.GaussianBlur(0.8)))), "L")
    giay = _to_giay(mem, hat + 1)
    # Mép xé hơi tối để viền tách khỏi nền giấy sáng.
    trong = ~_gian(~vien, 2)
    mep = vien & ~trong
    ga = np.asarray(giay).astype(np.float32)
    ga[mep, :3] *= 0.9
    giay = Image.fromarray(ga.astype(np.uint8), "RGBA")

    ra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ra = Image.alpha_composite(ra, _bong(mem, lech_bong[0], lech_bong[1], mo_bong))
    ra = Image.alpha_composite(ra, giay)
    return Image.alpha_composite(ra, nen)


def _canh_xe(rng: random.Random, dai: float, s: float, sau: tuple) -> list:
    """Danh sách (vị trí dọc cạnh, độ lõm vào) của một cạnh xé, nhân hệ số `s`: độ sâu lượn chậm trong khoảng `sau`
    (mốc cách nhau ~70 px, nội suy) cộng răng nhỏ không đều (bước 3–12 px) để mép trông như giấy xé tay."""
    moc = [rng.random() for _ in range(int(dai / (70 * s)) + 2)]

    def sau_tai(t: float) -> float:
        lan = float(np.interp(t / (70 * s), range(len(moc)), moc))
        return max(0.0, (sau[0] + (sau[1] - sau[0]) * lan + rng.uniform(-1.8, 1.8)) * s)

    diem = [(0.0, sau_tai(0.0))]
    t = 0.0
    while True:
        t += rng.uniform(3, 12) * s
        if t >= dai:
            break
        diem.append((t, sau_tai(t)))
    diem.append((dai, sau_tai(dai)))
    return diem


def _mat_na_xe(kich: tuple, hop: tuple, xe: set, rng, s: float, sau: tuple, ss: int) -> Image.Image:
    """Mặt nạ L chữ nhật `hop` = (x0, y0, x1, y1), vẽ ở `ss`× rồi thu về `kich` cho mép mịn; mỗi cạnh trong `xe` bị
    xé lõm vào trong. Xé bằng cách xoá dải ngoài răng cưa của từng cạnh, nên hai cạnh xé gặp nhau ở góc không tạo gai."""
    x0, y0, x1, y1 = (c * ss for c in hop)
    m = Image.new("L", (kich[0] * ss, kich[1] * ss), 0)
    ve = ImageDraw.Draw(m)
    ve.rectangle((x0, y0, x1 - 1, y1 - 1), fill=255)
    for canh in ("tren", "phai", "duoi", "trai"):   # thứ tự cố định để tất định
        if canh not in xe:
            continue
        doc = canh in ("phai", "trai")
        dai = (y1 - y0) if doc else (x1 - x0)
        rang = [(t * ss, k * ss) for t, k in _canh_xe(rng, dai / ss, s, sau)]
        if canh == "tren":
            pts = [(x0 + t, y0 + k) for t, k in rang] + [(x1 + 2, y0 - 2), (x0 - 2, y0 - 2)]
        elif canh == "duoi":
            pts = [(x0 + t, y1 - k) for t, k in rang] + [(x1 + 2, y1 + 2), (x0 - 2, y1 + 2)]
        elif canh == "trai":
            pts = [(x0 + k, y0 + t) for t, k in rang] + [(x0 - 2, y1 + 2), (x0 - 2, y0 - 2)]
        else:
            pts = [(x1 - k, y0 + t) for t, k in rang] + [(x1 + 2, y1 + 2), (x1 + 2, y0 - 2)]
        ve.polygon(pts, fill=0)
    return m.resize(kich, Image.LANCZOS)


def khung_xe(im_rgb: Image.Image, hat: int) -> Image.Image:
    """Ảnh -> ảnh in trên giấy: viền giấy trắng 1,5%, hai cạnh mép xé (luôn có cạnh trên hoặc dưới; dải giấy trắng
    ở mép xé rộng hẹp không đều), hai cạnh thẳng, bóng đổ, lề trong suốt."""
    anh = im_rgb.convert("RGB")
    w, h = anh.size
    s = max(1.0, max(w, h) / 700)
    v = max(3, round(0.015 * max(w, h)))
    lech_bong = (max(2, round(2 * s)), max(3, round(5 * s)))
    mo_bong = 4 * s
    pad = max(round(0.02 * max(w, h)), lech_bong[1] + math.ceil(3 * mo_bong) + 2)
    W, H = w + 2 * v + 2 * pad, h + 2 * v + 2 * pad
    rng = random.Random(hat)
    ngang = rng.choice(["tren", "duoi"])
    xe = {ngang, rng.choice([c for c in ("tren", "phai", "duoi", "trai") if c != ngang])}

    x0, y0, x1, y1 = pad, pad, pad + w + 2 * v, pad + h + 2 * v
    giay_m = _mat_na_xe((W, H), (x0, y0, x1, y1), xe, rng, s, (0, 7), 2)
    # Mép ảnh xé sâu hơn mép giấy nên lộ dải giấy trắng rộng hẹp không đều.
    anh_m = _mat_na_xe((W, H), (x0 + v, y0 + v, x1 - v, y1 - v), xe, rng, s, (2, 14), 2)

    ra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ra = Image.alpha_composite(ra, _bong(giay_m, lech_bong[0], lech_bong[1], mo_bong))
    ra = Image.alpha_composite(ra, _to_giay(giay_m, hat + 1))
    lop = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lop.paste(anh, (pad + v, pad + v))
    lop.putalpha(anh_m)
    return Image.alpha_composite(ra, lop)


# ---------------------------------------------------------------- hiệu ứng in

def _tach_alpha(im: Image.Image):
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        im = im.convert("RGBA")
        return im.convert("RGB"), im.getchannel("A")
    return im.convert("RGB"), None


def duotone(im: Image.Image, mau_toi, mau_sang) -> Image.Image:
    """Hai màu: độ sáng 0 -> `mau_toi`, 255 -> `mau_sang`, nội suy tuyến tính; giữ alpha."""
    rgb, al = _tach_alpha(im)
    xam = rgb.convert("L")
    kenh = [xam.point([round(t + (s - t) * v / 255) for v in range(256)]) for t, s in zip(mau_toi, mau_sang)]
    ra = Image.merge("RGB", kenh)
    if al is not None:
        ra = ra.convert("RGBA")
        ra.putalpha(al)
    return ra


def halftone(im: Image.Image, buoc: int = 8, mau_muc=MUC_IN, mau_giay=GIAY) -> Image.Image:
    """In chấm: lưới chấm tròn xoay 45°, bán kính theo độ tối trung bình quanh chấm, màu mực trên màu giấy. Vẽ ở 2×
    rồi thu nhỏ nên chỉ có 5 mức phủ (ít màu, mép chấm mịn); giữ alpha."""
    rgb, al = _tach_alpha(im)
    xam = rgb.convert("L").filter(ImageFilter.BoxBlur(max(1, buoc // 2)))
    toi = 1.0 - np.asarray(xam, np.float32) / 255.0
    w, h = rgb.size
    ss = 2
    ys, xs = np.mgrid[0:h * ss, 0:w * ss].astype(np.float32)
    xs = (xs + 0.5) / ss
    ys = (ys + 0.5) / ss
    c = math.sqrt(0.5)
    u, v = (xs + ys) * c, (xs - ys) * c
    uc = (np.floor(u / buoc) + 0.5) * buoc
    vc = (np.floor(v / buoc) + 0.5) * buoc
    # Tâm chấm về toạ độ ảnh để đọc độ tối.
    xc = np.clip(((uc + vc) * c).astype(np.int32), 0, w - 1)
    yc = np.clip(((uc - vc) * c).astype(np.int32), 0, h - 1)
    ban_kinh = np.minimum(buoc * np.sqrt(toi[yc, xc] / math.pi), buoc * 0.72)
    phu = ((u - uc) ** 2 + (v - vc) ** 2) < ban_kinh ** 2
    phu = phu.reshape(h, ss, w, ss).mean(axis=(1, 3))
    muc = np.array(mau_muc, np.float32)
    giay = np.array(mau_giay, np.float32)
    ra = np.rint(giay + (muc - giay) * phu[..., None]).astype(np.uint8)
    out = Image.fromarray(ra, "RGB")
    if al is not None:
        out = out.convert("RGBA")
        out.putalpha(al)
    return out


def _hieu_ung_in(im: Image.Image, tuy_chon, bang_mau: str) -> Image.Image:
    toi, sang = MAU_DUOTONE.get(bang_mau, MAU_DUOTONE["kem"])
    if "duotone" in tuy_chon:
        rgb, al = _tach_alpha(im)
        xam = ImageOps.autocontrast(rgb.convert("L"), cutoff=1,
                                    mask=al.point(lambda a: 255 if a > 128 else 0) if al is not None else None)
        im = duotone(xam.convert("RGB") if al is None else Image.merge("RGBA", (xam, xam, xam, al)), toi, sang)
    if "halftone" in tuy_chon:
        buoc = max(8, round(max(im.size) / 90))
        im = halftone(im, buoc, toi, sang) if "duotone" in tuy_chon else halftone(im, buoc)
    return im


# ---------------------------------------------------------------- một mục

def _mo(goc: Path) -> Image.Image:
    try:
        with Image.open(goc) as im:
            im.load()
            return ImageOps.exif_transpose(im)
    except OSError as exc:
        raise XuLyError("input", f"Không đọc được ảnh `{goc.name}`: {exc}", FIX_ANH_HONG) from None


def _cat_sat(im: Image.Image) -> Image.Image:
    hop = im.getchannel("A").point(lambda a: 255 if a > 16 else 0).getbbox()
    return im.crop(hop) if hop else im


def xu_ly_muc(thu_muc: Path, muc, run=subprocess.run, kho: str = "ngang", bang_mau: str = "kem") -> list:
    """Xử lý một mục kế hoạch thành `ke_hoach.file_xu_ly`. Ảnh cắt nền tách không sạch: chuyển sang khung
    (đặt `muc.kieu = "khung"` để bên gọi biết kiểu cuối) và trả cảnh báo. Trả danh sách cảnh báo."""
    thu_muc = Path(thu_muc)
    goc = ke_hoach.file_goc(thu_muc, muc)
    if not goc.is_file():
        raise XuLyError("input", f"Không có file `{goc.relative_to(thu_muc).as_posix()}`.",
                        "Đặt ảnh đúng tên đó vào thư mục `anh/` hoặc sửa nhịp `anh:` trong video.md rồi chạy lại.")
    canh_bao = []
    hat = ke_hoach.hat(muc)
    ra = None
    if muc.kieu == "cat":
        vat = tach_nen(goc, run)
        if alpha_sach(vat):
            vat = _thu_nho(_cat_sat(vat), CANH_VAT_TOI_DA)
            ra = vien_xe(_hieu_ung_in(vat, muc.tuy_chon, bang_mau), hat)
            ra = ra.crop(ra.getchannel("A").getbbox() or (0, 0) + ra.size)
        else:
            canh_bao.append(f"Cảnh {muc.canh}, nhịp {muc.chi_so + 1}: ảnh tách nền không sạch, đã chuyển sang `khung`.")
            muc.kieu = "khung"
    if muc.kieu == "khung":
        anh = cat_phu(_mo(goc).convert("RGB"), 1.5 if kho == "ngang" else 1 / 1.5)
        anh = _thu_nho(anh, CANH_TOI_DA - 80)
        ra = khung_xe(_hieu_ung_in(anh, muc.tuy_chon, bang_mau), hat)
    elif muc.kieu == "phu":
        anh = cat_phu(_mo(goc).convert("RGB"), 16 / 9 if kho == "ngang" else 9 / 16)
        ra = _hieu_ung_in(_thu_nho(anh, CANH_TOI_DA), muc.tuy_chon, bang_mau)
    ra = _thu_nho(ra, CANH_TOI_DA)
    dich = ke_hoach.file_xu_ly(thu_muc, muc)
    dich.parent.mkdir(parents=True, exist_ok=True)
    tam = dich.with_name(dich.stem + ".tam.png")
    try:
        ra.save(tam, "PNG")
        os.replace(tam, dich)
    except OSError:
        tam.unlink(missing_ok=True)
        raise
    return canh_bao
