"""Chủ đề của khung hình và font đóng gói: Itim (`viet-tay`, phụ đề), Be Vietnam Pro (`cat-dan`); bộ đọc bảng cmap
và khối @font-face nhúng data:."""

from __future__ import annotations

import base64
import json
import struct
from pathlib import Path

_FONTS = Path(__file__).resolve().parent / "runtime" / "fonts"
FONT = _FONTS / "Itim-Regular.ttf"
TEN = "Itim"
# Be Vietnam Pro của phong cách `cat-dan`: độ đậm -> file (nguồn và SHA-256 ở runtime/fonts/README.md).
TEN_CAT_DAN = "BeVietnamPro"
FONT_CAT_DAN = {400: _FONTS / "BeVietnamPro-Regular.ttf", 800: _FONTS / "BeVietnamPro-ExtraBold.ttf"}

# Chủ đề (`du["chuDe"]`) theo khoá đầu `phong-cach`: font, kiểu hiện chữ (`viet` bút viết, `truot` trượt và mờ dần),
# kiểu nét (`ve` vẽ theo nhịp, `nhanh` vẽ nhanh và đậm); `cat-dan` thêm bốn màu nhãn (cảnh N dùng màu (N-1) % 4) và
# màu giấy nền.
CHU_DE = {
    "viet-tay": {"ten": "viet-tay", "font": TEN, "hienChu": "viet", "net": "ve"},
    "cat-dan": {"ten": "cat-dan", "font": TEN_CAT_DAN, "hienChu": "truot", "net": "nhanh",
                "mauNhan": ["#b07419", "#1f6f78", "#c8452f", "#2f4f9e"], "giay": "#f3ead7"},
}

_THUONG = "ạảãàáâậầấẩẫăặằắẳẵẹẻẽèéêệềếểễịỉĩìíọỏõòóôộồốổỗơợờớởỡụủũùúưựừứửữỵỷỹỳýđ"
CHU_VIET = _THUONG + _THUONG.upper()


def _doan_dinh_dang_4(data: bytes, offset: int) -> set[int]:
    seg_count_x2 = struct.unpack_from(">H", data, offset + 6)[0]
    seg_count = seg_count_x2 // 2
    end_codes_off = offset + 14
    end_codes = struct.unpack_from(f">{seg_count}H", data, end_codes_off)
    start_codes_off = end_codes_off + seg_count_x2 + 2
    start_codes = struct.unpack_from(f">{seg_count}H", data, start_codes_off)
    id_delta_off = start_codes_off + seg_count_x2
    id_deltas = struct.unpack_from(f">{seg_count}h", data, id_delta_off)
    id_range_off_off = id_delta_off + seg_count_x2
    id_range_offsets = struct.unpack_from(f">{seg_count}H", data, id_range_off_off)

    ma = set()
    for i in range(seg_count):
        start, end = start_codes[i], end_codes[i]
        if start == 0xFFFF and end == 0xFFFF:
            continue
        id_range_offset = id_range_offsets[i]
        for c in range(start, end + 1):
            if id_range_offset == 0:
                glyph_id = (c + id_deltas[i]) & 0xFFFF
            else:
                addr = id_range_off_off + i * 2 + id_range_offset + (c - start) * 2
                if addr + 2 > len(data):
                    continue
                glyph_id = struct.unpack_from(">H", data, addr)[0]
                if glyph_id != 0:
                    glyph_id = (glyph_id + id_deltas[i]) & 0xFFFF
            if glyph_id != 0:
                ma.add(c)
    return ma


def _doan_dinh_dang_12(data: bytes, offset: int) -> set[int]:
    so_nhom = struct.unpack_from(">I", data, offset + 12)[0]
    ma = set()
    pos = offset + 16
    for _ in range(so_nhom):
        start, end, _glyph_dau = struct.unpack_from(">III", data, pos)
        ma.update(range(start, end + 1))
        pos += 12
    return ma


def bang_ma(path) -> set:
    """Đọc bảng `cmap` (định dạng 4 và 12) của một font TrueType, trả về tập mã Unicode có mặt."""
    data = Path(path).read_bytes()
    so_bang = struct.unpack_from(">H", data, 4)[0]
    cmap_offset = None
    pos = 12
    for _ in range(so_bang):
        tag, _checksum, offset, _length = struct.unpack_from(">4sIII", data, pos)
        if tag == b"cmap":
            cmap_offset = offset
        pos += 16
    if cmap_offset is None:
        return set()

    so_bang_con = struct.unpack_from(">H", data, cmap_offset + 2)[0]
    ma = set()
    pos = cmap_offset + 4
    for _ in range(so_bang_con):
        _platform, _encoding, sub_offset = struct.unpack_from(">HHI", data, pos)
        sub_offset += cmap_offset
        dinh_dang = struct.unpack_from(">H", data, sub_offset)[0]
        if dinh_dang == 4:
            ma |= _doan_dinh_dang_4(data, sub_offset)
        elif dinh_dang == 12:
            ma |= _doan_dinh_dang_12(data, sub_offset)
        pos += 8
    return ma


def chu_de(phong_cach) -> dict:
    """Bản sao chủ đề của `phong_cach` (không có thì `viet-tay`)."""
    return json.loads(json.dumps(CHU_DE.get(phong_cach or "viet-tay", CHU_DE["viet-tay"])))


def _face(ten: str, path: Path, dam: str = "") -> str:
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"@font-face{{font-family:'{ten}';{dam}src:url(data:font/ttf;base64,{b64});}}"


def font_css(phong_cach: str = "viet-tay") -> str:
    """Khối @font-face nhúng data: của chủ đề. `cat-dan` nhúng Be Vietnam Pro 400 và 800, và vẫn nhúng Itim."""
    css = _face(TEN, FONT)
    if phong_cach == "cat-dan":
        css += "".join(_face(TEN_CAT_DAN, path, f"font-weight:{dam};") for dam, path in FONT_CAT_DAN.items())
    return css
