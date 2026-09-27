"""Phụ đề karaoke: file .ass với \\kf theo mốc từng từ, font theo chủ đề (`kieu_phu_de`). Chỉ dùng thư viện chuẩn.

Chữ hiển thị luôn là token gốc của kịch bản (đã bỏ đánh dấu nhấn nhưng giữ nguyên dấu câu, chữ hoa/thường);
mốc thời gian của từng token lấy từ sự kiện giọng máy (`tu`) bằng đúng phép khớp chữ mà `giong.py` dùng cho
mốc đầu câu (`giong.can_chinh_tu`), vì một token kịch bản có thể trải trên nhiều sự kiện (số đọc từng chữ
số) hoặc nhiều token gộp vào một sự kiện. Không khớp chắc chắn được thì chia đều theo tỉ lệ ký tự, như
đường ước lượng của `lich.moc_tu_uoc_luong`.
"""

from __future__ import annotations

import re

from . import giong
from .lich import doan_loi

GIOI_HAN_NGANG = 42
GIOI_HAN_DOC = 22
GIOI_HAN_KY_TU = GIOI_HAN_NGANG  # tên cũ, giữ để không phá chữ ký hàm hiện có
FONT_VIET_TAY = "Itim"
# Tên họ font thật trong bảng `name` của TTF (không phải `phong.TEN_CAT_DAN` dùng cho CSS @font-face),
# vì FFmpeg/libass khớp font qua fontsdir bằng tên họ đọc từ chính file, không phải chuỗi CSS tự đặt.
FONT_CAT_DAN = "Be Vietnam Pro"
_MARKUP_RE = re.compile(r"\*\*|~|\^|==|\(\(|\)\)|__|\{\{|\}\}")
# libass không có thoát cho dấu gạch ngược: `\` trong chữ thầy cô (`a\Nb`, `\h`) đổi thành ⧵ (U+29F5, trông gần như
# nhau) để không bao giờ thành mã điều khiển; `{`, `}` thoát bằng dấu gạch ngược đứng trước.
_ESCAPE = (("\\", "⧵"), ("{", "\\{"), ("}", "\\}"))

_STYLE_ITIM = ("Style: Itim,Itim,40,&H0000D7FF,&H00FFFFFF,&H00000000,&H00000000,"
               "0,0,0,0,100,100,1.25,0,1,3,0,2,10,10,55,1")


def _style_khung(font: str) -> str:
    """Kiểu có khung nền (`cat-dan` hoặc khổ `doc`): chữ trắng (Primary), từ đang đọc tô vàng (Secondary, `\\kf`
    sáng dần từ Secondary sang Primary); nền đen 60% (`BackColour`), viền cùng màu nền để khung liền (`OutlineColour`)."""
    return (f"Style: Khung,{font},40,&H00FFFFFF,&H0000D7FF,&H66000000,&H66000000,"
            "0,0,0,0,100,100,1.25,0,3,3,0,2,10,10,55,1")


def kieu_phu_de(chu_de: str, kho_ten: str) -> dict:
    """Kiểu phụ đề karaoke theo chủ đề (`viet-tay`/`cat-dan`) và khổ (`ngang`/`doc`): font, cỡ chữ, có khung nền
    hay không, giới hạn ký tự một dòng. `cat-dan` hoặc bất kỳ khổ `doc` đều có khung."""
    return {
        "font": FONT_CAT_DAN if chu_de == "cat-dan" else FONT_VIET_TAY,
        "co": 40,
        "khung": chu_de == "cat-dan" or kho_ten == "doc",
        "gioi_han": GIOI_HAN_DOC if kho_ten == "doc" else GIOI_HAN_NGANG,
    }


def _header(rong: int, cao: int, style_line: str) -> str:
    return f"""[Script Info]
Title: Phụ đề karaoke
ScriptType: v4.00+
PlayResX: {rong}
PlayResY: {cao}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{style_line}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def _thoat(chu: str) -> str:
    for cu, moi in _ESCAPE:
        chu = chu.replace(cu, moi)
    return chu


def _thoi_gian(giay: float) -> str:
    giay = max(giay, 0.0)
    tong_cs = int(round(giay * 100))
    gio, du = divmod(tong_cs, 360000)
    phut, du = divmod(du, 6000)
    s, cs = divmod(du, 100)
    return f"{gio}:{phut:02d}:{s:02d}.{cs:02d}"


def _boc_dong(tokens: list, gioi_han: int = GIOI_HAN_KY_TU) -> list:
    """Chia chỉ số token (0..n-1) thành các dòng, mỗi dòng tối đa `gioi_han` ký tự hiển thị, không cắt giữa từ."""
    dong: list = []
    hien: list = []
    dai = 0
    for i, tok in enumerate(tokens):
        them = len(tok) + (1 if hien else 0)
        if hien and dai + them > gioi_han:
            dong.append(hien)
            hien, dai = [], 0
            them = len(tok)
        hien.append(i)
        dai += them
    if hien:
        dong.append(hien)
    return dong or [[]]


def _do_dai_dong(chi_so: list, tokens: list) -> int:
    return sum(len(tokens[i]) for i in chi_so) + len(chi_so) - 1


def _can_bang_hai_dong(nhom_dong: list, tokens: list, gioi_han: int = GIOI_HAN_KY_TU) -> list:
    """Cân bằng lại ranh giới giữa 2 dòng của cùng một Dialogue (độ dài ~ số ký tự) để dòng 2 không mồ côi:
    khi gộp lại có ít nhất 4 từ, dòng 2 phải có ít nhất 2 từ. Không đổi tập token, chỉ đổi điểm cắt."""
    if len(nhom_dong) != 2:
        return nhom_dong
    chi_so = nhom_dong[0] + nhom_dong[1]
    if len(chi_so) < 4:
        return nhom_dong
    tot_nhat = None
    for k in range(2, len(chi_so) - 1):
        d1, d2 = chi_so[:k], chi_so[k:]
        l1, l2 = _do_dai_dong(d1, tokens), _do_dai_dong(d2, tokens)
        if l1 > gioi_han or l2 > gioi_han:
            continue
        lech = abs(l1 - l2)
        if tot_nhat is None or lech < tot_nhat[0]:
            tot_nhat = (lech, d1, d2)
    return nhom_dong if tot_nhat is None else [tot_nhat[1], tot_nhat[2]]


def _chia_ti_le(tokens: list, start: float, end: float) -> list:
    """Chia đều theo tỉ lệ ký tự trong `[start, end)`, như `lich.moc_tu_uoc_luong` — dùng khi không có sự
    kiện giọng máy, hoặc khi khớp chữ với sự kiện không đủ tin cậy."""
    tong = sum(len(t) for t in tokens) or 1
    da_qua = 0
    ket = []
    for t in tokens:
        ket.append(start + da_qua / tong * (end - start))
        da_qua += len(t)
    return ket


def _noi_suy_theo_su_kien(idx_su_kien: list, tokens: list, tu: list, start: float, end: float) -> list:
    """Mốc bắt đầu từng token: token khớp trực tiếp với sự kiện thì lấy đúng giờ sự kiện đó; token bị gộp
    vào sự kiện của token liền trước (`idx_su_kien[k] is None`) thì chia đều theo tỉ lệ ký tự giữa hai mốc
    đã biết gần nhất (hoặc `start`/`end` ở hai đầu)."""
    n = len(tokens)
    biet = [tu[idx]["t"] if idx is not None else None for idx in idx_su_kien]
    ket: list = [None] * n
    k = 0
    while k < n:
        if biet[k] is not None:
            ket[k] = biet[k]
            k += 1
            continue
        m = k
        while m < n and biet[m] is None:
            m += 1
        truoc_t = biet[k - 1] if k > 0 else start
        sau_t = biet[m] if m < n else end
        tong = sum(len(tokens[x]) for x in range(k, m)) or 1
        da_qua = 0
        for x in range(k, m):
            ket[x] = truoc_t + da_qua / tong * (sau_t - truoc_t)
            da_qua += len(tokens[x])
        k = m
    return ket


def _mocs_tu_kich_ban(tokens: list, tu: list, start: float, end: float) -> list:
    if not tokens:
        return []
    if not tu:
        return _chia_ti_le(tokens, start, end)
    chuan_tu = [giong._chuan_hoa(t) for t in tokens]
    chuan_su_kien = [giong._chuan_hoa(w["chu"]) for w in tu]
    idx_su_kien, _i, j = giong.can_chinh_tu(chuan_tu, chuan_su_kien)
    khop = idx_su_kien[0] is not None and abs(len(tu) - j) <= max(3, round(len(tu) * 0.1))
    if not khop:
        return _chia_ti_le(tokens, start, end)
    return _noi_suy_theo_su_kien(idx_su_kien, tokens, tu, start, end)


def _nhom_cau(cl) -> list:
    """Gom mốc từ theo từng câu của từng đoạn lời (`lich.doan_loi`: lời, và lời giải của cảnh câu hỏi);
    trả `[(cau_text, start, end, [tu...])]` (thời gian trong cảnh)."""
    ket: list = []
    for cau, moc_cau, het, moc_tu in doan_loi(cl):
        if not cau:
            continue
        bien = list(moc_cau[1:]) + [het]
        nhom = [[] for _ in cau]
        idx = 0
        for w in moc_tu:
            while idx < len(bien) - 1 and w["t"] >= bien[idx] - 1e-6:
                idx += 1
            nhom[idx].append(w)
        ket.extend((cau[k], moc_cau[k], bien[k], nhom[k]) for k in range(len(cau)))
    return ket


def _kf_cs(neo: float, moc: list) -> list:
    """`moc`: n+1 mốc giây (đầu = neo), trả n khoảng centi-giây không âm, không giảm, cộng lại đúng tổng."""
    cs = [max(round((m - neo) * 100), 0) for m in moc]
    for i in range(1, len(cs)):
        cs[i] = max(cs[i], cs[i - 1])
    return [cs[i + 1] - cs[i] for i in range(len(cs) - 1)]


def _dialogue(bat_dau_canh: float, start: float, end: float, style: str) -> str:
    return (f"Dialogue: 0,{_thoi_gian(bat_dau_canh + start)},{_thoi_gian(bat_dau_canh + end)},"
            f"{style},,0,0,0,,")


def _nhom_theo_dong_doi(dong: list, tokens: list, gioi_han: int) -> list:
    """Gộp các dòng (chỉ số toàn cục) thành từng nhóm tối đa 2 dòng = 1 Dialogue, cân bằng lại ranh giới
    ở nhóm có đúng 2 dòng."""
    return [_can_bang_hai_dong(dong[i:i + 2], tokens, gioi_han) for i in range(0, len(dong), 2)]


def _tach_theo_dau_phay(tokens: list) -> list:
    """Chỉ số token (0..n-1), tách thành các mệnh đề tại token kết thúc bằng dấu phẩy (giữ dấu phẩy ở cuối)."""
    doan: list = []
    hien: list = []
    for i, tok in enumerate(tokens):
        hien.append(i)
        if tok.endswith(","):
            doan.append(hien)
            hien = []
    if hien:
        doan.append(hien)
    return doan or [[]]


def _tach_thanh_cac_phan(tokens: list, gioi_han: int) -> list:
    """Câu quá dài ở khổ dọc: tách theo dấu phẩy trước; mệnh đề nào vẫn còn dài hơn 2 dòng thì tách tiếp
    theo dòng/từ (như đường cũ). Trả về danh sách "phần", mỗi phần là 1-2 dòng (chỉ số toàn cục)."""
    ket: list = []
    for menh_de in _tach_theo_dau_phay(tokens):
        con = [tokens[i] for i in menh_de]
        dong_menh_de = [[menh_de[j] for j in d] for d in _boc_dong(con, gioi_han)]
        ket.extend(_nhom_theo_dong_doi(dong_menh_de, tokens, gioi_han))
    return ket


def _dialogue_tu_nhom(nhom_dong: list, tokens: list, texts: list, moc: list, bat_dau_canh: float, style: str) -> str:
    chi_so = [j for dong_k in nhom_dong for j in dong_k]
    g_start, g_end = moc[chi_so[0]], moc[chi_so[-1] + 1]
    kf = _kf_cs(g_start, [moc[j] for j in chi_so] + [g_end])
    parts = []
    pos = 0
    for li, dong_k in enumerate(nhom_dong):
        for j2, idx in enumerate(dong_k):
            dai = kf[pos]
            pos += 1
            cuoi_dong = j2 == len(dong_k) - 1
            if cuoi_dong:
                hau_to = "\\N" if li < len(nhom_dong) - 1 else ""
            else:
                hau_to = " "
            parts.append(f"{{\\kf{dai}}}{texts[idx]}{hau_to}")
    return _dialogue(bat_dau_canh, g_start, g_end, style) + "".join(parts)


def _dialogues_cau(bat_dau_canh: float, start: float, end: float, tu: list, cau_text: str,
                    gioi_han: int = GIOI_HAN_NGANG, style: str = "Itim", tach_menh_de: bool = False,
                    canh_bao: list | None = None, so_canh=None) -> list:
    tokens = _MARKUP_RE.sub("", cau_text).split()
    if not tokens:
        return []
    texts = [_thoat(t) for t in tokens]
    moc_bat_dau = _mocs_tu_kich_ban(tokens, tu, start, end)
    moc = moc_bat_dau + [end]
    dong = _boc_dong(tokens, gioi_han)
    if tach_menh_de and len(dong) > 2:
        cac_phan = _tach_thanh_cac_phan(tokens, gioi_han)
        if canh_bao is not None and len(cac_phan) > 1:
            canh_bao.append(f"Cảnh {so_canh}: câu phụ đề dài, đã tách thành {len(cac_phan)} phần.")
    else:
        cac_phan = _nhom_theo_dong_doi(dong, tokens, gioi_han)
    return [_dialogue_tu_nhom(nhom, tokens, texts, moc, bat_dau_canh, style) for nhom in cac_phan]


def tao_ass(cac_lich: list, rong: int = 1280, cao: int = 720, chu_de: str = "viet-tay", kho_ten: str = "ngang",
            canh_bao: list | None = None) -> str:
    """`chu_de` (`du["chuDe"]["ten"]`) và `kho_ten` (`ngang`/`doc`) chọn font, khung nền và giới hạn ký tự
    (`kieu_phu_de`); mặc định giữ đúng đường `viet-tay` khổ ngang cũ (Itim, không khung, 42 ký tự)."""
    kieu = kieu_phu_de(chu_de, kho_ten)
    if kieu["khung"]:
        style_name, style_line = "Khung", _style_khung(kieu["font"])
    else:
        style_name, style_line = "Itim", _STYLE_ITIM
    tach_menh_de = kho_ten == "doc"
    dialogues: list = []
    for cl in cac_lich:
        for cau_text, start, end, tu in _nhom_cau(cl):
            dialogues.extend(_dialogues_cau(cl.bat_dau, start, end, tu, cau_text, gioi_han=kieu["gioi_han"],
                                            style=style_name, tach_menh_de=tach_menh_de, canh_bao=canh_bao,
                                            so_canh=cl.so))
    return _header(rong, cao, style_line) + "\n".join(dialogues) + ("\n" if dialogues else "")
