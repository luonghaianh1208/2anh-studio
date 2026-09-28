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

# Khung nền (`cat-dan` hoặc khổ `doc`): một hộp bo góc liền cho MỖI DÒNG VẬT LÝ, vẽ bằng `\p1` (không dùng
# BorderStyle=3: libass vẽ hộp theo từng cụm `\kf` nên ra nhiều hộp rời theo từ; BorderStyle=4 cũng không hợp vì
# libass gộp cả khối nhiều dòng thành một hộp theo dòng rộng nhất, không co theo từng dòng). Cả hộp lẫn chữ neo
# `\an7\pos(x,y)` ở góc trên-trái: dùng `\an5` (giữa) cùng lúc với một sự kiện `\p1` khác đang hiển thị khiến
# libass (bản FFmpeg 8.1.2 kèm) lệch vị trí chữ xuống dưới-phải một cách sai (đã kiểm bằng đốt FFmpeg thật,
# xem báo cáo Task 7); `\an7` không bị lỗi này.
KHUNG_CAO_HOP = 50       # chiều cao hộp, điểm CSS
KHUNG_BAN_KINH = 14      # bán kính bo góc
KHUNG_DEM_NGANG = 14     # đệm ngang mỗi bên giữa chữ và mép hộp
KHUNG_DEM_DOC_CHU = 6    # khoảng từ mép trên hộp tới đỉnh chữ
KHUNG_RONG_KY_TU = 15    # ước lượng bảo thủ độ rộng một ký tự ở Fontsize 40 (đo bằng đốt FFmpeg thật)
KHUNG_KHOANG_DONG = 56   # khoảng cách theo chiều dọc giữa tâm hai dòng liền nhau
KHUNG_LE_DUOI = 60       # khoảng từ tâm dòng cuối tới mép dưới khung hình

_STYLE_KHUNG_NEN = ("Style: KhungNen,Itim,40,&H66000000,&H66000000,&H00000000,&H00000000,"
                    "0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1")


def _style_khung_chu(font: str) -> str:
    """Kiểu chữ trong khung nền: chữ trắng (Primary), từ đang đọc tô vàng (Secondary, `\\kf` sáng dần từ
    Secondary sang Primary); không viền/bóng riêng vì độ tương phản đã có từ hộp nền."""
    return f"Style: Khung,{font},40,&H00FFFFFF,&H0000D7FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1"


def _duong_ve_hop(rong_hop: float, cao_hop: float, ban_kinh: float) -> str:
    """Đường vẽ ASS (`\\p1`) hình chữ nhật bo góc, gốc toạ độ ở góc trên-trái (dùng với `\\an7\\pos`)."""
    def f(v: float) -> str:
        return f"{v:.0f}"
    r, w, h = ban_kinh, rong_hop, cao_hop
    return (f"m {f(r)} 0 l {f(w - r)} 0 "
            f"b {f(w)} 0 {f(w)} 0 {f(w)} {f(r)} "
            f"l {f(w)} {f(h - r)} "
            f"b {f(w)} {f(h)} {f(w)} {f(h)} {f(w - r)} {f(h)} "
            f"l {f(r)} {f(h)} "
            f"b 0 {f(h)} 0 {f(h)} 0 {f(h - r)} "
            f"l 0 {f(r)} "
            f"b 0 0 0 0 {f(r)} 0")


def _do_rong_dong(chi_so: list, tokens: list) -> float:
    """Ước lượng độ rộng hiển thị (điểm CSS) của một dòng vật lý, từ số ký tự (kể khoảng trắng)."""
    return _do_dai_dong(chi_so, tokens) * KHUNG_RONG_KY_TU


def kieu_phu_de(chu_de: str, kho_ten: str) -> dict:
    """Kiểu phụ đề karaoke theo chủ đề (`viet-tay`/`cat-dan`) và khổ (`ngang`/`doc`): font, cỡ chữ, có khung nền
    hay không, giới hạn ký tự một dòng. `cat-dan` hoặc bất kỳ khổ `doc` đều có khung."""
    return {
        "font": FONT_CAT_DAN if chu_de == "cat-dan" else FONT_VIET_TAY,
        "co": 40,
        "khung": chu_de == "cat-dan" or kho_ten == "doc",
        "gioi_han": GIOI_HAN_DOC if kho_ten == "doc" else GIOI_HAN_NGANG,
    }


def _header(rong: int, cao: int, style_lines: list) -> str:
    style_block = "\n".join(style_lines)
    return f"""[Script Info]
Title: Phụ đề karaoke
ScriptType: v4.00+
PlayResX: {rong}
PlayResY: {cao}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{style_block}

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


def _dialogue(bat_dau_canh: float, start: float, end: float, style: str, layer: int = 0) -> str:
    return (f"Dialogue: {layer},{_thoi_gian(bat_dau_canh + start)},{_thoi_gian(bat_dau_canh + end)},"
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


def _dialogues_khung_tu_nhom(nhom_dong: list, tokens: list, texts: list, moc: list, bat_dau_canh: float,
                              rong: int, cao: int) -> list:
    """Khung nền: mỗi dòng vật lý trong `nhom_dong` (1-2 dòng) ra 2 sự kiện cùng Start/End — hộp nền (Layer 0,
    kiểu `KhungNen`) và chữ (Layer 1, kiểu `Khung`) — neo cùng `\\an7\\pos` nên hộp luôn khít đúng dòng của nó,
    không phải một hộp chung cho cả khối nhiều dòng."""
    k = len(nhom_dong)
    g_start = moc[nhom_dong[0][0]]
    g_end = moc[nhom_dong[-1][-1] + 1]
    giua_x = rong / 2
    y_duoi = cao - KHUNG_LE_DUOI
    ket: list = []
    for li, dong_k in enumerate(nhom_dong):
        cy = y_duoi - (k - 1 - li) * KHUNG_KHOANG_DONG
        cuc_bo_end = moc[nhom_dong[li + 1][0]] if li + 1 < k else g_end
        kf = _kf_cs(g_start, [moc[j] for j in dong_k] + [cuc_bo_end])
        w_hop = _do_rong_dong(dong_k, tokens) + 2 * KHUNG_DEM_NGANG
        x0_hop = giua_x - w_hop / 2
        y0_hop = cy - KHUNG_CAO_HOP / 2
        duong = _duong_ve_hop(w_hop, KHUNG_CAO_HOP, KHUNG_BAN_KINH)
        ket.append(_dialogue(bat_dau_canh, g_start, g_end, "KhungNen", layer=0)
                   + f"{{\\an7\\pos({x0_hop:.0f},{y0_hop:.0f})\\p1}}{duong}{{\\p0}}")
        x0_chu, y0_chu = x0_hop + KHUNG_DEM_NGANG, y0_hop + KHUNG_DEM_DOC_CHU
        chu = "".join(f"{{\\kf{kf[i]}}}{texts[idx]}" + (" " if i < len(dong_k) - 1 else "")
                      for i, idx in enumerate(dong_k))
        ket.append(_dialogue(bat_dau_canh, g_start, g_end, "Khung", layer=1)
                   + f"{{\\an7\\pos({x0_chu:.0f},{y0_chu:.0f})}}{chu}")
    return ket


def _dialogues_cau(bat_dau_canh: float, start: float, end: float, tu: list, cau_text: str,
                    gioi_han: int = GIOI_HAN_NGANG, style: str = "Itim", khung: bool = False,
                    rong: int = 1280, cao: int = 720, tach_menh_de: bool = False,
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
    if khung:
        ket: list = []
        for nhom in cac_phan:
            ket.extend(_dialogues_khung_tu_nhom(nhom, tokens, texts, moc, bat_dau_canh, rong, cao))
        return ket
    return [_dialogue_tu_nhom(nhom, tokens, texts, moc, bat_dau_canh, style) for nhom in cac_phan]


def tao_ass(cac_lich: list, rong: int = 1280, cao: int = 720, chu_de: str = "viet-tay", kho_ten: str = "ngang",
            canh_bao: list | None = None) -> str:
    """`chu_de` (`du["chuDe"]["ten"]`) và `kho_ten` (`ngang`/`doc`) chọn font, khung nền và giới hạn ký tự
    (`kieu_phu_de`); mặc định giữ đúng đường `viet-tay` khổ ngang cũ (Itim, không khung, 42 ký tự)."""
    kieu = kieu_phu_de(chu_de, kho_ten)
    if kieu["khung"]:
        style_name, style_lines = "Khung", [_style_khung_chu(kieu["font"]), _STYLE_KHUNG_NEN]
    else:
        style_name, style_lines = "Itim", [_STYLE_ITIM]
    tach_menh_de = kho_ten == "doc"
    dialogues: list = []
    for cl in cac_lich:
        for cau_text, start, end, tu in _nhom_cau(cl):
            dialogues.extend(_dialogues_cau(cl.bat_dau, start, end, tu, cau_text, gioi_han=kieu["gioi_han"],
                                            style=style_name, khung=kieu["khung"], rong=rong, cao=cao,
                                            tach_menh_de=tach_menh_de, canh_bao=canh_bao, so_canh=cl.so))
    return _header(rong, cao, style_lines) + "\n".join(dialogues) + ("\n" if dialogues else "")
