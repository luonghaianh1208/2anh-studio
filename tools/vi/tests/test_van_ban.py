"""Test cho lệnh soạn văn bản hành chính theo Nghị định 30 (tools/vi/van_ban.py)."""

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tools" / "vi"))

import van_ban  # noqa: E402

EXAMPLES = REPO_ROOT / "tools" / "vi" / "nd30" / "examples"
SCRIPT = REPO_ROOT / "tools" / "vi" / "van_ban.py"
REMINDER = "Văn bản chưa đóng dấu, chưa ký; soát và điền đủ trước khi ban hành."


def load_example(name: str) -> dict:
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


def filled_cong_van() -> dict:
    spec = load_example("cong_van.json")
    spec["body"][1]["text"] = (
        "Thời gian: 08 giờ 00 ngày 15/10/2026; địa điểm: Hội trường Phòng Giáo dục và Đào tạo."
    )
    spec["signature"]["nguoi_ky"] = "Nguyễn Văn An"
    return spec


class CliCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.folder = self.root / "van-ban"
        self.folder.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def write_spec(self, spec, folder: Path | None = None) -> Path:
        folder = folder or self.folder
        path = folder / "noi-dung.json"
        path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def run_cli(self, *args: str) -> tuple[int, dict, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = van_ban.main([str(a) for a in args])
        text = out.getvalue()
        lines = [line for line in text.splitlines() if line.strip()]
        self.assertEqual(len(lines), 1, f"stdout phải đúng một dòng JSON, nhận: {text!r}")
        return code, json.loads(lines[0]), text


class CleanAndDraftTest(CliCase):
    def test_filled_cong_van_is_final(self):
        self.write_spec(filled_cong_van())
        code, data, _ = self.run_cli(self.folder)
        self.assertEqual(code, 0, data)
        self.assertTrue(data["ready"])
        self.assertIsNone(data["error"])
        self.assertFalse(data["ban_nhap"])
        self.assertEqual(data["so_o_can_bo_sung"], 0)
        self.assertEqual(data["loai_van_ban"], "Công văn")
        self.assertEqual(data["profile"], "administrative")
        self.assertEqual(data["kiem_tra"]["loi"], 0)
        self.assertGreater(data["kiem_tra"]["dat"], 0)
        self.assertTrue((self.folder / "van-ban.docx").is_file())
        self.assertTrue((self.folder / "kiem-tra.md").is_file())
        self.assertEqual(
            sorted(Path(p).name for p in data["files"]), ["kiem-tra.md", "van-ban.docx"]
        )

    def test_original_example_is_a_draft_with_two_blanks(self):
        self.write_spec(load_example("cong_van.json"))
        code, data, _ = self.run_cli(self.folder)
        self.assertEqual(code, 0, data)
        self.assertTrue(data["ready"])
        self.assertTrue(data["ban_nhap"])
        self.assertEqual(data["so_o_can_bo_sung"], 2)
        self.assertEqual(data["kiem_tra"]["loi"], 0)
        joined = "\n".join(data["warnings"])
        self.assertIn("[CẦN BỔ SUNG: thời gian, địa điểm tổ chức]", joined)
        self.assertIn("[CẦN BỔ SUNG: họ tên Trưởng phòng]", joined)
        self.assertTrue((self.folder / "van-ban.docx").is_file())
        report = (self.folder / "kiem-tra.md").read_text(encoding="utf-8")
        self.assertIn("Công văn", report)
        self.assertIn("administrative", report)
        self.assertIn("[CẦN BỔ SUNG: họ tên Trưởng phòng]", report)
        self.assertIn(REMINDER, report)
        self.assertIn("✓", report)

    def test_question_marks_count_as_blanks(self):
        spec = filled_cong_van()
        spec["header"]["trich_yeu"] = "triển khai tập huấn ??? cho cán bộ"
        self.write_spec(spec)
        code, data, _ = self.run_cli(self.folder)
        self.assertEqual(code, 0, data)
        self.assertTrue(data["ban_nhap"])
        self.assertEqual(data["so_o_can_bo_sung"], 1)

    def test_nhap_flag_only_changes_wording(self):
        self.write_spec(load_example("cong_van.json"))
        _, plain, _ = self.run_cli(self.folder)
        _, draft, _ = self.run_cli(self.folder, "--nhap")
        self.assertTrue(draft["ban_nhap"])
        self.assertEqual(draft["so_o_can_bo_sung"], plain["so_o_can_bo_sung"])
        self.assertEqual(draft["kiem_tra"], plain["kiem_tra"])
        self.assertNotEqual(draft["warnings"][0], plain["warnings"][0])
        self.assertIn("--nhap", draft["warnings"][0])

    def test_every_nd30_example_builds(self):
        examples = sorted(EXAMPLES.glob("*.json"))
        self.assertGreaterEqual(len(examples), 9)
        for example in examples:
            with self.subTest(example=example.name):
                folder = self.root / example.stem
                folder.mkdir()
                spec = load_example(example.name)
                self.write_spec(spec, folder)
                code, data, _ = self.run_cli(folder)
                self.assertEqual(code, 0, data)
                self.assertTrue(data["ready"], data)
                self.assertEqual(data["profile"], spec.get("profile", "administrative"))
                self.assertTrue((folder / "van-ban.docx").is_file())

    def test_legal_documents_keep_profile_from_json(self):
        for name in ("nghi_quyet_hdnd.json", "quyet_dinh_ubnd_qppl.json"):
            with self.subTest(example=name):
                folder = self.root / Path(name).stem
                folder.mkdir()
                spec = load_example(name)
                spec["profile"] = "minutes-administrative"
                self.write_spec(spec, folder)
                code, data, _ = self.run_cli(folder)
                self.assertEqual(code, 0, data)
                self.assertEqual(data["profile"], "minutes-administrative")
                report = (folder / "kiem-tra.md").read_text(encoding="utf-8")
                self.assertIn("minutes-administrative", report)

    def test_no_nd30_text_leaks_to_stdout(self):
        self.write_spec(load_example("cong_van.json"))
        _, _, text = self.run_cli(self.folder)
        self.assertNotIn("Đã xuất", text)
        self.assertNotIn("===", text)


class SubprocessTest(CliCase):
    def test_vietnamese_folder_with_spaces(self):
        folder = self.root / "_van-ban" / "Công văn tập huấn AI"
        folder.mkdir(parents=True)
        self.write_spec(load_example("cong_van.json"), folder)
        env = dict(os.environ)
        env.pop("PYTHONIOENCODING", None)
        env.pop("PYTHONUTF8", None)
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), str(folder)],
            capture_output=True, env=env, timeout=120,
        )
        stdout = proc.stdout.decode("utf-8")
        lines = [line for line in stdout.splitlines() if line.strip()]
        self.assertEqual(len(lines), 1, stdout)
        data = json.loads(lines[0])
        self.assertEqual(proc.returncode, 0, data)
        self.assertTrue(data["ready"])
        self.assertTrue((folder / "van-ban.docx").is_file())
        self.assertTrue((folder / "kiem-tra.md").is_file())
        self.assertTrue(any("Công văn tập huấn AI" in p for p in data["files"]))


class ErrorTest(CliCase):
    def test_missing_source_is_input(self):
        code, data, _ = self.run_cli(self.folder)
        self.assertEqual(code, 1)
        self.assertFalse(data["ready"])
        self.assertEqual(data["error"]["step"], "input")
        self.assertIn("noi-dung.json", data["error"]["message"])

    def test_missing_folder_is_input(self):
        code, data, _ = self.run_cli(self.root / "khong-co")
        self.assertEqual(data["error"]["step"], "input")

    def test_broken_json_reports_line(self):
        (self.folder / "noi-dung.json").write_text(
            '{\n  "header": {\n    "ky_hieu": "GDĐT"\n    "trich_yeu": "x"\n  }\n}\n',
            encoding="utf-8",
        )
        code, data, _ = self.run_cli(self.folder)
        self.assertEqual(code, 1)
        self.assertEqual(data["error"]["step"], "json")
        self.assertIn("dòng 4", data["error"]["message"])

    def test_missing_ky_hieu_names_the_field(self):
        spec = filled_cong_van()
        del spec["header"]["ky_hieu"]
        self.write_spec(spec)
        code, data, _ = self.run_cli(self.folder)
        self.assertEqual(code, 1)
        self.assertEqual(data["error"]["step"], "json")
        self.assertIn("header.ky_hieu", data["error"]["message"])
        self.assertFalse((self.folder / "van-ban.docx").exists())

    def test_unknown_body_type_names_the_item(self):
        spec = filled_cong_van()
        spec["body"].append({"type": "hinh-anh", "text": "x"})
        self.write_spec(spec)
        _, data, _ = self.run_cli(self.folder)
        self.assertEqual(data["error"]["step"], "json")
        self.assertIn("body[3].type", data["error"]["message"])

    def test_unknown_profile_is_json_error(self):
        spec = filled_cong_van()
        spec["profile"] = "dang"
        self.write_spec(spec)
        _, data, _ = self.run_cli(self.folder)
        self.assertEqual(data["error"]["step"], "json")
        self.assertIn("profile", data["error"]["message"])

    def test_locked_target_is_write(self):
        self.write_spec(filled_cong_van())
        with mock.patch.object(van_ban.os, "replace", side_effect=PermissionError("locked")):
            code, data, _ = self.run_cli(self.folder)
        self.assertEqual(code, 1)
        self.assertEqual(data["error"]["step"], "write")
        self.assertEqual(data["error"]["fix"], "Đóng file Word đang mở rồi chạy lại.")
        leftovers = [p.name for p in self.folder.iterdir() if p.name != "noi-dung.json"]
        self.assertEqual(leftovers, [])

    def test_real_format_error_is_the_thuc_and_removes_docx(self):
        (self.folder / "van-ban.docx").write_bytes(b"old")
        spec = filled_cong_van()
        spec["body"].append({"type": "paragraph", "text": "• Nội dung gạch đầu dòng tự động"})
        self.write_spec(spec)
        code, data, _ = self.run_cli(self.folder)
        self.assertEqual(code, 1)
        self.assertFalse(data["ready"])
        self.assertEqual(data["error"]["step"], "the-thuc")
        self.assertIn("A. Bullet tự động", data["error"]["message"])
        self.assertGreaterEqual(data["kiem_tra"]["loi"], 1)
        self.assertFalse((self.folder / "van-ban.docx").exists())
        self.assertTrue((self.folder / "kiem-tra.md").is_file())
        self.assertNotIn("van-ban.docx", " ".join(data["files"]))

    def test_real_error_beside_blanks_is_still_the_thuc(self):
        spec = load_example("cong_van.json")
        spec["body"].append({"type": "paragraph", "text": "• Gạch đầu dòng"})
        self.write_spec(spec)
        _, data, _ = self.run_cli(self.folder)
        self.assertEqual(data["error"]["step"], "the-thuc")
        self.assertNotIn("A. Placeholder", data["error"]["message"])
        self.assertFalse((self.folder / "van-ban.docx").exists())

    def test_faked_hard_error_is_the_thuc(self):
        self.write_spec(filled_cong_van())
        real = van_ban.run_validator

        def fake(vd, path, profile, allow_placeholder):
            results = real(vd, path, profile, allow_placeholder)
            return results + [(vd.FAIL, "A. Font & màu", "Chữ không đen (1 chỗ)")]

        with mock.patch.object(van_ban, "run_validator", side_effect=fake):
            _, data, _ = self.run_cli(self.folder)
        self.assertEqual(data["error"]["step"], "the-thuc")
        self.assertIn("A. Font & màu", data["error"]["message"])
        self.assertFalse((self.folder / "van-ban.docx").exists())

    def test_missing_python_docx_is_docx(self):
        self.write_spec(filled_cong_van())
        err = ImportError("No module named 'docx'", name="docx")
        with mock.patch.object(van_ban, "load_nd30", side_effect=err):
            code, data, _ = self.run_cli(self.folder)
        self.assertEqual(code, 1)
        self.assertEqual(data["error"]["step"], "docx")

    def test_bad_argument_is_input(self):
        code, data, _ = self.run_cli(self.folder, "--khong-co")
        self.assertEqual(data["error"]["step"], "input")

    def test_error_steps_stay_in_contract(self):
        self.assertEqual(
            set(van_ban.ERROR_STEPS),
            {"input", "json", "the-thuc", "docx", "write", "internal"},
        )


class EmitEncodingTest(unittest.TestCase):
    def test_emit_falls_back_to_utf8_buffer(self):
        class LegacyStdout:
            def __init__(self):
                self.buffer = io.BytesIO()

            def write(self, text):
                text.encode("cp1252")
                return len(text)

            def flush(self):
                pass

        stream = LegacyStdout()
        with mock.patch.object(van_ban.sys, "stdout", stream):
            van_ban.emit({"ready": False, "warnings": ["Còn ô cần bổ sung"]})
        data = json.loads(stream.buffer.getvalue().decode("utf-8").strip())
        self.assertEqual(data["warnings"], ["Còn ô cần bổ sung"])


if __name__ == "__main__":
    unittest.main()
