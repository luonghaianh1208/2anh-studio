"""Vox v2: nền AI từng cảnh, kiểu ảnh cắt dán, lời liền mạch, giọng VieNeu, nguồn ghi ra file, cảnh mở có hình."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from anh_vox_parts import ke_hoach, xu_ly  # noqa: E402
from video_ma_parts import giong, kiem, lich, parse, thoi_luong, vox  # noqa: E402

DAU = "---\ntieu-de: Giao tiếp\nphong-cach: vox\n---\n\n"
CANH = ("## Cảnh 1\nbo-cuc: mot\nnen: mặt bàn văn phòng nhìn từ trên xuống\nloi: Bạn hỏi một câu. Họ nghe ra câu khác.\n"
        "nhip: @dau | nhan: Một câu | tren\nnhip: @dau | anh: ve: cụm cắt dán hai người | giua\n\n"
        "## Cảnh 2\nbo-cuc: toan-canh\nloi: Gặp trực tiếp.\nnhip: @dau | anh: ve: hai người trò chuyện | nen\n\n"
        "## Cảnh 3\nbo-cuc: mot\nloi: Một hai ba bốn năm sáu bảy.\nnhip: sáu | chu: Sáu\n")


def doc(dau=DAU, canh=CANH):
    return parse.parse(dau + canh)


class MacDinhTest(unittest.TestCase):
    def test_vox_defaults(self):
        v = doc()
        self.assertEqual((v.meta["phong-anh"], v.meta["nen-canh"], v.meta["giong"]), ("cat-dan", "ve", "thu-giang"))

    def test_other_styles_keep_the_edge_voice(self):
        v = parse.parse("---\ntieu-de: T\nmon: A\nlop: 1\n---\n\n## Cảnh 1\nloai: tieu-de\nchu: A\nloi: B.\n")
        self.assertEqual(v.meta["giong"], "nu")

    def test_background_description_is_a_scene_field(self):
        v = doc()
        self.assertEqual(v.canh[0].truong["nen"], ["mặt bàn văn phòng nhìn từ trên xuống"])
        with self.assertRaises(parse.ParseError):
            doc(canh="## Cảnh 1\nbo-cuc: mot\nnen: " + "x" * 301 + "\nloi: A.\nnhip: @dau | chu: A\n")


class NenCanhTest(unittest.TestCase):
    def test_every_scene_without_a_full_frame_photo_gets_a_background(self):
        ds = ke_hoach.lap(doc())
        nen = [m for m in ds if m.kieu == "nen"]
        self.assertEqual([m.canh for m in nen], [1, 3], "cảnh 2 đã có ảnh phủ kín khung")
        self.assertEqual([ke_hoach.khoa(m) for m in nen], ["1-nen", "3-nen"])
        self.assertIn("mặt bàn văn phòng", nen[0].prompt)
        self.assertIn("Giao tiếp", nen[1].prompt, "không tả nền thì lập từ tên video và lời")
        self.assertIn("Một hai ba", nen[1].prompt)
        for m in nen:
            self.assertIn("không có chữ", m.prompt)
            self.assertIn("chừa vùng giấy sáng", m.prompt)
            self.assertEqual(m.kich_thuoc, "1536x1024")
            self.assertTrue(ke_hoach.file_xu_ly(Path("x"), m).name.endswith("-nen.jpg"))

    def test_collage_style_is_in_every_ai_prompt(self):
        for m in ke_hoach.lap(doc()):
            self.assertIn("cắt dán", m.prompt)

    def test_backgrounds_can_be_switched_off(self):
        ds = ke_hoach.lap(doc(DAU.replace("phong-cach: vox\n", "phong-cach: vox\nnen-canh: khong\n")))
        self.assertFalse([m for m in ds if m.kieu == "nen"])

    def test_portrait_background_size(self):
        ds = ke_hoach.lap(doc(DAU.replace("phong-cach: vox\n", "phong-cach: vox\nkho: doc\n")))
        self.assertEqual({m.kich_thuoc for m in ds if m.kieu == "nen"}, {"1024x1536"})

    def test_background_is_cover_cropped_to_the_baked_size(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as tmp:
            thu_muc = Path(tmp)
            m = [x for x in ke_hoach.lap(doc()) if x.kieu == "nen"][0]
            goc = ke_hoach.file_goc(thu_muc, m)
            goc.parent.mkdir(parents=True)
            Image.new("RGB", (1024, 1024), (120, 40, 40)).save(goc)
            self.assertEqual(xu_ly.xu_ly_muc(thu_muc, m, kho="ngang"), [])
            with Image.open(ke_hoach.file_xu_ly(thu_muc, m)) as im:
                self.assertEqual(im.size, xu_ly.NEN_KICH["ngang"])
                self.assertEqual(im.format, "JPEG")

    def test_missing_background_is_a_warning_in_plan_only_and_an_error_otherwise(self):
        dau = DAU.replace("phong-cach: vox\n", "phong-cach: vox\ngiong: nu\n")
        canh = "## Cảnh 1\nbo-cuc: mot\nloi: A b.\nnhip: @dau | chu: A\n"
        with tempfile.TemporaryDirectory() as tmp:
            w = kiem.kiem(doc(dau, canh), Path(tmp), chi_canh_bao=True)
            self.assertTrue(any("chưa có nền AI" in x for x in w), w)
            with self.assertRaises(kiem.CanhError) as c:
                kiem.kiem(doc(dau, canh), Path(tmp))
            self.assertIn("anh_vox.py", c.exception.fix)
            self.assertIn("nen-canh: khong", c.exception.fix)
            khong = dau.replace("giong: nu\n", "giong: nu\nnen-canh: khong\n")
            self.assertEqual(kiem.kiem(doc(khong, canh), Path(tmp)), [])

    def test_background_reaches_the_page_data(self):
        from PIL import Image
        dau = DAU.replace("phong-cach: vox\n", "phong-cach: vox\ngiong: nu\n")
        v = doc(dau, "## Cảnh 1\nbo-cuc: mot\nloi: A b.\nnhip: @dau | chu: A\n")
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "anh" / "ai" / "xu-ly"
            d.mkdir(parents=True)
            Image.new("RGB", (64, 36), (1, 2, 3)).save(d / "n.jpg")
            (Path(tmp) / "anh" / "ai" / "vox.json").write_text(json.dumps(
                {"1-nen": {"file": "ai/xu-ly/n.jpg", "kieu": "nen", "mo_hinh": "m"}}), encoding="utf-8")
            tn = vox.tai_nguyen(v.canh[0], Path(tmp))
        self.assertTrue(tn["nen"]["dataUrl"].startswith("data:image/jpeg;base64,"))
        plan, _ = lich.dung_lich(v.canh, [lich.GiongInfo(None, 2.0, [0.0], False, "may")])
        du = vox.du_lieu_canh(v.canh[0], plan[0], tn, v.meta)
        self.assertEqual(du["nen"]["rong"], 64)
        self.assertIsNone(du["nguon"], "nguồn số liệu không hiện trên hình")


class MoCanhTest(unittest.TestCase):
    def canh_bao(self, canh):
        dau = DAU.replace("phong-cach: vox\n", "phong-cach: vox\nnen-canh: khong\n")
        with tempfile.TemporaryDirectory() as tmp:
            return [w for w in kiem.kiem(doc(dau, canh), Path(tmp)) if "hiện muộn" in w]

    def test_scene_that_opens_empty_is_warned(self):
        w = self.canh_bao("## Cảnh 1\nbo-cuc: mot\nloi: Một hai ba bốn năm sáu bảy.\nnhip: sáu | chu: Sáu\n")
        self.assertEqual(len(w), 1)
        self.assertIn("@dau", w[0])

    def test_scene_with_an_opening_beat_is_fine(self):
        self.assertEqual(self.canh_bao("## Cảnh 1\nbo-cuc: mot\nloi: Một hai ba bốn năm sáu bảy.\n"
                                       "nhip: @dau | nhan: Mở | tren\nnhip: sáu | chu: Sáu\n"), [])
        self.assertEqual(self.canh_bao("## Cảnh 1\nbo-cuc: mot\nloi: Một hai ba bốn năm sáu bảy.\nnhip: hai | chu: Hai\n"), [])


class LoiLienMachTest(unittest.TestCase):
    def test_vox_scenes_have_a_short_lead_in_and_tail(self):
        v = doc(DAU, "## Cảnh 1\nbo-cuc: mot\nloi: A b.\nnhip: @dau | chu: A\n")
        plan, _ = lich.dung_lich(v.canh, [lich.GiongInfo(None, 4.0, [0.0], False, "may")])
        cl = plan[0]
        self.assertEqual(cl.dan_dau, lich.VOX_DAN_DAU)
        self.assertAlmostEqual(cl.thoi_luong, 4.0 + lich.VOX_DAN_DAU + lich.VOX_DUOI, delta=1 / lich.FPS)
        self.assertEqual(cl.moc_cau[0], lich.VOX_DAN_DAU)
        self.assertLessEqual(lich.VOX_DAN_DAU + lich.VOX_DUOI, 0.6, "giữa hai cảnh nghỉ không quá 0,6 giây")
        self.assertAlmostEqual(lich.doan_loi(cl)[0][2], lich.VOX_DAN_DAU + 4.0)

    def test_old_styles_keep_their_lead_in(self):
        v = parse.parse("---\ntieu-de: T\nmon: A\nlop: 1\n---\n\n## Cảnh 1\nloai: tieu-de\nchu: A\nloi: B.\n")
        plan, _ = lich.dung_lich(v.canh, [lich.GiongInfo(None, 4.0, [0.0], False, "may")])
        self.assertEqual(plan[0].dan_dau, lich.DAN_DAU)
        self.assertAlmostEqual(plan[0].thoi_luong, 4.0 + lich.DAN_DAU + lich.DUOI, delta=1 / lich.FPS)

    def test_audio_starts_at_the_scene_lead_in(self):
        from video_ma_parts import ghep
        cmd = " ".join(map(str, ghep.lenh_am_canh(Path("a.mp3"), Path("a.wav"), 5.0, dan_dau=lich.VOX_DAN_DAU)))
        self.assertIn(f"adelay={int(lich.VOX_DAN_DAU * 1000)}:all=1", cmd)


class GiongVieneuTest(unittest.TestCase):
    def test_word_times_are_spread_inside_each_sentence(self):
        tu = giong._moc_tu_theo_cau(["Một hai.", "Ba."], [0.0, 2.0], [1.0, 0.5])
        self.assertEqual([w["chu"] for w in tu], ["Một", "hai.", "Ba."])
        self.assertEqual(tu[0]["t"], 0.0)
        self.assertLess(tu[1]["t"], 1.0)
        self.assertEqual(tu[2]["t"], 2.0)

    def test_all_missing_scenes_are_read_in_one_run_and_cached(self):
        goi = []

        def gia(viec, voice, toc_do, run=None):
            goi.append([loi for loi, _ in viec])
            for _loi, dich in viec:
                Path(dich).write_bytes(b"mp3")
            return [{"cau": [0.0], "tu": [{"t": 0.0, "d": 0.5, "chu": "A"}]} for _ in viec]

        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(giong, "_vieneu_chay", gia):
            d = Path(tmp)
            self.assertEqual(giong.tao_truoc_vieneu([("canh-1", "Một."), ("canh-2", "Hai.")], d, "thu-giang", "vua"), 2)
            self.assertEqual(goi, [["Một.", "Hai."]], "một tiến trình cho mọi cảnh")
            self.assertEqual(giong.tao_truoc_vieneu([("canh-1", "Một."), ("canh-2", "Hai.")], d, "thu-giang", "vua"), 0)
            self.assertEqual(giong.tao_truoc_vieneu([("canh-1", "Một."), ("canh-2", "Hai đổi.")], d, "thu-giang", "vua"), 1)
            g = giong.lay_giong(1, "Một.", d, "thu-giang", "vua", do_dai=lambda p: 1.0)
            self.assertEqual((g.nguon, g.uoc_luong, g.uoc_luong_tu), ("may", False, False))

    def test_user_voice_file_is_never_replaced(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(giong, "_vieneu_chay") as gia:
            d = Path(tmp)
            (d / "canh-1.mp3").write_bytes(b"giong nguoi dung")
            self.assertEqual(giong.tao_truoc_vieneu([("canh-1", "Một.")], d, "thu-giang", "vua"), 0)
            gia.assert_not_called()
            self.assertEqual((d / "canh-1.mp3").read_bytes(), b"giong nguoi dung")

    def test_missing_vieneu_is_a_voice_error_with_a_fix(self):
        from video_parts import media
        with mock.patch.object(giong, "vieneu_python", return_value=None), self.assertRaises(media.MediaError) as c:
            giong.tong_hop_vieneu("Một.", "vieneu:Thu Giang", "vua", Path("x.mp3"))
        self.assertEqual(c.exception.step, "giong")
        self.assertIn("giong: nu", c.exception.fix)

    def test_estimate_uses_the_vieneu_pace(self):
        v = doc(DAU, "## Cảnh 1\nbo-cuc: mot\nloi: " + " ".join(["từ"] * 43) + ". Hết.\nnhip: @dau | chu: A\n")
        mong = 44 / thoi_luong.TOC_DO_VIENEU["vua"] + thoi_luong.MOI_CANH_VOX + thoi_luong.NGHI_CAU_VIENEU
        self.assertAlmostEqual(thoi_luong.uoc_tinh(v), mong, places=3)
        self.assertGreater(thoi_luong.toc("vua", "thu-giang"), thoi_luong.toc("vua", "nu"))


class NguonTepTest(unittest.TestCase):
    def test_sources_file_lists_models_photos_numbers_and_music(self):
        dau = DAU.replace("phong-cach: vox\n", "phong-cach: vox\nnen-canh: khong\n")
        v = doc(dau, "## Cảnh 1\nbo-cuc: mot\nnguon: Bộ luật Lao động 2019, Điều 105\nloi: Hà Nội đẹp.\n"
                     "nhip: @dau | anh: tim: hanoi | giua\n")
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "anh" / "ai"
            d.mkdir(parents=True)
            (d / "vox.json").write_text(json.dumps({
                "1-0": {"file": "ai/xu-ly/a.png", "kieu": "khung", "mo_hinh": None, "nguon": "Ảnh: A (CC BY 2.0)"},
                "1-nen": {"file": "ai/xu-ly/n.jpg", "kieu": "nen", "mo_hinh": "ag/gemini-3.1-flash-image", "nguon": None},
            }), encoding="utf-8")
            chu = vox.nguon_van_ban(v, Path(tmp), {"nguon": "Nhạc: Bài X · Y (CC BY)"})
        for cum in ("Giao tiếp", "ag/gemini-3.1-flash-image", "Cảnh 1: Ảnh: A (CC BY 2.0)",
                    "Cảnh 1: Bộ luật Lao động 2019, Điều 105", "Nhạc nền: Nhạc: Bài X"):
            self.assertIn(cum, chu)


if __name__ == "__main__":
    unittest.main()
