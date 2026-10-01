"""anh_vox.py: danh sách ảnh, cấu hình, gọi API kiểu OpenAI (máy chủ giả), lưu đệm, khoá không lộ."""
import base64, io, json, os, shutil, subprocess, sys, tempfile, threading, unittest
from unittest import mock
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))
from anh_vox_parts import ke_hoach, nguon_ve  # noqa: E402
from video_ma_parts import parse  # noqa: E402

KHOA = "sk-bi-mat-khong-duoc-lo"


def png_xanh(w=64, h=64, nen=(0, 255, 0)) -> bytes:
    from PIL import Image
    im = Image.new("RGB", (w, h), nen)
    for x in range(w // 4, 3 * w // 4):
        for y in range(h // 4, 3 * h // 4):
            im.putpixel((x, y), (200, 60, 40))
    b = io.BytesIO()
    im.save(b, "PNG")
    return b.getvalue()


class _May(BaseHTTPRequestHandler):
    goi: list = []
    tra = "b64"
    con_loi = 0

    def do_POST(self):
        than = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        _May.goi.append({"auth": self.headers.get("Authorization"), **than})
        if _May.tra in ("401", "500"):
            self.send_response(int(_May.tra))
            self.end_headers()
            self.wfile.write(b'{"error":{"message":"tu choi"}}')
            return
        if _May.tra == "loi":
            self.send_response(429)
            self.end_headers()
            self.wfile.write(b'{"error":{"message":"quota exceeded"}}')
            return
        if _May.tra == "mang-tam" and _May.con_loi > 0:
            _May.con_loi -= 1
            self.send_response(503)
            self.end_headers()
            self.wfile.write(b'{"error":{"message":"tam thoi qua tai"}}')
            return
        if _May.tra == "mot-loi" and len(_May.goi) > 1:
            self.send_response(429)
            self.end_headers()
            self.wfile.write(b'{"error":{"message":"qua tai"}}')
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if _May.tra == "url":
            noi_dung = {"data": [{"url": f"http://127.0.0.1:{self.server.server_port}/anh.png"}]}
        elif _May.tra == "xam":
            noi_dung = {"data": [{"b64_json": base64.b64encode(png_xanh(256, 256, (235, 235, 235))).decode()}]}
        else:
            noi_dung = {"data": [{"b64_json": base64.b64encode(png_xanh(256, 256)).decode()}]}
        self.wfile.write(json.dumps(noi_dung).encode())

    def do_GET(self):
        if self.path == "/anh.png":
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.end_headers()
            self.wfile.write(png_xanh())
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, *a):
        pass


def may_gia():
    srv = HTTPServer(("127.0.0.1", 0), _May)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_port}/v1"


VIDEO = ("---\ntieu-de: T\nphong-cach: vox\n---\n\n"
         "## Cảnh 1\nbo-cuc: hai-ben\nloi: Cốc cà phê và chiếc bánh.\n"
         "nhip: Cốc cà phê | anh: ve: cốc cà phê sứ trắng | trai\n"
         "nhip: chiếc bánh | anh: ve: bánh sừng bò | phai | khung\n\n"
         "## Cảnh 2\nbo-cuc: toan-canh\nloi: Phố cổ Hà Nội.\nnhip: @dau | anh: tim: hanoi old quarter | nen\n")


class KeHoachTest(unittest.TestCase):
    def test_plan_lists_every_image_with_stable_names(self):
        ds = ke_hoach.lap(parse.parse(VIDEO))
        self.assertEqual([(m.canh, m.chi_so, m.kieu, m.nguon) for m in ds],
                         [(1, 0, "cat", "ve"), (1, 1, "khung", "ve"), (2, 0, "phu", "tim")])
        self.assertIn("#00FF00", ds[0].prompt)
        self.assertNotIn("#00FF00", ds[1].prompt)
        self.assertIn("không có chữ", ds[0].prompt)
        self.assertEqual(ds[0].kich_thuoc, "1024x1024")
        self.assertEqual(ds[1].kich_thuoc, "1536x1024")
        self.assertEqual(ds[0].ma, ke_hoach.ma_anh(ds[0].prompt, ds[0].kich_thuoc))
        self.assertEqual(ke_hoach.lap(parse.parse(VIDEO))[0].ma, ds[0].ma, "tên phải tất định")

    def test_style_suffix_changes_the_prompt(self):
        a = ke_hoach.lap(parse.parse(VIDEO))[0]
        b = ke_hoach.lap(parse.parse(VIDEO.replace("phong-cach: vox\n", "phong-cach: vox\nphong-anh: minh-hoa\n")))[0]
        self.assertNotEqual(a.prompt, b.prompt)

    def test_portrait_frame_size(self):
        ds = ke_hoach.lap(parse.parse(VIDEO.replace("phong-cach: vox\n", "phong-cach: vox\nkho: doc\n")
                                      .replace("| trai", "| tren").replace("| phai", "| duoi")))
        self.assertEqual(ds[1].kich_thuoc, "1024x1536")

    def test_processed_file_names(self):
        ds = ke_hoach.lap(parse.parse(VIDEO))
        self.assertEqual(ke_hoach.file_xu_ly(Path("x"), ds[0]).name, f"{ds[0].ma}-100-cat.png")
        self.assertEqual(ke_hoach.file_xu_ly(Path("x"), ds[1]).name, f"{ds[1].ma}-101-khung.png")


class CauHinhTest(unittest.TestCase):
    def test_defaults_and_env(self):
        with tempfile.TemporaryDirectory() as home:
            c = nguon_ve.doc_cau_hinh({}, Path(home))
            self.assertEqual((c.url, c.mo_hinh, c.khoa), ("http://localhost:20128/v1", "ag/gemini-3.1-flash-image", None))
            c = nguon_ve.doc_cau_hinh({"ANH_AI_URL": "http://h/v1", "ANH_AI_KEY": "k", "ANH_AI_MO_HINH": "m"}, Path(home))
            self.assertEqual((c.url, c.khoa, c.mo_hinh), ("http://h/v1", "k", "m"))

    def test_config_file(self):
        with tempfile.TemporaryDirectory() as home:
            d = Path(home) / ".2anh-studio"
            d.mkdir()
            (d / "anh-ai.json").write_text(json.dumps({"url": "http://f/v1", "khoa": "kf", "mo_hinh": "mf"}), encoding="utf-8")
            c = nguon_ve.doc_cau_hinh({}, Path(home))
            self.assertEqual((c.url, c.khoa, c.mo_hinh), ("http://f/v1", "kf", "mf"))


class VeTest(unittest.TestCase):
    def setUp(self):
        _May.goi.clear()
        _May.tra = "b64"
        _May.con_loi = 0
        self.srv, self.url = may_gia()

    def tearDown(self):
        self.srv.shutdown()
        self.srv.server_close()

    def test_draw_sends_openai_request_with_key(self):
        anh = nguon_ve.ve(nguon_ve.CauHinh(self.url, KHOA, "m1"), "cốc", "1024x1024")
        self.assertTrue(anh.startswith(b"\x89PNG"))
        self.assertEqual(_May.goi[0]["model"], "m1")
        self.assertEqual(_May.goi[0]["size"], "1024x1024")
        self.assertEqual(_May.goi[0]["auth"], f"Bearer {KHOA}")

    def test_provider_error_is_named_and_hides_the_key(self):
        _May.tra = "loi"
        with self.assertRaises(nguon_ve.VeError) as c:
            nguon_ve.ve(nguon_ve.CauHinh(self.url, KHOA, "m1"), "cốc", "1024x1024")
        self.assertEqual(c.exception.step, "nha-cung-cap")
        self.assertIn("quota exceeded", c.exception.message)
        self.assertNotIn(KHOA, c.exception.message + c.exception.fix)

    def test_unreachable_server_is_a_network_error(self):
        with self.assertRaises(nguon_ve.VeError) as c:
            nguon_ve.ve(nguon_ve.CauHinh("http://127.0.0.1:1/v1", None, "m"), "x", "1024x1024", timeout=2)
        self.assertEqual(c.exception.step, "mang")

    def test_url_response_is_downloaded(self):
        _May.tra = "url"
        anh = nguon_ve.ve(nguon_ve.CauHinh(self.url, KHOA, "m1"), "cốc", "1024x1024")
        self.assertTrue(anh.startswith(b"\x89PNG"))


class CliTest(unittest.TestCase):
    def setUp(self):
        _May.goi.clear()
        _May.tra = "b64"
        _May.con_loi = 0
        self.srv, self.url = may_gia()

    def tearDown(self):
        self.srv.shutdown()
        self.srv.server_close()

    def chay(self, thu_muc, *them, env=None):
        e = {**os.environ, "ANH_AI_URL": self.url, "ANH_AI_KEY": KHOA, "ANH_AI_MO_HINH": "m1", **(env or {})}
        r = subprocess.run([sys.executable, str(TOOLS_VI / "anh_vox.py"), str(thu_muc), *them], capture_output=True,
                           text=True, encoding="utf-8", env=e)
        self.assertNotIn(KHOA, r.stdout + r.stderr)
        return json.loads(r.stdout.strip().splitlines()[-1])

    def test_plan_only_writes_the_plan_and_calls_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "video.md").write_text(VIDEO.replace(
                "nhip: @dau | anh: tim: hanoi old quarter | nen\n", "nhip: @dau | chu: Phố cổ\n").replace(
                "bo-cuc: toan-canh", "bo-cuc: mot"), encoding="utf-8")
            out = self.chay(tmp, "--chi-ke-hoach")
            self.assertTrue(out["ready"])
            self.assertEqual(out["so_anh"], 2)
            self.assertTrue((Path(tmp) / "anh" / "ai" / "ke-hoach.json").is_file())
        self.assertEqual(_May.goi, [])

    def test_draws_once_then_reuses_and_redraws_when_the_model_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "video.md").write_text(VIDEO.replace(
                "nhip: @dau | anh: tim: hanoi old quarter | nen\n", "nhip: @dau | chu: Phố cổ\n").replace(
                "bo-cuc: toan-canh", "bo-cuc: mot"), encoding="utf-8")
            out = self.chay(tmp)
            self.assertTrue(out["ready"], out)
            self.assertEqual((out["da_ve"], out["dung_lai"]), (2, 0))
            nguon = json.loads((Path(tmp) / "anh" / "ai" / "nguon.json").read_text(encoding="utf-8"))
            self.assertEqual({n["mo_hinh"] for n in nguon}, {"m1"})
            self.assertEqual((self.chay(tmp)["da_ve"]), 0)
            self.assertEqual(self.chay(tmp, env={"ANH_AI_MO_HINH": "m2"})["da_ve"], 2)

    def test_limit_stops_before_drawing(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "video.md").write_text(VIDEO.replace(
                "nhip: @dau | anh: tim: hanoi old quarter | nen\n", "nhip: @dau | chu: Phố cổ\n").replace(
                "bo-cuc: toan-canh", "bo-cuc: mot"), encoding="utf-8")
            out = self.chay(tmp, "--toi-da", "1")
        self.assertFalse(out["ready"])
        self.assertEqual(out["error"]["step"], "input")
        self.assertIn("--toi-da", out["error"]["fix"])
        self.assertEqual(_May.goi, [])

    def test_key_with_control_char_is_rejected_without_leaking(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "video.md").write_text(VIDEO.replace(
                "nhip: @dau | anh: tim: hanoi old quarter | nen\n", "nhip: @dau | chu: Phố cổ\n").replace(
                "bo-cuc: toan-canh", "bo-cuc: mot"), encoding="utf-8")
            khoa_hong = "sk-bi-mat\n"
            e = {**os.environ, "ANH_AI_URL": self.url, "ANH_AI_KEY": khoa_hong, "ANH_AI_MO_HINH": "m1"}
            r = subprocess.run([sys.executable, str(TOOLS_VI / "anh_vox.py"), str(tmp)], capture_output=True,
                               text=True, encoding="utf-8", env=e)
            out = json.loads(r.stdout.strip().splitlines()[-1])
            self.assertEqual(out["error"]["step"], "cau-hinh")
            self.assertNotIn("sk-bi-mat", r.stdout + r.stderr)
        self.assertEqual(_May.goi, [])

    def test_platform_drawn_images_are_reused_regardless_of_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            video_hai_anh = VIDEO.replace(
                "nhip: @dau | anh: tim: hanoi old quarter | nen\n", "nhip: @dau | chu: Phố cổ\n").replace(
                "bo-cuc: toan-canh", "bo-cuc: mot")
            (Path(tmp) / "video.md").write_text(video_hai_anh, encoding="utf-8")
            ds = ke_hoach.lap(parse.parse(video_hai_anh))
            thu_muc_goc = Path(tmp) / "anh" / "ai" / "goc"
            thu_muc_goc.mkdir(parents=True)
            for m in ds:
                (thu_muc_goc / f"{m.ma}.png").write_bytes(png_xanh())
            out1 = self.chay(tmp)
            self.assertTrue(out1["ready"], out1)
            self.assertEqual(out1["da_ve"], 0)
            self.assertTrue(out1["warnings"])
            out2 = self.chay(tmp)
            self.assertTrue(out2["ready"], out2)
            self.assertEqual(out2["da_ve"], 0)
            self.assertTrue(out2["warnings"])
        self.assertEqual(_May.goi, [])

    def test_partial_failure_saves_successful_draws_and_resumes(self):
        with tempfile.TemporaryDirectory() as tmp:
            video_hai_anh = VIDEO.replace(
                "nhip: @dau | anh: tim: hanoi old quarter | nen\n", "nhip: @dau | chu: Phố cổ\n").replace(
                "bo-cuc: toan-canh", "bo-cuc: mot")
            (Path(tmp) / "video.md").write_text(video_hai_anh, encoding="utf-8")
            _May.tra = "mot-loi"
            out = self.chay(tmp)
            self.assertFalse(out["ready"], out)
            self.assertEqual(out["error"]["step"], "nha-cung-cap")
            nguon = json.loads((Path(tmp) / "anh" / "ai" / "nguon.json").read_text(encoding="utf-8"))
            self.assertEqual(len(nguon), 1)
            file_thanh_cong = Path(tmp) / "anh" / "ai" / "goc" / f"{nguon[0]['ma']}.png"
            self.assertTrue(file_thanh_cong.is_file())
            _May.tra = "b64"
            out2 = self.chay(tmp)
            self.assertTrue(out2["ready"], out2)
            self.assertEqual(out2["da_ve"], 1)

    def test_retries_on_transient_errors_then_succeeds(self):
        with tempfile.TemporaryDirectory() as tmp:
            video_mot_anh = ("---\ntieu-de: T\nphong-cach: vox\n---\n\n"
                              "## Cảnh 1\nbo-cuc: hai-ben\nloi: Cốc cà phê.\n"
                              "nhip: Cốc cà phê | anh: ve: cốc cà phê sứ trắng | trai\n"
                              "nhip: @dau | chu: OK | phai\n")
            (Path(tmp) / "video.md").write_text(video_mot_anh, encoding="utf-8")
            _May.tra = "mang-tam"
            _May.con_loi = 2
            out = self.chay(tmp)
            self.assertTrue(out["ready"], out)
            self.assertEqual(out["da_ve"], 1)
            self.assertEqual(len(_May.goi), 3)

    def test_steps_are_the_documented_ones(self):
        import anh_vox
        self.assertEqual(anh_vox.ERROR_STEPS, ("input", "parse", "cau-hinh", "mang", "nha-cung-cap", "tach-nen", "write", "internal"))

    @unittest.skipUnless(shutil.which("ffmpeg"), "cần FFmpeg")
    def test_full_run_writes_processed_images_and_the_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "video.md").write_text(VIDEO.replace(
                "nhip: @dau | anh: tim: hanoi old quarter | nen\n", "nhip: @dau | chu: Phố cổ\n").replace(
                "bo-cuc: toan-canh", "bo-cuc: mot"), encoding="utf-8")
            out = self.chay(tmp)
            self.assertTrue(out["ready"], out)
            bang = json.loads((Path(tmp) / "anh" / "ai" / "vox.json").read_text(encoding="utf-8"))
            self.assertEqual(set(bang), {"1-0", "1-1"})
            self.assertEqual(bang["1-0"]["kieu"], "cat")
            self.assertEqual(bang["1-1"]["kieu"], "khung")
            for v in bang.values():
                self.assertTrue((Path(tmp) / "anh" / v["file"]).is_file())
            self.assertEqual({v["mo_hinh"] for v in bang.values()}, {"m1"})
            self.assertIn("anh/ai/vox.json", out["files"])
            # Bảng ghi mục kế hoạch gốc để video_ma nhận ra ảnh cũ khi video.md đổi.
            video = parse.parse((Path(tmp) / "video.md").read_text(encoding="utf-8"))
            for m in ke_hoach.lap(video):
                v = bang[f"{m.canh}-{m.chi_so}"]
                self.assertEqual((v["ma_ke_hoach"], v["tuy_chon"], v["loai_nguon"]), (m.ma, list(m.tuy_chon), m.nguon))
            from video_ma_parts import kiem
            self.assertEqual(kiem.kiem(video, Path(tmp), doc_nhac_nen=False), [])

    def _video_mot_cat(self, tmp, cong_cu="api"):
        video = ("---\ntieu-de: T\nphong-cach: vox\n---\n\n"
                 "## Cảnh 1\nbo-cuc: hai-ben\nloi: Cốc cà phê.\n"
                 "nhip: Cốc cà phê | anh: ve: cốc cà phê sứ trắng | trai\n")
        (Path(tmp) / "video.md").write_text(video, encoding="utf-8")
        m = ke_hoach.lap(parse.parse(video))[0]
        goc = ke_hoach.file_goc(Path(tmp), m)
        goc.parent.mkdir(parents=True)
        goc.write_bytes(png_xanh(256, 256, (235, 235, 235)))   # nền xám: tách không sạch
        (goc.parent.parent / "nguon.json").write_text(json.dumps([
            {"file": f"ai/goc/{m.ma}.png", "cong_cu": cong_cu, "mo_hinh": "m1", "prompt": m.prompt,
             "ngay": "2026-10-01", "ma": m.ma}]), encoding="utf-8")
        return m

    def _phai_thanh_khung(self, out):
        self.assertTrue(out["ready"], out)
        bang = json.loads((Path(self._tmp_hien) / "anh" / "ai" / "vox.json").read_text(encoding="utf-8"))
        self.assertEqual(bang["1-0"]["kieu"], "khung")
        self.assertTrue(any("khung" in w for w in out["warnings"]), out["warnings"])

    @unittest.skipUnless(shutil.which("ffmpeg"), "cần FFmpeg")
    def test_platform_drawn_unclean_cutout_becomes_a_frame_without_calling_the_api(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._tmp_hien = tmp
            self._video_mot_cat(tmp, cong_cu="nen-tang")
            _May.tra = "401"
            self._phai_thanh_khung(self.chay(tmp))
        self.assertEqual(_May.goi, [])

    @unittest.skipUnless(shutil.which("ffmpeg"), "cần FFmpeg")
    def test_failed_redraw_falls_back_to_a_frame(self):
        for loi in ("401", "500"):
            with self.subTest(loi=loi), tempfile.TemporaryDirectory() as tmp:
                self._tmp_hien = tmp
                self._video_mot_cat(tmp)
                _May.goi.clear()
                _May.tra = loi
                out = self.chay(tmp)   # self.chay cũng kiểm khoá không lộ ra stdout/stderr
                self._phai_thanh_khung(out)
                self.assertTrue(any("không vẽ lại được" in w for w in out["warnings"]), out["warnings"])
                self.assertGreaterEqual(len(_May.goi), 1)

    @unittest.skipUnless(shutil.which("ffmpeg"), "cần FFmpeg")
    def test_unclean_cutout_is_redrawn_once_with_a_stricter_prompt(self):
        with tempfile.TemporaryDirectory() as tmp:
            m = self._video_mot_cat(tmp)
            out = self.chay(tmp)
            self.assertTrue(out["ready"], out)
            self.assertEqual(len(_May.goi), 1)
            self.assertIn("tuyệt đối đồng màu", _May.goi[0]["prompt"])
            bang = json.loads((Path(tmp) / "anh" / "ai" / "vox.json").read_text(encoding="utf-8"))
            self.assertEqual(bang["1-0"]["kieu"], "cat")
            self.assertNotEqual(bang["1-0"]["ma"], m.ma)
            self.assertEqual(bang["1-0"]["ma_ke_hoach"], m.ma)
            nguon = json.loads((Path(tmp) / "anh" / "ai" / "nguon.json").read_text(encoding="utf-8"))
            self.assertIn(bang["1-0"]["ma"], {n["ma"] for n in nguon})
            # Chạy lại: dùng lại ảnh vẽ lại, không gọi API nữa.
            self.assertTrue(self.chay(tmp)["ready"])
            self.assertEqual(len(_May.goi), 1)

    @unittest.skipUnless(shutil.which("ffmpeg"), "cần FFmpeg")
    def test_still_unclean_after_redraw_becomes_a_frame_with_a_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._video_mot_cat(tmp)
            _May.tra = "xam"
            out = self.chay(tmp)
            self.assertTrue(out["ready"], out)
            self.assertEqual(len(_May.goi), 1)
            bang = json.loads((Path(tmp) / "anh" / "ai" / "vox.json").read_text(encoding="utf-8"))
            self.assertEqual(bang["1-0"]["kieu"], "khung")
            self.assertTrue(bang["1-0"]["file"].endswith("-khung.png"))
            self.assertTrue(any("khung" in w for w in out["warnings"]), out["warnings"])


VIDEO_TIM = ("---\ntieu-de: T\nphong-cach: vox\n---\n\n"
             "## Cảnh 1\nbo-cuc: toan-canh\nloi: Phố cổ Hà Nội.\nnhip: @dau | anh: tim: hanoi old quarter | nen\n")


@unittest.skipUnless(shutil.which("ffmpeg"), "cần FFmpeg")
class AnhThatTest(unittest.TestCase):
    """Ảnh thật `tim:` chạy image_search.py qua subprocess — giả lập, không ra mạng."""

    def setUp(self):
        import anh_vox
        self.anh_vox = anh_vox
        self._tmp = tempfile.TemporaryDirectory()
        self.thu_muc = Path(self._tmp.name)
        (self.thu_muc / "video.md").write_text(VIDEO_TIM, encoding="utf-8")
        self.lenh = []

    def tearDown(self):
        self._tmp.cleanup()

    def _gia(self, ma_thoat=0, nguon=True):
        def run(cmd, *a, **k):
            self.lenh.append(cmd)
            ten = cmd[cmd.index("--filename") + 1]
            ra = Path(cmd[cmd.index("-o") + 1])
            if ma_thoat == 0:
                from PIL import Image
                ra.mkdir(parents=True, exist_ok=True)
                Image.new("RGB", (1600, 1000), (90, 110, 140)).save(ra / ten, "JPEG")
                if nguon:
                    (ra / "image_sources.json").write_text(json.dumps({"items": [
                        {"filename": ten, "author": "Ai Đó", "license_name": "CC BY 4.0", "provider": "openverse"}]}),
                        encoding="utf-8")
            return subprocess.CompletedProcess(cmd, ma_thoat, "", "loi gia")
        return run

    def _chay(self, run):
        with mock.patch.object(self.anh_vox.subprocess, "run", run):
            return self.anh_vox.chay(self.thu_muc, False, 20, [])

    def test_real_photo_is_fetched_processed_and_credited(self):
        kq = self._chay(self._gia())
        self.assertEqual(len(self.lenh), 1)
        cmd = self.lenh[0]
        self.assertIn("image_search.py", cmd[1])
        self.assertEqual(cmd[2], "hanoi old quarter")
        self.assertEqual(cmd[cmd.index("--orientation") + 1], "landscape")
        bang = json.loads((self.thu_muc / "anh" / "ai" / "vox.json").read_text(encoding="utf-8"))
        self.assertEqual(bang["1-0"]["kieu"], "phu")
        self.assertIsNone(bang["1-0"]["mo_hinh"])
        self.assertEqual(bang["1-0"]["nguon"], "Ảnh: Ai Đó · CC BY 4.0 · openverse")
        self.assertTrue((self.thu_muc / "anh" / bang["1-0"]["file"]).is_file())
        self.assertIn("anh/ai/vox.json", kq["files"])
        # Đã có ảnh: không tìm lại.
        self._chay(self._gia())
        self.assertEqual(len(self.lenh), 1)

    def test_search_failure_is_a_network_error(self):
        with self.assertRaises(nguon_ve.VeError) as c:
            self._chay(self._gia(ma_thoat=1))
        self.assertEqual(c.exception.step, "mang")
        self.assertIn("hanoi old quarter", c.exception.message)

    def test_photo_without_credit_is_refused(self):
        with self.assertRaises(nguon_ve.VeError) as c:
            self._chay(self._gia(nguon=False))
        self.assertEqual(c.exception.step, "nha-cung-cap")
        self.assertIn("chưa có nguồn", c.exception.message)


if __name__ == "__main__":
    unittest.main()
