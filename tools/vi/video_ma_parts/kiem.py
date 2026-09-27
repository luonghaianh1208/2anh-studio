"""Kiểm giới hạn chữ và nội dung cảnh của video.md. Chỉ dùng thư viện chuẩn."""

from __future__ import annotations

import re
from pathlib import Path

from thi_nghiem_parts import thu_vien

from . import anh, hinh, nhac, parse
from .parse import ParseError, Scene, Video

LIMITS = {
    ("tieu-de", "chu"): 90, ("tieu-de", "phu"): 90,
    ("khai-niem", "thuat-ngu"): 60, ("khai-niem", "dinh-nghia"): 220,
    ("cong-thuc", "bieu-thuc"): 90, ("cong-thuc", "giai-thich"): 60,
    ("y-tung-y", "tieu-de"): 90, ("y-tung-y", "y"): 60,
    ("quy-trinh", "tieu-de"): 90, ("quy-trinh", "buoc"): 50,
    ("so-sanh", "tieu-de"): 90, ("so-sanh", "trai"): 24, ("so-sanh", "phai"): 24,
    ("so-sanh", "y-trai"): 60, ("so-sanh", "y-phai"): 60,
    ("do-thi", "tieu-de"): 90, ("do-thi", "truc-ngang"): 40, ("do-thi", "truc-doc"): 40,
    ("minh-hoa", "tieu-de"): 90, ("anh", "chu-thich"): 90,
    ("bieu-do", "tieu-de"): 90, ("bieu-do", "don-vi"): 12, ("bieu-do", "truc-ngang"): 40, ("bieu-do", "truc-doc"): 40,
    ("so-do", "trung-tam"): 30, ("so-do", "nhanh"): 40,
    ("dong-thoi-gian", "tieu-de"): 90,
    ("cau-hoi", "cau-hoi"): 160, ("cau-hoi", "lua-chon"): 60, ("cau-hoi", "giai-thich"): 180,
}
# Trường hai phần `<nhãn> | <…>`: giới hạn của nhãn và của mô tả (None: phần sau là số, parse đã kiểm).
LIMITS_HAI_PHAN = {("bieu-do", "du-lieu"): (16, None), ("dong-thoi-gian", "moc"): (12, 60)}
# Khổ dọc 9:16 (`kho: doc`, ô hẹp 624): giới hạn đo bằng Chromium, chuỗi thử "Nghiêng nghiễm nhiên " ở số dòng lặp
# tối đa, có và không có hình ở cột phụ (bảng đo ở docs/vi/phat-trien/2026-09-27-video-ma-vi12-kiem-thu.md). Không
# lớn hơn khổ ngang. Ba trường thấp hơn khổ ngang vì cột phụ khổ dọc là khối dưới nội dung (ô nội dung chỉ cao 300).
# Số của `du-lieu` có giới hạn riêng ở khổ dọc vì cột hẹp (khổ ngang chỉ có parse.SO_DAI).
LIMITS_DOC = {**LIMITS, ("khai-niem", "dinh-nghia"): 132, ("cong-thuc", "giai-thich"): 51, ("y-tung-y", "y"): 40}
LIMITS_HAI_PHAN_DOC = {("bieu-do", "du-lieu"): (16, 8), ("dong-thoi-gian", "moc"): (12, 60)}
LOI_DAI = 700
MAX_THAM_SO = 3
MAX_DO = 3
_MARKUP_RE = re.compile(r"\*\*|~|\^")
# Cùng ngữ pháp với catDanhDau trong runtime/khung-video.js. `____` (ô trống, 3+ gạch) và ` == ` có khoảng trắng
# hai bên là chữ thường, không mở cụm.
_CUM_RE = re.compile(r"(?<!=)==(?![=\s])(.+?)(?<![=\s])==(?!=)|\(\((.+?)\)\)|(?<!_)__(?![_\s])(.+?)(?<![_\s])__(?!_)")
_DAU_RE = re.compile(r"(?<!=)==(?!=)|(?<!_)__(?!_)|\(\(")
_SO_RE = re.compile(r"\{\{(.*?)\}\}")
_SO_DUNG = re.compile(r"-?\d+(?:\.\d+)?")
# Trường công thức: `((`, `__` là toán, không phải cụm nhấn.
KHONG_CUM = {("cong-thuc", "bieu-thuc")}
MAX_CUM = 3


class CanhError(Exception):
    """Nội dung cảnh sai; luôn nêu số cảnh (0 là khối thông tin đầu, ví dụ nhạc nền). `fix`: cách sửa riêng, nếu có."""

    def __init__(self, so: int, message: str, fix: str | None = None) -> None:
        super().__init__(f"Cảnh {so}: {message}")
        self.so = so
        self.message = message
        self.fix = fix


def _trong_cum(m: re.Match) -> str:
    return next(g for g in m.groups() if g is not None)


def hien_thi(chu: str, cum: bool = True) -> int:
    if cum:
        chu = _CUM_RE.sub(_trong_cum, chu)
    chu = _SO_RE.sub(lambda m: m.group(1).replace(".", ","), chu)
    return len(_MARKUP_RE.sub("", chu))


def _dau_mo(chu: str) -> str | None:
    """Dấu mở cụm còn trong chữ (bỏ qua `==`/`__` có khoảng trắng hai bên)."""
    for m in _DAU_RE.finditer(chu):
        truoc = m.start() == 0 or chu[m.start() - 1].isspace()
        sau = m.end() == len(chu) or chu[m.end()].isspace()
        if m.group(0) == "((" or not (truoc and sau):
            return m.group(0)
    return None


def _dem_dinh_dang(chu: str) -> tuple:
    return (chu.count("**"), chu.replace("**", "").count("~"), chu.replace("**", "").count("^"))


def kiem_danh_dau(key: str, value: str, no: int, cum: bool = True) -> None:
    """Cụm nhấn `==`, `((…))`, `__` và số chạy `{{…}}`: không lồng, không cắt ngang `**`/`~`/`^`, có đóng,
    ngoặc trong cụm cân, tối đa 3 cụm, số dùng dấu chấm. `cum=False` (công thức) chỉ kiểm số."""
    if cum:
        _kiem_cum(key, value, no)
    for m in _SO_RE.finditer(value):
        if _SO_DUNG.fullmatch(m.group(1)) is None:
            raise ParseError(no, f"`{key}`: `{m.group(0)}` phải là một số, dấu thập phân là dấu chấm (ví dụ `{{{{1500.5}}}}`).")
    con_lai = _SO_RE.sub("", value)
    if "{{" in con_lai or "}}" in con_lai:
        raise ParseError(no, f"`{key}` có `{{{{` hoặc `}}}}` chưa thành cặp; số chạy viết dạng `{{{{12}}}}`.")


def _kiem_cum(key: str, value: str, no: int) -> None:
    cac_cum = list(_CUM_RE.finditer(value))
    for m in cac_cum:
        trong = _trong_cum(m)
        if _CUM_RE.search(trong) or _dau_mo(trong):
            raise ParseError(no, f"`{key}` có cụm nhấn lồng trong cụm khác (`{m.group(0)}`). Mỗi cụm nhấn đứng riêng.")
        if trong.count("(") != trong.count(")"):
            raise ParseError(no, f"`{key}`: ngoặc trong cụm `{m.group(0)}` không cân. Công thức có ngoặc thì bỏ "
                                 "khoanh `((…))`, dùng `==…==` hoặc viết ngoặc đủ cặp bên trong.")
    dau = _dau_mo(_CUM_RE.sub("", value))
    if dau:
        dong = "))" if dau == "((" else dau
        raise ParseError(no, f"`{key}` có `{dau}` chưa đóng bằng `{dong}`.")
    if len(cac_cum) > MAX_CUM:
        raise ParseError(no, f"`{key}` có {len(cac_cum)} cụm nhấn, tối đa {MAX_CUM} cụm mỗi dòng.")
    # `**`, `~`, `^` phải mở và đóng cùng phía của cụm (trong cụm hoặc ngoài cụm), không cắt ngang ranh giới.
    tong = _dem_dinh_dang(value)
    cac_manh = [_trong_cum(m) for m in cac_cum] + _CUM_RE.split(value)[::4]
    for i, loai in enumerate(("**", "~", "^")):
        if tong[i] % 2 == 0 and any(_dem_dinh_dang(manh or "")[i] % 2 for manh in cac_manh):
            raise ParseError(no, f"`{key}`: `{loai}` cắt ngang ranh giới cụm nhấn. Đặt `{loai}…{loai}` trọn trong "
                                 "cụm hoặc trọn ngoài cụm.")


def tham_so_theo_thoi_gian(scene: Scene) -> dict:
    out: dict = {}
    for value in scene.truong.get("tham-so", []):
        giay, ma, gia_tri = value.split()
        out.setdefault(ma, []).append((float(giay), float(gia_tri)))
    for ma in out:
        out[ma].sort(key=lambda mot: mot[0])
    return out


def ma_do(scene: Scene, model) -> list:
    if "do" in scene.truong:
        return [ma.strip() for ma in scene.truong["do"][0].split(",") if ma.strip()]
    return [dl["ma"] for dl in model.khai_bao["daiLuongDo"][:2]]


def _kiem_thi_nghiem(scene: Scene, thu_muc: Path) -> None:
    mau = scene.truong["mau"][0]
    if mau == thu_vien.NEW_MODEL:
        raise CanhError(scene.so, "Video chỉ dùng mẫu có sẵn trong thư viện thí nghiệm, không dùng `moi`. Mẫu có: "
                        + ", ".join(thu_vien.list_models()) + ".")
    if mau not in thu_vien.list_models():
        raise CanhError(scene.so, f"không có mẫu `{mau}` trong thư viện thí nghiệm. Mẫu có: "
                        + ", ".join(thu_vien.list_models()) + ".")
    try:
        model = thu_vien.load(mau, thu_muc)
    except thu_vien.ModelError as exc:
        raise CanhError(scene.so, str(exc)) from exc
    lich = tham_so_theo_thoi_gian(scene)
    dong_theo_ma: dict = {}
    for value, no in zip(scene.truong.get("tham-so", []), scene.dong_truong.get("tham-so", [])):
        dong_theo_ma.setdefault(value.split()[1], []).append((no, float(value.split()[2])))
    for ma, cac_dong in dong_theo_ma.items():
        ts = model.tham_so(ma)
        if ts is None:
            co = ", ".join(t["ma"] for t in model.khai_bao["thamSo"])
            raise CanhError(scene.so, f"tham số `{ma}` không có trong mẫu `{mau}` (dòng {cac_dong[0][0]}). Có: {co}.")
        if ts.get("kieu") != "so":
            raise CanhError(scene.so, f"tham số `{ma}` không phải số nên chưa dùng được trong video.")
        for no, gia_tri in cac_dong:
            if not ts["min"] <= gia_tri <= ts["max"]:
                raise ParseError(no, f"`{ma}` = {gia_tri:g} ngoài khoảng cho phép {ts['min']:g}–{ts['max']:g}.")
    if len(lich) > MAX_THAM_SO:
        raise CanhError(scene.so, f"chỉ đổi tối đa {MAX_THAM_SO} tham số khác nhau trong một cảnh (đang có {len(lich)}).")
    codes = ma_do(scene, model)
    if len(codes) > MAX_DO:
        raise CanhError(scene.so, f"`do` chỉ liệt kê tối đa {MAX_DO} đại lượng (đang có {len(codes)}).")
    for ma in codes:
        if model.dai_luong(ma) is None:
            co = ", ".join(dl["ma"] for dl in model.khai_bao["daiLuongDo"])
            raise CanhError(scene.so, f"đại lượng đo `{ma}` không có trong mẫu `{mau}`. Có: {co}.")


def _kiem_hinh_anh(scene: Scene, thu_muc: Path) -> None:
    if scene.loai == "minh-hoa":
        for value, no in zip(scene.truong["hinh"], scene.dong_truong["hinh"]):
            try:
                ten, _nhan = hinh.tach_minh_hoa(value)
                hinh.doc(ten)
            except hinh.HinhError as exc:
                raise CanhError(scene.so, f"{exc} (dòng {no}).") from exc
        return
    if "hinh" in scene.truong:
        value, no = scene.truong["hinh"][0], scene.dong_truong["hinh"][0]
        try:
            hinh.doc(value)
        except hinh.HinhError as exc:
            raise CanhError(scene.so, f"{exc} (dòng {no}).") from exc
    if "anh" in scene.truong:
        value, no = scene.truong["anh"][0], scene.dong_truong["anh"][0]
        nguon_tay = scene.truong.get("nguon", [None])[0]
        try:
            anh.doc(thu_muc, value, nguon_tay)
        except anh.AnhError as exc:
            raise CanhError(scene.so, f"{exc} (dòng {no}).") from exc


def _kiem_do_dai(so: int, key: str, value: str, no: int, gioi_han: int, cum: bool, doc: bool = False) -> None:
    kiem_danh_dau(key, value, no, cum)
    so_ky_tu = hien_thi(value, cum)
    if so_ky_tu > gioi_han:
        loai = " (giới hạn khổ dọc)" if doc else ""
        raise CanhError(so, f"`{key}` dài {so_ky_tu} ký tự, tối đa {gioi_han}{loai} (dòng {no}). Rút gọn nội dung.")


def doc_nhac(video: Video, thu_muc: Path):
    """Nhạc nền của video (`nhac.doc`), None khi không có `nhac-nen`. Lỗi là CanhError số cảnh 0, nêu dòng khoá đầu."""
    ten = video.meta.get("nhac-nen")
    if not ten:
        return None
    try:
        return nhac.doc(thu_muc, ten, video.meta.get("nguon-nhac"))
    except nhac.NhacError as exc:
        raise CanhError(0, f"nhạc nền: {exc} (dòng {video.dong_meta.get('nhac-nen', '?')}).") from exc


def kiem(video: Video, thu_muc: Path, doc_nhac_nen: bool = True) -> list:
    """`doc_nhac_nen=False`: người gọi đã đọc nhạc nền (`doc_nhac`) rồi, không đo lại bằng ffprobe."""
    warnings: list = []
    if doc_nhac_nen:
        doc_nhac(video, thu_muc)
    doc = video.meta.get("kho") == "doc"
    bang, bang_hai_phan = (LIMITS_DOC, LIMITS_HAI_PHAN_DOC) if doc else (LIMITS, LIMITS_HAI_PHAN)
    for scene in video.canh:
        for key, values in scene.truong.items():
            hai_phan = bang_hai_phan.get((scene.loai, key))
            if hai_phan is not None:
                tach = parse.tach_du_lieu if key == "du-lieu" else parse.tach_moc
                for value, no in zip(values, scene.dong_truong[key]):
                    for chu, gioi_han in zip(tach(value), hai_phan):
                        if gioi_han is not None:
                            _kiem_do_dai(scene.so, key, chu, no, gioi_han, True, doc)
                continue
            gioi_han = bang.get((scene.loai, key))
            if gioi_han is None:
                continue
            for value, no in zip(values, scene.dong_truong[key]):
                cum = (scene.loai, key) not in KHONG_CUM
                if (scene.loai, key) == ("cong-thuc", "bieu-thuc"):
                    value = value.replace(parse.PHAN_CONG_THUC, " ")
                _kiem_do_dai(scene.so, key, value, no, gioi_han, cum, doc)
        if len(scene.loi) > LOI_DAI:
            warnings.append(f"Cảnh {scene.so}: lời dài {len(scene.loi)} ký tự (quá {LOI_DAI}); nên tách thành hai cảnh.")
        loi_giai = scene.truong.get("loi-giai", [""])[0]
        if len(loi_giai) > LOI_DAI:
            warnings.append(f"Cảnh {scene.so}: lời giải dài {len(loi_giai)} ký tự (quá {LOI_DAI}); nên rút gọn.")
        if scene.loai == "thi-nghiem":
            _kiem_thi_nghiem(scene, thu_muc)
        _kiem_hinh_anh(scene, thu_muc)
    return warnings
