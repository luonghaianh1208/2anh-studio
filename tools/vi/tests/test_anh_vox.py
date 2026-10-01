"""anh_vox.py: danh sách ảnh, cấu hình, gọi API kiểu OpenAI (máy chủ giả), lưu đệm, khoá không lộ."""
import base64, io, json, os, subprocess, sys, tempfile, threading, unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))
from anh_vox_parts import ke_hoach, nguon_ve  # noqa: E402
from video_ma_parts import parse  # noqa: E402

KHOA = "sk-bi-mat-khong-duoc-lo"


def png_xanh(w=64, h=64) -> bytes:
    from PIL import Image
    im = Image.new("RGB", (w, h), (0, 255, 0))
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
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"data": [{"b64_json": base64.b64encode(png_xanh()).decode()}]}).encode())

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


class CliTest(unittest.TestCase):
    def setUp(self):
        _May.goi.clear()
        _May.tra = "b64"
        _May.con_loi = 0
        self.srv, self.url = may_gia()

    def tearDown(self):
        self.srv.shutdown()

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


if __name__ == "__main__":
    unittest.main()
