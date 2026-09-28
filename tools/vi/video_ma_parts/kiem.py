"""Kiểm giới hạn chữ và nội dung cảnh của video.md. Chỉ dùng thư viện chuẩn."""

from __future__ import annotations

import re
import unicodedata
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
    # Tiêu đề lớn của cảnh kể chuyện (chữ hoa, spec Q6): 36 ở khổ ngang, 28 ở khổ dọc (LIMITS_DOC).
    ("ke-chuyen", "tieu-de"): 36,
}
# Trường hai phần `<nhãn> | <…>`: giới hạn của nhãn và của mô tả (None: phần sau là số, parse đã kiểm).
LIMITS_HAI_PHAN = {("bieu-do", "du-lieu"): (16, None), ("dong-thoi-gian", "moc"): (12, 60)}
# Khổ dọc 9:16 (`kho: doc`, ô hẹp 624): giới hạn đo bằng Chromium, chuỗi thử "Nghiêng nghiễm nhiên " ở số dòng lặp
# tối đa, có và không có hình ở cột phụ (bảng đo ở docs/vi/phat-trien/2026-09-27-video-ma-vi12-kiem-thu.md). Không
# lớn hơn khổ ngang. Ba trường thấp hơn khổ ngang vì cột phụ khổ dọc là khối dưới nội dung (ô nội dung chỉ cao 300).
# Số của `du-lieu` có giới hạn riêng ở khổ dọc vì cột hẹp (khổ ngang chỉ có parse.SO_DAI).
LIMITS_DOC = {**LIMITS, ("khai-niem", "dinh-nghia"): 132, ("cong-thuc", "giai-thich"): 51, ("y-tung-y", "y"): 40,
              ("ke-chuyen", "tieu-de"): 28}
LIMITS_HAI_PHAN_DOC = {("bieu-do", "du-lieu"): (16, 8), ("dong-thoi-gian", "moc"): (12, 60)}
# Phong cách cắt dán (`phong-cach: cat-dan`, font Be Vietnam Pro rộng hơn Itim, nhãn tiêu đề chữ hoa ExtraBold): giới hạn
# đo bằng tools/vi/tests/do_gioi_han.py, cùng chuỗi thử và cách đo như khổ dọc (bảng đo ở file kiểm thử vi.12). Không
# lớn hơn bảng viet-tay cùng khổ; bảng viet-tay không bao giờ hạ vì font của cat-dan.
LIMITS_CAT_DAN = {**LIMITS, ("tieu-de", "chu"): 88, ("cong-thuc", "bieu-thuc"): 89, ("cong-thuc", "giai-thich"): 59,
                  ("y-tung-y", "y"): 54, ("anh", "chu-thich"): 89}
LIMITS_HAI_PHAN_CAT_DAN = dict(LIMITS_HAI_PHAN)
_DO_CAT_DAN_DOC = {**LIMITS_DOC, ("khai-niem", "dinh-nghia"): 127, ("cong-thuc", "giai-thich"): 45, ("y-tung-y", "y"): 34,
                   ("do-thi", "truc-doc"): 38, ("bieu-do", "don-vi"): 10, ("bieu-do", "truc-doc"): 36}
# Khổ dọc không bao giờ lớn hơn khổ ngang cùng phong cách: chặn bằng bảng cat-dan ngang (tieu-de chu 88, bieu-thuc 89,
# chu-thich 89 dù đo dọc cho 90).
LIMITS_CAT_DAN_DOC = {k: min(v, LIMITS_CAT_DAN[k]) for k, v in _DO_CAT_DAN_DOC.items()}
LIMITS_HAI_PHAN_CAT_DAN_DOC = {("bieu-do", "du-lieu"): (16, 7), ("dong-thoi-gian", "moc"): (10, 60)}
# Thẻ thông tin (`the`, spec Q5): nhãn, giá trị, chú thích tính trên chữ hiện; giống nhau ở mọi khổ và phong cách (ô thẻ
# đo bằng Chromium ở đúng giới hạn này, test_video_ma_the). Giá trị là một khối không ngắt (như công thức): không có
# cụm nhấn, chỉ số chạy `{{…}}`. Dòng tài liệu (`tai-lieu`) là chữ thường, không định dạng.
GIOI_HAN_THE = (("nhãn", 24, True), ("giá trị", 16, False), ("chú thích", 60, True))
TAI_LIEU_DAI = 90
# Cảnh có thẻ hay dòng tài liệu (`the`, `tai-lieu`): thẻ chiếm góc phải trên (khổ ngang) hay 160 điểm dưới tiêu đề
# (khổ dọc), dòng tài liệu chiếm góc phải dưới. Bố cục co lại theo (bước hàng theo chiều cao ô, chữ tiêu đề bìa nhỏ
# hơn); trường nào vẫn không vừa thì hạ ở đây. Đo bằng tools/vi/tests/do_gioi_han.py --co-the với thẻ ở giới hạn và dòng
# tài liệu 90 ký tự (bảng đo ở file kiểm thử vi.12). Áp dụng khi cảnh có `the`, `tai-lieu` hoặc cả hai.
HA_CO_THE = {
    ("ngang", "viet-tay"): {},
    ("ngang", "cat-dan"): {},
    ("doc", "viet-tay"): {("cong-thuc", "bieu-thuc"): 89},
    ("doc", "cat-dan"): {("cong-thuc", "bieu-thuc"): 85},
}
# Công thức (spec Q14): dòng chỉ xuống giữa hai phần ` | `, trước toán tử quan hệ (` = `, ` ≈ `…) hoặc, khi một đoạn
# rộng quá ô cả lúc đã thu chữ tới 70 %, ở khoảng trắng như vi.11; một đoạn liền (không khoảng trắng) không bao giờ bị
# ngắt. Đoạn liền dài nhất còn vẽ được, đo bằng Chromium (chuỗi "Nghiêngnghiễmnhiên" lặp, lấy nhỏ nhất của có/không cột
# phụ, có/không thẻ; bảng đo ở file kiểm thử vi.12).
DOAN_LIEN = {("ngang", "viet-tay"): 66, ("ngang", "cat-dan"): 55, ("doc", "viet-tay"): 34, ("doc", "cat-dan"): 28}
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


def bang_gioi_han(ten_kho: str, phong_cach: str = "viet-tay", co_the: bool = False) -> tuple:
    """(giới hạn trường đơn, giới hạn trường hai phần) theo khổ (`ngang`/`doc`) và phong cách (`viet-tay`/`cat-dan`);
    `co_the`: cảnh có thẻ hay dòng tài liệu (HA_CO_THE)."""
    doc = ten_kho == "doc"
    if phong_cach == "cat-dan":
        L, H = (LIMITS_CAT_DAN_DOC, LIMITS_HAI_PHAN_CAT_DAN_DOC) if doc else (LIMITS_CAT_DAN, LIMITS_HAI_PHAN_CAT_DAN)
    else:
        L, H = (LIMITS_DOC, LIMITS_HAI_PHAN_DOC) if doc else (LIMITS, LIMITS_HAI_PHAN)
    if co_the:
        L = {**L, **HA_CO_THE[(ten_kho, "cat-dan" if phong_cach == "cat-dan" else "viet-tay")]}
    return L, H


def co_the(scene: Scene) -> bool:
    return "the" in scene.truong or "tai-lieu" in scene.truong


def _ghi_chu_gioi_han(ten_kho: str, phong_cach: str, co_the_: bool = False) -> str:
    phan = ((["khổ dọc"] if ten_kho == "doc" else []) + (["phong cách cắt dán"] if phong_cach == "cat-dan" else [])
            + (["cảnh có thẻ hoặc dòng tài liệu"] if co_the_ else []))
    return f" (giới hạn {', '.join(phan)})" if phan else ""


def _kiem_do_dai(so: int, key: str, value: str, no: int, gioi_han: int, cum: bool, ghi_chu: str = "") -> None:
    kiem_danh_dau(key, value, no, cum)
    so_ky_tu = hien_thi(value, cum)
    if so_ky_tu > gioi_han:
        raise CanhError(so, f"`{key}` dài {so_ky_tu} ký tự, tối đa {gioi_han}{ghi_chu} (dòng {no}). Rút gọn nội dung.")


def _kiem_the(scene: Scene) -> None:
    if "the" in scene.truong:
        value, no = scene.truong["the"][0], scene.dong_truong["the"][0]
        for chu, (ten, gioi_han, cum) in zip(parse.tach_the(value), GIOI_HAN_THE):
            _kiem_do_dai(scene.so, f"the ({ten})", chu, no, gioi_han, cum)
    if "tai-lieu" in scene.truong:
        value, no = scene.truong["tai-lieu"][0], scene.dong_truong["tai-lieu"][0]
        if len(value) > TAI_LIEU_DAI:
            raise CanhError(scene.so, f"`tai-lieu` dài {len(value)} ký tự, tối đa {TAI_LIEU_DAI} (dòng {no}). Rút gọn dòng tài liệu.")


def _kiem_doan_lien(so: int, value: str, no: int, ten_kho: str, phong_cach: str) -> None:
    toi_da = DOAN_LIEN[(ten_kho, "cat-dan" if phong_cach == "cat-dan" else "viet-tay")]
    for doan in value.split():
        n = hien_thi(doan, cum=False)
        if n > toi_da:
            raise CanhError(so, f'phần công thức "{doan}" quá dài cho khổ này (dòng {no}: đoạn liền {n} ký tự, tối đa '
                                f"{toi_da}).", "Thêm khoảng trắng quanh dấu `=`, `+`… hoặc tách công thức thành nhiều phần "
                                               "bằng ` | `, rồi chạy lại.")


FIX_AI = ("Chạy `python tools/vi/anh_ai.py <thư_mục> ke-hoach`, vẽ từng ảnh theo kế hoạch, rồi chạy "
          "`python tools/vi/anh_ai.py <thư_mục> nhan`. Nền tảng không có công cụ vẽ thì đổi sang `nen: mau/...` "
          "và `nhan-vat: nguoi-que`.")
FIX_TACH_NEN = ("Chạy `python tools/vi/anh_ai.py <thư_mục> nhan` để tách nền xanh của ảnh nhân vật; vẫn lỗi thì vẽ lại "
                "tư thế đó trên nền xanh lá thuần #00FF00.")
FIX_NGUON_AI = ("Chạy `python tools/vi/anh_ai.py <thư_mục> nhan` để ghi nguồn ảnh AI vào `anh/ai/nguon.json`, rồi chạy lại.")
FIX_VE_LAI = "chạy lại `python tools/vi/anh_ai.py <thư_mục> ke-hoach`, vẽ lại mục đó, rồi `nhan`."
# Đuôi thay thế khi tìm file AI: nền cắt khổ là JPEG nhưng PNG vẫn nhận; nhân vật cần PNG trong suốt, JPEG thì vẫn tìm
# thấy để báo "chưa tách nền" thay vì "thiếu".
_DUOI_AI = {".jpg": (".jpg", ".png"), ".png": (".png", ".jpg")}


def file_ai(thu_muc: Path, ten: str):
    """File AI `ai/<tên>` có thật trong anh/ (thử đuôi thay thế); None khi không có."""
    goc, duoi = ten.rsplit(".", 1)
    for d in _DUOI_AI.get("." + duoi, ("." + duoi,)):
        if (Path(thu_muc) / "anh" / f"{goc}{d}").is_file():
            return f"{goc}{d}"
    return None


def can_ai(video: Video) -> list:
    """Mọi ảnh AI video cần, theo thứ tự cảnh, không lặp: [(số cảnh đầu tiên cần, `ai/<file>`)]. Nền `ve:` của cảnh
    ke-chuyen (`ai/nen-<số>.jpg`; `nhu-canh` dùng lại file của cảnh gốc) và, khi `nhan-vat: ve:`, mỗi tư thế nhân vật
    xuất hiện (`ai/tu-the-<tên>.png`)."""
    ds: list = []
    ve_nhan_vat = video.meta.get("nhan-vat", "").startswith("ve:")
    for scene in video.canh:
        if scene.nen is not None and scene.nen["kieu"] == "ai":
            ds.append((scene.so, scene.nen["file"]))
        tu_the = parse.tu_the_cua(scene, video.meta)
        if ve_nhan_vat and tu_the:
            ds.append((scene.so, f"ai/tu-the-{tu_the}.png"))
    da: set = set()
    return [(so, f) for so, f in ds if not (f in da or da.add(f))]


def _kiem_ai(video: Video, thu_muc: Path) -> None:
    thieu = [(so, f) for so, f in can_ai(video) if file_ai(thu_muc, f) is None]
    if thieu:
        raise CanhError(thieu[0][0], f"thiếu {len(thieu)} ảnh AI: " + ", ".join(f"`anh/{f}`" for _, f in thieu) + ".", FIX_AI)


def nen_goc(scene: Scene) -> dict:
    """Nền thật của cảnh ke-chuyen: `nhu-canh` giải về nền của cảnh gốc."""
    return scene.nen.get("goc", scene.nen) if scene.nen["kieu"] == "nhu" else scene.nen


def _cung_mo_ta(a: str, b: str) -> bool:
    return unicodedata.normalize("NFC", " ".join(a.split())) == unicodedata.normalize("NFC", " ".join(b.split()))


def _kiem_ve_cu(so: int, ten: str, info: dict, mo_ta: str, canh_ve, warnings: list, da_bao: set) -> str | None:
    """Ảnh AI `anh/<ten>` có vẽ đúng mô tả hiện tại (`mo_ta`) và, với nền, đúng cảnh `canh_ve` không (spec Q10: tên
    file theo số cảnh và tư thế nên ảnh cũ trùng tên). Trả lý do sai; bản ghi cũ không có mô tả thì cảnh báo một lần."""
    if info.get("moTa") is None:
        if ten not in da_bao:
            da_bao.add(ten)
            warnings.append(f"Cảnh {so}: `anh/{ten}` chưa ghi mô tả đã vẽ trong `anh/ai/nguon.json` (bản ghi cũ), không "
                            "kiểm được ảnh còn khớp video.md không; chạy lại `python tools/vi/anh_ai.py <thư_mục> nhan` "
                            "để ghi.")
        return None
    if not _cung_mo_ta(info["moTa"], mo_ta):
        return f"vẽ theo mô tả cũ \"{info['moTa']}\", không khớp mô tả hiện tại \"{mo_ta}\""
    if canh_ve is not None and info.get("canhVe") is not None and info["canhVe"] != canh_ve:
        return f"vẽ cho Cảnh {info['canhVe']}, không phải Cảnh {canh_ve} (cảnh đã đánh số lại?)"
    return None


def _kiem_nen_nhan_vat(scene: Scene, video: Video, thu_muc: Path, da_doc: dict, warnings: list, da_bao: set) -> None:
    def doc(ten: str, nguon_tay=None):
        if ten not in da_doc:
            da_doc[ten] = anh.doc(thu_muc, ten, nguon_tay)
        return da_doc[ten]

    if scene.nen is not None:
        nen, no = nen_goc(scene), scene.dong_truong["nen"][0]
        ten = nen["file"] if nen["kieu"] == "file" else (file_ai(thu_muc, nen["file"]) if nen["kieu"] == "ai" else None)
        if ten:
            try:
                info = doc(ten)
            except anh.AnhError as exc:
                raise CanhError(scene.so, f"nền: {exc} (dòng {no}).") from exc
            if nen["kieu"] == "ai":
                # Cảnh gốc của nền: chính cảnh này, hoặc cảnh mà `nhu-canh` trỏ về.
                goc = scene.nen["canh"] if scene.nen["kieu"] == "nhu" else scene.so
                sai = _kiem_ve_cu(scene.so, ten, info, nen["mo_ta"], goc, warnings, da_bao)
                if sai:
                    raise CanhError(scene.so, f"nền `anh/{ten}` {sai} (dòng {no}).", FIX_VE_LAI)
    tu_the = parse.tu_the_cua(scene, video.meta)
    if tu_the and video.meta.get("nhan-vat", "").startswith("ve:"):
        ten = file_ai(thu_muc, f"ai/tu-the-{tu_the}.png")
        try:
            info = doc(ten)
        except anh.NguonAiError as exc:
            raise CanhError(scene.so, f"nhân vật: {exc}.", FIX_NGUON_AI) from exc
        except anh.AnhError as exc:
            raise CanhError(scene.so, f"nhân vật: {exc}.", FIX_TACH_NEN) from exc
        if not info["alpha"]:
            raise CanhError(scene.so, f"ảnh nhân vật `anh/{ten}` chưa tách nền (không có phần trong suốt).", FIX_TACH_NEN)
        mo_ta_nv = video.meta["nhan-vat"][len("ve:"):].strip()
        sai = _kiem_ve_cu(scene.so, ten, info, mo_ta_nv, None, warnings, da_bao)
        if sai:
            raise CanhError(scene.so, f"tư thế `{tu_the}` (`anh/{ten}`) {sai} (khoá đầu `nhan-vat`, dòng "
                                      f"{video.dong_meta.get('nhan-vat', '?')}).", FIX_VE_LAI)


def doc_nhac(video: Video, thu_muc: Path):
    """Nhạc nền của video (`nhac.doc`), None khi không có `nhac-nen`. Lỗi là CanhError số cảnh 0, nêu dòng khoá đầu."""
    ten = video.meta.get("nhac-nen")
    if not ten:
        return None
    try:
        return nhac.doc(thu_muc, ten, video.meta.get("nguon-nhac"))
    except nhac.NhacError as exc:
        raise CanhError(0, f"nhạc nền: {exc} (dòng {video.dong_meta.get('nhac-nen', '?')}).") from exc


KE_CHUYEN_LIEN_TOI_DA = 2
TU_THE_LIEN_TOI_DA = 2


def _nen_la_mau(scene: Scene, video: Video) -> bool:
    """Nền `ke-chuyen` là nền mẫu chung chung (kể cả `nhu-canh` trỏ về một nền mẫu)."""
    nen = scene.nen if scene.nen is not None else parse.giai_nen(scene.truong["nen"][0], scene.so, video.canh)
    if nen["kieu"] == "nhu":
        nen = nen["goc"]
    return nen["kieu"] == "mau"


def canh_bao_hinh_khop_loi(video: Video) -> list:
    """Cảnh báo (không chặn) những chỗ hình dễ không nói gì về lời đọc: cảnh kể chuyện trên nền mẫu mà không có
    thẻ nêu ý của lời, quá nhiều cảnh kể chuyện liền nhau, nhân vật đứng một tư thế qua nhiều cảnh liền."""
    ket: list = []
    lien, tu_the_truoc, lien_tu_the = 0, None, 0
    for scene in video.canh:
        if scene.loai == "ke-chuyen":
            lien += 1
            if "the" not in scene.truong and _nen_la_mau(scene, video):
                ket.append(f"Cảnh {scene.so}: cảnh kể chuyện dùng nền mẫu mà không có `the`; nền mẫu không nói được "
                           "nội dung lời. Thêm `the` nêu ý chính hoặc con số của lời, hoặc đổi sang cảnh có chữ và hình.")
            if lien == KE_CHUYEN_LIEN_TOI_DA + 1:
                ket.append(f"Cảnh {scene.so}: {lien} cảnh kể chuyện liền nhau; xen một cảnh có chữ và hình "
                           "(`khai-niem`, `y-tung-y`, `minh-hoa`…) để hình mang nội dung bài.")
        else:
            lien = 0
        tu_the = parse.tu_the_cua(scene, video.meta)
        lien_tu_the = lien_tu_the + 1 if tu_the is not None and tu_the == tu_the_truoc else 1
        if tu_the is not None and lien_tu_the == TU_THE_LIEN_TOI_DA + 1:
            ket.append(f"Cảnh {scene.so}: nhân vật giữ tư thế `{tu_the}` {lien_tu_the} cảnh liền; chọn tư thế "
                       "khớp cảm xúc của lời từng cảnh.")
        tu_the_truoc = tu_the
    return ket


def kiem(video: Video, thu_muc: Path, doc_nhac_nen: bool = True) -> list:
    """`doc_nhac_nen=False`: người gọi đã đọc nhạc nền (`doc_nhac`) rồi, không đo lại bằng ffprobe."""
    warnings: list = []
    if doc_nhac_nen:
        doc_nhac(video, thu_muc)
    _kiem_ai(video, thu_muc)
    da_doc: dict = {}
    da_bao: set = set()
    ten_kho, phong_cach = video.meta.get("kho", "ngang"), video.meta.get("phong-cach", "viet-tay")
    for scene in video.canh:
        bang, bang_hai_phan = bang_gioi_han(ten_kho, phong_cach, co_the(scene))
        ghi_chu = _ghi_chu_gioi_han(ten_kho, phong_cach, co_the(scene))
        _kiem_the(scene)
        for key, values in scene.truong.items():
            hai_phan = bang_hai_phan.get((scene.loai, key))
            if hai_phan is not None:
                tach = parse.tach_du_lieu if key == "du-lieu" else parse.tach_moc
                for value, no in zip(values, scene.dong_truong[key]):
                    for chu, gioi_han in zip(tach(value), hai_phan):
                        if gioi_han is not None:
                            _kiem_do_dai(scene.so, key, chu, no, gioi_han, True, ghi_chu)
                continue
            gioi_han = bang.get((scene.loai, key))
            if gioi_han is None:
                continue
            for value, no in zip(values, scene.dong_truong[key]):
                cum = (scene.loai, key) not in KHONG_CUM
                if (scene.loai, key) == ("cong-thuc", "bieu-thuc"):
                    value = value.replace(parse.PHAN_CONG_THUC, " ")
                _kiem_do_dai(scene.so, key, value, no, gioi_han, cum, ghi_chu)
                if (scene.loai, key) == ("cong-thuc", "bieu-thuc"):
                    _kiem_doan_lien(scene.so, value, no, ten_kho, phong_cach)
        if len(scene.loi) > LOI_DAI:
            warnings.append(f"Cảnh {scene.so}: lời dài {len(scene.loi)} ký tự (quá {LOI_DAI}); nên tách thành hai cảnh.")
        loi_giai = scene.truong.get("loi-giai", [""])[0]
        if len(loi_giai) > LOI_DAI:
            warnings.append(f"Cảnh {scene.so}: lời giải dài {len(loi_giai)} ký tự (quá {LOI_DAI}); nên rút gọn.")
        if scene.loai == "thi-nghiem":
            _kiem_thi_nghiem(scene, thu_muc)
        _kiem_hinh_anh(scene, thu_muc)
        _kiem_nen_nhan_vat(scene, video, thu_muc, da_doc, warnings, da_bao)
    return warnings
