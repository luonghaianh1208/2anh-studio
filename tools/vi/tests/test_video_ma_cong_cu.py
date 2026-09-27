"""Test công cụ dòng lệnh video_ma.py: mọi nhánh ra đúng một dòng JSON, không gọi giọng thật, Chromium/FFmpeg giả lập."""

import contextlib
import io
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))

import video_ma  # noqa: E402
from video_ma_parts import lich  # noqa: E402
from video_parts import media  # noqa: E402

MAU = (TOOLS_VI / "fixtures" / "video-mau" / "video.md").read_text(encoding="utf-8")
MOT_CANH = "---\ntieu-de: T\nmon: Toán\nlop: 8\n---\n\n## Cảnh 1\nloai: tieu-de\nchu: Xin chào\nloi: Xin chào các em.\n"
THI_NGHIEM_MUON = ("---\ntieu-de: T\nmon: Vật lí\nlop: 10\n---\n\n## Cảnh 1\nloai: tieu-de\nchu: Xin chào\nloi: Xin chào các em.\n\n"
                   "## Cảnh 2\nloai: thi-nghiem\nmau: li-con-lac-don\ntham-so: 0 chieu-dai 0.4\ntham-so: 20 chieu-dai 1.6\n"
                   "loi: Con lắc dài dần.\n")


class FakeBrowser:
    def __enter__(self):
        return object()

    def __exit__(self, *a):
        return False


def fake_chup(page, html, so_khung, fps, thu_muc, so_dau, ghi_log=None):
    thu_muc.mkdir(parents=True, exist_ok=True)
    for i in range(so_khung):
        (thu_muc / f"f{so_dau + i:06d}.jpg").write_bytes(b"x")
    return so_dau + so_khung


def fake_cuoi(page, html, duong_dan):
    duong_dan.parent.mkdir(parents=True, exist_ok=True)
    duong_dan.write_bytes(b"png")


def trinh_duyet_gia():
    return [mock.patch.object(video_ma, "co_ffmpeg", return_value=True),
            mock.patch.object(video_ma, "co_chromium", return_value=True),
            mock.patch.object(video_ma.chup, "trinh_duyet", side_effect=lambda: FakeBrowser()),
            mock.patch.object(video_ma.chup, "trang_moi", return_value=object()),
            mock.patch.object(video_ma.chup, "kiem_tran", return_value=[]),
            mock.patch.object(video_ma.chup, "doc_su_kien", return_value=[])]


def chay(args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = video_ma.main(args)
    lines = [l for l in out.getvalue().splitlines() if l.strip()]
    return code, lines, err.getvalue()


class CliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name) / "bai"
        self.dir.mkdir()

    def viet(self, text):
        (self.dir / "video.md").write_text(text, encoding="utf-8")

    def one_json(self, args):
        code, lines, _ = chay(args)
        self.assertEqual(len(lines), 1, lines)
        return code, json.loads(lines[0])

    def test_missing_folder_and_missing_file_are_input_errors(self):
        code, data = self.one_json([str(self.dir / "khong-co")])
        self.assertEqual((code, data["error"]["step"], data["ready"]), (1, "input", False))
        code, data = self.one_json([str(self.dir)])
        self.assertEqual((code, data["error"]["step"]), (1, "input"))
        self.assertIn("video-giai-thich.md", data["error"]["fix"])

    def test_parse_error_names_the_line(self):
        self.viet("---\ntieu-de: T\nmon: Toán\n---\n")
        code, data = self.one_json([str(self.dir)])
        self.assertEqual((code, data["error"]["step"]), (1, "parse"))
        self.assertIn("Dòng 4", data["error"]["message"])

    def test_scene_content_error_is_canh(self):
        self.viet(MOT_CANH.replace("chu: Xin chào", "chu: " + "a" * 95))
        code, data = self.one_json([str(self.dir)])
        self.assertEqual((code, data["error"]["step"]), (1, "canh"))
        self.assertIn("Cảnh 1", data["error"]["message"])

    def test_plan_only_checks_and_writes_nothing(self):
        self.viet(MAU)
        code, data = self.one_json([str(self.dir), "--plan-only"])
        self.assertEqual(code, 0)
        self.assertTrue(data["ready"])
        self.assertEqual(data["so_canh"], 8)
        self.assertEqual(data["files"], [])
        self.assertIsNone(data["error"])
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()), ["video.md"])

    def test_picture_fixture_passes_plan_only_offline(self):
        # Mẫu có hình, ảnh dọc tên có dấu cách và dấu (nguồn trong image_sources.json), ảnh có `nguon:`, thí nghiệm.
        mau_hinh = TOOLS_VI / "fixtures" / "video-hinh"
        code, data = self.one_json([str(mau_hinh), "--plan-only"])
        self.assertEqual((code, data["error"]), (0, None), data)
        self.assertEqual(data["so_canh"], 6)
        self.assertEqual(data["warnings"], [])
        text = (mau_hinh / "video.md").read_text(encoding="utf-8")
        for loai in ("tieu-de", "khai-niem", "y-tung-y", "minh-hoa", "anh", "thi-nghiem"):
            self.assertIn(f"loai: {loai}\n", text)
        self.assertTrue((mau_hinh / "anh" / "quả nặng dọc.png").is_file())
        self.assertFalse((mau_hinh / "xem-truoc").exists())

    def test_missing_ffmpeg_and_chromium_are_reported_before_any_voice(self):
        self.viet(MOT_CANH)
        with mock.patch.object(video_ma, "co_ffmpeg", return_value=False), \
                mock.patch.object(video_ma.giong, "lay_giong", side_effect=AssertionError("không được gọi giọng")):
            code, data = self.one_json([str(self.dir)])
        self.assertEqual((code, data["error"]["step"]), (1, "ffmpeg"))
        with mock.patch.object(video_ma, "co_ffmpeg", return_value=True), \
                mock.patch.object(video_ma, "co_chromium", return_value=False), \
                mock.patch.object(video_ma.giong, "lay_giong", side_effect=AssertionError("không được gọi giọng")):
            code, data = self.one_json([str(self.dir)])
        self.assertEqual((code, data["error"]["step"]), (1, "chromium"))
        self.assertIn("pptmaster.ps1", data["error"]["fix"])

    def test_voice_error_is_reported_as_giong(self):
        self.viet(MOT_CANH)
        boom = media.MediaError("giong", "mất mạng", "Có mạng rồi chạy lại.")
        with contextlib.ExitStack() as stack:
            for patch in trinh_duyet_gia():
                stack.enter_context(patch)
            stack.enter_context(mock.patch.object(video_ma.giong, "lay_giong", side_effect=boom))
            code, data = self.one_json([str(self.dir)])
        self.assertEqual((code, data["error"]["step"]), (1, "giong"))

    def test_relative_folder_reaches_voice_and_ffmpeg_as_absolute_path(self):
        self.viet(MOT_CANH)
        seen = []

        def ghi(so, loi, thu_muc_giong, *a):
            seen.append(thu_muc_giong)
            raise media.MediaError("giong", "dừng ở đây", "")

        old = Path.cwd()
        os.chdir(self.tmp.name)
        self.addCleanup(os.chdir, old)
        with contextlib.ExitStack() as stack:
            for patch in trinh_duyet_gia():
                stack.enter_context(patch)
            stack.enter_context(mock.patch.object(video_ma.giong, "lay_giong", side_effect=ghi))
            self.one_json(["bai"])
        self.assertTrue(seen and seen[0].is_absolute(), seen)
        self.assertEqual(seen[0], (Path(self.tmp.name) / "bai" / "giong").resolve())

    def test_unexpected_error_is_internal(self):
        self.viet(MOT_CANH)
        with mock.patch.object(video_ma, "co_ffmpeg", side_effect=RuntimeError("bất ngờ")):
            code, data = self.one_json([str(self.dir)])
        self.assertEqual((code, data["error"]["step"]), (1, "internal"))
        self.assertIn("bất ngờ", data["error"]["message"])

    def test_success_payload_and_temp_folder_is_cleaned(self):
        self.viet(MOT_CANH)
        giong = lich.GiongInfo(mp3=self.dir / "giong" / "canh-1.mp3", giay=3.0, moc_cau=[0.0], uoc_luong=False, nguon="may")

        class FakeBrowser:
            def __enter__(self_inner):
                return object()

            def __exit__(self_inner, *a):
                return False

        (self.dir / ".khung" / "anh").mkdir(parents=True)
        (self.dir / ".khung" / "anh" / "f000000.jpg").write_bytes(b"khung-cu")

        def fake_chup(page, html, so_khung, fps, thu_muc, so_dau, ghi_log=None):
            self.assertFalse((thu_muc / "f000000.jpg").exists(), "khung cũ phải bị dọn trước khi chụp")
            for i in range(so_khung):
                (thu_muc / f"f{so_dau + i:06d}.jpg").write_bytes(b"x")
            return so_dau + so_khung

        def fake_ghep(thu_muc, cac_lich, cac_giong, phu_de, **kw):
            (thu_muc / "video.mp4").write_bytes(b"mp4")
            return ["video.mp4"]

        with mock.patch.object(video_ma, "co_ffmpeg", return_value=True), \
                mock.patch.object(video_ma, "co_chromium", return_value=True), \
                mock.patch.object(video_ma.giong, "lay_giong", return_value=giong), \
                mock.patch.object(video_ma.chup, "trinh_duyet", return_value=FakeBrowser()), \
                mock.patch.object(video_ma.chup, "trang_moi", return_value=object()), \
                mock.patch.object(video_ma.chup, "kiem_tran", return_value=[]), \
                mock.patch.object(video_ma.chup, "chup_canh", side_effect=fake_chup), \
                mock.patch.object(video_ma.chup, "doc_su_kien", return_value=[]), \
                mock.patch.object(video_ma.ghep, "ghep_video", side_effect=fake_ghep):
            code, data = self.one_json([str(self.dir)])
        self.assertEqual(code, 0, data)
        self.assertTrue(data["ready"])
        self.assertEqual(data["files"], ["video.mp4"])
        self.assertEqual(data["so_canh"], 1)
        self.assertEqual(data["giong"], "may")
        self.assertEqual(data["phong_cach"], "viet-tay")
        self.assertAlmostEqual(data["thoi_luong_giay"], lich.thoi_luong_canh(3.0), delta=0.01)
        self.assertFalse((self.dir / ".khung").exists())

    def test_thu_muc_khung_tam_duoc_don(self):
        self.test_success_payload_and_temp_folder_is_cleaned()

    def test_overflow_is_a_canh_error_before_capturing(self):
        self.viet(MOT_CANH)
        giong = lich.GiongInfo(mp3=self.dir / "x.mp3", giay=3.0, moc_cau=[0.0], uoc_luong=False, nguon="co-san")

        class FakeBrowser:
            def __enter__(self_inner):
                return object()

            def __exit__(self_inner, *a):
                return False

        with mock.patch.object(video_ma, "co_ffmpeg", return_value=True), \
                mock.patch.object(video_ma, "co_chromium", return_value=True), \
                mock.patch.object(video_ma.giong, "lay_giong", side_effect=AssertionError("không được gọi giọng trước khi kiểm tràn")), \
                mock.patch.object(video_ma.chup, "trinh_duyet", return_value=FakeBrowser()), \
                mock.patch.object(video_ma.chup, "trang_moi", return_value=object()), \
                mock.patch.object(video_ma.chup, "kiem_tran", return_value=["chu"]), \
                mock.patch.object(video_ma.chup, "chup_canh", side_effect=AssertionError("không được chụp")):
            code, data = self.one_json([str(self.dir)])
        self.assertEqual((code, data["error"]["step"]), (1, "canh"))
        self.assertIn("chu", data["error"]["message"])
        self.assertIn("Cảnh 1", data["error"]["message"])
        self.assertFalse((self.dir / ".khung").exists())

    def test_preview_needs_no_voice_and_no_ffmpeg(self):
        self.viet(MAU)

        class FakeBrowser:
            def __enter__(self_inner):
                return object()

            def __exit__(self_inner, *a):
                return False

        def fake_cuoi(page, html, duong_dan):
            duong_dan.parent.mkdir(parents=True, exist_ok=True)
            duong_dan.write_bytes(b"png")

        with mock.patch.object(video_ma, "co_ffmpeg", return_value=False), \
                mock.patch.object(video_ma, "co_chromium", return_value=True), \
                mock.patch.object(video_ma.giong, "lay_giong", side_effect=AssertionError("không được gọi giọng")), \
                mock.patch.object(video_ma.chup, "trinh_duyet", return_value=FakeBrowser()), \
                mock.patch.object(video_ma.chup, "trang_moi", return_value=object()), \
                mock.patch.object(video_ma.chup, "kiem_tran", return_value=[]), \
                mock.patch.object(video_ma.chup, "chup_cuoi", side_effect=fake_cuoi):
            code, data = self.one_json([str(self.dir), "--xem-truoc"])
        self.assertEqual(code, 0, data)
        self.assertEqual(data["files"], [f"xem-truoc/canh-{i}.png" for i in range(1, 9)])
        self.assertTrue((self.dir / "xem-truoc" / "canh-8.png").is_file())

    def test_preview_reaches_the_last_late_parameter_mark(self):
        self.viet(THI_NGHIEM_MUON)
        trang = {}

        def cuoi(page, html, duong_dan):
            trang[duong_dan.name] = html
            fake_cuoi(page, html, duong_dan)

        with contextlib.ExitStack() as stack:
            for patch in trinh_duyet_gia():
                stack.enter_context(patch)
            stack.enter_context(mock.patch.object(video_ma.chup, "chup_cuoi", side_effect=cuoi))
            code, data = self.one_json([str(self.dir), "--xem-truoc"])
        self.assertEqual(code, 0, data)

        def thoi_luong(html):
            return float(re.search(r'"thoiLuong": ([0-9.]+)', html).group(1))

        self.assertGreaterEqual(thoi_luong(trang["canh-2.png"]), 20.0 + lich.DAN_DAU)
        self.assertAlmostEqual(thoi_luong(trang["canh-1.png"]), lich.thoi_luong_canh(8.0), delta=0.01)

    def test_preview_clears_old_images(self):
        self.viet(MOT_CANH)
        cu = self.dir / "xem-truoc" / "canh-9.png"
        cu.parent.mkdir()
        cu.write_bytes(b"cu")
        with contextlib.ExitStack() as stack:
            for patch in trinh_duyet_gia():
                stack.enter_context(patch)
            stack.enter_context(mock.patch.object(video_ma.chup, "chup_cuoi", side_effect=fake_cuoi))
            code, data = self.one_json([str(self.dir), "--xem-truoc"])
        self.assertEqual(code, 0, data)
        self.assertEqual(sorted(p.name for p in (self.dir / "xem-truoc").iterdir()), ["canh-1.png"])

    def test_capture_failure_is_a_dung_error_with_the_text(self):
        self.viet(MOT_CANH)
        giong = lich.GiongInfo(mp3=self.dir / "x.mp3", giay=3.0, moc_cau=[0.0], uoc_luong=False, nguon="may")
        with contextlib.ExitStack() as stack:
            for patch in trinh_duyet_gia():
                stack.enter_context(patch)
            stack.enter_context(mock.patch.object(video_ma.giong, "lay_giong", return_value=giong))
            stack.enter_context(mock.patch.object(video_ma.chup, "chup_canh", side_effect=RuntimeError("Timeout 30000ms exceeded")))
            code, data = self.one_json([str(self.dir)])
        self.assertEqual((code, data["error"]["step"]), (1, "dung"))
        self.assertIn("Timeout 30000ms exceeded", data["error"]["message"])
        with contextlib.ExitStack() as stack:
            for patch in trinh_duyet_gia():
                stack.enter_context(patch)
            stack.enter_context(mock.patch.object(video_ma.chup, "chup_cuoi", side_effect=RuntimeError("page crashed")))
            code, data = self.one_json([str(self.dir), "--xem-truoc"])
        self.assertEqual((code, data["error"]["step"]), (1, "dung"))
        self.assertIn("page crashed", data["error"]["message"])

    def test_failing_capture_range_is_dung_naming_the_scene_and_cleans_the_frames(self):
        self.viet(MOT_CANH)
        giong = lich.GiongInfo(mp3=self.dir / "x.mp3", giay=3.0, moc_cau=[0.0], uoc_luong=False, nguon="may")

        def hong(cong_viec):
            (Path(cong_viec["thu_muc_anh"]) / "f000000.jpg").write_bytes(b"x")
            raise RuntimeError("Target page crashed")

        with contextlib.ExitStack() as stack:
            for patch in trinh_duyet_gia():
                stack.enter_context(patch)
            stack.enter_context(mock.patch.object(video_ma.giong, "lay_giong", return_value=giong))
            stack.enter_context(mock.patch.object(video_ma.chup, "chup_dai", side_effect=hong))
            stack.enter_context(mock.patch.object(video_ma.ghep, "ghep_video", side_effect=AssertionError("không được ghép")))
            code, data = self.one_json([str(self.dir)])
        self.assertEqual((code, data["error"]["step"]), (1, "dung"))
        self.assertIn("cảnh 1", data["error"]["message"])
        self.assertIn("Target page crashed", data["error"]["message"])
        self.assertFalse((self.dir / ".khung").exists())

    def test_build_hands_every_scene_to_the_parallel_capture(self):
        self.viet(MOT_CANH + "\n## Cảnh 2\nloai: tieu-de\nchu: Tạm biệt\nloi: Tạm biệt các em.\n")
        giong = lich.GiongInfo(mp3=self.dir / "x.mp3", giay=3.0, moc_cau=[0.0], uoc_luong=False, nguon="may")
        seen = {}

        def gia(cac_du, models_js, so_khung, fps, thu_muc_anh, so_tt, **kw):
            seen.update(cac_du=cac_du, models_js=models_js, so_khung=so_khung, fps=fps, thu_muc_anh=thu_muc_anh, so_tt=so_tt)

        with contextlib.ExitStack() as stack:
            for patch in trinh_duyet_gia():
                stack.enter_context(patch)
            stack.enter_context(mock.patch.object(video_ma.giong, "lay_giong", return_value=giong))
            stack.enter_context(mock.patch.object(video_ma.chup, "so_tien_trinh", return_value=3))
            stack.enter_context(mock.patch.object(video_ma.chup, "chup_song_song", side_effect=gia))
            stack.enter_context(mock.patch.object(video_ma.ghep, "ghep_video", return_value=["video.mp4"]))
            code, lines, err = chay([str(self.dir)])
        data = json.loads(lines[0])
        self.assertEqual(code, 0, data)
        self.assertEqual([du["so"] for du in seen["cac_du"]], [1, 2])
        self.assertEqual([du["co"]["lauBang"] for du in seen["cac_du"]], [False, True])
        n = round(lich.thoi_luong_canh(3.0) * 30)
        self.assertEqual((seen["so_khung"], seen["fps"], seen["so_tt"]), ([n, n], 30, 3))
        self.assertEqual(Path(seen["thu_muc_anh"]), self.dir / ".khung" / "anh")
        json.dumps([seen["cac_du"], seen["models_js"]])
        self.assertIn("2 tiến trình", err)

    def test_stale_separate_subtitle_is_removed_when_not_in_file_mode(self):
        self.viet(MOT_CANH)
        (self.dir / "phu-de.srt").write_text("cu", encoding="utf-8")
        giong = lich.GiongInfo(mp3=self.dir / "x.mp3", giay=3.0, moc_cau=[0.0], uoc_luong=False, nguon="may")
        with contextlib.ExitStack() as stack:
            for patch in trinh_duyet_gia():
                stack.enter_context(patch)
            stack.enter_context(mock.patch.object(video_ma.giong, "lay_giong", return_value=giong))
            stack.enter_context(mock.patch.object(video_ma.chup, "chup_canh", side_effect=fake_chup))
            stack.enter_context(mock.patch.object(video_ma.ghep, "ghep_video", return_value=["video.mp4"]))
            code, data = self.one_json([str(self.dir)])
        self.assertEqual(code, 0, data)
        self.assertFalse((self.dir / "phu-de.srt").exists())

    def test_help_and_bad_arguments_still_yield_one_json_line(self):
        for args in (["--help"], ["-h"], [], [str(self.dir), "--bua"]):
            with self.subTest(args=args):
                code, lines, _ = chay(args)
                self.assertEqual(len(lines), 1, lines)
                data = json.loads(lines[0])
                self.assertEqual((code, data["error"]["step"]), (1, "input"))
                self.assertIn("--plan-only", data["error"]["fix"])

    def test_json_line_is_valid_even_with_vietnamese_text(self):
        self.viet(MOT_CANH.replace("Xin chào các em.", "Nhờ ướt nhẫm quyết định."))
        code, lines, _ = chay([str(self.dir), "--plan-only"])
        self.assertEqual(len(lines), 1)
        json.loads(lines[0])

    def quiz_build(self, tts):
        """Dựng video một cảnh câu hỏi với giọng máy giả `tts` (lay_giong thật, không mạng); trả (mã, JSON, giọng)."""
        self.viet(CAU_HOI)
        that = video_ma.giong.lay_giong
        seen = {}

        def lay(*a, **kw):
            return that(*a, tong_hop=tts, do_dai=lambda p: 3.0, **kw)

        def ghep_gia(thu_muc, cac_lich, cac_giong, phu_de, **kw):
            seen["lich"], seen["giong"] = cac_lich, cac_giong
            return ["video.mp4"]

        with contextlib.ExitStack() as stack:
            for patch in trinh_duyet_gia():
                stack.enter_context(patch)
            stack.enter_context(mock.patch.object(video_ma.giong, "lay_giong", side_effect=lay))
            stack.enter_context(mock.patch.object(video_ma.chup, "chup_canh", side_effect=fake_chup))
            stack.enter_context(mock.patch.object(video_ma.ghep, "ghep_video", side_effect=ghep_gia))
            code, data = self.one_json([str(self.dir)])
        return code, data, seen

    def test_quiz_scene_gets_a_second_voice_for_the_answer(self):
        calls = []

        def tts(text, voice, rate, out_path):
            calls.append(text)
            Path(out_path).write_bytes(b"ID3" + text.encode("utf-8"))
            return [0.0]

        code, data, seen = self.quiz_build(tts)
        self.assertEqual(code, 0, data)
        self.assertEqual(calls, ["Câu hỏi đây.", "Đáp án B."])
        self.assertTrue((self.dir / "giong" / "canh-1.mp3").is_file())
        self.assertTrue((self.dir / "giong" / "canh-1-giai.mp3").is_file())
        g = seen["giong"][0]
        self.assertEqual(g.giai.mp3, self.dir / "giong" / "canh-1-giai.mp3")
        self.assertAlmostEqual(seen["lich"][0].bat_dau_giai, lich.DAN_DAU + 3.0 + 3 + lich.CHO_GIAI)
        self.assertAlmostEqual(data["thoi_luong_giay"], lich.thoi_luong_cau_hoi(3.0, 3, 3.0), delta=0.01)

    def test_teacher_question_file_with_failing_answer_voice_names_the_answer_file(self):
        (self.dir / "giong").mkdir()
        (self.dir / "giong" / "canh-1.mp3").write_bytes(b"ID3thay-co")

        def tts(text, voice, rate, out_path):
            raise media.MediaError("giong", "Không tạo được giọng đọc (thường do mất mạng): timeout", video_ma.giong.FIX_GIONG)

        code, data, _ = self.quiz_build(tts)
        self.assertEqual((code, data["error"]["step"]), (1, "giong"))
        self.assertIn("canh-1-giai.mp3", data["error"]["message"])
        self.assertIn("canh-1-giai.mp3", data["error"]["fix"])
        self.assertEqual((self.dir / "giong" / "canh-1.mp3").read_bytes(), b"ID3thay-co")

    def test_teacher_answer_file_is_used_and_not_overwritten(self):
        (self.dir / "giong").mkdir()
        (self.dir / "giong" / "canh-1-giai.mp3").write_bytes(b"ID3giai-thay-co")
        calls = []

        def tts(text, voice, rate, out_path):
            calls.append(text)
            Path(out_path).write_bytes(b"ID3may")
            return [0.0]

        code, data, seen = self.quiz_build(tts)
        self.assertEqual(code, 0, data)
        self.assertEqual(calls, ["Câu hỏi đây."])
        self.assertEqual((self.dir / "giong" / "canh-1-giai.mp3").read_bytes(), b"ID3giai-thay-co")
        self.assertEqual(seen["giong"][0].giai.nguon, "co-san")
        self.assertEqual(data["giong"], "hon-hop")

    def test_quiz_plan_only_passes(self):
        self.viet(CAU_HOI)
        code, data = self.one_json([str(self.dir), "--plan-only"])
        self.assertEqual((code, data["error"]), (0, None), data)


CAU_HOI = ("---\ntieu-de: T\nmon: Vật lí\nlop: 10\n---\n\n## Cảnh 1\nloai: cau-hoi\ncau-hoi: Chu kì đổi thế nào?\n"
           "lua-chon: Giảm\nlua-chon: Tăng\ndap-an: B\ncho: 3\ngiai-thich: Dây dài hơn thì chu kì lớn hơn.\n"
           "loi-giai: Đáp án B.\nloi: Câu hỏi đây.\n")


if __name__ == "__main__":
    unittest.main()
