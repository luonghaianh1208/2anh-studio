"""Danh sách ảnh của video Vox và tên file tất định (video_ma đọc lại cùng tên)."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from video_ma_parts.vox import DAU_NHAN_VAT

DUOI_PHONG = {
    # Kiểu video mẫu Vox: tranh cắt dán hỗn hợp, giấy cũ, tranh khắc, tông trầm.
    "cat-dan": ("tranh cắt dán hỗn hợp kiểu tạp chí cổ, ghép từ ảnh in chấm lưới và tranh khắc, giấy cũ ngả màu, "
                "mép giấy xé, tông đỏ trầm, xanh than, vàng đất và kem"),
    "chup-that": "ảnh chụp thật, ánh sáng tự nhiên, chi tiết sắc nét",
    "minh-hoa": "tranh minh hoạ phẳng, nét gọn, màu tươi",
}
DUOI_CAT = "cả cụm nằm gọn ở giữa, tách rời khỏi nền, nền xanh lá thuần #00FF00 phẳng, không bóng đổ, không viền"
DUOI_NEN = ("nền phủ kín khung làm phông cho video, các mảng giấy xé và hình mờ nằm ở rìa và các góc, "
            "chừa vùng giấy sáng ít chi tiết ở giữa và bên trái để đặt chữ, không có nhân vật lớn ở giữa")
DUOI_CHUNG = "không có chữ, không có chữ cái, không có logo"

# `phong-anh: cat-dan` (mặc định): prompt chi tiết theo video mẫu Vox, tiếng Anh vì mô hình vẽ theo sát hơn. Ba phần:
# phong cách chung (kỹ thuật, bảng màu, chất giấy) cho mọi ảnh; bố cục riêng cho nền, vật cắt rời, ảnh khung/phủ.
# Giấy kem chỉ nằm ở phần nền: để ở phần chung thì mô hình vẽ cả tờ giấy sau vật, tách nền ra cả tờ giấy.
CAT_DAN_CHUNG = (
    "Editorial mixed-media paper collage in the style of Vox explainer videos. Elements are cut out from vintage "
    "black-and-white halftone photographs and 19th-century copperplate engravings, printed in muted sepia with visible "
    "halftone dots, combined with flat torn-paper shapes in a strictly limited palette: deep navy blue #1F3A5F, "
    "vermilion red #D9472B, mustard yellow #E3A72F, teal #2A7F7A and cream #EFE6D2. Torn paper edges with white "
    "fibrous rims, soft drop shadows between paper layers, subtle risograph grain."
)
CAT_DAN = {
    "nen": (
        "Wide background plate on aged cream newsprint paper with fine fibers and faint stains. A large calm area of "
        "plain cream paper fills the centre and the left two thirds, almost empty, reserved for text. Collage pieces "
        "only along the edges and corners: big torn shapes of navy, vermilion and mustard paper, a strip of graph paper "
        "with faint blue grid lines, a halftone dot patch, a fragment of an engraved banknote guilloche pattern, and a "
        "few engraved details about the theme: {mo_ta}. Low clutter, generous negative space, flat front-facing view, "
        "no people."
    ),
    "cat": (
        "One single hero cut-out showing exactly this and nothing else: {mo_ta}. Rendered as a detailed vintage halftone "
        "photograph or copperplate engraving in muted sepia, cut out along its silhouette with a thin white paper border, "
        "with one or two small flat torn paper shapes in navy, vermilion or mustard tucked directly behind it. Do not add "
        "extra people, extra objects, picture frames or a paper sheet behind the whole group. People, when present, look "
        "like real adults from a 1950s photograph, natural proportions. Centered with wide margin, standing directly on a "
        "perfectly flat pure green #00FF00 background that fills the whole image edge to edge, no shadow on the green."
    ),
    "khung": (
        "A single rectangular vintage picture filling the entire image edge to edge: {mo_ta}. Halftone photograph or "
        "engraving in muted sepia with small accents from the palette, no border, no frame, no paper margin."
    ),
    "phu": (
        "A full-frame collage scene filling the entire image edge to edge: {mo_ta}. Layered cut-out halftone photographs "
        "and engravings over aged cream paper, with large torn shapes of navy, vermilion and mustard paper."
    ),
}
CAT_DAN_CAM = "No text, no letters, no numbers, no logos, no watermark."
# `phong-anh: ban-ve`: bản vẽ kỹ thuật. Vật cắt rời vẽ trên một tấm thẻ giấy xanh (nét trắng mảnh không tách được
# khỏi nền xanh lá), cả tấm thẻ được tách ra.
BAN_VE_CHUNG = (
    "Technical blueprint illustration in an engineering drafting style: crisp white and pale cyan line drawings with "
    "thin precise strokes, hatching on shaded surfaces, dimension lines with small arrowheads, construction lines and "
    "circle-centre marks, on deep blueprint blue paper #123A5C with a faint square grid and slight paper texture. The "
    "only accent colour is safety orange #F28C28, used for one highlighted part."
)
BAN_VE = {
    "nen": (
        "Wide background plate. A large calm area of plain blueprint paper fills the centre and the left two thirds, "
        "almost empty, reserved for text. Drafting details only along the edges and corners: partial technical drawings "
        "about the theme: {mo_ta}, dimension lines, a title-block corner frame left blank, compass and ruler marks. "
        "Low clutter, flat front-facing view, no people."
    ),
    "cat": (
        "One single technical drawing showing exactly this and nothing else: {mo_ta}. Drawn on a rectangular card of "
        "blueprint paper with clean straight edges and a thin white border, the card centered with wide margin on a "
        "perfectly flat pure green #00FF00 background that fills the whole image edge to edge, no shadow on the green."
    ),
    "khung": "A single rectangular technical blueprint drawing filling the entire image edge to edge: {mo_ta}. No border.",
    "phu": "A full-frame technical blueprint scene filling the entire image edge to edge: {mo_ta}.",
}
# Phong cách ảnh có prompt chi tiết: (phần chung, bố cục theo kiểu ảnh).
PHONG_CHI_TIET = {"cat-dan": (CAT_DAN_CHUNG, CAT_DAN), "ban-ve": (BAN_VE_CHUNG, BAN_VE)}
# Nhân vật chính cố định (`nhan-vat-chinh`): mô tả `ve:` gọi nhân vật bằng `vox.DAU_NHAN_VAT`.
CAU_NHAN_VAT = ("the main character ({mo_ta}); draw the same main character with the same face, hair, clothes and "
                "colours as in every other image of this video")
KHO_ANH = {"cat": "1024x1024", ("khung", "ngang"): "1536x1024", ("khung", "doc"): "1024x1536",
           ("phu", "ngang"): "1536x1024", ("phu", "doc"): "1024x1536",
           ("nen", "ngang"): "1536x1024", ("nen", "doc"): "1024x1536"}
# Nền AI của cảnh không thuộc nhịp nào: chỉ số nhịp quy ước -1, khoá trong vox.json là "<cảnh>-nen".
CHI_SO_NEN = -1
LOI_TRONG_NEN = 160


@dataclass
class Muc:
    ma: str
    canh: int
    chi_so: int
    kieu: str          # cat | khung | phu | nen
    nguon: str         # ve | tim | file
    prompt: str        # ve: câu lệnh đầy đủ; tim: từ khoá; file: tên file
    kich_thuoc: str
    tuy_chon: tuple


def ma_anh(prompt: str, kich_thuoc: str) -> str:
    return hashlib.sha256(f"{prompt}\n{kich_thuoc}".encode("utf-8")).hexdigest()[:16]


def hat(m: Muc) -> int:
    return m.canh * 100 + (99 if m.kieu == "nen" else m.chi_so)


def khoa(m: Muc) -> str:
    """Khoá của mục trong `anh/ai/vox.json`."""
    return f"{m.canh}-nen" if m.kieu == "nen" else f"{m.canh}-{m.chi_so}"


def _kieu(n, nguon: str) -> str:
    if n.o == "nen":
        return "phu"
    if nguon != "ve" or "khung" in n.tuy_chon:
        return "khung"   # ảnh thật và ảnh có sẵn luôn là khung (spec 4.6)
    return "cat"


def _nen_canh(video, c) -> Muc:
    """Nền AI của cảnh: theo trường `nen` của cảnh, không ghi thì lập từ tên video và lời của cảnh."""
    mo_ta = c.truong.get("nen", [""])[0].strip()
    if mo_ta.startswith("ve:"):
        mo_ta = mo_ta[3:].strip()
    if not mo_ta:
        mo_ta = f"phông nền cho video «{video.meta['tieu-de']}», gợi ý nội dung: {c.loi[:LOI_TRONG_NEN]}"
    kt = KHO_ANH[("nen", video.meta["kho"])]
    if video.meta["phong-anh"] in PHONG_CHI_TIET:
        chung, bo = PHONG_CHI_TIET[video.meta["phong-anh"]]
        prompt = " ".join([chung, bo["nen"].format(mo_ta=mo_ta), CAT_DAN_CAM])
    else:
        prompt = ", ".join([mo_ta, DUOI_PHONG[video.meta["phong-anh"]], DUOI_NEN, DUOI_CHUNG])
    return Muc(ma_anh(prompt, kt), c.so, CHI_SO_NEN, "nen", "ve", prompt, kt, ())


def _prompt_ve(video, mo_ta: str, kieu: str) -> str:
    nhan_vat = video.meta.get("nhan-vat-chinh")
    if nhan_vat and DAU_NHAN_VAT in mo_ta:
        mo_ta = mo_ta.replace(DAU_NHAN_VAT, CAU_NHAN_VAT.format(mo_ta=nhan_vat))
    if video.meta["phong-anh"] in PHONG_CHI_TIET:
        chung, bo = PHONG_CHI_TIET[video.meta["phong-anh"]]
        return " ".join([chung, bo[kieu].format(mo_ta=mo_ta), CAT_DAN_CAM])
    phan = [mo_ta, DUOI_PHONG[video.meta["phong-anh"]]]
    if kieu == "cat":
        phan.append(DUOI_CAT)
    phan.append(DUOI_CHUNG)
    return ", ".join(phan)


def lap(video) -> list:
    kho = video.meta["kho"]
    ve_nen = video.meta.get("nen-canh", "ve") == "ve"
    ds = []
    for c in video.canh:
        co_phu = False
        for n in c.nhip or []:
            if n.vat != "anh":
                continue
            nd = n.noi_dung
            nguon = "ve" if nd.startswith("ve:") else ("tim" if nd.startswith("tim:") else "file")
            kieu = _kieu(n, nguon)
            co_phu = co_phu or kieu == "phu"
            kt = KHO_ANH["cat"] if kieu == "cat" else KHO_ANH[(kieu, kho)]
            if nguon == "ve":
                prompt = _prompt_ve(video, nd[3:].strip(), kieu)
            else:
                prompt = nd[4:].strip() if nguon == "tim" else nd
            ma = ma_anh(prompt, kt) if nguon == "ve" else hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:10]
            ds.append(Muc(ma, c.so, n.chi_so, kieu, nguon, prompt, kt, n.tuy_chon))
        # Cảnh đã có ảnh phủ kín khung (`toan-canh`, ô `nen`) thì không cần nền AI riêng.
        if ve_nen and not co_phu and c.nhip is not None:
            ds.append(_nen_canh(video, c))
    return ds


def file_goc(thu_muc: Path, m: Muc) -> Path:
    if m.nguon == "ve":
        return thu_muc / "anh" / "ai" / "goc" / f"{m.ma}.png"
    if m.nguon == "tim":
        return thu_muc / "anh" / f"tim-{m.ma}.jpg"
    return thu_muc / "anh" / m.prompt


def file_xu_ly(thu_muc: Path, m: Muc) -> Path:
    if m.kieu == "nen":   # nền phủ khung: JPEG cho nhẹ trang
        return thu_muc / "anh" / "ai" / "xu-ly" / f"{m.ma}-{hat(m)}-nen.jpg"
    duoi = "".join(f"-{t}" for t in ("duotone", "halftone") if t in m.tuy_chon)
    return thu_muc / "anh" / "ai" / "xu-ly" / f"{m.ma}-{hat(m)}-{m.kieu}{duoi}.png"
