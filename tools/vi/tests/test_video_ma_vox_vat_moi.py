"""Vox: vật nhiều mục (`cot`, `chu-trinh`, `moc`, `thap`), dấu xanh (`dau … | dung`), nhịp im (`giu` của cảnh) và
video ngắn từ 10 giây."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from video_ma_parts import lich, parse, thoi_luong, vox  # noqa: E402

DAU = "---\ntieu-de: T\nphong-cach: vox\nnen-canh: khong\ngiong: nu\n{them}---\n\n"


def mot_canh(nhip, bo_cuc="mot", loi="Doanh thu tăng đều qua ba năm.", them_canh="", them=""):
    return parse.parse(DAU.format(them=them) + f"## Cảnh 1\nbo-cuc: {bo_cuc}\nloi: {loi}\n{them_canh}nhip: {nhip}\n")


class VatNhieuMucTest(unittest.TestCase):
    def test_bar_chart_items_parse_label_value_and_unit(self):
        v = mot_canh("@dau | cot: 2022 = 12; 2023 = 30,5; 2024 = 45% | giua")
        n = v.canh[0].nhip[0]
        ds = vox.tach_danh_sach(n.vat, n.noi_dung)
        self.assertEqual(ds, [{"nhan": "2022", "giaTri": 12.0, "thapPhan": 0, "donVi": ""},
                              {"nhan": "2023", "giaTri": 30.5, "thapPhan": 1, "donVi": ""},
                              {"nhan": "2024", "giaTri": 45.0, "thapPhan": 0, "donVi": "%"}])

    def test_cycle_timeline_and_pyramid_parse(self):
        for nhip, ky_vong in (
            ("@dau | chu-trinh: Bốc hơi; Ngưng tụ; Mưa; Thấm xuống đất | giua", [{"nhan": "Bốc hơi"}, {"nhan": "Ngưng tụ"},
                                                                               {"nhan": "Mưa"}, {"nhan": "Thấm xuống đất"}]),
            ("@dau | moc: 1945: Độc lập; 1975: Thống nhất | giua", [{"moc": "1945", "nhan": "Độc lập"},
                                                                     {"moc": "1975", "nhan": "Thống nhất"}]),
            ("@dau | thap: Tự thể hiện; Tôn trọng; Xã hội; An toàn | giua", [{"nhan": "Tự thể hiện"}, {"nhan": "Tôn trọng"},
                                                                           {"nhan": "Xã hội"}, {"nhan": "An toàn"}]),
        ):
            with self.subTest(nhip=nhip):
                n = mot_canh(nhip).canh[0].nhip[0]
                self.assertEqual(vox.tach_danh_sach(n.vat, n.noi_dung), ky_vong)

    def test_item_count_and_lengths_are_bounded(self):
        for nhip, chu in (
            ("@dau | cot: Một = 1 | giua", "từ 2 đến 5 mục"),
            ("@dau | chu-trinh: A; B | giua", "từ 3 đến 6 mục"),
            ("@dau | cot: 2022 = 12; 2023 | giua", "`<nhãn> = <số><đơn vị>`"),
            ("@dau | cot: Năm hai nghìn hai mươi hai = 12; B = 3 | giua", "nhãn tối đa"),
            ("@dau | moc: 1945 Độc lập; 1975: Thống nhất | giua", "`<mốc>: <nhãn>`"),
            ("@dau | thap: A; B; Một tầng tháp có chữ quá dài so với ô | giua", "tối đa 24"),
            ("@dau | cot: A = -3; B = 4 | giua", "số âm"),
        ):
            with self.subTest(nhip=nhip), self.assertRaises(parse.ParseError) as c:
                mot_canh(nhip)
            self.assertIn(chu, str(c.exception))

    def test_page_data_carries_the_items(self):
        v = mot_canh("@dau | moc: 1945: Độc lập; 1975: Thống nhất | giua")
        d = vox._nhip_du_lieu(v.canh[0].nhip[0], "giua", 0.25)
        self.assertEqual(d["ds"], [{"moc": "1945", "nhan": "Độc lập"}, {"moc": "1975", "nhan": "Thống nhất"}])

    def test_list_objects_need_a_real_slot(self):
        with self.assertRaises(parse.ParseError) as c:
            mot_canh("@dau | thap: A; B; C", bo_cuc="chong")
        self.assertIn("không dùng `chong`", str(c.exception))


class DauXanhTest(unittest.TestCase):
    def test_green_stamp_option_is_for_stamps_only(self):
        n = mot_canh("@dau | dau: ĐÚNG | giua | dung").canh[0].nhip[0]
        self.assertEqual(n.tuy_chon, ("dung",))
        with self.assertRaises(parse.ParseError) as c:
            mot_canh("@dau | chu: Đúng rồi | giua | dung")
        self.assertIn("chỉ dùng cho `dau`", str(c.exception))


class NhipImTest(unittest.TestCase):
    def test_hold_lengthens_the_scene_and_the_estimate(self):
        co = mot_canh("@dau | chu: Ba năm | giua", them_canh="giu: 1,5\n")
        khong = mot_canh("@dau | chu: Ba năm | giua")
        self.assertEqual(co.canh[0].truong["giu"], ["1.5"])
        self.assertAlmostEqual(thoi_luong.uoc_tinh(co) - thoi_luong.uoc_tinh(khong), 1.5, places=6)
        giong = lich.GiongInfo(mp3=Path("x.mp3"), giay=3.0, moc_cau=[], uoc_luong=True, nguon="may", moc_tu=[],
                               uoc_luong_tu=True)
        a, _ = lich.dung_lich(co.canh, [giong])
        b, _ = lich.dung_lich(khong.canh, [giong])
        self.assertAlmostEqual(a[0].thoi_luong - b[0].thoi_luong, 1.5, delta=1 / lich.FPS)

    def test_hold_is_bounded(self):
        for gia_tri in ("0.2", "4", "lâu"):
            with self.subTest(gia_tri=gia_tri), self.assertRaises(parse.ParseError) as c:
                mot_canh("@dau | chu: Ba năm | giua", them_canh=f"giu: {gia_tri}\n")
            self.assertIn("`giu`", str(c.exception))


class VideoNganTest(unittest.TestCase):
    def test_ten_second_videos_are_allowed(self):
        self.assertEqual(vox.THOI_LUONG, (10, 600))
        self.assertEqual(mot_canh("@dau | chu: Ba năm | giua", them="thoi-luong: 10\n").meta["thoi-luong"], "10")
        with self.assertRaises(parse.ParseError) as c:
            mot_canh("@dau | chu: Ba năm | giua", them="thoi-luong: 9\n")
        self.assertIn("từ 10 đến 600", str(c.exception))


if __name__ == "__main__":
    unittest.main()
