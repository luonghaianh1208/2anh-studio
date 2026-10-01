"""Dữ liệu trang của cảnh Vox: mốc nhịp theo mốc từ, ô tự chọn, chuyển cảnh xen kẽ, ảnh từ vox.json."""
import json, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from video_ma_parts import kiem, lich, parse, phong, vox  # noqa: E402


def moc(loi: str, buoc=0.4):
    return [{"t": lich.DAN_DAU + i * buoc, "d": buoc, "chu": w, "khoa": lich.khoa_so_khop(w)}
            for i, w in enumerate(loi.split())]


VID = ("---\ntieu-de: T\nphong-cach: vox\n---\n\n"
       "## Cảnh 1\nbo-cuc: hai-ben\nloi: Tiền nhiều, tiền ít, rồi hết.\n"
       "nhip: @dau | nhan: Tiền | giua\nnhip: tiền | chu: Nhiều\nnhip: tiền ít | chu: Ít\n\n"
       "## Cảnh 2\nbo-cuc: mot\nloi: Hai.\nnhip: @dau | dau: XONG\n\n"
       "## Cảnh 3\nbo-cuc: mot\nloi: Ba.\nnhip: @dau | so: {{85.5}}% người\n")


class MocTest(unittest.TestCase):
    def test_beat_times_follow_the_words(self):
        v = parse.parse(VID)
        c = v.canh[0]
        t = vox.moc_nhip(c.nhip, moc(c.loi), lich.DAN_DAU)
        self.assertEqual(t, [lich.DAN_DAU, lich.DAN_DAU + 0.0, lich.DAN_DAU + 0.8])

    def test_unmatched_estimated_word_falls_back_to_order(self):
        c = parse.parse(VID).canh[0]
        t = vox.moc_nhip(c.nhip, [], lich.DAN_DAU)   # chưa có mốc từ: nối tiếp nhau, mỗi nhịp cách đúng 0,6 giây
        self.assertEqual(len(t), 3)
        self.assertTrue(t[0] <= t[1] <= t[2])

    def test_cue_matches_a_word_joined_by_punctuation(self):
        # "chu-kì" là một mục `moc_tu` (khoa_so_khop không tách dấu gạch nối); cụm nhịp "chu kì" phải vẫn khớp.
        v = parse.parse("---\ntieu-de: T\nphong-cach: vox\n---\n\n## Cảnh 1\nbo-cuc: mot\n"
                         "loi: Mỗi chu-kì kéo dài lâu.\nnhip: @dau | chu: X\nnhip: chu kì | chu: Y\n")
        c = v.canh[0]
        t = vox.moc_nhip(c.nhip, moc(c.loi), lich.DAN_DAU)
        self.assertEqual(t[1], lich.DAN_DAU + 0.4)

    def test_cue_matches_a_comma_separated_number(self):
        # "85,5%" là một mục `moc_tu`; cụm nhịp "85,5%" phải khớp đúng mục đó, không rơi về nối tiếp +0,6s.
        v = parse.parse("---\ntieu-de: T\nphong-cach: vox\n---\n\n## Cảnh 1\nbo-cuc: mot\n"
                         "loi: Tăng 85,5% so với trước.\nnhip: @dau | chu: X\nnhip: 85,5% | chu: Y\n")
        c = v.canh[0]
        t = vox.moc_nhip(c.nhip, moc(c.loi), lich.DAN_DAU)
        self.assertEqual(t[1], lich.DAN_DAU + 0.4)

    def test_cue_matches_across_a_standalone_dash(self):
        # "–" đứng riêng là một mục `moc_tu` nhưng khai triển ra rỗng (bỏ qua); cụm nhịp "A B" phải khớp đúng từ "A".
        v = parse.parse("---\ntieu-de: T\nphong-cach: vox\n---\n\n## Cảnh 1\nbo-cuc: mot\n"
                         "loi: A – B là hai.\nnhip: @dau | chu: X\nnhip: A B | chu: Y\n")
        c = v.canh[0]
        t = vox.moc_nhip(c.nhip, moc(c.loi), lich.DAN_DAU)
        self.assertEqual(t[1], lich.DAN_DAU + 0.0)


class DuLieuTest(unittest.TestCase):
    def du(self, k=0, meta_them=""):
        v = parse.parse(VID.replace("phong-cach: vox\n", "phong-cach: vox\n" + meta_them))
        plan, _ = lich.dung_lich(v.canh, [lich.GiongInfo(None, 3.0, [0.0], False, "may", moc_tu=moc(c.loi)) for c in v.canh])
        return [vox.du_lieu_canh(c, cl, {"anh": {}}, v.meta) for c, cl in zip(v.canh, plan)][k], v

    def test_shape(self):
        du, _ = self.du()
        self.assertEqual(du["loai"], "vox")
        self.assertEqual(du["boCuc"], "hai-ben")
        self.assertEqual([n["o"] for n in du["nhip"]], ["giua", "trai", "phai"])   # ô trống kế tiếp theo thứ tự ô
        self.assertEqual(du["chuDe"]["ten"], "vox")
        self.assertIsNone(du["co"]["chuyen"])

    def test_counter_and_text(self):
        du, _ = self.du(2)
        self.assertEqual(du["nhip"][0]["so"], {"giaTri": 85.5, "truoc": "", "sau": "% người", "thapPhan": 1})

    def test_transitions_alternate(self):
        self.assertEqual(self.du(1)[0]["co"]["chuyen"], "xe-giay")
        self.assertEqual(self.du(2)[0]["co"]["chuyen"], "lia")
        self.assertEqual(self.du(2, "chuyen-canh: khong\n")[0]["co"]["chuyen"], None)


def _o_list(md: str) -> list:
    v = parse.parse(md)
    plan, _ = lich.dung_lich(v.canh, [lich.GiongInfo(None, 3.0, [0.0], False, "may", moc_tu=moc(c.loi)) for c in v.canh])
    du = vox.du_lieu_canh(v.canh[0], plan[0], {"anh": {}}, v.meta)
    return [n["o"] for n in du["nhip"]]


class SlotTest(unittest.TestCase):
    def test_slot_overflow_never_lands_on_nen(self):
        # toan-canh chỉ có 2 ô ngoài `nen` (giua, duoi). Hai nhịp không ghi ô đầu tiên chiếm hết `giua`/`duoi`;
        # nhịp thứ ba ghi tường minh `nen` (ảnh phủ kín khung) nên là nhịp *gần nhất* trước nhịp thứ tư — nếu ô hết
        # thì "dùng lại ô cuối" theo đúng nhịp liền trước (lỗi cũ), nhịp thứ tư sẽ ăn nhầm "nen"; phải rơi về ô cuối
        # của bố cục ("duoi") thay vì ô của nhịp liền trước.
        md = ("---\ntieu-de: T\nphong-cach: vox\n---\n\n## Cảnh 1\nbo-cuc: toan-canh\nloi: Một hai ba bốn.\n"
              "nhip: một | chu: A\nnhip: hai | nhan: B\nnhip: ba | anh: tim: x | nen\nnhip: bốn | dau: C\n")
        o = _o_list(md)
        self.assertEqual(o, ["giua", "duoi", "nen", "duoi"])

    def test_unslotted_beat_skips_a_slot_a_later_beat_names_explicitly(self):
        md = ("---\ntieu-de: T\nphong-cach: vox\n---\n\n## Cảnh 1\nbo-cuc: hai-ben\nloi: Một hai.\n"
              "nhip: @dau | chu: A\nnhip: một | chu: B | trai\n")
        self.assertEqual(_o_list(md), ["phai", "trai"])

    def test_unslotted_arrow_does_not_take_a_slot(self):
        # Mũi tên vẽ trên cả khung, không chiếm ô: ảnh sau nó vẫn vào `phai`, không bị đẩy sang `giua`.
        md = ("---\ntieu-de: T\nphong-cach: vox\n---\n\n## Cảnh 1\nbo-cuc: hai-ben\nloi: Một hai ba.\n"
              "nhip: @dau | anh: tim: x | trai\nnhip: hai | mui-ten: trai -> phai\nnhip: ba | anh: tim: y\n")
        o = _o_list(md)
        self.assertEqual((o[0], o[2]), ("trai", "phai"))
        self.assertIsNone(o[1])


class SoTest(unittest.TestCase):
    def test_counter_text_drops_the_emphasis_marks(self):
        md = ("---\ntieu-de: T\nphong-cach: vox\n---\n\n## Cảnh 1\nbo-cuc: mot\nnguon: X\nloi: Ba.\n"
              "nhip: @dau | so: ==Tăng== {{85}}% ((giá))\n")
        v = parse.parse(md)
        plan, _ = lich.dung_lich(v.canh, [lich.GiongInfo(None, 3.0, [0.0], False, "may", moc_tu=moc(c.loi)) for c in v.canh])
        so = vox.du_lieu_canh(v.canh[0], plan[0], {"anh": {}}, v.meta)["nhip"][0]["so"]
        self.assertEqual((so["truoc"], so["sau"]), ("Tăng ", "% giá"))


class ChuDeTest(unittest.TestCase):
    def test_theme_and_fonts(self):
        self.assertEqual(phong.chu_de("vox")["ten"], "vox")
        self.assertIn("Be Vietnam Pro", phong.font_css("vox"))

    def test_subtitles_get_the_dark_box(self):
        from video_ma_parts import karaoke
        self.assertEqual(karaoke.kieu_phu_de("vox", "ngang"), karaoke.kieu_phu_de("cat-dan", "ngang"))


class KiemTest(unittest.TestCase):
    def test_missing_processed_image_is_a_scene_error_with_the_fix(self):
        md = ("---\ntieu-de: T\nphong-cach: vox\n---\n\n## Cảnh 1\nbo-cuc: mot\nloi: Cốc.\n"
              "nhip: Cốc | anh: ve: cốc sứ | giua\n")
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(kiem.CanhError) as c:
                kiem.kiem(parse.parse(md), Path(tmp))
        self.assertIn("anh_vox.py", c.exception.fix)

    def test_resources_read_from_the_index(self):
        from PIL import Image
        md = ("---\ntieu-de: T\nphong-cach: vox\n---\n\n## Cảnh 1\nbo-cuc: mot\nloi: Cốc.\n"
              "nhip: Cốc | anh: ve: cốc sứ | giua\n")
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "anh" / "ai" / "xu-ly"
            d.mkdir(parents=True)
            Image.new("RGBA", (40, 30), (1, 2, 3, 255)).save(d / "a-100-cat.png")
            (Path(tmp) / "anh" / "ai" / "vox.json").write_text(json.dumps(
                {"1-0": {"file": "ai/xu-ly/a-100-cat.png", "kieu": "cat", "ma": "a", "mo_hinh": "m", "nguon": None}}),
                encoding="utf-8")
            v = parse.parse(md)
            self.assertEqual(kiem.kiem(v, Path(tmp)), [])
            tn = vox.tai_nguyen(v.canh[0], Path(tmp))
        a = tn["anh"][0]
        self.assertEqual((a["rong"], a["cao"], a["kieu"], a["moHinh"]), (40, 30, "cat", "m"))
        self.assertTrue(a["dataUrl"].startswith("data:image/png;base64,"))


if __name__ == "__main__":
    unittest.main()
