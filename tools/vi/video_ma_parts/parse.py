"""Đọc video.md thành dữ liệu; lỗi luôn kèm số dòng. Ngữ pháp ở docs/vi/tro-ly/video-giai-thich.md. Chỉ dùng thư viện chuẩn."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

META_REQUIRED = ("tieu-de", "mon", "lop")
META_CHOICES = {
    # Phong cách: viết tay trên bảng, hoặc cắt dán giấy kiểu Vox (runtime/cat-dan.css, cat-dan.js).
    "phong-cach": ("viet-tay", "cat-dan"),
    "giong": ("nu", "nam"),
    "toc-do": ("cham", "vua", "nhanh"),
    "phu-de": ("hinh", "file", "khong", "karaoke"),
    "ban-tay": ("co", "khong"),
    "may-quay": ("co", "khong"),
    "chuyen-canh": ("lau-bang", "lat-trang", "truot", "phong", "mo-man", "luan-phien", "khong"),
    "chu-dong": ("co", "khong"),
    "am-thanh": ("co", "khong"),
    # Khổ khung (kho.py): ngang 16:9 hoặc dọc 9:16; độ phân giải xuất 1080 (Full HD) hoặc 720 cho máy yếu.
    "kho": ("ngang", "doc"),
    "do-phan-giai": ("1080", "720"),
}
# Khoá đầu tự do (không có mặc định): nhạc nền là tên file trong nhac/; nguồn nhạc là chữ (chỉ dùng kèm `nhac-nen`).
META_FREE = ("nhac-nen", "nguon-nhac")
META_DEFAULTS = {
    "phong-cach": "viet-tay", "giong": "nu", "toc-do": "vua", "phu-de": "karaoke",
    "ban-tay": "co", "may-quay": "co", "chuyen-canh": "lau-bang",
    "chu-dong": "co", "am-thanh": "co", "kho": "ngang", "do-phan-giai": "1080",
}

# loại cảnh -> (trường đơn bắt buộc, trường đơn tuỳ chọn, trường lặp {khoá: (tối thiểu, tối đa)})
SCENE_SPEC = {
    "tieu-de": (("chu",), ("phu", "hinh", "anh", "nguon"), {}),
    "khai-niem": (("thuat-ngu", "dinh-nghia"), ("hinh", "anh", "nguon"), {}),
    "cong-thuc": (("bieu-thuc",), ("hinh", "anh", "nguon"), {"giai-thich": (0, 4)}),
    "y-tung-y": (("tieu-de",), ("hinh", "anh", "nguon"), {"y": (1, 6)}),
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
}
BIEU_DO_KIEU = ("cot", "duong", "tron")
# Cảnh câu hỏi: lựa chọn tự đánh A–D; `cho` là số giây đếm ngược (số nguyên).
CHU_LUA_CHON = "ABCD"
CHO_MAC_DINH = 5
CHO_TOI_THIEU, CHO_TOI_DA = 3, 10
SO_DAI = 10
# `bieu-thuc` của `cong-thuc` tách phần bằng ` | ` (dấu gạch đứng có khoảng trắng hai bên); tối đa 4 phần.
PHAN_CONG_THUC = " | "
MAX_PHAN = 4
SCENE_TYPES = tuple(SCENE_SPEC)
# Trường `chuyen:` (mọi loại cảnh, từ cảnh 2) ghi đè khoá đầu `chuyen-canh` cho riêng cảnh đó.
SCENE_KIEU_CHUYEN = ("lau-bang", "lat-trang", "truot", "phong", "mo-man", "khong")

_KEY_RE = re.compile(r"^([a-z][a-z0-9-]*):\s*(.*)$")
_SCENE_RE = re.compile(r"^##\s+Cảnh\s+(\d+)\s*$")
_URL_RE = re.compile(r"https?://|www\.", re.IGNORECASE)
_POINT_RE = re.compile(r"^-?\d+(?:\.\d+)?\s*,\s*-?\d+(?:\.\d+)?$")
_PARAM_RE = re.compile(r"^\d+(?:\.\d+)?\s+[a-z0-9-]+\s+-?\d+(?:\.\d+)?$")
_DATA_RE = re.compile(r"^(.*?\S)\s*\|\s*(-?\d+(?:\.\d+)?)$")
_MOC_RE = re.compile(r"^(.*?\S)\s*\|\s*(\S.*)$")


def tach_du_lieu(value: str) -> tuple:
    """`<nhãn> | <số>` -> (nhãn, chuỗi số); None nếu sai dạng. Tách ở dấu `|` cuối cùng."""
    match = _DATA_RE.match(value)
    return (match.group(1), match.group(2)) if match else None


def tach_moc(value: str) -> tuple:
    """`<nhãn> | <mô tả>` -> (nhãn, mô tả); None nếu sai dạng. Tách ở dấu `|` đầu tiên."""
    match = _MOC_RE.match(value)
    return (match.group(1), match.group(2).strip()) if match else None


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
            if key not in META_REQUIRED and key not in META_CHOICES and key not in META_FREE:
                raise ParseError(i + 1, f"Khoá `{key}` không có trong khối thông tin.")
            if key in meta:
                raise ParseError(i + 1, f"Khoá `{key}` bị lặp.")
            _check_value(i + 1, key, value)
            if key in META_CHOICES and value not in META_CHOICES[key]:
                raise ParseError(i + 1, f"`{key}` phải là một trong: {', '.join(META_CHOICES[key])}.")
            meta[key] = value
            dong_meta[key] = i + 1
        i += 1
    else:
        raise ParseError(start, "Khối thông tin chưa đóng bằng dòng `---`.")
    for key in META_REQUIRED:
        if key not in meta:
            raise ParseError(i + 1, f"Khối thông tin thiếu `{key}`.")
    if "nguon-nhac" in meta and "nhac-nen" not in meta:
        raise ParseError(dong_meta["nguon-nhac"], "`nguon-nhac` chỉ dùng kèm `nhac-nen` (nguồn của file nhạc nền); "
                                                  "thêm dòng `nhac-nen: <file trong nhac/>` hoặc bỏ dòng này.")
    for key, default in META_DEFAULTS.items():
        meta.setdefault(key, default)
    return meta, dong_meta, i + 1


def _finish(so: int, dong0: int, fields: list) -> Scene:
    truong: dict = {}
    dong_truong: dict = {}
    for key, value, no in fields:
        truong.setdefault(key, []).append(value)
        dong_truong.setdefault(key, []).append(no)
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
                scenes.append(_finish(*current))
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
        scenes.append(_finish(*current))
    if not scenes:
        raise ParseError(i + 1, "video.md chưa có cảnh nào; bắt đầu bằng `## Cảnh 1`.")
    return Video(meta=meta, canh=scenes, dong_meta=dong_meta)
