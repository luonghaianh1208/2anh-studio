"""Test phụ đề karaoke: file .ass với \\kf theo mốc từng từ. Không chạy FFmpeg thật trừ lớp cuối."""

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))

from video_ma_parts import ghep, karaoke, lich  # noqa: E402
from video_ma_parts.phong import FONT as ITIM_FONT  # noqa: E402
from video_parts import srt  # noqa: E402

_KF_RE = re.compile(r"\\kf(\d+)")
_KF_TAG_RE = re.compile(r"\{\\kf\d+\}")
# Dialogue: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
_DIALOGUE_RE = re.compile(r"^Dialogue: \d+,(\d+:\d{2}:\d{2}\.\d{2}),(\d+:\d{2}:\d{2}\.\d{2}),"
                          r"[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,(.*)$")


def _tu(t, d, chu):
    return {"t": t, "d": d, "chu": chu, "khoa": chu.lower()}


def canh(so, bat_dau, giay_giong, cau, moc_cau, tu):
    return lich.CanhLich(so=so, bat_dau=bat_dau, thoi_luong=lich.DAN_DAU + giay_giong + 0.6, so_khung=1,
                         giay_giong=giay_giong, cau=cau, moc_cau=moc_cau, moc_cau_giong=[m - lich.DAN_DAU for m in moc_cau],
                         uoc_luong=False, moc_tu=tu)


def _thoi_gian_giay(nhan: str) -> float:
    gio, phut, giay = nhan.split(":")
    s, cs = giay.split(".")
    return int(gio) * 3600 + int(phut) * 60 + int(s) + int(cs) / 100


def _dialogues(text: str) -> list:
    return [l for l in text.splitlines() if l.startswith("Dialogue:")]


def _hien_thi(dialogue_text: str) -> str:
    """Chữ hiển thị của một Dialogue: bỏ thẻ `\\kf`, đổi `\\N` (xuống dòng) thành khoảng trắng."""
    return _KF_TAG_RE.sub("", dialogue_text).replace("\\N", " ")


DATA = Path(__file__).resolve().parent / "data"


class TuongThichVi11Test(unittest.TestCase):
    """`viet-tay` khổ ngang phải ra `.ass` giống hệt vi.11 (chụp từ `tao_ass` trước khi thêm khung/khổ dọc ở Task 7)."""

    def test_viet_tay_ngang_ass_is_byte_identical_to_the_vi11_capture(self):
        cl1 = canh(1, 0.0, 4.0, ["Xin chao cac em."], [lich.DAN_DAU], [
            {"t": lich.DAN_DAU + 0.0, "d": 0.3, "chu": "Xin", "khoa": "xin"},
            {"t": lich.DAN_DAU + 0.4, "d": 0.3, "chu": "chao", "khoa": "chao"},
            {"t": lich.DAN_DAU + 0.9, "d": 0.3, "chu": "cac", "khoa": "cac"},
            {"t": lich.DAN_DAU + 1.3, "d": 0.3, "chu": "em.", "khoa": "em"},
        ])
        cau_text = "Thứ nhất, dây dài hơn thì chu kì lớn hơn."
        loi_may = ["Thứ", "nhất", "dây", "dài", "hơn", "thì", "chu", "kì", "lớn", "hơn"]
        tu2 = [{"t": lich.DAN_DAU + i * 0.3, "d": 0.25, "chu": w, "khoa": w.lower()} for i, w in enumerate(loi_may)]
        cl2 = canh(2, 10.0, len(loi_may) * 0.3, [cau_text], [lich.DAN_DAU], tu2)
        cau_long = "Chu kì tỉ lệ với căn bậc hai của chiều dài dây."
        tu_van = cau_long.rstrip(".").split()
        tu3 = [{"t": lich.DAN_DAU + i * 0.3, "d": 0.25, "chu": w, "khoa": w.lower()} for i, w in enumerate(tu_van)]
        cl3 = canh(3, 20.0, len(tu_van) * 0.3, [cau_long], [lich.DAN_DAU], tu3)
        cl4 = canh(4, 30.0, 1.0, ["Tap hop A = {1}."], [lich.DAN_DAU], [
            {"t": lich.DAN_DAU + 0.0, "d": 0.2, "chu": "Tap", "khoa": "tap"},
            {"t": lich.DAN_DAU + 0.3, "d": 0.2, "chu": "hop", "khoa": "hop"},
            {"t": lich.DAN_DAU + 0.6, "d": 0.2, "chu": "A", "khoa": "a"},
            {"t": lich.DAN_DAU + 0.8, "d": 0.2, "chu": "={1}.", "khoa": "1"},
        ])
        text = karaoke.tao_ass([cl1, cl2, cl3, cl4])
        mong_doi = (DATA / "karaoke_viet_tay_ngang.ass").read_text(encoding="utf-8")
        self.assertEqual(text, mong_doi)


class CauTrucTest(unittest.TestCase):
    def test_has_all_three_required_sections(self):
        text = karaoke.tao_ass([])
        for section in ("[Script Info]", "[V4+ Styles]", "[Events]"):
            self.assertIn(section, text)
        self.assertIn("PlayResX: 1280", text)
        self.assertIn("PlayResY: 720", text)
        self.assertIn("WrapStyle: 0", text)

    def test_style_uses_itim_yellow_spoken_and_white_unspoken(self):
        text = karaoke.tao_ass([])
        style_line = next(l for l in text.splitlines() if l.startswith("Style:"))
        self.assertIn("Itim", style_line)
        self.assertIn("&H0000D7FF", style_line)
        self.assertIn("&H00FFFFFF", style_line)
        self.assertIn("MarginV", text)
        fields = style_line.split(",")
        # Format: Name,Fontname,Fontsize,Primary,Secondary,Outline,Back,Bold,Italic,Underline,
        # StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
        # PlayResX/Y = 1280x720 (không phải mặc định libass 384x288 của đường SRT cũ), nên FontSize/Outline/
        # MarginV/Spacing phải nhân theo tỉ lệ 720/288 = 2.5 mới hiển thị đúng cỡ chữ như bản SRT cũ.
        self.assertEqual(fields[2], "40")  # Fontsize = 16 * 2.5
        self.assertEqual(fields[-2], "55")  # MarginV = 22 * 2.5
        self.assertEqual(fields[16], "3")  # Outline width ~= 1.5 * 2.5


class KfSumTest(unittest.TestCase):
    def test_kf_total_matches_sentence_duration_in_centiseconds(self):
        cl = canh(1, 0.0, 4.0, ["Xin chao cac em."],
                  [lich.DAN_DAU], [
                      _tu(0.0, 0.3, "Xin"), _tu(0.4, 0.3, "chao"),
                      _tu(0.9, 0.3, "cac"), _tu(1.3, 0.3, "em."),
                  ])
        # moc_tu trong CanhLich đã cộng DAN_DAU theo lich.dung_lich thật
        cl.moc_tu = [{"t": lich.DAN_DAU + w["t"], "d": w["d"], "chu": w["chu"], "khoa": w["chu"].lower()} for w in cl.moc_tu]
        text = karaoke.tao_ass([cl])
        dialogues = [l for l in text.splitlines() if l.startswith("Dialogue:")]
        self.assertEqual(len(dialogues), 1)
        match = _DIALOGUE_RE.match(dialogues[0])
        self.assertIsNotNone(match)
        start, end = _thoi_gian_giay(match.group(1)), _thoi_gian_giay(match.group(2))
        du_kf = sum(int(n) for n in _KF_RE.findall(match.group(3)))
        du_that = round((end - start) * 100)
        self.assertLessEqual(abs(du_kf - du_that), 1)

    def test_multiple_sentences_each_get_their_own_dialogue_with_matching_totals(self):
        cl = canh(1, 10.0, 5.0, ["Cau mot day.", "Cau hai ngan hon."],
                  [lich.DAN_DAU, lich.DAN_DAU + 2.0],
                  [
                      {"t": lich.DAN_DAU + 0.0, "d": 0.3, "chu": "Cau", "khoa": "cau"},
                      {"t": lich.DAN_DAU + 0.4, "d": 0.3, "chu": "mot", "khoa": "mot"},
                      {"t": lich.DAN_DAU + 0.8, "d": 0.3, "chu": "day.", "khoa": "day"},
                      {"t": lich.DAN_DAU + 2.0, "d": 0.3, "chu": "Cau", "khoa": "cau"},
                      {"t": lich.DAN_DAU + 2.4, "d": 0.3, "chu": "hai", "khoa": "hai"},
                      {"t": lich.DAN_DAU + 2.8, "d": 0.3, "chu": "ngan", "khoa": "ngan"},
                      {"t": lich.DAN_DAU + 3.2, "d": 0.3, "chu": "hon.", "khoa": "hon"},
                  ])
        text = karaoke.tao_ass([cl])
        dialogues = [l for l in text.splitlines() if l.startswith("Dialogue:")]
        self.assertEqual(len(dialogues), 2)
        for line in dialogues:
            match = _DIALOGUE_RE.match(line)
            start, end = _thoi_gian_giay(match.group(1)), _thoi_gian_giay(match.group(2))
            du_kf = sum(int(n) for n in _KF_RE.findall(match.group(3)))
            self.assertLessEqual(abs(du_kf - round((end - start) * 100)), 1)
        # mốc toàn cục cộng thêm bat_dau của cảnh (10.0 giây)
        first_start = _thoi_gian_giay(_DIALOGUE_RE.match(dialogues[0]).group(1))
        self.assertAlmostEqual(first_start, 10.0 + lich.DAN_DAU, delta=0.02)


class ThoatKyTuTest(unittest.TestCase):
    def test_braces_and_backslash_in_words_are_escaped(self):
        cl = canh(1, 0.0, 1.0, ["Tap hop A = {1}."],
                  [lich.DAN_DAU],
                  [
                      {"t": lich.DAN_DAU + 0.0, "d": 0.2, "chu": "Tap", "khoa": "tap"},
                      {"t": lich.DAN_DAU + 0.3, "d": 0.2, "chu": "hop", "khoa": "hop"},
                      {"t": lich.DAN_DAU + 0.6, "d": 0.2, "chu": "A", "khoa": "a"},
                      {"t": lich.DAN_DAU + 0.8, "d": 0.2, "chu": "={1}.", "khoa": "1"},
                  ])
        text = karaoke.tao_ass([cl])
        dialogue = next(l for l in text.splitlines() if l.startswith("Dialogue:"))
        self.assertIn(r"\{1\}", dialogue)
        self.assertNotIn("={1}.", dialogue)


    def test_dau_gach_nguoc_khong_thanh_ma_dieu_khien_libass(self):
        # libass không có thoát `\\`: `\N`, `\h` trong chữ của thầy cô sẽ thành xuống dòng / khoảng trắng cứng.
        cl = canh(1, 0.0, 1.0, [r"Gõ a\Nb và \h nhé."], [lich.DAN_DAU], [])
        dialogue = next(l for l in karaoke.tao_ass([cl]).splitlines() if l.startswith("Dialogue:"))
        chu = _DIALOGUE_RE.match(dialogue).group(3)
        self.assertEqual(_hien_thi(chu), "Gõ a⧵Nb và ⧵h nhé.")
        self.assertNotIn("\\N", _KF_TAG_RE.sub("", chu))
        self.assertNotIn("\\h", chu)
        self.assertNotIn("\\\\", chu)


class ChuKichBanTest(unittest.TestCase):
    """Chữ hiển thị karaoke phải là token gốc của kịch bản (giữ dấu câu), không phải chữ giọng máy đọc ra."""

    def test_punctuation_from_the_script_is_kept_even_when_tts_words_lack_it(self):
        cau_text = "Thứ nhất, dây dài hơn thì chu kì lớn hơn."
        # Giọng máy (WordBoundary) không bao giờ trả dấu câu kèm theo từ.
        loi_may = ["Thứ", "nhất", "dây", "dài", "hơn", "thì", "chu", "kì", "lớn", "hơn"]
        tu = [{"t": lich.DAN_DAU + i * 0.3, "d": 0.25, "chu": w, "khoa": w.lower()} for i, w in enumerate(loi_may)]
        cl = canh(1, 0.0, len(loi_may) * 0.3, [cau_text], [lich.DAN_DAU], tu)
        text = karaoke.tao_ass([cl])
        dialogues = _dialogues(text)
        self.assertGreaterEqual(len(dialogues), 1)
        hien_thi = " ".join(_hien_thi(_DIALOGUE_RE.match(d).group(3)) for d in dialogues)
        self.assertIn("nhất,", hien_thi)
        self.assertIn("hơn.", hien_thi)
        self.assertNotIn("nhất dây", hien_thi)  # dấu phẩy sau "nhất" không bị rơi mất

        for d in dialogues:
            match = _DIALOGUE_RE.match(d)
            start, end = _thoi_gian_giay(match.group(1)), _thoi_gian_giay(match.group(2))
            du_kf = sum(int(n) for n in _KF_RE.findall(match.group(3)))
            self.assertLessEqual(abs(du_kf - round((end - start) * 100)), 1)

    def test_a_script_number_spoken_as_several_tts_events_does_not_crash_and_keeps_totals(self):
        cau_text = "Số đo là 1500 đơn vị"
        # "1500" được giọng máy đọc thành 4 sự kiện đánh vần rời rạc, không khớp chữ được với token "1500".
        loi_may = ["Số", "đo", "là", "một", "nghìn", "năm", "trăm", "đơn", "vị"]
        tu = [{"t": lich.DAN_DAU + i * 0.2, "d": 0.15, "chu": w, "khoa": w.lower()} for i, w in enumerate(loi_may)]
        cl = canh(1, 0.0, len(loi_may) * 0.2, [cau_text], [lich.DAN_DAU], tu)
        text = karaoke.tao_ass([cl])  # không được ném lỗi
        dialogues = _dialogues(text)
        self.assertGreaterEqual(len(dialogues), 1)
        hien_thi = " ".join(_hien_thi(_DIALOGUE_RE.match(d).group(3)) for d in dialogues)
        self.assertIn("1500", hien_thi)  # giữ đúng chữ số của kịch bản, không phải chữ đánh vần
        for d in dialogues:
            match = _DIALOGUE_RE.match(d)
            start, end = _thoi_gian_giay(match.group(1)), _thoi_gian_giay(match.group(2))
            du_kf = sum(int(n) for n in _KF_RE.findall(match.group(3)))
            self.assertLessEqual(abs(du_kf - round((end - start) * 100)), 1)

    def test_answer_sentence_dialogue_starts_exactly_at_the_answer_offset(self):
        """Cảnh câu hỏi: đoạn lời giải (`cau_giai`) vẫn bắt đầu đúng `bat_dau_giai`, không đổi so với trước."""
        bat_dau_giai = round(lich.DAN_DAU + 1.2 + 2.0 + lich.CHO_GIAI, 3)  # dẫn đầu + hỏi + chờ + khoảng lặng
        cl = lich.CanhLich(
            so=1, bat_dau=20.0, thoi_luong=10.0, so_khung=1, giay_giong=1.2,
            cau=["Cau hoi la gi"], moc_cau=[lich.DAN_DAU], moc_cau_giong=[0.0], uoc_luong=False,
            moc_tu=[
                {"t": lich.DAN_DAU + 0.0, "d": 0.25, "chu": "Cau", "khoa": "cau"},
                {"t": lich.DAN_DAU + 0.3, "d": 0.25, "chu": "hoi", "khoa": "hoi"},
                {"t": lich.DAN_DAU + 0.6, "d": 0.25, "chu": "la", "khoa": "la"},
                {"t": lich.DAN_DAU + 0.9, "d": 0.25, "chu": "gi", "khoa": "gi"},
                {"t": bat_dau_giai + 0.0, "d": 0.25, "chu": "Dap", "khoa": "dap"},
                {"t": bat_dau_giai + 0.3, "d": 0.25, "chu": "an", "khoa": "an"},
                {"t": bat_dau_giai + 0.6, "d": 0.25, "chu": "la", "khoa": "la"},
                {"t": bat_dau_giai + 0.9, "d": 0.25, "chu": "B", "khoa": "b"},
            ],
            giay_giai=1.2, bat_dau_giai=bat_dau_giai, cau_giai=["Dap an la B"], moc_cau_giai=[bat_dau_giai],
        )
        text = karaoke.tao_ass([cl])
        dialogues = _dialogues(text)
        giai = next(d for d in dialogues if "Dap" in _hien_thi(_DIALOGUE_RE.match(d).group(3)))
        start = _thoi_gian_giay(_DIALOGUE_RE.match(giai).group(1))
        self.assertAlmostEqual(start, cl.bat_dau + bat_dau_giai, delta=0.02)


class BocDongTest(unittest.TestCase):
    def test_a_long_sentence_balances_its_two_lines_instead_of_orphaning_one_word(self):
        cau_text = "Chu kì tỉ lệ với căn bậc hai của chiều dài dây."
        tu_van = cau_text.rstrip(".").split()
        tu = [{"t": lich.DAN_DAU + i * 0.3, "d": 0.25, "chu": w, "khoa": w.lower()} for i, w in enumerate(tu_van)]
        cl = canh(1, 0.0, len(tu_van) * 0.3, [cau_text], [lich.DAN_DAU], tu)
        text = karaoke.tao_ass([cl])
        dialogues = _dialogues(text)
        self.assertEqual(len(dialogues), 1, dialogues)
        dong = _DIALOGUE_RE.match(dialogues[0]).group(3).split("\\N")
        self.assertEqual(len(dong), 2, dong)
        so_tu = [len(_KF_TAG_RE.sub("", d).strip().split()) for d in dong]
        self.assertGreaterEqual(min(so_tu), 2, so_tu)  # không dòng nào mồ côi 1 từ
        do_dai = [len(_KF_TAG_RE.sub("", d)) for d in dong]
        self.assertLessEqual(abs(do_dai[0] - do_dai[1]), 10, do_dai)  # hai dòng cân đối


class BocDongCuTest(unittest.TestCase):
    def test_long_sentence_wraps_to_at_most_two_lines(self):
        tu = [{"t": lich.DAN_DAU + i * 0.3, "d": 0.25, "chu": f"tuso{i}", "khoa": f"tuso{i}"} for i in range(10)]
        cl = canh(1, 0.0, 3.0, [" ".join(w["chu"] for w in tu)], [lich.DAN_DAU], tu)
        text = karaoke.tao_ass([cl])
        dialogues = [l for l in text.splitlines() if l.startswith("Dialogue:")]
        for line in dialogues:
            match = _DIALOGUE_RE.match(line)
            for sub in match.group(3).split("\\N"):
                hien = _KF_TAG_RE.sub("", sub)
                self.assertLessEqual(len(hien), 50, sub)

    def test_very_long_sentence_splits_into_consecutive_dialogues(self):
        tu = [{"t": lich.DAN_DAU + i * 0.3, "d": 0.25, "chu": "tuvuadai" * 2 + str(i), "khoa": "x"} for i in range(12)]
        cl = canh(1, 0.0, 5.0, [" ".join(w["chu"] for w in tu)], [lich.DAN_DAU], tu)
        text = karaoke.tao_ass([cl])
        dialogues = [l for l in text.splitlines() if l.startswith("Dialogue:")]
        self.assertGreater(len(dialogues), 1)


def _khung_tho(video: Path, giay: float, rong: int = 1280, cao: int = 720) -> bytes:
    """Trích một khung tại `giay` giây, trả về mảng byte thô RGB24 (không qua PNG)."""
    proc = subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{giay:.3f}", "-i", str(video),
         "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True, timeout=30)
    assert len(proc.stdout) == rong * cao * 3, (len(proc.stdout), proc.stderr)
    return proc.stdout


def _hop_chu(raw: bytes, rong: int = 1280, cao: int = 720, day_duoi: int = 150, nguong: int = 80):
    """Hộp bao các điểm ảnh sáng (chữ/viền trắng hoặc vàng) trong dải `day_duoi` điểm ảnh cuối khung.
    Trả `{"cao", "duoi", "giua_x"}` (toạ độ tuyệt đối trong khung) hoặc `None` nếu không thấy chữ."""
    y0 = cao - day_duoi
    min_r = max_r = min_c = max_c = None
    for y in range(y0, cao):
        hang = y * rong * 3
        for x in range(rong):
            o = hang + x * 3
            if max(raw[o], raw[o + 1], raw[o + 2]) > nguong:
                if min_r is None or y < min_r:
                    min_r = y
                max_r = y
                if min_c is None or x < min_c:
                    min_c = x
                if max_c is None or x > max_c:
                    max_c = x
    if min_r is None:
        return None
    return {"cao": max_r - min_r + 1, "duoi": max_r, "giua_x": (min_c + max_c) / 2}


class KichThuocChuTest(unittest.TestCase):
    """So kích thước chữ karaoke với kiểu SRT cũ (`hinh`) đã dùng ổn: cùng chữ, cùng vị trí, đốt bằng FFmpeg thật."""

    CHU = "Chu ki dao dong."

    def _dung(self, thu_muc: Path, vf: str, ten: str) -> Path:
        out = thu_muc / ten
        subprocess.run(
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi",
             "-i", "color=c=black:s=1280x720:d=2.5", "-vf", vf, "-r", "30", "-pix_fmt", "yuv420p", str(out)],
            cwd=thu_muc, check=True, timeout=60)
        return out

    @unittest.skipUnless(shutil.which("ffmpeg"), "máy không có FFmpeg")
    def test_karaoke_text_height_matches_the_old_burned_srt_look(self):
        with tempfile.TemporaryDirectory() as tmp:
            thu_muc = Path(tmp)
            lam = thu_muc / ".khung"
            fonts_dir = lam / "fonts"
            fonts_dir.mkdir(parents=True)
            shutil.copy2(ITIM_FONT, fonts_dir / ITIM_FONT.name)

            cl = canh(1, 0.0, 1.2, [self.CHU], [lich.DAN_DAU], [
                {"t": lich.DAN_DAU + 0.0, "d": 0.3, "chu": "Chu", "khoa": "chu"},
                {"t": lich.DAN_DAU + 0.3, "d": 0.3, "chu": "ki", "khoa": "ki"},
                {"t": lich.DAN_DAU + 0.6, "d": 0.3, "chu": "dao", "khoa": "dao"},
                {"t": lich.DAN_DAU + 0.9, "d": 0.3, "chu": "dong.", "khoa": "dong"},
            ])
            (lam / "phu-de.ass").write_text(karaoke.tao_ass([cl]), encoding="utf-8")
            cmd_ass = ghep.lenh_video(Path("am.txt"), Path("out-karaoke.mp4"), 30, ".khung/phu-de.ass")
            vf_ass = cmd_ass[cmd_ass.index("-vf") + 1]

            cue = srt.Cue(index=1, start=lich.DAN_DAU, end=lich.DAN_DAU + 1.2, text=self.CHU)
            (lam / "phu-de.srt").write_text(srt.render_srt([cue]), encoding="utf-8")
            cmd_srt = ghep.lenh_video(Path("am.txt"), Path("out-hinh.mp4"), 30, ".khung/phu-de.srt")
            vf_srt = cmd_srt[cmd_srt.index("-vf") + 1]

            video_karaoke = self._dung(thu_muc, vf_ass, "karaoke.mp4")
            video_hinh = self._dung(thu_muc, vf_srt, "hinh.mp4")

            moc = lich.DAN_DAU + 0.6
            hop_karaoke = _hop_chu(_khung_tho(video_karaoke, moc))
            hop_hinh = _hop_chu(_khung_tho(video_hinh, moc))
            self.assertIsNotNone(hop_karaoke, "không thấy chữ karaoke trong khung")
            self.assertIsNotNone(hop_hinh, "không thấy chữ SRT (hinh) trong khung")

            self.assertGreaterEqual(hop_karaoke["cao"], 28, hop_karaoke)
            ti_le = hop_karaoke["cao"] / hop_hinh["cao"]
            self.assertTrue(0.75 <= ti_le <= 1.25, (hop_karaoke, hop_hinh, ti_le))
            self.assertGreaterEqual(719 - hop_karaoke["duoi"], 10, "chữ phải cách mép dưới ít nhất 10px")
            self.assertLessEqual(abs(hop_karaoke["giua_x"] - 640), 20, hop_karaoke)


class KieuPhuDeTest(unittest.TestCase):
    def test_viet_tay_ngang_has_no_box_uses_itim_and_42_chars(self):
        kieu = karaoke.kieu_phu_de("viet-tay", "ngang")
        self.assertEqual(kieu, {"font": "Itim", "co": 40, "khung": False, "gioi_han": 42})

    def test_cat_dan_ngang_has_a_box_and_be_vietnam_pro(self):
        kieu = karaoke.kieu_phu_de("cat-dan", "ngang")
        self.assertTrue(kieu["khung"])
        self.assertEqual(kieu["font"], "Be Vietnam Pro")
        self.assertEqual(kieu["gioi_han"], 42)

    def test_viet_tay_doc_has_a_box_keeps_itim_and_22_chars(self):
        kieu = karaoke.kieu_phu_de("viet-tay", "doc")
        self.assertTrue(kieu["khung"])
        self.assertEqual(kieu["font"], "Itim")
        self.assertEqual(kieu["gioi_han"], 22)

    def test_cat_dan_doc_has_a_box_be_vietnam_pro_and_22_chars(self):
        kieu = karaoke.kieu_phu_de("cat-dan", "doc")
        self.assertTrue(kieu["khung"])
        self.assertEqual(kieu["font"], "Be Vietnam Pro")
        self.assertEqual(kieu["gioi_han"], 22)


class KhungNenTest(unittest.TestCase):
    """`.ass` của `cat-dan` (hay bất kỳ khổ `doc`) phải có khung nền: BorderStyle=3, nền đen 60%, viền cùng
    màu nền, chữ trắng, và SecondaryColour vàng cho `\\kf`."""

    def _canh(self):
        return canh(1, 0.0, 1.5, ["Chu ki dao dong cua con lac don."], [lich.DAN_DAU], [
            {"t": lich.DAN_DAU + i * 0.25, "d": 0.2, "chu": w, "khoa": w.lower()}
            for i, w in enumerate(["Chu", "ki", "dao", "dong", "cua", "con", "lac", "don."])
        ])

    def test_cat_dan_ngang_ass_has_borderstyle_3_and_box_colours(self):
        text = karaoke.tao_ass([self._canh()], chu_de="cat-dan", kho_ten="ngang")
        style_line = next(l for l in text.splitlines() if l.startswith("Style:"))
        fields = style_line.split(",")
        self.assertEqual(fields[15], "3")  # BorderStyle
        self.assertEqual(fields[3], "&H00FFFFFF")  # PrimaryColour trắng
        self.assertEqual(fields[4], "&H0000D7FF")  # SecondaryColour vàng
        self.assertEqual(fields[5], "&H66000000")  # OutlineColour = nền
        self.assertEqual(fields[6], "&H66000000")  # BackColour đen 60%
        self.assertIn("Be Vietnam Pro", style_line)

    def test_viet_tay_doc_ass_also_gets_the_box_but_keeps_itim(self):
        text = karaoke.tao_ass([self._canh()], chu_de="viet-tay", kho_ten="doc")
        style_line = next(l for l in text.splitlines() if l.startswith("Style:"))
        self.assertEqual(style_line.split(",")[15], "3")
        self.assertIn("Itim", style_line)
        self.assertNotIn("Be Vietnam Pro", style_line)

    def test_viet_tay_ngang_ass_has_no_box(self):
        text = karaoke.tao_ass([self._canh()], chu_de="viet-tay", kho_ten="ngang")
        style_line = next(l for l in text.splitlines() if l.startswith("Style:"))
        self.assertEqual(style_line.split(",")[15], "1")


class KhoDocTest(unittest.TestCase):
    """Ở khổ dọc, mọi dòng hiển thị phải <= 22 ký tự, tổng \\kf của các phần bằng thời lượng câu, và câu
    dài hơn 2 dòng phải tách kèm cảnh báo."""

    def _canh_dai(self, so=1, bat_dau=0.0):
        cau_text = "Chu kì tỉ lệ với căn bậc hai của chiều dài dây, và không phụ thuộc vào biên độ dao động nhỏ."
        tu_van = cau_text.replace(",", "").rstrip(".").split()
        tu = [{"t": lich.DAN_DAU + i * 0.28, "d": 0.24, "chu": w, "khoa": w.lower()} for i, w in enumerate(tu_van)]
        return canh(so, bat_dau, len(tu_van) * 0.28, [cau_text], [lich.DAN_DAU], tu), cau_text

    def test_every_displayed_line_is_at_most_22_characters(self):
        cl, _ = self._canh_dai()
        text = karaoke.tao_ass([cl], chu_de="viet-tay", kho_ten="doc")
        for d in _dialogues(text):
            chu = _DIALOGUE_RE.match(d).group(3)
            for dong in chu.split("\\N"):
                hien = _KF_TAG_RE.sub("", dong)
                self.assertLessEqual(len(hien), 22, hien)

    def test_kf_total_still_matches_sentence_duration_after_splitting(self):
        cl, _ = self._canh_dai()
        text = karaoke.tao_ass([cl], chu_de="viet-tay", kho_ten="doc")
        dialogues = _dialogues(text)
        self.assertGreater(len(dialogues), 1, "câu dài phải tách thành nhiều sự kiện ở khổ dọc")
        tong_kf = 0
        tong_giay = 0.0
        for d in dialogues:
            match = _DIALOGUE_RE.match(d)
            start, end = _thoi_gian_giay(match.group(1)), _thoi_gian_giay(match.group(2))
            tong_giay += end - start
            tong_kf += sum(int(n) for n in _KF_RE.findall(match.group(3)))
        self.assertLessEqual(abs(tong_kf - round(tong_giay * 100)), len(dialogues))

    def test_long_sentence_in_doc_mode_warns_with_scene_number_and_part_count(self):
        cl, _ = self._canh_dai(so=7)
        canh_bao: list = []
        text = karaoke.tao_ass([cl], chu_de="viet-tay", kho_ten="doc", canh_bao=canh_bao)
        so_phan = len(_dialogues(text))
        self.assertEqual(len(canh_bao), 1)
        self.assertIn("Cảnh 7", canh_bao[0])
        self.assertIn(f"{so_phan} phần", canh_bao[0])

    def test_short_sentence_in_doc_mode_does_not_warn(self):
        cl = canh(1, 0.0, 1.0, ["Cau ngan."], [lich.DAN_DAU],
                  [{"t": lich.DAN_DAU + 0.0, "d": 0.3, "chu": "Cau", "khoa": "cau"},
                   {"t": lich.DAN_DAU + 0.4, "d": 0.3, "chu": "ngan.", "khoa": "ngan"}])
        canh_bao: list = []
        karaoke.tao_ass([cl], chu_de="viet-tay", kho_ten="doc", canh_bao=canh_bao)
        self.assertEqual(canh_bao, [])

    def test_ngang_khong_tach_theo_dau_phay_giu_duong_cu(self):
        """Ở khổ ngang (42 ký tự), câu dài vẫn tách theo cách cũ (không ưu tiên dấu phẩy), không cảnh báo mới."""
        cl, _ = self._canh_dai()
        canh_bao: list = []
        karaoke.tao_ass([cl], chu_de="viet-tay", kho_ten="ngang", canh_bao=canh_bao)
        self.assertEqual(canh_bao, [])


class FfmpegBurnTest(unittest.TestCase):
    @unittest.skipUnless(shutil.which("ffmpeg"), "máy không có FFmpeg")
    def test_real_ffmpeg_burns_vietnamese_karaoke_into_a_colour_video(self):
        from video_ma_parts.phong import FONT as ITIM_FONT, TEN as ITIM_TEN

        cl = canh(1, 0.0, 1.4, ["Chu ki con lac don."],
                  [lich.DAN_DAU],
                  [
                      {"t": lich.DAN_DAU + 0.0, "d": 0.3, "chu": "Chu", "khoa": "chu"},
                      {"t": lich.DAN_DAU + 0.3, "d": 0.3, "chu": "ki", "khoa": "ki"},
                      {"t": lich.DAN_DAU + 0.6, "d": 0.3, "chu": "con", "khoa": "con"},
                      {"t": lich.DAN_DAU + 0.9, "d": 0.3, "chu": "lac", "khoa": "lac"},
                      {"t": lich.DAN_DAU + 1.2, "d": 0.2, "chu": "don.", "khoa": "don"},
                  ])
        with tempfile.TemporaryDirectory() as tmp:
            thu_muc = Path(tmp)
            (thu_muc / "phu-de.ass").write_text(karaoke.tao_ass([cl]), encoding="utf-8")
            fonts_dir = thu_muc / "fonts"
            fonts_dir.mkdir()
            shutil.copy2(ITIM_FONT, fonts_dir / ITIM_FONT.name)
            out = thu_muc / "out.mp4"
            cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi",
                   "-i", "color=c=blue:s=1280x720:d=2", "-vf",
                   f"subtitles=phu-de.ass:fontsdir=fonts", "-r", "30", "-pix_fmt", "yuv420p", str(out)]
            proc = subprocess.run(cmd, cwd=thu_muc, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(out.is_file())


if __name__ == "__main__":
    unittest.main()
