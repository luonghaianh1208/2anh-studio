"""Câu lệnh (prompt) tiếng Anh gửi công cụ vẽ AI: nền cảnh, nhân vật mẫu, tư thế nhân vật."""

from __future__ import annotations

# Câu phong cách cố định theo `phong-cach` (video_ma_parts/parse.py META_CHOICES).
PHONG_CACH_ANH = {
    "viet-tay": "warm hand-drawn children's book illustration, soft watercolor texture, clean ink outlines, cozy natural light",
    "cat-dan": "editorial paper collage, cut-paper shapes, torn edges, halftone dots, vintage print texture, flat bold colors",
}

# Câu cấm chữ/logo trên ảnh: có mặt trong mọi câu lệnh để công cụ vẽ không tự chèn chữ.
CAM = "No text, no letters, no numbers, no captions, no logos, no watermark, no signature."

# Khổ khung -> cụm tỉ lệ trong câu lệnh nền cảnh.
_KHO_EN = {"ngang": "16:9 landscape", "doc": "9:16 portrait"}

# Mười mô tả tư thế tiếng Anh cố định, cùng tên và thứ tự với video_ma_parts/parse.py TU_THE.
TU_THE_EN = {
    "dung": "standing straight, arms relaxed at the sides",
    "chao": "waving one hand in a friendly greeting",
    "chi-tay": "pointing to the side with one hand",
    "giai-thich": "one hand raised with an open palm, as if explaining something",
    "suy-nghi": "one hand resting on the chin, looking thoughtful",
    "ngac-nhien": "both hands raised near the face, wide eyes, surprised expression",
    "vo-dau": "both hands on the head, stressed and confused expression",
    "dung-lai": "one hand raised forward, palm out, as if signaling to stop",
    "an-mung": "both arms raised up in celebration, joyful expression",
    "buon": "shoulders slumped, head lowered, sad expression",
}


def nen(mo_ta: str, phong_cach: str, kho: str) -> str:
    """Câu lệnh vẽ nền cảnh: phong cách, khung cảnh cho video giải thích (chừa giữa cho nhân vật/tiêu đề), mô tả của
    thầy cô (giữ nguyên tiếng Việt), câu cấm chữ."""
    canh = (f"Background scene for an educational explainer video, {_KHO_EN[kho]} composition, leave the center area "
            "calm and uncluttered for a character and titles, no people.")
    return f"{PHONG_CACH_ANH[phong_cach]}. {canh} {mo_ta.strip()}. {CAM}"


def nhan_vat_mau(mo_ta: str, phong_cach: str) -> str:
    """Câu lệnh vẽ ảnh mẫu nhân vật (nền xanh thuần để tách nền)."""
    dau = ("Character reference sheet: one single full-body character, front view, standing straight, neutral "
           "friendly expression, centered, on a solid pure green (#00FF00) background with no shadow and no "
           "gradient; the character must not wear or hold anything green.")
    return f"{dau} {PHONG_CACH_ANH[phong_cach]}. {mo_ta.strip()}. {CAM}"


def tu_the(ten: str, mo_ta: str, phong_cach: str) -> str:
    """Câu lệnh vẽ một tư thế của nhân vật, dựa trên ảnh mẫu tham chiếu (cùng khuôn mặt/tóc/trang phục/màu sắc).
    Giữ cùng khuôn với `nen`/`nhan_vat_mau` (câu phong cách + mô tả của thầy cô + câu cấm chữ) vì đây là chỗ nhất
    quán hình ảnh giữa các tư thế quan trọng nhất (spec Q10)."""
    dau = ("The same character as the reference image, same face, hair, clothes and colors; full body, "
           f"{TU_THE_EN[ten]}, on a solid pure green (#00FF00) background, no shadow; the character must not "
           "wear or hold anything green.")
    return f"{dau} {PHONG_CACH_ANH[phong_cach]}. {mo_ta.strip()}. {CAM}"
