"""Bố cục `dung-canh` của Vox: cảnh giấy cắt nhiều lớp (hậu cảnh, vai phụ, vai chính, tiền cảnh, chữ)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from anh_vox_parts import ke_hoach  # noqa: E402
from video_ma_parts import parse, vox  # noqa: E402

DAU = "---\ntieu-de: T\nphong-cach: vox\ngiong: nu\n---\n\n## Cảnh 1\nbo-cuc: dung-canh\nloi: Vua ngồi trên ngai, các quan đứng chầu hai bên.\n"
DU = ("nhip: @dau | anh: ve: cung điện thời Lý nhìn chính diện | hau-canh\n"
      "nhip: @dau | anh: ve: nhà vua mặc áo bào vàng ngồi trên ngai | chinh\n"
      "nhip: các quan | anh: ve: hai vị quan áo đỏ đứng chắp tay | phu\n"
      "nhip: hai bên | anh: ve: cành đào nở hoa vươn ra từ góc | tien-canh\n"
      "nhip: @dau | nhan: Buổi chầu | tren\n")


def doc(nhip=DU):
    return parse.parse(DAU + nhip)


class DungCanhParseTest(unittest.TestCase):
    def test_a_full_layered_scene_parses(self):
        c = doc().canh[0]
        self.assertEqual([n.o for n in c.nhip], ["hau-canh", "chinh", "phu", "tien-canh", "tren"])

    def test_every_beat_names_its_slot_and_role(self):
        for nhip, chu in (
            ("nhip: @dau | anh: ve: nhà vua ngồi trên ngai\n", "cần ghi rõ ô"),
            ("nhip: @dau | anh: ve: nhà vua ngồi trên ngai | tren\n", "Ảnh của `dung-canh` đặt ở một vai"),
            ("nhip: @dau | anh: ve: nhà vua | chinh\nnhip: @dau | chu: Vua | chinh\n", "`tren` hoặc `giua`"),
            ("nhip: @dau | anh: ve: nhà vua | chinh\nnhip: các quan | anh: ve: vị quan | chinh\n", "chỉ có một ảnh"),
            ("nhip: @dau | anh: ve: nhà vua | chinh | khung\n", "không dùng `khung`"),
            ("nhip: @dau | chu: Buổi chầu | tren\n", "ít nhất ảnh `hau-canh` hoặc nhân vật `chinh`"),
        ):
            with self.subTest(nhip=nhip), self.assertRaises(parse.ParseError) as c:
                doc(nhip)
            self.assertIn(chu, str(c.exception))

    def test_layer_order_is_far_to_near(self):
        self.assertEqual(vox.VAI_DUNG_CANH, ("hau-canh", "phu-2", "phu", "chinh", "tien-canh"))


class DungCanhAnhTest(unittest.TestCase):
    def test_background_is_an_empty_stage_and_people_are_full_body_cutouts(self):
        ds = {m.chi_so: m for m in ke_hoach.lap(doc())}
        hau, chinh, phu, tien = ds[0], ds[1], ds[2], ds[3]
        self.assertEqual(hau.kieu, "phu")
        self.assertIn("Empty of people", hau.prompt)
        for m in (chinh, phu, tien):
            with self.subTest(o=m.chi_so):
                self.assertEqual(m.kieu, "cat")
                self.assertIn("full-body", m.prompt)
                self.assertIn("#00FF00", m.prompt)
        self.assertEqual((chinh.kich_thuoc, phu.kich_thuoc), ("1024x1536", "1024x1536"))
        self.assertEqual(tien.kich_thuoc, "1024x1024")
        # Cảnh đã có hậu cảnh phủ kín khung thì không vẽ nền AI riêng.
        self.assertFalse([m for m in ds.values() if m.kieu == "nen"])


if __name__ == "__main__":
    unittest.main()
