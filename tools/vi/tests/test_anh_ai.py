"""Kế hoạch ảnh AI (`anh_ai.py ke-hoach`): thứ tự mục, câu cấm chữ, tham chiếu tư thế, ổn định, lỗi parse."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))

import anh_ai  # noqa: E402
from anh_ai_parts import cau_lenh  # noqa: E402
from video_ma_parts import parse  # noqa: E402

VIDEO_MD = """---
tieu-de: Vì sao giá tăng
mon: KTPL
lop: 11
nhan-vat: ve: cô giáo trẻ, áo dài xanh
---

## Cảnh 1
loai: ke-chuyen
tieu-de: Mở đầu câu chuyện
nen: ve: cánh đồng lúa chín buổi sáng
tu-the: chao
loi: Xin chào các em.

## Cảnh 2
loai: ke-chuyen
tieu-de: Nhắc lại khung cảnh
nen: nhu-canh 1
tu-the: giai-thich
loi: Chúng ta cùng xem lại.

## Cảnh 3
loai: ke-chuyen
tieu-de: Chuyển sang thành phố
nen: ve: khu chợ đông người buổi sáng
loi: Bây giờ ta sang cảnh khác.
"""


def viet_video_md(thu_muc: Path, text: str = VIDEO_MD) -> Path:
    thu_muc.mkdir(parents=True, exist_ok=True)
    (thu_muc / "video.md").write_text(text, encoding="utf-8")
    return thu_muc


class LapKeHoachTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.thu_muc = viet_video_md(Path(self.tmp.name) / "bai")

    def test_sau_muc_dung_thu_tu(self):
        warnings: list = []
        kq = anh_ai.chay_ke_hoach(self.thu_muc, warnings)
        self.assertEqual(kq["so_anh"], 6)
        ke_hoach = json.loads((self.thu_muc / "anh" / "ai" / "ke-hoach.json").read_text(encoding="utf-8"))
        muc = ke_hoach["muc"]
        self.assertEqual(len(muc), 6)
        self.assertEqual(
            [(m["loai"], m["file"]) for m in muc],
            [
                ("nhan-vat-mau", "nhan-vat-mau.png"),
                ("tu-the", "tu-the-dung.png"),
                ("tu-the", "tu-the-chao.png"),
                ("tu-the", "tu-the-giai-thich.png"),
                ("nen", "nen-1.png"),
                ("nen", "nen-3.png"),
            ],
        )
        # Cảnh 2 dùng lại nền của Cảnh 1 (`nhu-canh 1`): cùng mục nền-1, không tạo mục riêng.
        nen1 = next(m for m in muc if m["file"] == "nen-1.png")
        self.assertEqual(nen1["canh"], [1, 2])
        nen3 = next(m for m in muc if m["file"] == "nen-3.png")
        self.assertEqual(nen3["canh"], [3])

    def test_moi_prompt_chua_cau_cam(self):
        warnings: list = []
        anh_ai.chay_ke_hoach(self.thu_muc, warnings)
        ke_hoach = json.loads((self.thu_muc / "anh" / "ai" / "ke-hoach.json").read_text(encoding="utf-8"))
        for muc in ke_hoach["muc"]:
            self.assertIn(cau_lenh.CAM, muc["prompt"], muc)

    def test_muc_tu_the_co_tham_chieu(self):
        warnings: list = []
        anh_ai.chay_ke_hoach(self.thu_muc, warnings)
        ke_hoach = json.loads((self.thu_muc / "anh" / "ai" / "ke-hoach.json").read_text(encoding="utf-8"))
        for muc in ke_hoach["muc"]:
            if muc["loai"] == "tu-the":
                self.assertEqual(muc["tham_chieu"], "goc/nhan-vat-mau.png")
            else:
                self.assertIsNone(muc["tham_chieu"])

    def test_muc_tu_the_co_cau_phong_cach_va_mo_ta(self):
        # R9: câu lệnh tư thế cũng phải có câu phong cách và mô tả nhân vật (nguyên văn), không chỉ tư thế + câu cấm.
        warnings: list = []
        anh_ai.chay_ke_hoach(self.thu_muc, warnings)
        ke_hoach = json.loads((self.thu_muc / "anh" / "ai" / "ke-hoach.json").read_text(encoding="utf-8"))
        mo_ta = "cô giáo trẻ, áo dài xanh"
        for muc in ke_hoach["muc"]:
            if muc["loai"] != "tu-the":
                continue
            self.assertIn(cau_lenh.PHONG_CACH_ANH[ke_hoach["phong_cach"]], muc["prompt"], muc)
            self.assertIn(mo_ta, muc["prompt"], muc)
            self.assertIn("pure green (#00FF00) background", muc["prompt"], muc)
            self.assertIn(cau_lenh.CAM, muc["prompt"], muc)

    def test_chay_hai_lan_ra_cung_byte(self):
        warnings: list = []
        anh_ai.chay_ke_hoach(self.thu_muc, warnings)
        a = (self.thu_muc / "anh" / "ai" / "ke-hoach.json").read_bytes()
        warnings2: list = []
        anh_ai.chay_ke_hoach(self.thu_muc, warnings2)
        b = (self.thu_muc / "anh" / "ai" / "ke-hoach.json").read_bytes()
        self.assertEqual(a, b)

    def test_khong_co_anh_ve_thi_bao_khong_dung_anh_ai(self):
        thu_muc = viet_video_md(Path(self.tmp.name) / "khong-ai", "---\ntieu-de: Bài không AI\nmon: KTPL\nlop: 11\n---\n\n"
                                 "## Cảnh 1\nloai: khai-niem\nthuat-ngu: Lạm phát\ndinh-nghia: Mức giá chung tăng.\n"
                                 "loi: Xin chào các em.\n")
        warnings: list = []
        kq = anh_ai.chay_ke_hoach(thu_muc, warnings)
        self.assertEqual(kq["so_anh"], 0)
        self.assertIn(anh_ai.KHONG_AI, warnings)

    def test_video_md_loi_bao_step_parse(self):
        thu_muc = viet_video_md(Path(self.tmp.name) / "loi", "---\ntieu-de: Thiếu môn\nlop: 11\n---\n\n## Cảnh 1\n")
        with self.assertRaises(parse.ParseError):
            anh_ai.chay_ke_hoach(thu_muc, [])


class CliTest(unittest.TestCase):
    def test_video_md_loi_in_error_step_parse(self):
        with tempfile.TemporaryDirectory() as tmp:
            thu_muc = viet_video_md(Path(tmp) / "loi", "---\ntieu-de: Thiếu môn\nlop: 11\n---\n\n## Cảnh 1\n")
            proc = subprocess.run([sys.executable, str(TOOLS_VI / "anh_ai.py"), str(thu_muc), "ke-hoach"],
                                  capture_output=True, text=True, encoding="utf-8", timeout=60)
            out = json.loads(proc.stdout)
            self.assertFalse(out["ready"])
            self.assertEqual(out["error"]["step"], "parse")


if __name__ == "__main__":
    unittest.main()
