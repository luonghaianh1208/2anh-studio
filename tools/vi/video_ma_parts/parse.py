"""Đọc video.md thành dữ liệu; lỗi luôn kèm số dòng. Ngữ pháp ở docs/vi/tro-ly/nhip-vox.md (Vox) và docs/vi/tham-khao/ (kiểu cũ). Chỉ dùng thư viện chuẩn."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

from . import vox
from .vox import VOX_META_CHOICES

META_REQUIRED = ("tieu-de", "mon", "lop")
META_CHOICES = {
    # Phong cách: viết tay trên bảng, cắt dán giấy kiểu Vox (runtime/cat-dan.css, cat-dan.js), hoặc Vox (nhịp).
    "phong-cach": ("viet-tay", "cat-dan", "vox"),
    "giong": ("nu", "nam"),
    "toc-do": ("cham", "vua", "nhanh"),
    "phu-de": ("hinh", "file", "khong", "karaoke"),
    "ban-tay": ("co", "khong"),
    "may-quay": ("co", "khong"),
    "chuyen-canh": ("lau-bang", "lat-trang", "truot", "phong", "mo-man", "luan-phien", "khong", "xe-giay"),
    "chu-dong": ("co", "khong"),
    "am-thanh": ("co", "khong"),
    # Khổ khung (kho.py): ngang 16:9 hoặc dọc 9:16; độ phân giải xuất 1080 (Full HD) hoặc 720 cho máy yếu.
    "kho": ("ngang", "doc"),
    "do-phan-giai": ("1080", "720"),
    # Màu áo của người que (`nhan-vat: nguoi-que`); bảng mã màu ở runtime/nhan-vat.js.
    "mau-ao": ("vang", "do", "xanh-duong", "xanh-la", "cam", "tim", "hong", "xam"),
}
# Khoá đầu tự do (không có mặc định): nhạc nền là tên file trong nhac/; nguồn nhạc là chữ (chỉ dùng kèm `nhac-nen`);
# `loat` là tên loạt video (≤ 30 ký tự), có thì hiện tên loạt và "0k/N" ở hai góc trên.
# `nhan-vat`: `khong` (mặc định), `nguoi-que` hoặc `ve: <mô tả ≤ 200>` (nhân vật AI vẽ); kiểm ở _kiem_nhan_vat.
META_FREE = ("nhac-nen", "nguon-nhac", "loat", "nhan-vat", "thoi-luong")
# `ban-tay` và `chuyen-canh` không có mặt ở đây: mặc định của hai khoá này đổi theo `phong-cach` (lich.mac_dinh),
# nên kịch bản không ghi thì để trống trong `meta` thay vì điền cứng "co"/"lau-bang".
META_DEFAULTS = {
    "phong-cach": "viet-tay", "giong": "nu", "toc-do": "vua", "phu-de": "karaoke",
    "may-quay": "co",
    "chu-dong": "co", "am-thanh": "co", "kho": "ngang", "do-phan-giai": "1080",
    "nhan-vat": "khong", "mau-ao": "vang",
}

# loại cảnh -> (trường đơn bắt buộc, trường đơn tuỳ chọn, trường lặp {khoá: (tối thiểu, tối đa)})
SCENE_SPEC = {
    "tieu-de": (("chu",), ("phu", "hinh", "anh", "nguon", "the", "tai-lieu", "tu-the"), {}),
    "khai-niem": (("thuat-ngu", "dinh-nghia"), ("hinh", "anh", "nguon", "the", "tai-lieu", "tu-the"), {}),
    "cong-thuc": (("bieu-thuc",), ("hinh", "anh", "nguon", "the", "tai-lieu"), {"giai-thich": (0, 4)}),
    "y-tung-y": (("tieu-de",), ("hinh", "anh", "nguon", "the", "tai-lieu", "tu-the"), {"y": (1, 6)}),
    "quy-trinh": (("tieu-de",), (), {"buoc": (2, 5)}),
    "so-sanh": (("tieu-de", "trai", "phai"), (), {"y-trai": (1, 4), "y-phai": (1, 4)}),
    "do-thi": (("tieu-de", "truc-ngang", "truc-doc"), (), {"diem": (2, 12)}),
    "thi-nghiem": (("mau",), ("do",), {"tham-so": (0, 99)}),
    "minh-hoa": (("tieu-de",), (), {"hinh": (1, 3)}),
    "anh": (("anh", "chu-thich"), ("nguon",), {}),
    "bieu-do": (("tieu-de", "kieu"), ("don-vi", "truc-ngang", "truc-doc"), {"du-lieu": (2, 8)}),
    "so-do": (("trung-tam",), ("hinh",), {"nhanh": (2, 6)}),
    "dong-thoi-gian": (("tieu-de",), (), {"moc": (2, 6)}),
    "cau-hoi": (("cau-hoi", "dap-an", "giai-thich", "loi-giai"), ("cho",), {"lua-chon": (2, 4)}),
    # Cảnh kể chuyện (spec Q6): nền phủ kín khung (`nen`, giải bằng giai_nen), nhân vật, tiêu đề lớn; lời chỉ ở phụ đề.
    # Luôn ở cuối: thứ tự 8 loại đầu được test giữ.
    "ke-chuyen": (("tieu-de", "nen"), ("tu-the", "vi-tri", "the", "tai-lieu"), {}),
}
BIEU_DO_KIEU = ("cot", "duong", "tron")
# Cảnh câu hỏi: lựa chọn tự đánh A–D; `cho` là số giây đếm ngược (số nguyên).
CHU_LUA_CHON = "ABCD"
CHO_MAC_DINH = 5
CHO_TOI_THIEU, CHO_TOI_DA = 3, 10
SO_DAI = 10
# Tên loạt (`loat`) tối đa 30 ký tự; thẻ thông tin `the: <nhãn> | <giá trị> | <chú thích>` (chú thích bỏ trống được).
LOAT_DAI = 30
# `bieu-thuc` của `cong-thuc` tách phần bằng ` | ` (dấu gạch đứng có khoảng trắng hai bên); tối đa 4 phần.
PHAN_CONG_THUC = " | "
MAX_PHAN = 4
SCENE_TYPES = tuple(SCENE_SPEC)
# Trường `chuyen:` (mọi loại cảnh, từ cảnh 2) ghi đè khoá đầu `chuyen-canh` cho riêng cảnh đó.
SCENE_KIEU_CHUYEN = ("lau-bang", "lat-trang", "truot", "phong", "mo-man", "xe-giay", "khong")

# Mười tư thế của nhân vật dẫn chuyện (trường `tu-the`, runtime/nhan-vat.js). Loại cảnh nhận `tu-the` là loại có nó
# trong phần tuỳ chọn của SCENE_SPEC; nhân vật chiếm cột phụ nên `tu-the` không đi cùng `hinh`/`anh`.
TU_THE = ("dung", "chao", "chi-tay", "giai-thich", "suy-nghi", "ngac-nhien", "vo-dau", "dung-lai", "an-mung", "buon")
# Tên tiếng Anh hay gặp, chỉ để gợi ý tên đúng khi viết sai.
_TU_THE_ANH = {
    "dung": ("stand", "idle"), "chao": ("wave", "hello", "hi"), "chi-tay": ("point", "pointing"),
    "giai-thich": ("explain", "present"), "suy-nghi": ("think", "thinking"), "ngac-nhien": ("surprised", "surprise", "wow"),
    "vo-dau": ("confused", "stressed", "panic"), "dung-lai": ("stop", "halt"), "an-mung": ("celebrate", "cheer", "happy"),
    "buon": ("sad",),
}
NHAN_VAT_MO_TA = 200
_NHAN_VAT_VE_RE = re.compile(r"^ve:\s*(.*)$")
# Cảnh ke-chuyen: vị trí nhân vật (mặc định cảnh lẻ `trai`, cảnh chẵn `phai`, lich.py); tư thế khi không ghi `tu-the`.
VI_TRI = ("trai", "giua", "phai")
TU_THE_KE_CHUYEN = "dung"
# Tám nền mẫu (`nen: mau/<tên>`), cùng thứ tự với TEN của runtime/nen-mau.js. Nền AI vẽ (`nen: ve: <mô tả>`) nằm ở
# `anh/ai/nen-<số cảnh>.jpg` (anh_ai.py ghi); mô tả tối đa 200 ký tự như nhân vật.
NEN_MAU = ("giay", "bau-troi", "vu-tru", "lop-hoc", "phong-thi-nghiem", "thanh-pho", "dong-que", "vong-tron")
NEN_MO_TA = 200
_NHU_CANH_RE = re.compile(r"^nhu-canh\b\s*(.*)$")
_DUOI_ANH = (".jpg", ".jpeg", ".png", ".webp")
_SAI_NEN = ("`nen` phải là `mau/<tên nền mẫu>`, tên file ảnh trong `anh/` (ví dụ `ruong.jpg`), `ve: <mô tả nền>` "
            "hoặc `nhu-canh <số cảnh>`.")

_KEY_RE = re.compile(r"^([a-z][a-z0-9-]*):\s*(.*)$")
_SCENE_RE = re.compile(r"^##\s+Cảnh\s+(\d+)\s*$")
_URL_RE = re.compile(r"https?://|www\.", re.IGNORECASE)
_POINT_RE = re.compile(r"^-?\d+(?:\.\d+)?\s*,\s*-?\d+(?:\.\d+)?$")
_PARAM_RE = re.compile(r"^\d+(?:\.\d+)?\s+[a-z0-9-]+\s+-?\d+(?:\.\d+)?$")
_DATA_RE = re.compile(r"^(.*?\S)\s*\|\s*(-?\d+(?:\.\d+)?)$")
_MOC_RE = re.compile(r"^(.*?\S)\s*\|\s*(\S.*)$")
_THE_RE = re.compile(r"(?:^|\s)\|(?:\s|$)")


def tach_du_lieu(value: str) -> tuple:
    """`<nhãn> | <số>` -> (nhãn, chuỗi số); None nếu sai dạng. Tách ở dấu `|` cuối cùng."""
    match = _DATA_RE.match(value)
    return (match.group(1), match.group(2)) if match else None


def tach_moc(value: str) -> tuple:
    """`<nhãn> | <mô tả>` -> (nhãn, mô tả); None nếu sai dạng. Tách ở dấu `|` đầu tiên."""
    match = _MOC_RE.match(value)
    return (match.group(1), match.group(2).strip()) if match else None


def tach_the(value: str):
    """`<nhãn> | <giá trị> | <chú thích>` -> (nhãn, giá trị, chú thích); chú thích bỏ trống được (hai phần, hoặc phần
    ba trống). Tách ở ` | ` (gạch đứng có khoảng trắng hai bên, hay ở đầu/cuối dòng), nên `|x|` là chữ thường.
    None nếu sai dạng: thiếu nhãn hay giá trị, hoặc hơn ba phần."""
    phan = [p.strip() for p in _THE_RE.split(value)]
    if len(phan) not in (2, 3) or not phan[0] or not phan[1]:
        return None
    return (phan[0], phan[1], phan[2] if len(phan) == 3 else "")


def _bo_dau(chu: str) -> str:
    """Chữ thường, bỏ dấu thanh và dấu mũ, đ -> d, bỏ gạch nối và khoảng trắng: `Chí tay` -> `chitay`."""
    chu = unicodedata.normalize("NFD", chu.lower().replace("đ", "d"))
    return "".join(c for c in chu if not unicodedata.combining(c) and c not in "- _")


def _khoang_cach(a: str, b: str) -> int:
    truoc = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        hang = [i]
        for j, cb in enumerate(b, 1):
            hang.append(min(truoc[j] + 1, hang[j - 1] + 1, truoc[j - 1] + (ca != cb)))
        truoc = hang
    return truoc[-1]


def goi_y_tu_the(sai: str) -> list:
    """Tối đa 3 tên tư thế gần `sai` nhất theo khoảng cách chỉnh sửa trên chữ bỏ dấu, bỏ gạch (tính cả tên tiếng Anh
    hay gặp); bằng nhau thì theo thứ tự TU_THE."""
    goc = _bo_dau(sai)
    diem = {ten: min(_khoang_cach(goc, k) for k in (_bo_dau(ten), *_TU_THE_ANH[ten])) for ten in TU_THE}
    return sorted(TU_THE, key=lambda ten: (diem[ten], TU_THE.index(ten)))[:3]


def _kiem_nhan_vat(value: str, no: int) -> None:
    if value in ("khong", "nguoi-que"):
        return
    match = _NHAN_VAT_VE_RE.match(value)
    if match is None or not match.group(1).strip():
        raise ParseError(no, "`nhan-vat` phải là `khong`, `nguoi-que` hoặc `ve: <mô tả nhân vật>`.")
    if len(match.group(1).strip()) > NHAN_VAT_MO_TA:
        raise ParseError(no, f"`nhan-vat`: mô tả dài {len(match.group(1).strip())} ký tự, tối đa {NHAN_VAT_MO_TA}. Rút gọn mô tả.")


def _gan_nhat(sai: str, cac_ten: tuple, so: int = 3) -> list:
    goc = _bo_dau(sai)
    return sorted(cac_ten, key=lambda ten: (_khoang_cach(goc, _bo_dau(ten)), cac_ten.index(ten)))[:so]


def giai_nen(value: str, so_canh: int, cac_canh: list, dong: int = 0) -> dict:
    """Giá trị `nen` của cảnh `so_canh` -> một trong:
    {"kieu": "mau", "ten"} · {"kieu": "file", "file"} (tên file trần trong anh/) ·
    {"kieu": "ai", "mo_ta", "file": "ai/nen-<số cảnh>.jpg"} · {"kieu": "nhu", "canh": k, "goc": <nền gốc>}.
    `nhu-canh k` chỉ trỏ về cảnh `ke-chuyen` đứng trước; chuỗi `nhu-canh` giải về cảnh gốc (k là số cảnh gốc).
    `cac_canh`: các cảnh của video (ít nhất tới cảnh k). Lỗi là ParseError ở dòng `dong`."""
    if value.startswith("mau/"):
        ten = value[len("mau/"):].strip()
        if ten not in NEN_MAU:
            goi_y = _gan_nhat(ten, NEN_MAU, 1)[0]
            raise ParseError(dong, f"`nen`: không có nền mẫu `{ten}`. Có phải `{goi_y}`? Tám nền mẫu: {', '.join(NEN_MAU)}.")
        return {"kieu": "mau", "ten": ten}
    ve = _NHAN_VAT_VE_RE.match(value)
    if ve:
        mo_ta = ve.group(1).strip()
        if not mo_ta:
            raise ParseError(dong, "`nen` dạng `ve:` cần mô tả nền, ví dụ `nen: ve: ruộng bậc thang buổi sáng`.")
        if len(mo_ta) > NEN_MO_TA:
            raise ParseError(dong, f"`nen`: mô tả dài {len(mo_ta)} ký tự, tối đa {NEN_MO_TA}. Rút gọn mô tả.")
        return {"kieu": "ai", "mo_ta": mo_ta, "file": f"ai/nen-{so_canh}.jpg"}
    nhu = _NHU_CANH_RE.match(value)
    if nhu:
        so = nhu.group(1).strip()
        if not so.isascii() or not so.isdigit() or int(so) < 1:
            raise ParseError(dong, "`nen` dùng lại nền cảnh trước phải có dạng `nhu-canh <số>`, ví dụ `nhu-canh 2`.")
        k = int(so)
        if k == so_canh:
            raise ParseError(dong, f"`nen: nhu-canh {k}` trỏ tới chính nó (Cảnh {so_canh}); `nhu-canh` dùng lại nền của một "
                                   "cảnh `ke-chuyen` đứng trước.")
        if k > so_canh:
            raise ParseError(dong, f"`nen: nhu-canh {k}` trỏ tới cảnh sau (Cảnh {k}); `nhu-canh` chỉ dùng lại nền của một "
                                   "cảnh `ke-chuyen` đứng trước.")
        dich = cac_canh[k - 1]
        if dich.loai != "ke-chuyen":
            raise ParseError(dong, f"`nen: nhu-canh {k}`: Cảnh {k} là loại `{dich.loai}`, không có nền; `nhu-canh` chỉ dùng "
                                   "lại nền của cảnh `ke-chuyen`.")
        goc = dich.nen if dich.nen is not None else giai_nen(dich.truong["nen"][0], k, cac_canh, dich.dong_truong["nen"][0])
        return goc if goc["kieu"] == "nhu" else {"kieu": "nhu", "canh": k, "goc": goc}
    if ("/" in value or "\\" in value or ".." in value or re.match(r"^[a-zA-Z]:", value)
            or not value.lower().endswith(_DUOI_ANH)):
        raise ParseError(dong, _SAI_NEN)
    return {"kieu": "file", "file": value}


def tu_the_cua(scene, meta: dict):
    """Tư thế nhân vật của cảnh, None khi cảnh không có nhân vật: `tu-the` của cảnh; cảnh `ke-chuyen` không ghi thì
    `dung` (khi video có nhân vật). Dùng chung cho lich.py và việc liệt kê ảnh AI cần vẽ."""
    if meta.get("nhan-vat", "khong") == "khong":
        return None
    if "tu-the" in scene.truong:
        return scene.truong["tu-the"][0]
    return TU_THE_KE_CHUYEN if scene.loai == "ke-chuyen" else None


def phan_cong_thuc(value: str) -> list:
    return value.split(PHAN_CONG_THUC)


def _kiem_du_lieu(truong: dict, dong_truong: dict) -> None:
    kieu, no_kieu = truong["kieu"][0], dong_truong["kieu"][0]
    if kieu not in BIEU_DO_KIEU:
        raise ParseError(no_kieu, f"`kieu` phải là một trong: {', '.join(BIEU_DO_KIEU)}.")
    if kieu == "tron":
        for key in ("truc-ngang", "truc-doc", "don-vi"):
            if key in truong:
                raise ParseError(dong_truong[key][0], f"Biểu đồ `tron` ghi phần trăm, không có trục hay đơn vị; bỏ dòng `{key}`.")
    for value, no in zip(truong["du-lieu"], dong_truong["du-lieu"]):
        cap = tach_du_lieu(value)
        if cap is None:
            raise ParseError(no, "Dòng `du-lieu` phải có dạng `<nhãn> | <số>`, ví dụ `Lúa | 12.5` (dấu thập phân là dấu chấm).")
        if len(cap[1]) > SO_DAI:
            raise ParseError(no, f"Số `{cap[1]}` dài quá {SO_DAI} ký tự; đổi sang đơn vị lớn hơn.")
        if kieu == "tron" and float(cap[1]) <= 0:
            raise ParseError(no, f"Biểu đồ `tron` chỉ nhận số dương; `{cap[1]}` không vẽ được thành lát.")


def _kiem_cau_hoi(truong: dict, dong_truong: dict, dong0: int) -> None:
    chu = CHU_LUA_CHON[:len(truong["lua-chon"])]
    dap_an, no = truong["dap-an"][0].strip().upper(), dong_truong["dap-an"][0]
    if len(dap_an) != 1 or dap_an not in chu:
        raise ParseError(no, f"`dap-an` phải là một chữ cái trong số lựa chọn: {', '.join(chu)}.")
    truong["dap-an"] = [dap_an]
    if "cho" not in truong:
        truong["cho"], dong_truong["cho"] = [str(CHO_MAC_DINH)], [dong0]
        return
    cho, no = truong["cho"][0], dong_truong["cho"][0]
    if not cho.isascii() or not cho.isdigit() or not CHO_TOI_THIEU <= int(cho) <= CHO_TOI_DA:
        raise ParseError(no, f"`cho` là số giây đếm ngược, số nguyên từ {CHO_TOI_THIEU} đến {CHO_TOI_DA}.")
    truong["cho"] = [str(int(cho))]


def _kiem_bieu_thuc(value: str, no: int) -> None:
    phan = phan_cong_thuc(value)
    if len(phan) == 1:
        return
    if len(phan) > MAX_PHAN:
        raise ParseError(no, f"`bieu-thuc` có {len(phan)} phần, tối đa {MAX_PHAN} phần tách bằng ` | `.")
    if any(not p.strip() for p in phan):
        raise ParseError(no, "`bieu-thuc` có phần trống giữa hai dấu ` | `.")
    for p in phan:
        dem = (p.count("**"), p.replace("**", "").count("~"), p.replace("**", "").count("^"),
               p.count("{{") - p.count("}}"))
        if any(d % 2 for d in dem[:3]) or dem[3]:
            raise ParseError(no, "`**`, `~`, `^`, `{{…}}` phải mở và đóng trong cùng một phần; không cắt ngang dấu ` | `.")


class ParseError(Exception):
    """Lỗi trong video.md; luôn kèm số dòng để AI sửa được đúng chỗ."""

    def __init__(self, line_no: int, message: str) -> None:
        super().__init__(f"Dòng {line_no}: {message}")
        self.line_no = line_no
        self.message = message


@dataclass
class Scene:
    so: int
    dong: int
    loai: str
    loi: str
    truong: dict
    dong_truong: dict
    # Cảnh ke-chuyen: nền đã giải (giai_nen); cảnh khác là None.
    nen: dict | None = None
    # Cảnh vox: danh sách vox.Nhip đã đọc; cảnh khác là None.
    nhip: list | None = None


@dataclass
class Video:
    meta: dict
    canh: list
    # Số dòng của từng khoá đầu có trong video.md (lỗi nhạc nền nêu đúng dòng khoá).
    dong_meta: dict = field(default_factory=dict)


def _check_value(no: int, key: str, value: str) -> None:
    if value == "":
        raise ParseError(no, f"`{key}` đang trống.")
    if _URL_RE.search(value):
        raise ParseError(no, f"`{key}` chứa địa chỉ web. Không chèn địa chỉ web vào video.")


def _read_meta(lines: list, start: int) -> tuple:
    meta: dict = {}
    dong_meta: dict = {}
    i = start
    while i < len(lines):
        raw = lines[i].strip()
        if raw == "---":
            break
        if raw:
            match = _KEY_RE.match(raw)
            if match is None:
                raise ParseError(i + 1, "Dòng thông tin phải có dạng `khoá: giá trị`.")
            key, value = match.group(1), match.group(2).strip()
            if (key not in META_REQUIRED and key not in META_CHOICES and key not in META_FREE
                    and key not in VOX_META_CHOICES):
                raise ParseError(i + 1, f"Khoá `{key}` không có trong khối thông tin.")
            if key in meta:
                raise ParseError(i + 1, f"Khoá `{key}` bị lặp.")
            _check_value(i + 1, key, value)
            if key in META_CHOICES:
                # `chuyen-canh` của phong-cach `vox` dùng VOX_META_CHOICES; kiểm sau vòng lặp, khi đã biết phong-cach.
                if key != "chuyen-canh" and value not in META_CHOICES[key]:
                    raise ParseError(i + 1, f"`{key}` phải là một trong: {', '.join(META_CHOICES[key])}.")
            elif key in VOX_META_CHOICES and value not in VOX_META_CHOICES[key]:
                raise ParseError(i + 1, f"`{key}` phải là một trong: {', '.join(VOX_META_CHOICES[key])}.")
            if key == "nhan-vat":
                _kiem_nhan_vat(value, i + 1)
            if key == "thoi-luong" and (not value.isascii() or not value.isdigit()
                                         or not vox.THOI_LUONG[0] <= int(value) <= vox.THOI_LUONG[1]):
                raise ParseError(i + 1, "`thoi-luong` là số giây của video, số nguyên từ 15 đến 600, "
                                        "ví dụ `thoi-luong: 60`.")
            meta[key] = value
            dong_meta[key] = i + 1
        i += 1
    else:
        raise ParseError(start, "Khối thông tin chưa đóng bằng dòng `---`.")
    phong_cach = meta.get("phong-cach", META_DEFAULTS["phong-cach"])
    for key in (("tieu-de",) if phong_cach == "vox" else META_REQUIRED):
        if key not in meta:
            raise ParseError(i + 1, f"Khối thông tin thiếu `{key}`.")
    if "nguon-nhac" in meta and "nhac-nen" not in meta:
        raise ParseError(dong_meta["nguon-nhac"], "`nguon-nhac` chỉ dùng kèm `nhac-nen` (nguồn của file nhạc nền); "
                                                  "thêm dòng `nhac-nen: <file trong nhac/>` hoặc bỏ dòng này.")
    if len(meta.get("loat", "")) > LOAT_DAI:
        raise ParseError(dong_meta["loat"], f"`loat` dài {len(meta['loat'])} ký tự, tối đa {LOAT_DAI}. Rút gọn tên loạt.")
    for key in VOX_META_CHOICES:
        if key != "chuyen-canh" and key in meta and phong_cach != "vox":
            raise ParseError(dong_meta[key], f"`{key}` chỉ dùng với `phong-cach: vox`.")
    if "chuyen-canh" in meta:
        lua_chon = VOX_META_CHOICES["chuyen-canh"] if phong_cach == "vox" else META_CHOICES["chuyen-canh"]
        if meta["chuyen-canh"] not in lua_chon:
            raise ParseError(dong_meta["chuyen-canh"], f"`chuyen-canh` phải là một trong: {', '.join(lua_chon)}.")
    if phong_cach == "vox":
        for key in vox.VOX_CAM:
            if key in meta:
                raise ParseError(dong_meta[key], f"`{key}` là khoá của kiểu viết tay, không dùng với "
                                                  "`phong-cach: vox`; bỏ dòng này.")
    for key, default in META_DEFAULTS.items():
        meta.setdefault(key, default)
    if phong_cach == "vox":
        for key, choices in VOX_META_CHOICES.items():
            meta.setdefault(key, choices[0])
        for key in vox.VOX_CAM:
            meta.pop(key, None)
    return meta, dong_meta, i + 1


_VOX_ALLOWED = {"loi", "bo-cuc", "nhip", "chuyen", "nguon"}


def _finish_vox(so: int, dong0: int, truong: dict, dong_truong: dict, kho: str) -> Scene:
    if "loai" in truong:
        raise ParseError(dong_truong["loai"][0], "Cảnh Vox không có `loai`; tả cảnh bằng `bo-cuc` và các dòng `nhip`.")
    for key in truong:
        if key not in _VOX_ALLOWED:
            raise ParseError(dong_truong[key][0], f"Cảnh Vox không có trường `{key}`.")
    for key in ("loi", "bo-cuc"):
        if key not in truong:
            raise ParseError(dong0, f"Cảnh {so} thiếu `{key}`.")
        if len(truong[key]) > 1:
            raise ParseError(dong_truong[key][1], f"`{key}` bị lặp trong Cảnh {so}.")
    count = len(truong.get("nhip", []))
    if count < 1:
        raise ParseError(dong0, f"Cảnh {so} (loại vox) cần ít nhất 1 dòng `nhip`.")
    if count > vox.NHIP_TOI_DA:
        raise ParseError(dong_truong["nhip"][vox.NHIP_TOI_DA],
                          f"Cảnh loại vox chỉ có tối đa {vox.NHIP_TOI_DA} dòng `nhip`.")
    for value, no in zip(truong.get("chuyen", []), dong_truong.get("chuyen", [])):
        if so == 1:
            raise ParseError(no, "Cảnh 1 mở đầu video, không có cảnh trước để chuyển; bỏ dòng `chuyen:`.")
        if value not in vox.CHUYEN_CANH:
            raise ParseError(no, f"`chuyen` phải là một trong: {', '.join(vox.CHUYEN_CANH)}.")
    if "nguon" in truong and len(truong["nguon"][0]) > vox.NGUON_DAI:
        raise ParseError(dong_truong["nguon"][0],
                          f"`nguon` dài {len(truong['nguon'][0])} ký tự, tối đa {vox.NGUON_DAI}. Rút gọn nguồn.")
    loi = truong.pop("loi")[0]
    nhip = [vox.doc_nhip(v, no, k) for k, (v, no) in enumerate(zip(truong["nhip"], dong_truong["nhip"]))]
    scene = Scene(so=so, dong=dong0, loai="vox", loi=loi, truong=truong, dong_truong=dong_truong, nhip=nhip)
    vox.kiem_canh(scene, kho)
    return scene


def _finish(so: int, dong0: int, fields: list, vox_kho: str | None = None) -> Scene:
    truong: dict = {}
    dong_truong: dict = {}
    for key, value, no in fields:
        truong.setdefault(key, []).append(value)
        dong_truong.setdefault(key, []).append(no)
    if vox_kho is not None:
        return _finish_vox(so, dong0, truong, dong_truong, vox_kho)
    for key in ("loai", "loi"):
        if key not in truong:
            raise ParseError(dong0, f"Cảnh {so} thiếu `{key}`.")
        if len(truong[key]) > 1:
            raise ParseError(dong_truong[key][1], f"`{key}` bị lặp trong Cảnh {so}.")
    loai = truong["loai"][0]
    if loai not in SCENE_SPEC:
        raise ParseError(dong_truong["loai"][0], f"`loai` phải là một trong: {', '.join(SCENE_TYPES)}.")
    required, optional, repeated = SCENE_SPEC[loai]
    allowed = {"loai", "loi", "chuyen", *required, *optional, *repeated}
    for key, value, no in fields:
        if key not in allowed:
            raise ParseError(no, f"Cảnh loại `{loai}` không có trường `{key}`.")
    for value, no in zip(truong.get("chuyen", []), dong_truong.get("chuyen", [])):
        if so == 1:
            raise ParseError(no, "Cảnh 1 mở đầu video, không có cảnh trước để chuyển; bỏ dòng `chuyen:`.")
        if value == "luan-phien":
            raise ParseError(no, "`luan-phien` chỉ dùng ở khoá đầu `chuyen-canh: luan-phien`; "
                                 f"trường `chuyen` của cảnh là một trong: {', '.join(SCENE_KIEU_CHUYEN)}.")
        if value not in SCENE_KIEU_CHUYEN:
            raise ParseError(no, f"`chuyen` phải là một trong: {', '.join(SCENE_KIEU_CHUYEN)}.")
    for key in (*required, *optional, "chuyen"):
        if key in truong and len(truong[key]) > 1:
            raise ParseError(dong_truong[key][1], f"`{key}` bị lặp trong Cảnh {so}.")
    for key in required:
        if key not in truong:
            raise ParseError(dong0, f"Cảnh {so} (loại `{loai}`) thiếu `{key}`.")
    for key, (low, high) in repeated.items():
        count = len(truong.get(key, []))
        if count < low:
            raise ParseError(dong0, f"Cảnh {so} (loại `{loai}`) cần ít nhất {low} dòng `{key}`.")
        if count > high:
            raise ParseError(dong_truong[key][high], f"Cảnh loại `{loai}` chỉ có tối đa {high} dòng `{key}`.")
    if "hinh" in truong and "anh" in truong:
        dong_sau = max(dong_truong["hinh"][0], dong_truong["anh"][0])
        raise ParseError(dong_sau, f"Cảnh {so} chỉ được có `hinh` hoặc `anh`, không cả hai.")
    if "tu-the" in truong:
        ten, no = truong["tu-the"][0], dong_truong["tu-the"][0]
        if ten not in TU_THE:
            goi_y = ", ".join(f"`{g}`" for g in goi_y_tu_the(ten))
            raise ParseError(no, f"`tu-the` `{ten}` không có. Có phải: {goi_y}? Mười tư thế: {', '.join(TU_THE)}.")
        for khac in ("hinh", "anh"):
            if khac in truong:
                dong_sau = max(no, dong_truong[khac][0])
                raise ParseError(dong_sau, f"Cảnh {so} có nhân vật (`tu-the`) đứng ở cột phụ nên không có `{khac}`; "
                                           f"bỏ dòng `{khac}` hoặc dòng `tu-the`.")
    if "vi-tri" in truong and truong["vi-tri"][0] not in VI_TRI:
        raise ParseError(dong_truong["vi-tri"][0], f"`vi-tri` phải là một trong: {', '.join(VI_TRI)}.")
    if "nguon" in truong and "anh" not in truong:
        raise ParseError(dong_truong["nguon"][0],
                         f"`nguon` chỉ dùng kèm `anh` (dòng nguồn của ảnh thật); Cảnh {so} chưa có `anh`.")
    for value, no in zip(truong.get("diem", []), dong_truong.get("diem", [])):
        if _POINT_RE.match(value) is None:
            raise ParseError(no, "Điểm đồ thị phải có dạng `x, y` (hai số, dấu thập phân là dấu chấm).")
    for value, no in zip(truong.get("tham-so", []), dong_truong.get("tham-so", [])):
        if _PARAM_RE.match(value) is None:
            raise ParseError(no, "Dòng `tham-so` phải có dạng `<giây> <mã> <giá trị>`, ví dụ `0 chieu-dai 0.4`.")
    if loai == "bieu-do":
        _kiem_du_lieu(truong, dong_truong)
    for value, no in zip(truong.get("moc", []), dong_truong.get("moc", [])):
        if tach_moc(value) is None:
            raise ParseError(no, "Dòng `moc` phải có dạng `<nhãn> | <mô tả>`, ví dụ `1945 | Cách mạng tháng Tám`.")
    if "the" in truong and tach_the(truong["the"][0]) is None:
        raise ParseError(dong_truong["the"][0], "`the` phải có dạng `<nhãn> | <giá trị> | <chú thích>` (chú thích bỏ "
                                                "trống được), ví dụ `Siêu lạm phát | 1923 | Cộng hoà Weimar (Đức)`.")
    if loai == "cong-thuc":
        _kiem_bieu_thuc(truong["bieu-thuc"][0], dong_truong["bieu-thuc"][0])
    if loai == "cau-hoi":
        _kiem_cau_hoi(truong, dong_truong, dong0)
    loi = truong.pop("loi")[0]
    truong.pop("loai")
    dong_truong.pop("loai")
    dong_truong.pop("loi")
    return Scene(so=so, dong=dong0, loai=loai, loi=loi, truong=truong, dong_truong=dong_truong)


def parse(text: str) -> Video:
    # Chữ NFD (Unikey "Unicode tổ hợp", dán từ Mac/PDF) về NFC một lần ở đầu vào: khoá so khớp nhấn ý, tiêu đề cảnh
    # và tiền tố "Nhạc" đều so trên NFC.
    lines = unicodedata.normalize("NFC", text.lstrip("﻿")).splitlines()
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i >= len(lines) or lines[i].strip() != "---":
        raise ParseError(i + 1, "video.md phải mở đầu bằng khối thông tin giữa hai dòng `---`.")
    meta, dong_meta, i = _read_meta(lines, i + 1)
    vox_kho = meta["kho"] if meta["phong-cach"] == "vox" else None
    scenes: list = []
    current = None
    for index in range(i, len(lines)):
        no = index + 1
        raw = lines[index].strip()
        if not raw:
            continue
        heading = _SCENE_RE.match(raw)
        if heading:
            if current is not None:
                scenes.append(_finish(*current, vox_kho))
            expected = len(scenes) + 1
            if int(heading.group(1)) != expected:
                raise ParseError(no, f"Cảnh phải đánh số liên tiếp; ở đây phải là `## Cảnh {expected}`.")
            current = (expected, no, [])
            continue
        if current is None:
            raise ParseError(no, "Sau khối thông tin phải là `## Cảnh 1`.")
        match = _KEY_RE.match(raw)
        if match is None:
            raise ParseError(no, "Dòng trong cảnh phải có dạng `khoá: giá trị`.")
        key, value = match.group(1), match.group(2).strip()
        _check_value(no, key, value)
        current[2].append((key, value, no))
    if current is not None:
        scenes.append(_finish(*current, vox_kho))
    if not scenes:
        raise ParseError(i + 1, "video.md chưa có cảnh nào; bắt đầu bằng `## Cảnh 1`.")
    if meta.get("nhan-vat", "khong") == "khong":
        for scene in scenes:
            for key in ("tu-the", "vi-tri"):
                if key in scene.truong:
                    raise ParseError(scene.dong_truong[key][0], f"`{key}` cần nhân vật dẫn chuyện; thêm "
                                     "`nhan-vat: nguoi-que` (hoặc `nhan-vat: ve: <mô tả>`) vào khối thông tin, hoặc bỏ dòng này.")
    for scene in scenes:
        if scene.loai == "ke-chuyen":
            scene.nen = giai_nen(scene.truong["nen"][0], scene.so, scenes, scene.dong_truong["nen"][0])
    return Video(meta=meta, canh=scenes, dong_meta=dong_meta)
