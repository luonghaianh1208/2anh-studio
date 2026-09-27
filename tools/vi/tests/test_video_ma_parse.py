"""Test bộ đọc và bộ kiểm giới hạn của video.md (không cần Chromium, FFmpeg, mạng)."""

import sys
import tempfile
import unicodedata
import unittest
from pathlib import Path

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))

from video_ma_parts import kiem, parse  # noqa: E402

MAU = TOOLS_VI / "fixtures" / "video-mau" / "video.md"
META = "tieu-de: T\nmon: Toán\nlop: 8\n"


def doc(canh: str, meta: str = META) -> str:
    return f"---\n{meta}---\n\n{canh}"


def line_of(text: str, needle: str) -> int:
    for number, line in enumerate(text.splitlines(), 1):
        if needle in line:
            return number
    raise AssertionError(needle)


class FixtureTest(unittest.TestCase):
    def test_sample_parses_all_eight_scene_types_in_order(self):
        video = parse.parse(MAU.read_text(encoding="utf-8"))
        self.assertEqual([c.loai for c in video.canh], list(parse.SCENE_TYPES[:8]))
        self.assertEqual([c.so for c in video.canh], list(range(1, 9)))
        self.assertEqual(video.meta["giong"], "nu")
        self.assertEqual(video.meta["toc-do"], "vua")
        self.assertEqual(video.meta["phu-de"], "karaoke")
        self.assertEqual(video.meta["phong-cach"], "viet-tay")

    def test_sample_passes_the_limits_without_warnings(self):
        video = parse.parse(MAU.read_text(encoding="utf-8"))
        self.assertEqual(kiem.kiem(video, Path(".")), [])

    def test_repeated_fields_keep_order_and_line_numbers(self):
        text = MAU.read_text(encoding="utf-8")
        video = parse.parse(text)
        y = video.canh[3]
        self.assertEqual(len(y.truong["y"]), 3)
        self.assertEqual(y.dong_truong["y"][0], line_of(text, "Chiều dài dây l: dây dài"))


class ParseErrorTest(unittest.TestCase):
    def assert_error(self, text: str, line: int, fragment: str):
        with self.assertRaises(parse.ParseError) as caught:
            parse.parse(text)
        self.assertEqual(caught.exception.line_no, line, str(caught.exception))
        self.assertIn(fragment, str(caught.exception))

    def test_missing_front_matter(self):
        self.assert_error("## Cảnh 1\nloai: tieu-de\n", 1, "---")

    def test_missing_required_meta_points_at_the_closing_line(self):
        self.assert_error("---\ntieu-de: T\nmon: Toán\n---\n", 4, "lop")

    def test_unknown_meta_key(self):
        text = doc("## Cảnh 1\n", META + "mau-nen: do\n")
        self.assert_error(text, 5, "mau-nen")

    def test_bad_meta_value(self):
        text = doc("## Cảnh 1\n", META + "giong: tre-em\n")
        self.assert_error(text, 5, "giong")

    def test_no_scene(self):
        self.assert_error(doc(""), 6, "Cảnh 1")

    def test_scene_numbers_must_be_sequential(self):
        text = doc("## Cảnh 2\nloai: tieu-de\nchu: A\nloi: Xin chào.\n")
        self.assert_error(text, 7, "Cảnh 1")

    def test_missing_loi(self):
        text = doc("## Cảnh 1\nloai: tieu-de\nchu: A\n")
        self.assert_error(text, 7, "loi")

    def test_unknown_scene_type(self):
        text = doc("## Cảnh 1\nloai: hoat-hinh\nloi: Xin chào.\n")
        self.assert_error(text, 8, "loai")

    def test_unknown_field_for_the_type(self):
        text = doc("## Cảnh 1\nloai: tieu-de\nchu: A\nbuoc: B\nloi: Xin chào.\n")
        self.assert_error(text, 10, "buoc")

    def test_duplicate_single_field(self):
        text = doc("## Cảnh 1\nloai: tieu-de\nchu: A\nchu: B\nloi: Xin chào.\n")
        self.assert_error(text, 10, "chu")

    def test_too_many_repeated_items(self):
        ys = "".join(f"y: ý {i}\n" for i in range(7))
        text = doc(f"## Cảnh 1\nloai: y-tung-y\ntieu-de: A\n{ys}loi: Xin chào.\n")
        self.assert_error(text, line_of(text, "ý 6"), "tối đa 6")

    def test_too_few_repeated_items(self):
        text = doc("## Cảnh 1\nloai: quy-trinh\ntieu-de: A\nbuoc: B\nloi: Xin chào.\n")
        self.assert_error(text, 7, "buoc")

    def test_point_needs_two_numbers_with_dot_decimals(self):
        text = doc("## Cảnh 1\nloai: do-thi\ntieu-de: A\ntruc-ngang: x\ntruc-doc: y\ndiem: 1;2\ndiem: 2, 3\nloi: Xin chào.\n")
        self.assert_error(text, line_of(text, "1;2"), "x, y")

    def test_parameter_line_needs_three_parts(self):
        text = doc("## Cảnh 1\nloai: thi-nghiem\nmau: li-con-lac-don\ntham-so: 0 chieu-dai\nloi: Xin chào.\n")
        self.assert_error(text, line_of(text, "tham-so"), "<giây> <mã> <giá trị>")

    def test_web_addresses_are_refused(self):
        text = doc("## Cảnh 1\nloai: tieu-de\nchu: xem https://a.vn\nloi: Xin chào.\n")
        self.assert_error(text, line_of(text, "https"), "địa chỉ web")

    def test_empty_value(self):
        text = doc("## Cảnh 1\nloai: tieu-de\nchu:\nloi: Xin chào.\n")
        self.assert_error(text, line_of(text, "chu:"), "trống")

    def test_line_that_is_not_a_field(self):
        text = doc("## Cảnh 1\nloai: tieu-de\nĐây là một dòng lạ\nloi: Xin chào.\n")
        self.assert_error(text, line_of(text, "dòng lạ"), "khoá: giá trị")


class LimitTest(unittest.TestCase):
    def video(self, canh: str):
        return parse.parse(doc(canh))

    def test_title_over_limit_names_scene_and_line(self):
        text = doc(f"## Cảnh 1\nloai: tieu-de\nchu: {'a' * 91}\nloi: Xin chào.\n")
        with self.assertRaises(kiem.CanhError) as caught:
            kiem.kiem(parse.parse(text), Path("."))
        self.assertEqual(caught.exception.so, 1)
        self.assertIn("91", str(caught.exception))
        self.assertIn(f"dòng {line_of(text, 'aaa')}", str(caught.exception))

    def test_markup_characters_are_not_counted(self):
        video = self.video(f"## Cảnh 1\nloai: tieu-de\nchu: **{'a' * 90}**\nloi: Xin chào.\n")
        self.assertEqual(kiem.kiem(video, Path(".")), [])
        self.assertEqual(kiem.hien_thi("H~2~SO~4~ m/s^2^"), len("H2SO4 m/s2"))

    def test_long_narration_is_a_warning_not_an_error(self):
        video = self.video(f"## Cảnh 1\nloai: tieu-de\nchu: A\nloi: {'Câu này dài. ' * 60}\n")
        warnings = kiem.kiem(video, Path("."))
        self.assertEqual(len(warnings), 1)
        self.assertIn("Cảnh 1", warnings[0])
        self.assertIn("700", warnings[0])


class LimitDocTest(unittest.TestCase):
    """Khổ dọc (`kho: doc`) dùng bảng giới hạn riêng kiem.LIMITS_DOC, không lớn hơn khổ ngang."""

    MAU = {
        ("tieu-de", "chu"): "loai: tieu-de\nchu: {}\n",
        ("khai-niem", "dinh-nghia"): "loai: khai-niem\nthuat-ngu: Chu kì\ndinh-nghia: {}\n",
        ("cau-hoi", "giai-thich"): ("loai: cau-hoi\ncau-hoi: Hỏi?\nlua-chon: A\nlua-chon: B\ndap-an: A\n"
                                    "giai-thich: {}\nloi-giai: Vì A.\n"),
        ("so-sanh", "y-trai"): "loai: so-sanh\ntieu-de: So sánh\ntrai: A\nphai: B\ny-trai: {}\ny-phai: b\n",
    }

    def test_bang_doc_cung_khoa_va_khong_lon_hon_ngang(self):
        self.assertEqual(set(kiem.LIMITS_DOC), set(kiem.LIMITS))
        for khoa, gioi_han in kiem.LIMITS_DOC.items():
            with self.subTest(khoa=khoa):
                self.assertLessEqual(gioi_han, kiem.LIMITS[khoa])
                self.assertGreater(gioi_han, 0)
        self.assertEqual(set(kiem.LIMITS_HAI_PHAN_DOC), set(kiem.LIMITS_HAI_PHAN))
        for khoa, (nhan, mo_ta) in kiem.LIMITS_HAI_PHAN_DOC.items():
            ngang = kiem.LIMITS_HAI_PHAN[khoa]
            self.assertLessEqual(nhan, ngang[0])
            # Phần sau là số (`du-lieu`): khổ ngang chỉ có parse.SO_DAI, khổ dọc có thể chặt hơn.
            self.assertLessEqual(mo_ta, parse.SO_DAI if ngang[1] is None else ngang[1])

    def test_vuot_gioi_han_doc_la_loi_neu_dung_dong_con_ngang_thi_qua(self):
        thu = 0
        for (loai, truong), mau in self.MAU.items():
            doc_max, ngang_max = kiem.LIMITS_DOC[(loai, truong)], kiem.LIMITS[(loai, truong)]
            if doc_max >= ngang_max:
                continue
            thu += 1
            canh = "## Cảnh 1\n" + mau.format("a" * (doc_max + 1)) + "loi: Xin chào.\n"
            with self.subTest(loai=loai, truong=truong):
                text = doc(canh, META + "kho: doc\n")
                with self.assertRaises(kiem.CanhError) as caught:
                    kiem.kiem(parse.parse(text), Path("."))
                loi = str(caught.exception)
                self.assertIn(f"dòng {line_of(text, 'a' * (doc_max + 1))}", loi)
                self.assertIn(f"tối đa {doc_max}", loi)
                self.assertIn("giới hạn khổ dọc", loi)
                self.assertEqual(kiem.kiem(parse.parse(doc(canh)), Path(".")), [])
                ok = "## Cảnh 1\n" + mau.format("a" * doc_max) + "loi: Xin chào.\n"
                self.assertEqual(kiem.kiem(parse.parse(doc(ok, META + "kho: doc\n")), Path(".")), [])
        self.assertGreater(thu, 0, "cần ít nhất một trường có giới hạn dọc nhỏ hơn ngang")

    def test_so_du_lieu_bieu_do_theo_gioi_han_doc(self):
        so_max = kiem.LIMITS_HAI_PHAN_DOC[("bieu-do", "du-lieu")][1]
        self.assertLess(so_max, parse.SO_DAI)
        so = "1" * (so_max + 1)
        canh = f"## Cảnh 1\nloai: bieu-do\ntieu-de: Số\nkieu: cot\ndu-lieu: A | {so}\ndu-lieu: B | 2\nloi: Xin chào.\n"
        text = doc(canh, META + "kho: doc\n")
        with self.assertRaises(kiem.CanhError) as caught:
            kiem.kiem(parse.parse(text), Path("."))
        self.assertIn("giới hạn khổ dọc", str(caught.exception))
        self.assertIn(f"dòng {line_of(text, so)}", str(caught.exception))
        self.assertEqual(kiem.kiem(parse.parse(doc(canh)), Path(".")), [])
        ok = canh.replace(so, "1" * so_max)
        self.assertEqual(kiem.kiem(parse.parse(doc(ok, META + "kho: doc\n")), Path(".")), [])


class ExperimentSceneTest(unittest.TestCase):
    def check(self, extra: str):
        text = doc(f"## Cảnh 1\nloai: thi-nghiem\nmau: li-con-lac-don\n{extra}loi: Xin chào.\n")
        return text, lambda: kiem.kiem(parse.parse(text), Path("."))

    def test_new_model_is_not_allowed_in_video(self):
        text = doc("## Cảnh 1\nloai: thi-nghiem\nmau: moi\nloi: Xin chào.\n")
        with self.assertRaises(kiem.CanhError) as caught:
            kiem.kiem(parse.parse(text), Path("."))
        self.assertIn("thư viện", str(caught.exception))

    def test_unknown_model_lists_the_library(self):
        for mau in ("li-khong-co", "../../x"):
            with self.subTest(mau=mau):
                text = doc(f"## Cảnh 1\nloai: thi-nghiem\nmau: {mau}\nloi: Xin chào.\n")
                with self.assertRaises(kiem.CanhError) as caught:
                    kiem.kiem(parse.parse(text), Path("."))
                self.assertIn("li-con-lac-don", str(caught.exception))
                self.assertNotIn("moi", str(caught.exception))

    def test_unknown_parameter(self):
        _, run = self.check("tham-so: 0 toc-do 3\n")
        with self.assertRaises(kiem.CanhError) as caught:
            run()
        self.assertIn("toc-do", str(caught.exception))

    def test_value_outside_the_allowed_range_names_the_line(self):
        text, run = self.check("tham-so: 0 chieu-dai 5\n")
        with self.assertRaises(parse.ParseError) as caught:
            run()
        self.assertEqual(caught.exception.line_no, line_of(text, "tham-so"))
        self.assertIn("0.2", str(caught.exception))

    def test_more_than_three_parameters(self):
        _, run = self.check("tham-so: 0 chieu-dai 1\ntham-so: 0 g 9.8\ntham-so: 0 goc-lech 8\ntham-so: 0 khoi-luong 0.2\n")
        with self.assertRaises(kiem.CanhError):
            run()

    def test_unknown_measured_quantity(self):
        _, run = self.check("do: van-toc\n")
        with self.assertRaises(kiem.CanhError) as caught:
            run()
        self.assertIn("chu-ki", str(caught.exception))

    def test_schedule_is_sorted_and_default_measures_are_the_first_two(self):
        from thi_nghiem_parts import thu_vien

        text = doc("## Cảnh 1\nloai: thi-nghiem\nmau: li-con-lac-don\ntham-so: 6 chieu-dai 1.6\ntham-so: 0 chieu-dai 0.4\nloi: Xin chào.\n")
        scene = parse.parse(text).canh[0]
        self.assertEqual(kiem.tham_so_theo_thoi_gian(scene), {"chieu-dai": [(0.0, 0.4), (6.0, 1.6)]})
        model = thu_vien.load("li-con-lac-don", Path("."))
        self.assertEqual(kiem.ma_do(scene, model), ["chu-ki", "thoi-gian-10-dao-dong"])


class NewFieldsTest(unittest.TestCase):
    def test_meta_choices_have_new_keys_with_defaults(self):
        for key, choices, default in (
            ("ban-tay", ("co", "khong"), "co"),
            ("may-quay", ("co", "khong"), "co"),
            ("chuyen-canh", ("lau-bang", "lat-trang", "truot", "phong", "mo-man", "luan-phien", "khong"), "lau-bang"),
            ("kho", ("ngang", "doc"), "ngang"),
            ("do-phan-giai", ("1080", "720"), "1080"),
        ):
            self.assertEqual(parse.META_CHOICES[key], choices)
            self.assertEqual(parse.META_DEFAULTS[key], default)

    def test_kho_va_do_phan_giai(self):
        video = parse.parse(doc("## Cảnh 1\nloai: tieu-de\nchu: A\nloi: Xin chào.\n", META + "kho: doc\ndo-phan-giai: 720\n"))
        self.assertEqual((video.meta["kho"], video.meta["do-phan-giai"]), ("doc", "720"))
        video = parse.parse(doc("## Cảnh 1\nloai: tieu-de\nchu: A\nloi: Xin chào.\n"))
        self.assertEqual((video.meta["kho"], video.meta["do-phan-giai"]), ("ngang", "1080"))
        for dong, khoa in (("kho: vuong\n", "kho"), ("do-phan-giai: 4k\n", "do-phan-giai")):
            with self.subTest(dong=dong), self.assertRaises(parse.ParseError) as bat:
                parse.parse(doc("## Cảnh 1\nloai: tieu-de\nchu: A\nloi: Xin chào.\n", META + "giong: nu\n" + dong))
            self.assertEqual(bat.exception.line_no, 6)
            self.assertIn(f"`{khoa}`", str(bat.exception))

    def test_new_meta_keys_default_when_video_omits_them(self):
        video = parse.parse(doc("## Cảnh 1\nloai: tieu-de\nchu: A\nloi: Xin chào.\n"))
        self.assertEqual(video.meta["ban-tay"], "co")
        self.assertEqual(video.meta["may-quay"], "co")
        self.assertEqual(video.meta["chuyen-canh"], "lau-bang")

    def test_new_scene_types_are_registered(self):
        self.assertIn("minh-hoa", parse.SCENE_SPEC)
        self.assertIn("anh", parse.SCENE_SPEC)
        self.assertEqual(parse.SCENE_SPEC["minh-hoa"], (("tieu-de",), (), {"hinh": (1, 3)}))
        self.assertEqual(parse.SCENE_SPEC["anh"], (("anh", "chu-thich"), ("nguon",), {}))

    def test_hinh_and_anh_are_optional_fields_of_the_four_text_scenes(self):
        for loai in ("tieu-de", "khai-niem", "cong-thuc", "y-tung-y"):
            _, optional, _ = parse.SCENE_SPEC[loai]
            self.assertIn("hinh", optional, loai)
            self.assertIn("anh", optional, loai)

    def test_scene_with_both_hinh_and_anh_is_a_parse_error_at_the_second_line(self):
        text = doc("## Cảnh 1\nloai: tieu-de\nchu: A\nhinh: flask\nanh: x.png\nloi: Xin chào.\n")
        with self.assertRaises(parse.ParseError) as caught:
            parse.parse(text)
        self.assertEqual(caught.exception.line_no, line_of(text, "anh: x.png"))

    def test_scene_with_anh_then_hinh_points_at_the_hinh_line(self):
        text = doc("## Cảnh 1\nloai: tieu-de\nchu: A\nanh: x.png\nhinh: flask\nloi: Xin chào.\n")
        with self.assertRaises(parse.ParseError) as caught:
            parse.parse(text)
        self.assertEqual(caught.exception.line_no, line_of(text, "hinh: flask"))

    def test_minh_hoa_needs_at_least_one_picture(self):
        text = doc("## Cảnh 1\nloai: minh-hoa\ntieu-de: A\nloi: Xin chào.\n")
        with self.assertRaises(parse.ParseError):
            parse.parse(text)

    def test_minh_hoa_allows_at_most_three_pictures(self):
        hinhs = "".join(f"hinh: clock | Nhãn {i}\n" for i in range(4))
        text = doc(f"## Cảnh 1\nloai: minh-hoa\ntieu-de: A\n{hinhs}loi: Xin chào.\n")
        with self.assertRaises(parse.ParseError):
            parse.parse(text)


CANH_1 = "## Cảnh 1\nloai: tieu-de\nchu: A\nloi: Xin chào.\n\n"


class TransitionFieldTest(unittest.TestCase):
    def loi(self, text: str, needle: str, fragment: str):
        with self.assertRaises(parse.ParseError) as caught:
            parse.parse(text)
        self.assertEqual(caught.exception.line_no, line_of(text, needle))
        self.assertIn(fragment, caught.exception.message)

    def test_every_new_meta_value_parses(self):
        for kieu in ("lat-trang", "truot", "phong", "mo-man", "luan-phien"):
            with self.subTest(kieu=kieu):
                video = parse.parse(doc(CANH_1, META + f"chuyen-canh: {kieu}\n"))
                self.assertEqual(video.meta["chuyen-canh"], kieu)

    def test_chuyen_field_is_allowed_on_every_scene_type_after_the_first(self):
        mau = parse.parse(MAU.read_text(encoding="utf-8"))
        self.assertTrue(all(c.so == 1 or "chuyen" not in c.truong for c in mau.canh))
        self.assertEqual(parse.SCENE_KIEU_CHUYEN, ("lau-bang", "lat-trang", "truot", "phong", "mo-man", "khong"))
        toi_thieu = {
            "tieu-de": "chu: B\n",
            "khai-niem": "thuat-ngu: B\ndinh-nghia: C\n",
            "cong-thuc": "bieu-thuc: v = s/t\n",
            "y-tung-y": "tieu-de: B\ny: C\n",
            "quy-trinh": "tieu-de: B\nbuoc: C\nbuoc: D\n",
            "so-sanh": "tieu-de: B\ntrai: C\nphai: D\ny-trai: E\ny-phai: F\n",
            "do-thi": "tieu-de: B\ntruc-ngang: t\ntruc-doc: v\ndiem: 0, 0\ndiem: 1, 2\n",
            "thi-nghiem": "mau: li-con-lac-don\n",
            "minh-hoa": "tieu-de: B\nhinh: clock | Đồng hồ\n",
            "anh": "anh: a.png\nchu-thich: C\n",
        }
        for loai, truong in toi_thieu.items():
            with self.subTest(loai=loai):
                video = parse.parse(doc(CANH_1 + f"## Cảnh 2\nloai: {loai}\n{truong}chuyen: phong\nloi: Ok.\n"))
                self.assertEqual(video.canh[1].truong["chuyen"], ["phong"])

    def test_bad_value_points_at_the_line(self):
        text = doc(CANH_1 + "## Cảnh 2\nloai: tieu-de\nchu: B\nchuyen: xoay-tron\nloi: Ok.\n")
        self.loi(text, "chuyen: xoay-tron", "lat-trang")

    def test_luan_phien_is_only_a_meta_value(self):
        text = doc(CANH_1 + "## Cảnh 2\nloai: tieu-de\nchu: B\nchuyen: luan-phien\nloi: Ok.\n")
        self.loi(text, "chuyen: luan-phien", "chuyen-canh: luan-phien")

    def test_repeated_field_points_at_the_second_line(self):
        text = doc(CANH_1 + "## Cảnh 2\nloai: tieu-de\nchu: B\nchuyen: truot\nchuyen: phong\nloi: Ok.\n")
        self.loi(text, "chuyen: phong", "bị lặp")

    def test_first_scene_has_no_previous_scene_to_leave(self):
        text = doc("## Cảnh 1\nloai: tieu-de\nchu: A\nchuyen: truot\nloi: Xin chào.\n")
        self.loi(text, "chuyen: truot", "Cảnh 1")


class NhanTest(unittest.TestCase):
    def kiem_loi(self, canh: str, needle: str):
        text = doc(canh)
        with self.assertRaises(parse.ParseError) as caught:
            kiem.kiem(parse.parse(text), Path("."))
        self.assertEqual(caught.exception.line_no, line_of(text, needle))
        return caught.exception

    def test_chu_dong_is_a_meta_choice_defaulting_to_co(self):
        self.assertEqual(parse.META_CHOICES["chu-dong"], ("co", "khong"))
        self.assertEqual(parse.META_DEFAULTS["chu-dong"], "co")
        video = parse.parse(doc("## Cảnh 1\nloai: tieu-de\nchu: A\nloi: Xin chào.\n"))
        self.assertEqual(video.meta["chu-dong"], "co")
        video = parse.parse(doc("## Cảnh 1\nloai: tieu-de\nchu: A\nloi: Xin chào.\n", META + "chu-dong: khong\n"))
        self.assertEqual(video.meta["chu-dong"], "khong")

    def test_du_lieu_canh_carries_chu_dong(self):
        from video_ma_parts import lich

        for gia_tri, mong in (("co", True), ("khong", False)):
            video = parse.parse(doc("## Cảnh 1\nloai: tieu-de\nchu: A\nloi: Xin chào.\n", META + f"chu-dong: {gia_tri}\n"))
            giong = lich.GiongInfo(mp3=None, giay=3.0, moc_cau=[0.0], uoc_luong=False, nguon="may")
            plan, _ = lich.dung_lich(video.canh, [giong])
            du = lich.du_lieu_canh(video.canh[0], plan[0], None, {"meta": video.meta})
            self.assertIs(du["co"]["chuDong"], mong)

    def test_valid_emphasis_and_numbers_pass(self):
        text = doc("## Cảnh 1\nloai: y-tung-y\ntieu-de: ==Ba== ((bước)) __nhỏ__\n"
                   "y: Tăng {{1500.5}} lần và {{-2}} độ\ny: f(g(x)) vẫn là chữ thường\nloi: Xin chào.\n")
        self.assertEqual(kiem.kiem(parse.parse(text), Path(".")), [])

    def test_nested_emphasis_is_an_error_at_its_line(self):
        err = self.kiem_loi("## Cảnh 1\nloai: y-tung-y\ntieu-de: A\ny: ==chu ((kì)) này==\nloi: Xin chào.\n", "y: ==chu")
        self.assertIn("lồng", err.message)

    def test_unclosed_emphasis_is_an_error_at_its_line(self):
        for mo in ("==chu kì", "((chu kì", "__chu kì"):
            with self.subTest(mo=mo):
                err = self.kiem_loi(f"## Cảnh 1\nloai: y-tung-y\ntieu-de: A\ny: Một {mo} này\nloi: Xin chào.\n", "y: Một")
                self.assertIn("đóng", err.message)

    def test_more_than_three_emphasis_groups_in_a_field_is_an_error(self):
        self.kiem_loi("## Cảnh 1\nloai: khai-niem\nthuat-ngu: A\n"
                      "dinh-nghia: ==a== ((b)) __c__ ==d==\nloi: Xin chào.\n", "dinh-nghia:")

    def test_number_must_use_a_decimal_point(self):
        for sai in ("{{1,5}}", "{{mười}}", "{{}}", "{{3"):
            with self.subTest(sai=sai):
                err = self.kiem_loi(f"## Cảnh 1\nloai: y-tung-y\ntieu-de: A\ny: Được {sai} lần\nloi: Xin chào.\n", "y: Được")
                self.assertIn("{{", err.message)

    def test_cluster_with_unbalanced_parentheses_is_an_error(self):
        err = self.kiem_loi("## Cảnh 1\nloai: y-tung-y\ntieu-de: A\ny: Hàm ((f(x))) tăng\nloi: Xin chào.\n", "y: Hàm")
        self.assertIn("ngoặc", err.message)

    def test_emphasis_crossing_bold_or_sub_is_an_error(self):
        for sai in ("**a ==b** c==", "==a **b== c**", "==H~2== O~"):
            with self.subTest(sai=sai):
                err = self.kiem_loi(f"## Cảnh 1\nloai: y-tung-y\ntieu-de: A\ny: Ý {sai}\nloi: Xin chào.\n", "y: Ý")
                self.assertIn("cắt ngang", err.message)

    def test_formula_keeps_double_parentheses_and_underscores_literal(self):
        text = doc("## Cảnh 1\nloai: cong-thuc\nbieu-thuc: y = ((a+b))__c + f((x)) == {{2}}\n"
                   "giai-thich: ((a)) là hệ số\nloi: Xin chào.\n")
        self.assertEqual(kiem.kiem(parse.parse(text), Path(".")), [])
        self.assertEqual(kiem.hien_thi("y = ((a+b))__c", cum=False), len("y = ((a+b))__c"))
        self.kiem_loi("## Cảnh 1\nloai: cong-thuc\nbieu-thuc: y = {{1,5}}\nloi: Xin chào.\n", "bieu-thuc:")

    def test_fill_in_blank_and_spaced_equals_are_literal(self):
        text = doc("## Cảnh 1\nloai: y-tung-y\ntieu-de: Điền ____ vào chỗ trống\ny: a == b và ___ nhé\n"
                   "y: ==x== và __y__\nloi: Xin chào.\n")
        self.assertEqual(kiem.kiem(parse.parse(text), Path(".")), [])
        self.assertEqual(kiem.hien_thi("Điền ____ vào"), len("Điền ____ vào"))
        self.kiem_loi("## Cảnh 1\nloai: y-tung-y\ntieu-de: A\ny: a ==b và c\nloi: Xin chào.\n", "y: a ==b")

    def test_length_limit_counts_only_visible_text(self):
        chu = "==" + "a" * 60 + "== {{1500}}"
        text = doc(f"## Cảnh 1\nloai: y-tung-y\ntieu-de: A\ny: {'a' * 55} {{{{12}}}}\nloi: Xin chào.\n")
        self.assertEqual(kiem.kiem(parse.parse(text), Path(".")), [])
        self.assertEqual(kiem.hien_thi(chu), 60 + 1 + 4)
        self.assertEqual(kiem.hien_thi("((ab)) __c__ **d** H~2~"), len("ab c d H2"))


def bieu_do(kieu: str, du_lieu, them: str = "") -> str:
    dong = "".join(f"du-lieu: {d}\n" for d in du_lieu)
    return f"## Cảnh 1\nloai: bieu-do\ntieu-de: Sản lượng\nkieu: {kieu}\n{them}{dong}loi: Xin chào.\n"


class ChartMapTimelineTest(unittest.TestCase):
    """Biểu đồ, sơ đồ tư duy, dòng thời gian và công thức từng phần (Q3, Q4, Q12, spec §5)."""

    def parse_loi(self, canh: str, needle: str, fragment: str = ""):
        text = doc(canh)
        with self.assertRaises(parse.ParseError) as caught:
            kiem.kiem(parse.parse(text), Path("."))
        self.assertEqual(caught.exception.line_no, line_of(text, needle), str(caught.exception))
        self.assertIn(fragment, str(caught.exception))
        return caught.exception

    def canh_loi(self, canh: str, needle: str, fragment: str = ""):
        text = doc(canh)
        with self.assertRaises(kiem.CanhError) as caught:
            kiem.kiem(parse.parse(text), Path("."))
        self.assertIn(f"dòng {line_of(text, needle)}", str(caught.exception))
        self.assertIn(fragment, str(caught.exception))

    def dung(self, canh: str):
        video = parse.parse(doc(canh))
        self.assertEqual(kiem.kiem(video, Path(".")), [])
        return video.canh[0]

    def test_new_scene_types_are_registered(self):
        self.assertEqual(parse.SCENE_SPEC["bieu-do"],
                         (("tieu-de", "kieu"), ("don-vi", "truc-ngang", "truc-doc"), {"du-lieu": (2, 8)}))
        self.assertEqual(parse.SCENE_SPEC["so-do"], (("trung-tam",), ("hinh",), {"nhanh": (2, 6)}))
        self.assertEqual(parse.SCENE_SPEC["dong-thoi-gian"], (("tieu-de",), (), {"moc": (2, 6)}))
        self.assertEqual(parse.BIEU_DO_KIEU, ("cot", "duong", "tron"))

    def test_valid_charts_pass_including_negative_zero_and_huge_values(self):
        for kieu, du_lieu, them in (
            ("cot", ["Lúa | 12.5", "Ngô | -40", "Khoai | 0", "Đậu | 100000"],
             "don-vi: tấn\ntruc-ngang: Cây trồng\ntruc-doc: Sản lượng\n"),
            ("duong", ["T1 | 0.3", "T2 | 7.2", "T3 | -1"], ""),
            ("tron", ["A | 1", "B | 100000", "C | 0.5"], ""),
        ):
            with self.subTest(kieu=kieu):
                scene = self.dung(bieu_do(kieu, du_lieu, them))
                self.assertEqual(scene.truong["du-lieu"], du_lieu)

    def test_chart_kind_must_be_one_of_three(self):
        self.parse_loi(bieu_do("cot-chong", ["A | 1", "B | 2"]), "kieu:", "cot, duong, tron")

    def test_data_line_needs_a_label_a_bar_and_a_dot_decimal_number(self):
        for sai in ("Lúa 12", "Lúa | 1,5", "Lúa | mười", " | 3", "Lúa | 1e5", "Lúa | 12 tấn"):
            with self.subTest(sai=sai):
                self.parse_loi(bieu_do("cot", ["A | 1", sai]), f"du-lieu: {sai}", "<nhãn> | <số>")

    def test_number_longer_than_ten_characters_is_refused(self):
        self.dung(bieu_do("cot", ["A | 1", "B | -123456.78"]))
        self.parse_loi(bieu_do("cot", ["A | 1", "B | 12345678901"]), "B | 1234", "10 ký tự")

    def test_pie_refuses_zero_and_negative_values_at_their_line(self):
        for sai in ("0", "-3", "0.0"):
            with self.subTest(sai=sai):
                self.parse_loi(bieu_do("tron", ["A | 1", f"B | {sai}", "C | 2"]), f"B | {sai}", "số dương")

    def test_pie_has_no_axes_or_unit(self):
        for truong in ("truc-ngang: x\n", "truc-doc: y\n", "don-vi: kg\n"):
            with self.subTest(truong=truong):
                self.parse_loi(bieu_do("tron", ["A | 1", "B | 2"], truong), truong.strip(), "tron")

    def test_data_line_count_outside_two_to_eight(self):
        with self.assertRaises(parse.ParseError) as caught:
            parse.parse(doc(bieu_do("cot", ["A | 1"])))
        self.assertIn("ít nhất 2", str(caught.exception))
        text = doc(bieu_do("cot", [f"Mục {k} | {k}" for k in range(9)]))
        with self.assertRaises(parse.ParseError) as caught:
            parse.parse(text)
        self.assertEqual(caught.exception.line_no, line_of(text, "Mục 8 |"))

    def test_chart_text_limits(self):
        self.dung(bieu_do("cot", ["A" * 16 + " | 1", "B | 2"], "don-vi: " + "đ" * 12 + "\n"
                          + "truc-ngang: " + "x" * 40 + "\ntruc-doc: " + "y" * 40 + "\n"))
        self.canh_loi(bieu_do("cot", ["A" * 17 + " | 1", "B | 2"]), "AAAA", "tối đa 16")
        self.canh_loi(bieu_do("cot", ["A | 1", "B | 2"], "don-vi: " + "đ" * 13 + "\n"), "don-vi", "tối đa 12")
        self.canh_loi(bieu_do("cot", ["A | 1", "B | 2"], "truc-doc: " + "y" * 41 + "\n"), "truc-doc", "tối đa 40")
        self.parse_loi(bieu_do("cot", ["==A | 1", "B | 2"]), "==A", "đóng")

    def test_mind_map_fields_and_limits(self):
        nhanh = "".join(f"nhanh: {'n' * 40}\n" for _ in range(6))
        self.dung(f"## Cảnh 1\nloai: so-do\ntrung-tam: {'t' * 30}\nhinh: flask\n{nhanh}loi: Xin chào.\n")
        self.canh_loi(f"## Cảnh 1\nloai: so-do\ntrung-tam: {'t' * 31}\nnhanh: a\nnhanh: b\nloi: Xin chào.\n",
                      "trung-tam", "tối đa 30")
        self.canh_loi(f"## Cảnh 1\nloai: so-do\ntrung-tam: T\nnhanh: a\nnhanh: {'n' * 41}\nloi: Xin chào.\n",
                      "nnnn", "tối đa 40")
        with self.assertRaises(parse.ParseError):
            parse.parse(doc("## Cảnh 1\nloai: so-do\ntrung-tam: T\nnhanh: a\nloi: Xin chào.\n"))
        text = doc("## Cảnh 1\nloai: so-do\ntrung-tam: T\n" + "".join(f"nhanh: n{k}\n" for k in range(7)) + "loi: Xin chào.\n")
        with self.assertRaises(parse.ParseError) as caught:
            parse.parse(text)
        self.assertEqual(caught.exception.line_no, line_of(text, "nhanh: n6"))

    def test_timeline_fields_and_limits(self):
        moc = "".join(f"moc: {'N' * 12} | {'m' * 60}\n" for _ in range(6))
        scene = self.dung(f"## Cảnh 1\nloai: dong-thoi-gian\ntieu-de: Lịch sử\n{moc}loi: Xin chào.\n")
        self.assertEqual(len(scene.truong["moc"]), 6)
        self.canh_loi("## Cảnh 1\nloai: dong-thoi-gian\ntieu-de: A\nmoc: " + "N" * 13 + " | mô tả\nmoc: 1945 | b\nloi: Xin chào.\n",
                      "NNNN", "tối đa 12")
        self.canh_loi("## Cảnh 1\nloai: dong-thoi-gian\ntieu-de: A\nmoc: 1930 | " + "m" * 61 + "\nmoc: 1945 | b\nloi: Xin chào.\n",
                      "mmmm", "tối đa 60")
        self.parse_loi("## Cảnh 1\nloai: dong-thoi-gian\ntieu-de: A\nmoc: 1930 thành lập\nmoc: 1945 | b\nloi: Xin chào.\n",
                       "1930 thành lập", "<nhãn> | <mô tả>")
        with self.assertRaises(parse.ParseError):
            parse.parse(doc("## Cảnh 1\nloai: dong-thoi-gian\ntieu-de: A\nmoc: 1930 | a\nloi: Xin chào.\n"))
        text = doc("## Cảnh 1\nloai: dong-thoi-gian\ntieu-de: A\n" + "".join(f"moc: {k} | m{k}\n" for k in range(7))
                   + "loi: Xin chào.\n")
        with self.assertRaises(parse.ParseError) as caught:
            parse.parse(text)
        self.assertEqual(caught.exception.line_no, line_of(text, "moc: 6 |"))

    def test_formula_parts_split_on_spaced_bar(self):
        self.dung("## Cảnh 1\nloai: cong-thuc\nbieu-thuc: T = 2π√(l/g) | = 2π√(1/9.8) | ≈ {{2.0}} s\nloi: Xin chào.\n")
        self.dung("## Cảnh 1\nloai: cong-thuc\nbieu-thuc: |x| = 2 khi x = ±2\nloi: Xin chào.\n")
        # Giới hạn 90 ký tự tính mỗi dấu ` | ` là một khoảng trắng.
        self.dung("## Cảnh 1\nloai: cong-thuc\nbieu-thuc: " + "a" * 44 + " | " + "b" * 45 + "\nloi: Xin chào.\n")
        self.canh_loi("## Cảnh 1\nloai: cong-thuc\nbieu-thuc: " + "a" * 45 + " | " + "b" * 45 + "\nloi: Xin chào.\n",
                      "bieu-thuc", "tối đa 90")

    def test_formula_parts_errors_point_at_the_line(self):
        self.parse_loi("## Cảnh 1\nloai: cong-thuc\nbieu-thuc: a | b | c | d | e\nloi: Xin chào.\n", "bieu-thuc", "tối đa 4")
        self.parse_loi("## Cảnh 1\nloai: cong-thuc\nbieu-thuc: a |  | c\nloi: Xin chào.\n", "bieu-thuc", "trống")
        self.parse_loi("## Cảnh 1\nloai: cong-thuc\nbieu-thuc: **a | b**\nloi: Xin chào.\n", "bieu-thuc", "` | `")


def cau_hoi(lua_chon=("Tăng", "Giảm", "Không đổi"), them: str = "dap-an: B\n", bo: str = "") -> str:
    dong = {
        "cau-hoi": "cau-hoi: Chu kì thay đổi thế nào khi dây dài gấp bốn?\n",
        "lua-chon": "".join(f"lua-chon: {c}\n" for c in lua_chon),
        "giai-thich": "giai-thich: T tỉ lệ với căn bậc hai của l.\n",
        "loi-giai": "loi-giai: Đáp án B. Chu kì tăng gấp đôi.\n",
    }
    return ("## Cảnh 1\nloai: cau-hoi\n" + "".join(v for k, v in dong.items() if k != bo) + them
            + "loi: Chu kì thay đổi thế nào? A, tăng. B, giảm. C, không đổi.\n")


class QuizParseTest(unittest.TestCase):
    """Cảnh câu hỏi nhanh (Q8, spec §5)."""

    def loi(self, canh: str, needle: str, fragment: str = "", loai=parse.ParseError):
        text = doc(canh)
        with self.assertRaises(loai) as caught:
            kiem.kiem(parse.parse(text), Path("."))
        if loai is parse.ParseError:
            self.assertEqual(caught.exception.line_no, line_of(text, needle), str(caught.exception))
        else:
            self.assertIn(f"dòng {line_of(text, needle)}", str(caught.exception))
        self.assertIn(fragment, str(caught.exception))

    def test_quiz_scene_is_registered(self):
        self.assertEqual(parse.SCENE_SPEC["cau-hoi"],
                         (("cau-hoi", "dap-an", "giai-thich", "loi-giai"), ("cho",), {"lua-chon": (2, 4)}))

    def test_valid_quiz_parses_with_default_wait_and_normalised_answer(self):
        video = parse.parse(doc(cau_hoi(them="dap-an: b\n")))
        self.assertEqual(kiem.kiem(video, Path(".")), [])
        scene = video.canh[0]
        self.assertEqual(scene.truong["dap-an"], ["B"])
        self.assertEqual(scene.truong["cho"], ["5"])
        self.assertEqual(scene.truong["loi-giai"], ["Đáp án B. Chu kì tăng gấp đôi."])
        self.assertEqual(scene.loi, "Chu kì thay đổi thế nào? A, tăng. B, giảm. C, không đổi.")
        video = parse.parse(doc(cau_hoi(("a", "b", "c", "d"), them="dap-an: D\ncho: 10\n")))
        self.assertEqual(video.canh[0].truong["cho"], ["10"])

    def test_missing_answer_narration_is_a_parse_error(self):
        text = doc(cau_hoi(bo="loi-giai"))
        with self.assertRaises(parse.ParseError) as caught:
            parse.parse(text)
        self.assertIn("loi-giai", str(caught.exception))
        self.assertEqual(caught.exception.line_no, line_of(text, "## Cảnh 1"))

    def test_answer_letter_must_be_one_of_the_choices(self):
        self.loi(cau_hoi(them="dap-an: E\n"), "dap-an: E", "A, B, C")
        self.loi(cau_hoi(them="dap-an: D\n"), "dap-an: D", "A, B, C")
        self.loi(cau_hoi(("Có", "Không"), them="dap-an: C\n"), "dap-an: C", "A, B")
        self.loi(cau_hoi(them="dap-an: AB\n"), "dap-an: AB", "một chữ cái")

    def test_wait_must_be_whole_seconds_from_three_to_ten(self):
        for sai in ("12", "2", "0", "4.5", "năm"):
            with self.subTest(sai=sai):
                self.loi(cau_hoi(them=f"dap-an: B\ncho: {sai}\n"), f"cho: {sai}", "3 đến 10")

    def test_two_to_four_choices(self):
        with self.assertRaises(parse.ParseError) as caught:
            parse.parse(doc(cau_hoi(("Một",), them="dap-an: A\n")))
        self.assertIn("ít nhất 2", str(caught.exception))
        text = doc(cau_hoi(("a", "b", "c", "d", "e5")))
        with self.assertRaises(parse.ParseError) as caught:
            parse.parse(text)
        self.assertEqual(caught.exception.line_no, line_of(text, "lua-chon: e5"))

    def test_quiz_text_limits(self):
        dung = ("## Cảnh 1\nloai: cau-hoi\ncau-hoi: " + "q" * 160 + "\n" + "".join(f"lua-chon: {'c' * 60}\n" for _ in range(4))
                + "dap-an: C\ngiai-thich: " + "g" * 180 + "\nloi-giai: Đáp án C.\nloi: Câu hỏi.\n")
        self.assertEqual(kiem.kiem(parse.parse(doc(dung)), Path(".")), [])
        self.loi(dung.replace("q" * 160, "q" * 161), "qqqq", "tối đa 160", kiem.CanhError)
        self.loi(dung.replace("c" * 60, "c" * 61, 1), "cccc", "tối đa 60", kiem.CanhError)
        self.loi(dung.replace("g" * 180, "g" * 181), "gggg", "tối đa 180", kiem.CanhError)
        self.loi(dung.replace("dap-an: C", "dap-an: C\ncho: 3\ncho: 4"), "cho: 4", "bị lặp")

    def test_long_answer_narration_is_a_warning_like_loi(self):
        text = doc(cau_hoi(them="dap-an: B\n").replace("loi-giai: Đáp án B. Chu kì tăng gấp đôi.",
                                                        "loi-giai: " + "a" * (kiem.LOI_DAI + 1)))
        canh_bao = kiem.kiem(parse.parse(text), Path("."))
        self.assertEqual(len(canh_bao), 1)
        self.assertIn("lời giải", canh_bao[0])

    def test_loi_assignment_whitespace_nit_is_fixed(self):
        src = (TOOLS_VI / "video_ma_parts" / "parse.py").read_text(encoding="utf-8")
        self.assertNotIn("loi =truong", src)


class NfdTest(unittest.TestCase):
    """Unikey "Unicode tổ hợp", Mac, PDF cho chữ NFD: parse chuẩn hoá cả kịch bản về NFC một lần ở đầu vào."""

    def test_kich_ban_nfd_thanh_nfc_ca_tieu_de_canh(self):
        goc = ("﻿---\ntieu-de: Chu kì\nmon: Vật lí\nlop: 10\nnguon-nhac: Nhạc: Êm\nnhac-nen: êm.mp3\n---\n\n"
               "## Cảnh 1\nloai: y-tung-y\ntieu-de: Dao động\ny: ==chu kì== lặp lại\nloi: Chu kì là thời gian.\n")
        v = parse.parse(unicodedata.normalize("NFD", goc))
        nfc = lambda s: unicodedata.normalize("NFC", s)  # noqa: E731
        self.assertEqual(v.meta["tieu-de"], nfc("Chu kì"))
        self.assertEqual(v.meta["nguon-nhac"], nfc("Nhạc: Êm"))
        self.assertEqual(v.canh[0].loi, nfc("Chu kì là thời gian."))
        self.assertEqual(v.canh[0].truong["y"], [nfc("==chu kì== lặp lại")])


if __name__ == "__main__":
    unittest.main()
