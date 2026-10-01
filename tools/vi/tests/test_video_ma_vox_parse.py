"""Đọc video.md kiểu Vox: khối thông tin, nhịp, ô theo bố cục."""
import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from video_ma_parts import parse, vox  # noqa: E402

DAU = "---\ntieu-de: Giao tiếp\nphong-cach: vox\n---\n\n"


def doc(canh: str, dau: str = DAU):
    return parse.parse(dau + canh)


CANH_HAI_BEN = ("## Cảnh 1\nbo-cuc: hai-ben\n"
                "loi: Bạn nói \"để mai tính\", đồng nghiệp lại hiểu là \"không làm\".\n"
                "nhip: để mai tính | anh: ve: nhân viên nhún vai | trai\n"
                "nhip: hiểu | dau: HIỂU LẦM | giua\n"
                "nhip: không làm | anh: ve: đồng nghiệp khoanh tay | phai\n")


class MetaTest(unittest.TestCase):
    def test_vox_does_not_need_subject_or_grade(self):
        v = doc(CANH_HAI_BEN)
        self.assertEqual(v.meta["phong-cach"], "vox")
        self.assertNotIn("mon", v.meta)

    def test_other_styles_still_need_subject_and_grade(self):
        with self.assertRaises(parse.ParseError) as c:
            parse.parse("---\ntieu-de: T\n---\n\n## Cảnh 1\nloai: tieu-de\nchu: A\nloi: Chào.\n")
        self.assertIn("`mon`", str(c.exception))

    def test_vox_meta_values(self):
        v = doc(CANH_HAI_BEN, "---\ntieu-de: T\nphong-cach: vox\nthoi-luong: 60\nphong-anh: minh-hoa\n"
                              "bang-mau: dem\nchuyen-canh: lia\n---\n\n")
        self.assertEqual((v.meta["thoi-luong"], v.meta["phong-anh"], v.meta["bang-mau"], v.meta["chuyen-canh"]),
                         ("60", "minh-hoa", "dem", "lia"))
        v2 = doc(CANH_HAI_BEN)
        self.assertEqual((v2.meta["phong-anh"], v2.meta["bang-mau"], v2.meta["chuyen-canh"]), ("chup-that", "kem", "xen-ke"))

    def test_bad_duration(self):
        for gt in ("5", "601", "một phút", "60.5"):
            with self.subTest(gt=gt), self.assertRaises(parse.ParseError) as c:
                doc(CANH_HAI_BEN, f"---\ntieu-de: T\nphong-cach: vox\nthoi-luong: {gt}\n---\n\n")
            self.assertIn("thoi-luong", str(c.exception))

    def test_duration_allowed_for_old_styles_too(self):
        v = parse.parse("---\ntieu-de: T\nmon: Toán\nlop: 8\nthoi-luong: 90\n---\n\n## Cảnh 1\nloai: tieu-de\nchu: A\nloi: Chào.\n")
        self.assertEqual(v.meta["thoi-luong"], "90")

    def test_vox_rejects_handwriting_only_keys(self):
        for dong in ("ban-tay: co", "nhan-vat: nguoi-que", "mau-ao: do", "chu-dong: co", "may-quay: co"):
            with self.subTest(dong=dong), self.assertRaises(parse.ParseError) as c:
                doc(CANH_HAI_BEN, f"---\ntieu-de: T\nphong-cach: vox\n{dong}\n---\n\n")
            self.assertIn("vox", str(c.exception))

    def test_vox_values_only_for_vox(self):
        with self.assertRaises(parse.ParseError):
            parse.parse("---\ntieu-de: T\nmon: A\nlop: 1\nphong-anh: minh-hoa\n---\n\n## Cảnh 1\nloai: tieu-de\nchu: A\nloi: B.\n")


class NhipTest(unittest.TestCase):
    def test_beats_are_parsed(self):
        c = doc(CANH_HAI_BEN).canh[0]
        self.assertEqual(c.loai, "vox")
        self.assertEqual([(n.cum, n.vat, n.o) for n in c.nhip],
                         [("để mai tính", "anh", "trai"), ("hiểu", "dau", "giua"), ("không làm", "anh", "phai")])
        self.assertEqual(c.nhip[0].noi_dung, "ve: nhân viên nhún vai")
        self.assertEqual(c.nhip[2].chi_so, 2)

    def test_options(self):
        c = doc("## Cảnh 1\nbo-cuc: mot\nloi: Đây là Hà Nội.\nnhip: Hà Nội | anh: tim: hanoi old quarter | giua | khung duotone\n").canh[0]
        self.assertEqual(c.nhip[0].tuy_chon, ("khung", "duotone"))

    def test_loai_is_not_allowed_in_vox(self):
        with self.assertRaises(parse.ParseError) as c:
            doc("## Cảnh 1\nloai: tieu-de\nbo-cuc: mot\nloi: A.\nnhip: @dau | chu: A\n")
        self.assertIn("loai", str(c.exception))

    def test_phrase_must_be_in_narration(self):
        with self.assertRaises(parse.ParseError) as c:
            doc("## Cảnh 1\nbo-cuc: mot\nloi: Hôm nay trời đẹp.\nnhip: trời mưa | chu: Mưa\n")
        self.assertIn("trời mưa", str(c.exception))

    def test_phrase_matching_ignores_case_and_punctuation(self):
        c = doc("## Cảnh 1\nbo-cuc: mot\nloi: \"Để mai tính\", anh ấy nói.\nnhip: để MAI tính | chu: Để mai\n").canh[0]
        self.assertEqual(c.nhip[0].cum, "để MAI tính")

    def test_beats_follow_the_narration_order(self):
        with self.assertRaises(parse.ParseError) as c:
            doc("## Cảnh 1\nbo-cuc: hai-ben\nloi: Một hai ba.\nnhip: ba | chu: Ba | trai\nnhip: một | chu: Một | phai\n")
        self.assertIn("thứ tự", str(c.exception))

    def test_unslotted_caption_must_also_follow_the_narration_order(self):
        with self.assertRaises(parse.ParseError) as c:
            doc("## Cảnh 1\nbo-cuc: hai-ben\nloi: Một hai ba.\nnhip: ba | chu: Ba | trai\nnhip: hai | dau: HAI\n")
        self.assertIn("thứ tự", str(c.exception))

    def test_repeated_phrase_takes_the_next_occurrence(self):
        c = doc("## Cảnh 1\nbo-cuc: hai-ben\nloi: Tiền nhiều, tiền ít.\nnhip: tiền | chu: A | trai\nnhip: tiền | chu: B | phai\n").canh[0]
        self.assertEqual(len(c.nhip), 2)

    def test_scene_needs_at_least_one_beat_and_at_most_six(self):
        with self.assertRaises(parse.ParseError):
            doc("## Cảnh 1\nbo-cuc: mot\nloi: A.\n")
        nhip = "".join(f"nhip: @dau | nhan: N{k}\n" for k in range(7))
        with self.assertRaises(parse.ParseError) as c:
            doc("## Cảnh 1\nbo-cuc: mot\nloi: A.\n" + nhip)
        self.assertIn("6", str(c.exception))

    def test_slot_must_belong_to_the_layout(self):
        with self.assertRaises(parse.ParseError) as c:
            doc("## Cảnh 1\nbo-cuc: mot\nloi: A b.\nnhip: A | chu: X | trai\n")
        self.assertIn("giua", str(c.exception))

    def test_portrait_slots(self):
        dau = "---\ntieu-de: T\nphong-cach: vox\nkho: doc\n---\n\n"
        doc("## Cảnh 1\nbo-cuc: hai-ben\nloi: A b.\nnhip: A | chu: X | tren\n", dau)
        with self.assertRaises(parse.ParseError):
            doc("## Cảnh 1\nbo-cuc: hai-ben\nloi: A b.\nnhip: A | chu: X | trai\n", dau)

    def test_unknown_object_and_bad_contents(self):
        cases = [
            "nhip: A | video: x\n",                          # vật lạ
            "nhip: A | the: chỉ một phần\n",                 # thẻ sai dạng
            "nhip: A | so: không có số\n",                   # so thiếu {{…}}
            "nhip: A | mui-ten: giua\n",                      # mũi tên thiếu ->
            "nhip: A | anh: \n",                              # ảnh trống
            "nhip: A | chu: " + "x" * 41 + "\n",             # chữ quá 40
            "nhip: A | dau: " + "X" * 17 + "\n",             # dấu quá 16
            "nhip: A | chu: X | giua | nhay-mua\n",          # tuỳ chọn lạ
        ]
        for nhip in cases:
            with self.subTest(nhip=nhip), self.assertRaises(parse.ParseError):
                doc("## Cảnh 1\nbo-cuc: mot\nloi: A b.\n" + nhip)

    def test_at_most_two_big_lines(self):
        with self.assertRaises(parse.ParseError) as c:
            doc("## Cảnh 1\nbo-cuc: chong\nloi: A b c.\nnhip: A | chu: X\nnhip: b | chu: Y\nnhip: c | chu: Z\n")
        self.assertIn("chu", str(c.exception))

    def test_full_frame_photo_only_in_nen_slot(self):
        doc("## Cảnh 1\nbo-cuc: toan-canh\nloi: Phố cổ.\nnhip: @dau | anh: tim: hanoi street | nen\nnhip: Phố cổ | nhan: Hà Nội | duoi\n")
        with self.assertRaises(parse.ParseError):
            doc("## Cảnh 1\nbo-cuc: toan-canh\nloi: Phố cổ.\nnhip: @dau | chu: X | nen\n")

    def test_source_line_and_transition(self):
        v = doc("## Cảnh 1\nbo-cuc: mot\nloi: A.\nnhip: @dau | chu: A\n\n"
                "## Cảnh 2\nbo-cuc: mot\nchuyen: lia\nnguon: Gallup 2023\nloi: B.\nnhip: @dau | chu: B\n")
        self.assertEqual(v.canh[1].truong["nguon"], ["Gallup 2023"])
        with self.assertRaises(parse.ParseError):
            doc("## Cảnh 1\nbo-cuc: mot\nchuyen: lau-bang\nloi: A.\nnhip: @dau | chu: A\n")


class TuyChonGopTest(unittest.TestCase):
    """Tuỳ chọn viết chung một phần; tách thành nhiều phần ` | ` là lỗi, không lặng lẽ bỏ phần thừa."""

    def test_options_split_over_several_fields_are_an_error(self):
        for nhip in ("nhip: Hà Nội | anh: ve: phố cổ | phai | khung | duotone\n",
                     "nhip: Hà Nội | anh: ve: phố cổ | khung | duotone\n"):
            with self.subTest(nhip=nhip), self.assertRaises(parse.ParseError) as c:
                doc("## Cảnh 1\nbo-cuc: hai-ben\nloi: Đây là Hà Nội.\n" + nhip)
            self.assertIn("| phai | khung duotone", str(c.exception))

    def test_valid_shapes_still_parse(self):
        cases = {
            "nhip: Hà Nội | anh: ve: phố cổ | phai | khung duotone\n": ("phai", ("khung", "duotone")),
            "nhip: Hà Nội | anh: ve: phố cổ | khung duotone\n": (None, ("khung", "duotone")),
            "nhip: Hà Nội | anh: ve: phố cổ | phai\n": ("phai", ()),
            "nhip: Hà Nội | anh: ve: phố cổ\n": (None, ()),
            "nhip: Hà Nội | the: Nhãn | 12 | chú thích | phai | gan\n": ("phai", ("gan",)),
            "nhip: Hà Nội | the: Nhãn | 12 | phai\n": ("phai", ()),
        }
        for nhip, (o, tuy) in cases.items():
            with self.subTest(nhip=nhip):
                n = doc("## Cảnh 1\nbo-cuc: hai-ben\nloi: Đây là Hà Nội.\n" + nhip).canh[0].nhip[0]
                self.assertEqual((n.o, n.tuy_chon), (o, tuy))


class MuiTenTest(unittest.TestCase):
    def test_arrow_endpoints_must_be_slots_of_the_layout(self):
        doc("## Cảnh 1\nbo-cuc: hai-ben\nloi: A b.\nnhip: A | mui-ten: trai -> phai\n")
        for dau_mui in ("trai -> tren", "giua -> 5"):
            with self.subTest(dau_mui=dau_mui), self.assertRaises(parse.ParseError) as c:
                doc(f"## Cảnh 1\nbo-cuc: hai-ben\nloi: A b.\nnhip: A | mui-ten: {dau_mui}\n")
            self.assertIn("trai, phai, giua", str(c.exception))
        with self.assertRaises(parse.ParseError):
            doc("## Cảnh 1\nbo-cuc: hai-ben\nloi: A b.\nnhip: A | mui-ten: trai -> phai\n",
                "---\ntieu-de: T\nphong-cach: vox\nkho: doc\n---\n\n")
        with self.assertRaises(parse.ParseError) as c:
            doc("## Cảnh 1\nbo-cuc: chong\nloi: A b.\nnhip: A | chu: X\nnhip: b | mui-ten: 1 -> 2\n")
        self.assertIn("chong", str(c.exception))


class KhoaTuTest(unittest.TestCase):
    def test_tokens(self):
        self.assertEqual(vox.khoa_tu("\"Để mai tính\", anh ấy nói!"), ["để", "mai", "tính", "anh", "ấy", "nói"])

    def test_find_phrase(self):
        t = vox.khoa_tu("tiền nhiều, tiền ít")
        self.assertEqual(vox.tim_cum(t, "tiền", 0), 0)
        self.assertEqual(vox.tim_cum(t, "tiền", 1), 2)
        self.assertEqual(vox.tim_cum(t, "tiền ít", 0), 2)
        self.assertEqual(vox.tim_cum(t, "bạc", 0), -1)


if __name__ == "__main__":
    unittest.main()
