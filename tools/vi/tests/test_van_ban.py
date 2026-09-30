"""Test cho lệnh soạn văn bản hành chính theo Nghị định 30 (tools/vi/van_ban.py)."""

import contextlib
import io
import json
import os
import re
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
ISSUE_DATE = {"ngay": "05", "thang": "10", "nam": "2026"}
REMINDER = "Văn bản chưa đóng dấu, chưa ký; soát và điền đủ trước khi ban hành."


def load_example(name: str) -> dict:
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


def filled_cong_van() -> dict:
    spec = load_example("cong_van.json")
    spec["body"][1]["text"] = (
        "Thời gian: 08 giờ 00 ngày 15/10/2026; địa điểm: Hội trường Phòng Giáo dục và Đào tạo."
    )
    spec["signature"]["nguoi_ky"] = "Nguyễn Văn An"
    spec["header"].update(ISSUE_DATE)
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

    def test_original_example_also_lacks_the_issue_date(self):
        self.write_spec(load_example("cong_van.json"))
        code, data, _ = self.run_cli(self.folder)
        self.assertEqual(code, 0, data)
        self.assertTrue(data["ban_nhap"])
        self.assertEqual(data["so_o_can_bo_sung"], 3)
        self.assertIn("ngày ban hành", "\n".join(data["warnings"]))

    def test_original_example_is_a_draft_with_two_blanks(self):
        spec = load_example("cong_van.json")
        spec["header"].update(ISSUE_DATE)
        self.write_spec(spec)
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

    def test_engine_inserted_signer_blank_is_counted(self):
        spec = filled_cong_van()
        del spec["signature"]["nguoi_ky"]
        self.write_spec(spec)
        code, data, _ = self.run_cli(self.folder)
        self.assertEqual(code, 0, data)
        self.assertTrue(data["ban_nhap"])
        self.assertEqual(data["so_o_can_bo_sung"], 1)
        self.assertIn("còn 1 ô", data["warnings"][0])
        self.assertTrue(any("họ tên người ký" in w for w in data["warnings"][1:]), data)

    def test_checker_only_blank_is_listed_beside_json_blank(self):
        spec = filled_cong_van()
        spec["body"][1]["text"] = "[CẦN BỔ SUNG: x]"
        spec["kinh_gui"] = "<Tên đơn vị>"
        self.write_spec(spec)
        _, data, _ = self.run_cli(self.folder)
        self.assertTrue(data["ban_nhap"])
        self.assertEqual(data["so_o_can_bo_sung"], 2)
        joined = "\n".join(data["warnings"])
        self.assertIn("[CẦN BỔ SUNG: x]", joined)
        self.assertIn("<Tên đơn vị>", joined)
        report = (self.folder / "kiem-tra.md").read_text(encoding="utf-8")
        self.assertIn("<Tên đơn vị>", report)

    def test_lowercase_blank_is_counted(self):
        spec = filled_cong_van()
        spec["body"][1]["text"] = "Thời gian: [cần bổ sung: y]"
        self.write_spec(spec)
        _, data, _ = self.run_cli(self.folder)
        self.assertTrue(data["ban_nhap"])
        self.assertEqual(data["so_o_can_bo_sung"], 1)
        self.assertIn("[cần bổ sung: y]", "\n".join(data["warnings"]))

    def test_empty_issue_date_is_a_blank(self):
        spec = filled_cong_van()
        spec["header"].update({"ngay": "", "thang": "", "nam": ""})
        self.write_spec(spec)
        _, data, _ = self.run_cli(self.folder)
        self.assertTrue(data["ban_nhap"])
        self.assertEqual(data["so_o_can_bo_sung"], 1)
        self.assertIn("ngày ban hành", "\n".join(data["warnings"]))
        report = (self.folder / "kiem-tra.md").read_text(encoding="utf-8")
        self.assertIn("ngày ban hành", report)

    def test_empty_document_number_is_only_a_warning(self):
        spec = filled_cong_van()
        spec["header"]["so_vb"] = ""
        self.write_spec(spec)
        _, data, _ = self.run_cli(self.folder)
        self.assertFalse(data["ban_nhap"])
        self.assertEqual(data["so_o_can_bo_sung"], 0)
        self.assertTrue(any(w.startswith("B3.") for w in data["warnings"]), data)

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

    def test_legal_documents_pass_the_given_profile_through(self):
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


class SignerTitleTest(CliCase):
    """B6: chức vụ ngoài danh sách của bộ kiểm ND30 (HIỆU TRƯỞNG…) không còn là cảnh báo giả."""

    def run_signed(self, **signature):
        spec = filled_cong_van()
        spec["header"]["so_vb"] = "12"
        spec["signature"].update(signature)
        self.write_spec(spec)
        code, data, _ = self.run_cli(self.folder)
        self.assertEqual(code, 0, data)
        report = (self.folder / "kiem-tra.md").read_text(encoding="utf-8")
        return data, report

    def assert_no_b6_warning(self, data, report, title):
        self.assertFalse([w for w in data["warnings"] if w.startswith("B6")], data["warnings"])
        pattern = rf"^\| ✓ \| B6[^|]*\| Chức vụ người ký: {re.escape(title)} \|$"
        self.assertRegex(report, re.compile(pattern, re.M))

    def test_principal_is_ok_and_only_b7_remains(self):
        data, report = self.run_signed(chuc_vu="HIỆU TRƯỞNG")
        self.assert_no_b6_warning(data, report, "HIỆU TRƯỞNG")
        self.assertEqual(data["kiem_tra"]["canh_bao"], 1, data["warnings"])
        checks = [w for w in data["warnings"]
                  if not w.startswith((van_ban.CHECK_VALUES_PREFIX, "Có tên đơn vị cấp huyện"))]
        self.assertEqual(len(checks), 1, data["warnings"])
        self.assertTrue(checks[0].startswith("B7"))

    def test_vice_principal_signing_for_the_principal_is_ok(self):
        data, report = self.run_signed(quyen_han="KT.", chuc_vu_thay="HIỆU TRƯỞNG",
                                       chuc_vu="PHÓ HIỆU TRƯỞNG")
        self.assert_no_b6_warning(data, report, "PHÓ HIỆU TRƯỞNG")

    def test_head_of_department_is_ok(self):
        data, report = self.run_signed(chuc_vu="TỔ TRƯỞNG")
        self.assert_no_b6_warning(data, report, "TỔ TRƯỞNG")

    def test_empty_title_still_warns(self):
        data, report = self.run_signed(chuc_vu="")
        self.assertTrue([w for w in data["warnings"] if w.startswith("B6")], data["warnings"])
        self.assertIn("| ⚠ | B6. Người ký |", report)

    def test_lowercase_title_still_warns(self):
        data, _ = self.run_signed(chuc_vu="Hiệu trưởng")
        self.assertTrue([w for w in data["warnings"] if w.startswith("B6")], data["warnings"])


def _set(path, value):
    def apply(spec):
        node = spec
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
    return apply


def _drop(path):
    def apply(spec):
        node = spec
        for key in path[:-1]:
            node = node[key]
        node.pop(path[-1], None)
    return apply


class EmptyFieldBlankTest(CliCase):
    """Trường trống hay thiếu mà văn bản vẫn in ra được thì phải là ô cần bổ sung, không phải thành phẩm."""

    CASES = (
        ("nguoi_ky rỗng", _set(("signature", "nguoi_ky"), ""), "họ tên người ký"),
        ("chuc_vu rỗng", _set(("signature", "chuc_vu"), " "), "chức vụ người ký"),
        ("co_quan_ban_hanh rỗng", _set(("header", "co_quan_ban_hanh"), ""), "tên cơ quan ban hành"),
        ("ky_hieu rỗng", _set(("header", "ky_hieu"), ""), "ký hiệu văn bản"),
        ("trich_yeu rỗng", _set(("header", "trich_yeu"), ""), "trích yếu"),
        ("dia_danh rỗng", _set(("header", "dia_danh"), ""), "địa danh"),
        ("kinh_gui thiếu", _drop(("kinh_gui",)), "kính gửi"),
        ("kinh_gui rỗng", _set(("kinh_gui",), ""), "kính gửi"),
        ("body rỗng", _set(("body",), []), "nội dung"),
        ("thiếu tháng", _set(("header", "thang"), ""), "ngày ban hành"),
        ("thiếu năm", _set(("header", "nam"), ""), "ngày ban hành"),
    )

    def test_each_empty_field_is_a_named_blank(self):
        for name, mutate, phrase in self.CASES:
            with self.subTest(case=name):
                folder = self.root / re.sub(r"\W+", "-", name)
                folder.mkdir()
                spec = filled_cong_van()
                mutate(spec)
                self.write_spec(spec, folder)
                code, data, _ = self.run_cli(folder)
                self.assertEqual(code, 0, data)
                self.assertTrue(data["ban_nhap"], data)
                self.assertEqual(data["so_o_can_bo_sung"], 1, data["warnings"])
                blank_lines = [w for w in data["warnings"] if w.startswith("Ô cần bổ sung")]
                self.assertEqual(len(blank_lines), 1, data["warnings"])
                self.assertIn(phrase, blank_lines[0])
                report = (folder / "kiem-tra.md").read_text(encoding="utf-8")
                self.assertIn(phrase, section_of(report, "## Ô cần bổ sung"))

    def test_missing_signature_block_names_signer_and_title(self):
        spec = filled_cong_van()
        del spec["signature"]
        self.write_spec(spec)
        _, data, _ = self.run_cli(self.folder)
        self.assertTrue(data["ban_nhap"])
        joined = "\n".join(w for w in data["warnings"] if w.startswith("Ô cần bổ sung"))
        self.assertIn("họ tên người ký", joined)
        self.assertIn("chức vụ người ký", joined)

    def test_kinh_gui_is_optional_outside_cong_van(self):
        spec = load_example("quyet_dinh.json")
        spec["header"].update(ISSUE_DATE)
        spec.pop("kinh_gui", None)
        self.write_spec(spec)
        _, data, _ = self.run_cli(self.folder)
        self.assertNotIn("kính gửi", "\n".join(w for w in data["warnings"] if w.startswith("Ô cần")))

    def test_blank_day_with_month_and_year_is_still_final(self):
        spec = filled_cong_van()
        spec["header"]["ngay"] = ""
        self.write_spec(spec)
        _, data, _ = self.run_cli(self.folder)
        self.assertFalse(data["ban_nhap"], data["warnings"])
        self.assertEqual(data["so_o_can_bo_sung"], 0)


def section_of(text: str, heading: str) -> str:
    start = text.index(heading) + len(heading)
    end = text.find("\n## ", start)
    return text[start:] if end == -1 else text[start:end]


class ProfileGuardTest(CliCase):
    def test_lower_profile_on_a_real_document_is_refused(self):
        cases = (
            ("cong-van-general", filled_cong_van(), "general"),
            ("to-trinh-academic", load_example("input-sample.json"), "academic"),
        )
        for name, spec, profile in cases:
            with self.subTest(case=name):
                folder = self.root / name
                folder.mkdir()
                spec["profile"] = profile
                self.write_spec(spec, folder)
                code, data, _ = self.run_cli(folder)
                self.assertEqual(code, 1)
                self.assertEqual(data["error"]["step"], "json")
                self.assertIn("profile", data["error"]["message"])
                self.assertIn("dùng profile administrative", data["error"]["fix"])
                self.assertFalse((folder / "van-ban.docx").exists())

    def test_free_document_may_use_general(self):
        spec = filled_cong_van()
        spec["profile"] = "general"
        spec["header"]["is_cong_van"] = False
        spec["header"].pop("ten_loai_in_hoa", None)
        self.write_spec(spec)
        code, data, _ = self.run_cli(self.folder)
        self.assertEqual(code, 0, data)
        self.assertEqual(data["profile"], "general")


class CheckValuesTest(CliCase):
    """Giá trị máy không kiểm được đúng sai: in nguyên văn để thầy cô đối chiếu."""

    def test_report_and_warning_echo_values_verbatim(self):
        spec = load_example("quyet_dinh.json")
        spec["header"].update(ISSUE_DATE)
        spec["header"]["so_vb"] = "27"
        spec["kinh_gui"] = "Tổ Toán – Tin"
        spec["signature"].update({"nguoi_ky": "Trần Thị Bình", "chuc_vu": "HIỆU TRƯỞNG"})
        self.write_spec(spec)
        code, data, _ = self.run_cli(self.folder)
        self.assertEqual(code, 0, data)
        header = spec["header"]
        can_cu = next(b for b in spec["body"] if b.get("type") == "can_cu")["items"]
        expected = [f"27/{header['ky_hieu']}", "ngày 05 tháng 10 năm 2026", "Trần Thị Bình", "HIỆU TRƯỞNG",
                    header["co_quan_chu_quan"], header["co_quan_ban_hanh"], header["dia_danh"],
                    "Tổ Toán – Tin", *can_cu]
        report = section_of((self.folder / "kiem-tra.md").read_text(encoding="utf-8"),
                            "## Thầy cô đối chiếu")
        line = next(w for w in data["warnings"] if w.startswith(van_ban.CHECK_VALUES_PREFIX))
        for value in expected:
            with self.subTest(value=value):
                self.assertIn(value, report)
                self.assertIn(value, line)


class TextShapeTest(CliCase):
    def test_decomposed_blank_is_counted(self):
        import unicodedata
        spec = filled_cong_van()
        spec["body"][1]["text"] = unicodedata.normalize("NFD", "Thời gian: [CẦN BỔ SUNG: giờ họp]")
        self.write_spec(spec)
        _, data, _ = self.run_cli(self.folder)
        self.assertTrue(data["ban_nhap"], data["warnings"])
        self.assertEqual(data["so_o_can_bo_sung"], 1)

    def test_suspicious_filler_warns_without_making_a_draft(self):
        for text, shown in (("Thời gian: ........ ngày 15/10", "........"),
                            ("Địa điểm: …… phòng họp", "……"),
                            ("Theo Công văn số XX/XX của Sở", "XX/XX"),
                            ("Người phụ trách: [CAN BO SUNG: ten]", "[CAN BO SUNG")):
            with self.subTest(text=text):
                folder = self.root / f"f{abs(hash(text))}"
                folder.mkdir()
                spec = filled_cong_van()
                spec["body"][1]["text"] = text
                self.write_spec(spec, folder)
                code, data, _ = self.run_cli(folder)
                self.assertEqual(code, 0, data)
                self.assertFalse(data["ban_nhap"], data["warnings"])
                self.assertTrue([w for w in data["warnings"] if w.startswith("Nghi còn chỗ trống")
                                 and shown in w], data["warnings"])


def two_tier_cong_van() -> dict:
    """Công văn dùng đúng danh xưng sau 1/7/2025: chỉ cấp tỉnh và cấp xã, phường."""
    spec = filled_cong_van()
    spec["header"]["co_quan_chu_quan"] = "UBND TỈNH BẮC NINH"
    spec["header"]["co_quan_ban_hanh"] = "SỞ GIÁO DỤC VÀ ĐÀO TẠO"
    spec["kinh_gui"] = "Các trường trung học phổ thông trên địa bàn tỉnh"
    spec["body"][0]["text"] = "Sở Giáo dục và Đào tạo tổ chức tập huấn ứng dụng AI cho giáo viên."
    return spec


class OldAdministrativeUnitTest(CliCase):
    def test_example_with_district_units_warns_in_json_and_report(self):
        self.write_spec(filled_cong_van())  # ví dụ ND30 gốc: "UBND HUYỆN ...", "trên địa bàn huyện"
        code, data, _ = self.run_cli(self.folder)
        self.assertEqual(code, 0, data)
        notes = [w for w in data["warnings"] if w.startswith("Có tên đơn vị cấp huyện")]
        self.assertEqual(len(notes), 1, data["warnings"])
        self.assertIn("1/7/2025", notes[0])
        report = (self.folder / "kiem-tra.md").read_text(encoding="utf-8")
        self.assertIn("## Đơn vị hành chính", report)

    def test_warning_does_not_make_a_draft(self):
        self.write_spec(filled_cong_van())
        _, data, _ = self.run_cli(self.folder)
        self.assertFalse(data["ban_nhap"], data["warnings"])

    def test_every_old_level_is_caught_once(self):
        for text, shown in (("Kính gửi UBND quận Ba Đình", "quận"), ("các thị xã trong tỉnh", "thị xã"),
                            ("UBND thị trấn Đông Anh", "thị trấn"), ("Phòng GD&ĐT huyện Gia Lâm", "huyện")):
            with self.subTest(text=text):
                folder = self.root / f"u{abs(hash(text))}"
                folder.mkdir()
                spec = two_tier_cong_van()
                spec["body"][1]["text"] = text
                self.write_spec(spec, folder)
                _, data, _ = self.run_cli(folder)
                notes = [w for w in data["warnings"] if w.startswith("Có tên đơn vị cấp huyện")]
                self.assertEqual(len(notes), 1, data["warnings"])
                self.assertIn(shown, notes[0])

    def test_two_tier_names_do_not_warn(self):
        spec = two_tier_cong_van()
        spec["body"][1]["text"] = "Kính đề nghị UBND các xã, phường và đặc khu phối hợp; địa điểm: phường Kinh Bắc."
        self.write_spec(spec)
        _, data, _ = self.run_cli(self.folder)
        self.assertFalse([w for w in data["warnings"] if w.startswith("Có tên đơn vị cấp huyện")],
                         data["warnings"])


class NoYamlTest(CliCase):
    def test_core_flow_runs_without_pyyaml(self):
        self.write_spec(filled_cong_van())
        code = (
            "import sys; sys.modules['yaml'] = None; "
            f"sys.path.insert(0, {str(SCRIPT.parent)!r}); import van_ban; "
            f"sys.exit(van_ban.main([{str(self.folder)!r}]))"
        )
        proc = subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=120)
        lines = [l for l in proc.stdout.decode("utf-8").splitlines() if l.strip()]
        self.assertEqual(len(lines), 1, proc.stdout + proc.stderr)
        data = json.loads(lines[0])
        self.assertEqual(proc.returncode, 0, data)
        self.assertTrue(data["ready"])
        self.assertFalse(data["ban_nhap"], data["warnings"])
        self.assertEqual(data["kiem_tra"]["loi"], 0)
        self.assertTrue((self.folder / "van-ban.docx").is_file())


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

    def test_unwritable_folder_is_write(self):
        self.write_spec(filled_cong_van())
        with mock.patch.object(van_ban.tempfile, "mkstemp", side_effect=PermissionError("read-only")):
            code, data, _ = self.run_cli(self.folder)
        self.assertEqual(code, 1)
        self.assertEqual(data["error"]["step"], "write")

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
