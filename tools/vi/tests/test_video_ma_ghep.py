"""Test ghép video: lệnh FFmpeg, phụ đề, danh sách nối tiếng. Không chạy FFmpeg thật."""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))

from video_ma_parts import ghep, lich  # noqa: E402
from video_ma_parts import kho as kho_mod  # noqa: E402
from video_ma_parts.phong import FONT_CAT_DAN  # noqa: E402
from video_parts import media, srt  # noqa: E402


def canh_lich(so, bat_dau, thoi_luong, giay, cau, moc_giong):
    return lich.CanhLich(so=so, bat_dau=bat_dau, thoi_luong=thoi_luong, so_khung=round(thoi_luong * lich.FPS), giay_giong=giay,
                         cau=cau, moc_cau=[lich.DAN_DAU + m for m in moc_giong], moc_cau_giong=moc_giong, uoc_luong=False)


PLAN = [
    canh_lich(1, 0.0, 6.0, 4.0, ["Xin chào **các** em.", "Học H~2~SO~4~ nhé."], [0.0, 2.0]),
    canh_lich(2, 6.0, 3.0, 1.5, ["Tạm biệt."], [0.0]),
]


class SubtitleTest(unittest.TestCase):
    def test_cues_follow_sentence_marks_with_scene_offsets_and_strip_markup(self):
        cues = ghep.cues_phu_de(PLAN)
        self.assertEqual([c.index for c in cues], [1, 2, 3])
        self.assertEqual(cues[0].text, "Xin chào các em.")
        self.assertEqual(cues[1].text, "Học H2SO4 nhé.")
        self.assertAlmostEqual(cues[0].start, lich.DAN_DAU)
        self.assertAlmostEqual(cues[0].end, lich.DAN_DAU + 2.0)
        self.assertAlmostEqual(cues[1].start, lich.DAN_DAU + 2.0)
        self.assertAlmostEqual(cues[1].end, lich.DAN_DAU + 4.0)
        self.assertAlmostEqual(cues[2].start, 6.0 + lich.DAN_DAU)
        self.assertAlmostEqual(cues[2].end, 6.0 + lich.DAN_DAU + 1.5)

    def test_cues_bo_moi_dau_danh_dau_nhu_giong_doc(self):
        cau = "Ta có ==chu kì== và ((tần số)) cùng __H~2~O__ nặng **{{12.5}}** g^2^."
        plan = [canh_lich(1, 0.0, 6.0, 4.0, [cau], [0.0])]
        text = ghep.cues_phu_de(plan)[0].text
        self.assertEqual(text, "Ta có chu kì và tần số cùng H2O nặng 12.5 g2.")
        for dau in ("==", "((", "))", "__", "{{", "}}", "**", "~", "^"):
            self.assertNotIn(dau, text)

    def test_cues_render_to_valid_srt(self):
        text = srt.render_srt(ghep.cues_phu_de(PLAN))
        self.assertEqual(len(srt.parse_srt(text)), 3)


class CommandTest(unittest.TestCase):
    def test_audio_command_delays_pads_and_cuts_to_scene_length(self):
        cmd = ghep.lenh_am_canh(Path("giong/canh-1.mp3"), Path("am-1.wav"), 6.0)
        joined = " ".join(cmd)
        self.assertIn(f"adelay={int(round(lich.DAN_DAU * 1000))}:all=1", joined)
        self.assertIn("apad=whole_dur=6.000", joined)
        self.assertEqual(cmd[cmd.index("-t") + 1], "6.000")

    def test_audio_command_mixes_a_quiet_fixed_seed_noise_floor(self):
        cmd = ghep.lenh_am_canh(Path("giong/canh-1.mp3"), Path("am-1.wav"), 6.0)
        joined = " ".join(cmd)
        self.assertIn("anoisesrc=", joined)
        self.assertIn(f"seed={ghep.HAT_NHIEU}", joined)
        self.assertIn("amix=inputs=2:duration=first:normalize=0", joined)

    @unittest.skipUnless(shutil.which("ffmpeg"), "máy không có FFmpeg")
    def test_scene_audio_never_contains_digital_silence(self):
        """Loa Bluetooth/HDMI tự tắt khi gặp im lặng tuyệt đối và nuốt âm đầu của câu sau."""
        import struct
        import subprocess
        import wave
        with tempfile.TemporaryDirectory() as tmp:
            mp3 = Path(tmp) / "g.mp3"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
                            "sine=frequency=440:duration=0.5,apad=pad_dur=1.0,asetrate=44100", "-q:a", "5", str(mp3)], check=True)
            wav = Path(tmp) / "a.wav"
            subprocess.run(ghep.lenh_am_canh(mp3, wav, 3.0), check=True)
            with wave.open(str(wav)) as w:
                mau = struct.unpack("<%dh" % w.getnframes(), w.readframes(w.getnframes()))
                tan_so = w.getframerate()
            cua_so = tan_so // 20
            im_tuyet_doi = [i for i in range(0, len(mau) - cua_so, cua_so) if not any(mau[i:i + cua_so])]
            self.assertEqual(im_tuyet_doi, [])
            dinh_nen = max(abs(x) for x in mau[: tan_so // 2])
            self.assertLess(dinh_nen, 400, "lớp nền phải rất nhỏ (dưới khoảng −38 dBFS đỉnh)")

    def test_quiz_audio_command_adds_the_answer_voice_at_its_start(self):
        cmd = ghep.lenh_am_canh(Path("giong/canh-2.mp3"), Path("am-2.wav"), 14.0, giai=(Path("giong/canh-2-giai.mp3"), 9.537))
        joined = " ".join(cmd)
        self.assertEqual([cmd[i + 1] for i, x in enumerate(cmd) if x == "-i"][:2],
                         [str(Path("giong/canh-2.mp3")), str(Path("giong/canh-2-giai.mp3"))])
        self.assertIn(f"adelay={int(round(lich.DAN_DAU * 1000))}:all=1", joined)
        self.assertIn("adelay=9537:all=1", joined)
        self.assertEqual(joined.count("apad=whole_dur=14.000"), 2)
        self.assertIn("anoisesrc=", joined)
        self.assertIn("amix=inputs=3:duration=first:normalize=0", joined)
        self.assertEqual(cmd[cmd.index("-t") + 1], "14.000")

    @unittest.skipUnless(shutil.which("ffmpeg"), "máy không có FFmpeg")
    def test_quiz_scene_audio_has_the_answer_voice_at_bat_dau_giai(self):
        import struct
        import wave
        with tempfile.TemporaryDirectory() as tmp:
            hoi, giai = Path(tmp) / "hoi.mp3", Path(tmp) / "giai.mp3"
            for mp3, tan in ((hoi, 440), (giai, 880)):
                subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
                                f"sine=frequency={tan}:duration=0.6:sample_rate=24000", "-q:a", "5", str(mp3)], check=True)
            wav = Path(tmp) / "a.wav"
            subprocess.run(ghep.lenh_am_canh(hoi, wav, 5.0, giai=(giai, 3.2)), check=True)
            with wave.open(str(wav)) as w:
                mau = struct.unpack("<%dh" % w.getnframes(), w.readframes(w.getnframes()))
                tan_so = w.getframerate()
        self.assertAlmostEqual(len(mau) / tan_so, 5.0, delta=0.01)

        def dau_tieng(tu_giay):
            i = int(tu_giay * tan_so)
            while abs(mau[i]) < 3000:
                i += 1
            return i / tan_so

        self.assertAlmostEqual(dau_tieng(0.0), lich.DAN_DAU, delta=0.05)
        self.assertAlmostEqual(dau_tieng(2.0), 3.2, delta=0.05)
        im = [i for i in range(0, len(mau) - tan_so // 20, tan_so // 20) if not any(mau[i:i + tan_so // 20])]
        self.assertEqual(im, [], "vẫn có nhiễu nền, không im lặng tuyệt đối")
        self.assertLess(max(abs(x) for x in mau[int(1.8 * tan_so):int(3.1 * tan_so)]), 400, "đếm ngược chỉ có nhiễu nền")

    def test_video_command_uses_scene_fps_frames_and_30_fps_output(self):
        cmd = ghep.lenh_video(Path("am.txt"), Path(".khung/video.mp4"), lich.FPS, ".khung/phu-de.srt")
        self.assertEqual(cmd[cmd.index("-framerate") + 1], str(lich.FPS))
        self.assertEqual(cmd[cmd.index("-framerate") + 3], ".khung/anh/f%06d.jpg")
        self.assertEqual(cmd[cmd.index("-r") + 1], "30")
        self.assertIn("libx264", cmd)
        vf = cmd[cmd.index("-vf") + 1]
        self.assertTrue(vf.startswith("subtitles=.khung/phu-de.srt:fontsdir=.khung/fonts:force_style="), vf)
        self.assertIn("FontName=Itim", vf)

    def test_video_command_without_burned_subtitles_has_no_filter(self):
        cmd = ghep.lenh_video(Path("am.txt"), Path(".khung/video.mp4"), lich.FPS, None)
        self.assertNotIn("-vf", cmd)

    def test_video_command_burns_ass_karaoke_without_force_style(self):
        cmd = ghep.lenh_video(Path("am.txt"), Path(".khung/video.mp4"), lich.FPS, ".khung/phu-de.ass")
        vf = cmd[cmd.index("-vf") + 1]
        self.assertEqual(vf, "subtitles=.khung/phu-de.ass:fontsdir=.khung/fonts")

    def test_video_command_accepts_a_custom_force_style(self):
        cmd = ghep.lenh_video(Path("am.txt"), Path(".khung/video.mp4"), lich.FPS, ".khung/phu-de.srt", style="X=1")
        vf = cmd[cmd.index("-vf") + 1]
        self.assertIn("force_style='X=1'", vf)


class ForceStyleTest(unittest.TestCase):
    """`STYLE` cho `phu-de: hinh` nhận khung nền giống `.ass` karaoke khi `cat-dan` hoặc khổ `doc`."""

    def test_viet_tay_ngang_keeps_the_old_style(self):
        self.assertEqual(ghep._force_style("viet-tay", "ngang"), ghep.STYLE)

    def test_cat_dan_gets_a_box_with_be_vietnam_pro(self):
        style = ghep._force_style("cat-dan", "ngang")
        self.assertIn("BorderStyle=3", style)
        self.assertIn("BackColour=&H66000000&", style)
        self.assertIn("FontName=Be Vietnam Pro", style)

    def test_viet_tay_doc_gets_a_box_but_keeps_itim(self):
        style = ghep._force_style("viet-tay", "doc")
        self.assertIn("BorderStyle=3", style)
        self.assertIn("FontName=Itim", style)


class AssembleTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def project(self, name):
        thu_muc = Path(self.tmp.name) / name
        (thu_muc / ".khung" / "anh").mkdir(parents=True)
        return thu_muc

    def giong(self, thu_muc):
        out = []
        for cl in PLAN:
            mp3 = thu_muc / "giong" / f"canh-{cl.so}.mp3"
            mp3.parent.mkdir(exist_ok=True)
            mp3.write_bytes(b"ID3")
            out.append(lich.GiongInfo(mp3=mp3, giay=cl.giay_giong, moc_cau=[], uoc_luong=False, nguon="may"))
        return out

    def fake_run(self, thu_muc, calls, fail=None, kho=None):
        def run(cmd, **kwargs):
            calls.append((cmd, kwargs.get("cwd")))
            if cmd[0] == "ffprobe":
                mong = f"{kho.rong_xuat}x{kho.cao_xuat}" if kho is not None else ""
                return subprocess.CompletedProcess(cmd, 0, mong, "")
            if cmd[-1].endswith("video.mp4"):
                Path(cmd[-1] if Path(cmd[-1]).is_absolute() else Path(kwargs["cwd"]) / cmd[-1]).write_bytes(b"mp4")
            if fail:
                return subprocess.CompletedProcess(cmd, 1, "", "loi ffmpeg")
            return subprocess.CompletedProcess(cmd, 0, "", "")
        return run

    def test_folder_with_spaces_diacritics_and_apostrophe(self):
        thu_muc = self.project("Bài 5 – Sulfur dioxide (thử) 'a'")
        calls = []
        files = ghep.ghep_video(thu_muc, PLAN, self.giong(thu_muc), "hinh", run=self.fake_run(thu_muc, calls))
        self.assertEqual(files, ["video.mp4"])
        self.assertTrue((thu_muc / "video.mp4").is_file())
        listing = (thu_muc / ".khung" / "am.txt").read_text(encoding="utf-8")
        self.assertEqual(listing.count("file '"), 2)
        self.assertIn("Bài 5 – Sulfur dioxide (thử) '\\''a'\\''", listing)
        self.assertTrue(all(cwd == thu_muc for _, cwd in calls))
        self.assertEqual(len(calls), 3)

    def test_quiz_scene_audio_mixes_the_answer_voice(self):
        thu_muc = self.project("p-cau-hoi")
        cac_giong = self.giong(thu_muc)
        giai = thu_muc / "giong" / "canh-2-giai.mp3"
        giai.write_bytes(b"ID3")
        cac_giong[1].giai = lich.GiongInfo(mp3=giai, giay=1.0, moc_cau=[], uoc_luong=False, nguon="may")
        plan = [PLAN[0], canh_lich(2, 6.0, 9.0, 1.5, ["Tạm biệt."], [0.0])]
        plan[1].bat_dau_giai, plan[1].giay_giai, plan[1].cau_giai, plan[1].moc_cau_giai = 7.9, 1.0, ["Đáp án A."], [7.9]
        calls = []
        ghep.ghep_video(thu_muc, plan, cac_giong, "khong", run=self.fake_run(thu_muc, calls))
        am_1, am_2 = calls[0][0], calls[1][0]
        self.assertNotIn(str(giai), am_1)
        self.assertIn(str(giai), am_2)
        self.assertIn("adelay=7900:all=1", " ".join(am_2))

    def test_burned_subtitles_bundle_the_itim_font(self):
        thu_muc = self.project("p-font")
        calls = []
        ghep.ghep_video(thu_muc, PLAN, self.giong(thu_muc), "hinh", run=self.fake_run(thu_muc, calls))
        self.assertTrue((thu_muc / ".khung" / "fonts" / "Itim-Regular.ttf").is_file())
        joined = " ".join(calls[-1][0])
        self.assertIn("fontsdir=.khung/fonts", joined)
        self.assertIn("FontName=Itim", joined)

    def test_default_assembly_reads_and_writes_30_frames_per_second(self):
        thu_muc = self.project("p-fps")
        calls = []
        ghep.ghep_video(thu_muc, PLAN, self.giong(thu_muc), "khong", run=self.fake_run(thu_muc, calls))
        cmd = calls[-1][0]
        self.assertEqual(cmd[cmd.index("-framerate") + 1], "30")
        self.assertEqual(cmd[cmd.index("-r") + 1], "30")

    def test_output_rate_follows_the_capture_rate(self):
        cmd = ghep.lenh_video(Path("am.txt"), Path(".khung/video.mp4"), 25, None)
        self.assertEqual(cmd[cmd.index("-framerate") + 1], "25")
        self.assertEqual(cmd[cmd.index("-r") + 1], "25")

    def test_subtitle_modes(self):
        for mode, expect_srt, expect_burn in (("hinh", False, True), ("file", True, False), ("khong", False, False),
                                              ("karaoke", False, True)):
            with self.subTest(mode=mode):
                thu_muc = self.project(f"p-{mode}")
                calls = []
                files = ghep.ghep_video(thu_muc, PLAN, self.giong(thu_muc), mode, run=self.fake_run(thu_muc, calls))
                self.assertEqual((thu_muc / "phu-de.srt").is_file(), expect_srt)
                self.assertEqual("phu-de.srt" in files, expect_srt)
                joined = " ".join(calls[-1][0])
                self.assertEqual("subtitles=" in joined, expect_burn)

    def test_karaoke_mode_writes_ass_with_kf_tags_and_bundles_the_itim_font(self):
        thu_muc = self.project("p-karaoke")
        plan = [canh_lich(1, 0.0, 6.0, 4.0, ["Xin chao cac em."], [0.0])]
        plan[0].moc_tu = [
            {"t": lich.DAN_DAU + 0.0, "d": 0.3, "chu": "Xin", "khoa": "xin"},
            {"t": lich.DAN_DAU + 0.4, "d": 0.3, "chu": "chao", "khoa": "chao"},
            {"t": lich.DAN_DAU + 0.8, "d": 0.3, "chu": "cac", "khoa": "cac"},
            {"t": lich.DAN_DAU + 1.2, "d": 0.3, "chu": "em.", "khoa": "em"},
        ]
        calls = []
        ghep.ghep_video(thu_muc, plan, self.giong(thu_muc)[:1], "karaoke", run=self.fake_run(thu_muc, calls))
        ass_text = (thu_muc / ".khung" / "phu-de.ass").read_text(encoding="utf-8")
        self.assertIn("[Script Info]", ass_text)
        self.assertIn("[V4+ Styles]", ass_text)
        self.assertIn("[Events]", ass_text)
        self.assertIn(r"\kf", ass_text)
        self.assertTrue((thu_muc / ".khung" / "fonts" / "Itim-Regular.ttf").is_file())
        joined = " ".join(calls[-1][0])
        self.assertIn("subtitles=.khung/phu-de.ass:fontsdir=.khung/fonts", joined)
        self.assertNotIn("force_style", joined)

    def test_braces_are_escaped_only_in_burned_subtitles(self):
        plan = [canh_lich(1, 0.0, 6.0, 4.0, ["Tập hợp A = {1; 2; 3}."], [0.0])]
        hinh = self.project("p-ngoac-hinh")
        ghep.ghep_video(hinh, plan, self.giong(hinh)[:1], "hinh", run=self.fake_run(hinh, []))
        burned = (hinh / ".khung" / "phu-de.srt").read_text(encoding="utf-8")
        self.assertIn(r"Tập hợp A = \{1; 2; 3\}.", burned)
        tep = self.project("p-ngoac-file")
        ghep.ghep_video(tep, plan, self.giong(tep)[:1], "file", run=self.fake_run(tep, []))
        plain = (tep / "phu-de.srt").read_text(encoding="utf-8")
        self.assertIn("Tập hợp A = {1; 2; 3}.", plain)
        self.assertNotIn("\\{", plain)

    def test_backslash_cannot_become_a_libass_code_in_burned_subtitles(self):
        plan = [canh_lich(1, 0.0, 6.0, 4.0, [r"Gõ a\Nb và \h ở đây."], [0.0])]
        hinh = self.project("p-gach-nguoc")
        ghep.ghep_video(hinh, plan, self.giong(hinh)[:1], "hinh", run=self.fake_run(hinh, []))
        burned = (hinh / ".khung" / "phu-de.srt").read_text(encoding="utf-8")
        self.assertNotIn("\\", burned)
        self.assertIn("a⧵Nb", burned)

    def test_cat_dan_doc_hinh_bundles_be_vietnam_pro_and_burns_a_boxed_style(self):
        thu_muc = self.project("p-cat-dan-doc")
        k = kho_mod.Kho("doc", 720)
        calls = []
        ghep.ghep_video(thu_muc, PLAN, self.giong(thu_muc), "hinh", run=self.fake_run(thu_muc, calls, kho=k),
                        kho=k, chu_de="cat-dan")
        fonts_dir = thu_muc / ".khung" / "fonts"
        self.assertTrue((fonts_dir / "Itim-Regular.ttf").is_file())
        for duong_dan in FONT_CAT_DAN.values():
            self.assertTrue((fonts_dir / duong_dan.name).is_file())
        joined = " ".join(calls[-1][0])
        self.assertIn("BorderStyle=3", joined)
        self.assertIn("FontName=Be Vietnam Pro", joined)

    def test_karaoke_mode_with_doc_kho_bundles_be_vietnam_pro_when_cat_dan(self):
        thu_muc = self.project("p-cat-dan-karaoke")
        k = kho_mod.Kho("doc", 720)
        plan = [canh_lich(1, 0.0, 6.0, 4.0, ["Xin chao cac em."], [0.0])]
        calls = []
        ghep.ghep_video(thu_muc, plan, self.giong(thu_muc)[:1], "karaoke",
                        run=self.fake_run(thu_muc, calls, kho=k), kho=k, chu_de="cat-dan")
        fonts_dir = thu_muc / ".khung" / "fonts"
        for duong_dan in FONT_CAT_DAN.values():
            self.assertTrue((fonts_dir / duong_dan.name).is_file())
        ass_text = (thu_muc / ".khung" / "phu-de.ass").read_text(encoding="utf-8")
        style_line = next(l for l in ass_text.splitlines() if l.startswith("Style:"))
        self.assertEqual(style_line.split(",")[15], "3")  # BorderStyle
        self.assertIn("Be Vietnam Pro", ass_text)

    def test_karaoke_mode_with_viet_tay_ngang_still_only_bundles_itim(self):
        thu_muc = self.project("p-viet-tay-ngang")
        calls = []
        ghep.ghep_video(thu_muc, PLAN, self.giong(thu_muc), "karaoke", run=self.fake_run(thu_muc, calls))
        fonts_dir = thu_muc / ".khung" / "fonts"
        self.assertTrue((fonts_dir / "Itim-Regular.ttf").is_file())
        for duong_dan in FONT_CAT_DAN.values():
            self.assertFalse((fonts_dir / duong_dan.name).exists())

    def test_long_doc_sentence_warning_is_collected_into_canh_bao(self):
        thu_muc = self.project("p-canh-bao")
        k = kho_mod.Kho("doc", 720)
        cau = "Chu kì tỉ lệ với căn bậc hai của chiều dài dây, và không phụ thuộc vào biên độ dao động nhỏ."
        plan = [canh_lich(1, 0.0, 12.0, 8.0, [cau], [0.0])]
        canh_bao: list = []
        ghep.ghep_video(thu_muc, plan, self.giong(thu_muc)[:1], "karaoke",
                        run=self.fake_run(thu_muc, [], kho=k), kho=k, canh_bao=canh_bao)
        self.assertEqual(len(canh_bao), 1)
        self.assertIn("Cảnh 1", canh_bao[0])

    def test_ffmpeg_failure_is_a_dung_error(self):
        thu_muc = self.project("loi")
        with self.assertRaises(media.MediaError) as caught:
            ghep.ghep_video(thu_muc, PLAN, self.giong(thu_muc), "khong", run=self.fake_run(thu_muc, [], fail=True))
        self.assertEqual(caught.exception.step, "dung")
        self.assertIn("loi ffmpeg", str(caught.exception))

    def test_missing_ffmpeg_is_an_ffmpeg_error(self):
        thu_muc = self.project("khong-co")

        def run(cmd, **kwargs):
            raise FileNotFoundError("ffmpeg")

        with self.assertRaises(media.MediaError) as caught:
            ghep.ghep_video(thu_muc, PLAN, self.giong(thu_muc), "khong", run=run)
        self.assertEqual(caught.exception.step, "ffmpeg")

    def test_video_open_in_a_player_is_a_write_error_with_advice(self):
        thu_muc = self.project("dang-mo")
        (thu_muc / "video.mp4").write_bytes(b"cu")
        import os
        real_replace = os.replace

        def deny(src, dst):
            raise PermissionError("dang mo")

        os.replace = deny
        try:
            with self.assertRaises(media.MediaError) as caught:
                ghep.ghep_video(thu_muc, PLAN, self.giong(thu_muc), "khong", run=self.fake_run(thu_muc, []))
        finally:
            os.replace = real_replace
        self.assertEqual(caught.exception.step, "write")
        self.assertIn("trình phát", caught.exception.fix)


if __name__ == "__main__":
    unittest.main()
