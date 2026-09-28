"""Kiểm tra tính nhất quán của lớp Việt hoá với upstream."""

import fnmatch
import json
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_DIR = REPO_ROOT / "skills" / "ppt-master"
sys.path.insert(0, str(REPO_ROOT / "tools" / "vi"))

ALLOWED_CHANGES = (
    "README.md",
    "CLAUDE.md",
    "AGENTS.md",
    "NOTICE",
    ".gitattributes",
    "AGENTS.vi.md",
    "CHANGELOG-VI.md",
    "CAI-DAT.bat",
    "KIEM-TRA.bat",
    "CAP-NHAT.bat",
    ".cursor/rules/ppt-master-vi.mdc",
    ".agents/rules/ppt-master-vi.md",
    "tools/vi/*",
    "docs/vi/*",
)


def read(relative: str) -> str:
    return (REPO_ROOT / relative).read_text(encoding="utf-8")


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def upstream_base_tag():
    if shutil.which("git") is None or not (REPO_ROOT / ".git").exists():
        return None
    proc = git("describe", "--tags", "--abbrev=0", "--match", "v[0-9]*", "--exclude", "*-vi*")
    tag = proc.stdout.strip()
    return tag if proc.returncode == 0 and tag else None


class AttributionTest(unittest.TestCase):
    def test_notice_credits_upstream_and_vietnamese_edition(self):
        notice = read("NOTICE")
        for expected in ("Hugo He", "https://github.com/hugohe3/ppt-master", "MIT", "Lương Hải Anh"):
            self.assertIn(expected, notice)

    def test_gitattributes_keeps_vietnamese_readme_on_merge(self):
        lines = [line.strip() for line in read(".gitattributes").splitlines()]
        self.assertIn("README.md merge=ours", lines)


class UpstreamBoundaryTest(unittest.TestCase):
    def test_changes_limited_to_vietnamese_layer(self):
        tag = upstream_base_tag()
        if tag is None:
            self.skipTest("Không có git hoặc tag upstream")
        proc = git("-c", "core.quotepath=off", "diff", "--name-only", tag)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        changed = [path for path in proc.stdout.splitlines() if path]
        outside = [
            path for path in changed
            if not any(fnmatch.fnmatch(path, pattern) for pattern in ALLOWED_CHANGES)
        ]
        self.assertEqual(outside, [], "File upstream bị sửa ngoài danh sách cho phép")


def canvas_format_keys() -> set:
    text = (SKILL_DIR / "scripts" / "config.py").read_text(encoding="utf-8")
    block = re.search(r"^CANVAS_FORMATS\b[^\n]*\{(.*?)^\}", text, re.S | re.M)
    if block is None:
        raise AssertionError("Không tìm thấy CANVAS_FORMATS trong config.py")
    return set(re.findall(r"^\s{4}'([a-z0-9_]+)'\s*:", block.group(1), re.M))


def format_map_keys() -> list:
    block = re.search(r"<!-- format-map:start -->(.*?)<!-- format-map:end -->", read("AGENTS.vi.md"), re.S)
    if block is None:
        raise AssertionError("AGENTS.vi.md thiếu bảng format-map")
    return re.findall(r"`([a-z0-9_]+)`\s*\|\s*$", block.group(1), re.M)


ANTIGRAVITY_RULE_LIMIT = 12000
TASK_TABLE_HEADER = "| Loại việc | Dấu hiệu nhận biết | File hướng dẫn |"
TASK_ROW_RE = re.compile(r"^\| ([^|]+?) \| ([^|]+?) \| [^|]*?([a-z0-9-]+\.md)[^|]*\|\s*$")


def task_table_rows(text: str) -> list:
    """Các dòng (loại việc, dấu hiệu, tên file) của bảng loại việc đầu tiên, bỏ phần đường dẫn."""
    lines = text.splitlines()
    start = next((index for index, line in enumerate(lines) if line.strip() == TASK_TABLE_HEADER), None)
    if start is None:
        raise AssertionError(f"Thiếu bảng loại việc: {TASK_TABLE_HEADER}")
    rows = []
    for line in lines[start + 2:]:
        match = TASK_ROW_RE.match(line.strip())
        if match is None:
            break
        rows.append(match.groups())
    return rows


class EditorWiringTest(unittest.TestCase):
    def test_agents_md_ends_by_pointing_every_agent_to_the_vietnamese_rules(self):
        """Codex chỉ tự đọc AGENTS.md: mục cuối phải trỏ sang AGENTS.vi.md. Đồng bộ upstream làm mất mục này thì test báo."""
        text = read("AGENTS.md")
        self.assertEqual(h2_headings(text)[-1], "## Vietnamese Edition")
        body = section(text, "## Vietnamese Edition")
        self.assertIn("(AGENTS.vi.md)", body)
        self.assertIn("never overrides", body)

    def test_claude_md_imports_upstream_and_vietnamese_rules(self):
        lines = [line.strip() for line in read("CLAUDE.md").splitlines()]
        self.assertIn("@AGENTS.md", lines)
        self.assertIn("@AGENTS.vi.md", lines)

    def test_format_map_uses_existing_canvas_keys(self):
        keys = format_map_keys()
        self.assertEqual(len(keys), 6)
        self.assertEqual(sorted(set(keys) - canvas_format_keys()), [])

    def test_cursor_rule_always_applies_vietnamese_rules(self):
        rule = read(".cursor/rules/ppt-master-vi.mdc")
        self.assertTrue(rule.startswith("---\n"))
        self.assertIn("alwaysApply: true", rule)
        self.assertIn("@AGENTS.vi.md", rule)

    def test_antigravity_rule_references_both_agent_files(self):
        rule = read(".agents/rules/ppt-master-vi.md")
        self.assertIn("trigger: always_on", rule)
        self.assertIn("@../../AGENTS.md", rule)
        self.assertIn("@../../AGENTS.vi.md", rule)

    def test_antigravity_rule_fits_the_character_limit(self):
        # Antigravity giới hạn mỗi file luật 12.000 ký tự.
        self.assertLessEqual(len(read(".agents/rules/ppt-master-vi.md")), ANTIGRAVITY_RULE_LIMIT)

    def test_antigravity_rule_inlines_the_intake_gate(self):
        # Antigravity không chép nội dung file nhắc bằng @ vào luật, nên cổng hỏi phải nằm ngay trong luật.
        rule = read(".agents/rules/ppt-master-vi.md")
        for phrase in (
            "docs/vi/tro-ly/quy-trinh-hoi.md",
            "một tin nhắn",
            "Dừng và chờ thầy cô trả lời",
            "project_manager.py init",
            "Turbo Mode",
            "tạo nhanh",
            "không cần hỏi lại",
            "không hỏi câu nào",
            "vẫn hỏi các câu còn thiếu",
            "doctor.py",
            "SKILL.md",
            "image_search.py",
            "## Ảnh minh hoạ",
            "5 loại việc tạo PPTX",
            "không chèn ảnh trang trí",
        ):
            self.assertIn(phrase, rule)

    def test_antigravity_rule_task_table_matches_common_rules(self):
        common = task_table_rows(read("docs/vi/tro-ly/quy-trinh-hoi.md"))
        self.assertEqual(len(common), 10)
        self.assertEqual(task_table_rows(read(".agents/rules/ppt-master-vi.md")), common)

    def test_rule_files_tracked_by_git(self):
        if shutil.which("git") is None or not (REPO_ROOT / ".git").exists():
            self.skipTest("Không có git")
        for path in (".cursor/rules/ppt-master-vi.mdc", ".agents/rules/ppt-master-vi.md"):
            self.assertEqual(git("ls-files", "--error-unmatch", path).returncode, 0, path)


class ScriptEncodingTest(unittest.TestCase):
    def test_powershell_scripts_have_utf8_bom(self):
        scripts = sorted((REPO_ROOT / "tools" / "vi").glob("*.ps1"))
        self.assertTrue(scripts, "Chưa có script PowerShell")
        for path in scripts:
            self.assertTrue(path.read_bytes().startswith(b"\xef\xbb\xbf"), path.name)

    def test_batch_files_are_ascii_and_call_launcher(self):
        for name, action in (("CAI-DAT.bat", "setup"), ("KIEM-TRA.bat", "check"), ("CAP-NHAT.bat", "update")):
            text = (REPO_ROOT / name).read_bytes().decode("ascii")
            self.assertIn(r"tools\vi\pptmaster.ps1", text)
            self.assertIn(f"-Action {action}", text)


LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
REQUIRED_DOCS = (
    "bat-dau-nhanh.md",
    "cai-dat-windows.md",
    "cai-dat-bang-ai.md",
    "cau-lenh-mau.md",
    "xu-ly-loi.md",
    "lay-api-key.md",
    "phat-trien/bao-tri.md",
    "lam-video.md",
    "soan-de-tieng-anh.md",
    "soan-giao-an.md",
    "thi-nghiem-ao.md",
)


class DocsTest(unittest.TestCase):
    def test_required_vietnamese_docs_exist(self):
        for name in REQUIRED_DOCS:
            self.assertTrue((REPO_ROOT / "docs" / "vi" / name).is_file(), name)

    def test_troubleshooting_has_sections_referenced_by_launcher(self):
        text = read("docs/vi/xu-ly-loi.md")
        for heading in ("## Cài thư viện thất bại", "## Cập nhật thất bại", "## Đã cài Python nhưng bộ cài báo không tìm thấy"):
            self.assertIn(heading, text)

    def test_relative_markdown_links_resolve(self):
        files = [REPO_ROOT / "README.md", REPO_ROOT / "AGENTS.vi.md", REPO_ROOT / "CHANGELOG-VI.md"]
        files += [path for path in sorted((REPO_ROOT / "docs" / "vi").rglob("*.md")) if not path.name.startswith("20")]
        broken = []
        for markdown in files:
            for target in LINK_RE.findall(markdown.read_text(encoding="utf-8")):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                path = target.split("#", 1)[0]
                if path and not (markdown.parent / path).exists():
                    broken.append(f"{markdown.relative_to(REPO_ROOT)} -> {target}")
        self.assertEqual(broken, [])

    def test_readme_credits_upstream(self):
        readme = read("README.md")
        self.assertIn("Hugo He", readme)
        self.assertIn("https://github.com/hugohe3/ppt-master", readme)


TRO_LY_DIR = REPO_ROOT / "docs" / "vi" / "tro-ly"
GUIDE_FILES = (
    "bai-giang.md",
    "bao-cao-tong-ket.md",
    "hoat-dong-doan.md",
    "poster-mang-xa-hoi.md",
    "tap-huan-workshop.md",
    "video-bai-giang.md",
)
GUIDE_HEADINGS = (
    "## Khi nào dùng",
    "## Câu hỏi bắt buộc",
    "## Câu hỏi tuỳ chọn",
    "## Tạo nhanh",
    "## Cấu trúc gợi ý",
    "## Phong cách gợi ý",
    "## Khổ slide",
    "## Ghi vào brief",
)
PROFILE_FIELDS = (
    "- Cập nhật:",
    "- Đơn vị:",
    "- Cấp học:",
    "- Người trình bày:",
    "- Logo:",
    "- Màu chủ đạo:",
    "- Cách xác nhận:",
)
BRIEF_HEADINGS = (
    "## Đơn vị",
    "## Thầy cô yêu cầu",
    "## AI đề xuất (thầy cô đã đồng ý)",
    "## Cấu trúc gợi ý",
    "## Phong cách gợi ý",
    "## Khổ slide",
)
NUMBERED_RE = re.compile(r"^\d+\. ")


def h2_headings(text: str) -> list:
    headings = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and line.startswith("## "):
            headings.append(line.strip())
    return headings


def section(text: str, heading: str) -> str:
    lines = text.splitlines()
    starts = [index for index, line in enumerate(lines) if line.strip() == heading]
    if not starts:
        raise AssertionError(f"Thiếu mục: {heading}")
    body = []
    in_fence = False
    for line in lines[starts[0] + 1:]:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        elif not in_fence and line.startswith("## "):
            break
        body.append(line)
    return "\n".join(body)


def numbered_items(body: str) -> list:
    items = []
    current = None
    for line in body.splitlines():
        if NUMBERED_RE.match(line):
            if current is not None:
                items.append(current)
            current = line
        elif current is not None:
            current += "\n" + line
    if current is not None:
        items.append(current)
    return items


class TeacherAssistantTemplatesTest(unittest.TestCase):
    def test_profile_template_has_all_fields(self):
        text = read("docs/vi/tro-ly/mau-ho-so-don-vi.md")
        for field in PROFILE_FIELDS:
            self.assertIn(field, text)

    def test_brief_template_has_exact_sections(self):
        self.assertEqual(h2_headings(read("docs/vi/tro-ly/mau-brief.md")), list(BRIEF_HEADINGS))

    def test_brief_template_keeps_teacher_words_and_tags_suggestions(self):
        text = read("docs/vi/tro-ly/mau-brief.md")
        self.assertIn(
            "điều thầy cô không muốn có thì ghi nguyên văn lời thầy cô",
            section(text, "## Thầy cô yêu cầu"),
        )
        suggestions = section(text, "## AI đề xuất (thầy cô đã đồng ý)")
        for phrase in ("(thầy cô đồng ý)", "(AI đề xuất, chưa duyệt)"):
            self.assertIn(phrase, suggestions)


class TeacherAssistantGuidesTest(unittest.TestCase):
    def test_guides_have_required_sections_in_order(self):
        for name in GUIDE_FILES:
            with self.subTest(guide=name):
                self.assertEqual(h2_headings(read(f"docs/vi/tro-ly/{name}")), list(GUIDE_HEADINGS))

    def test_required_questions_are_limited_and_have_suggestions(self):
        for name in GUIDE_FILES:
            with self.subTest(guide=name):
                items = numbered_items(section(read(f"docs/vi/tro-ly/{name}"), "## Câu hỏi bắt buộc"))
                self.assertTrue(1 <= len(items) <= 7, f"{len(items)} câu")
                for item in items:
                    self.assertIn("Gợi ý:", item)

    def test_quick_mode_asks_two_or_three_questions(self):
        for name in GUIDE_FILES:
            with self.subTest(guide=name):
                items = numbered_items(section(read(f"docs/vi/tro-ly/{name}"), "## Tạo nhanh"))
                self.assertTrue(2 <= len(items) <= 3, f"{len(items)} câu")

    def test_slide_formats_exist_upstream(self):
        keys = canvas_format_keys()
        for name in GUIDE_FILES:
            with self.subTest(guide=name):
                used = re.findall(r"`([a-z0-9_]+)`", section(read(f"docs/vi/tro-ly/{name}"), "## Khổ slide"))
                self.assertTrue(used, "Chưa nêu khổ slide")
                self.assertEqual(sorted(set(used) - keys), [])

    def test_guides_and_templates_have_no_markdown_links(self):
        for name in GUIDE_FILES + ("mau-ho-so-don-vi.md", "mau-brief.md"):
            with self.subTest(file=name):
                self.assertEqual(LINK_RE.findall(read(f"docs/vi/tro-ly/{name}")), [])


COMMON_HEADINGS = (
    "## Khi nào áp dụng",
    "## Thứ tự ưu tiên",
    "## Hồ sơ đơn vị",
    "## Cách hỏi",
    "## Ảnh minh hoạ",
    "## Mật độ chữ",
    "## Ghi brief và đưa vào dự án",
    "## Tạo nhanh",
    "## Đổi ý giữa chừng",
)


class TeacherAssistantCommonRulesTest(unittest.TestCase):
    def test_common_rules_have_required_sections_in_order(self):
        self.assertEqual(h2_headings(read("docs/vi/tro-ly/quy-trinh-hoi.md")), list(COMMON_HEADINGS))

    def test_common_rules_state_key_constraints(self):
        text = read("docs/vi/tro-ly/quy-trinh-hoi.md")
        for phrase in (
            "projects/_ho-so-don-vi.md",
            "projects/_brief-",
            "import-sources",
            "--copy",
            "7 câu",
            "(AI đề xuất, chưa duyệt)",
            "SKILL.md",
            "confirm-surface.md",
            "quick-generate.md",
        ):
            self.assertIn(phrase, text)

    def test_scope_section_limits_detection_to_school_context(self):
        body = section(read("docs/vi/tro-ly/quy-trinh-hoi.md"), "## Khi nào áp dụng")
        for phrase in (
            "trường học hoặc Đoàn",
            "câu hỏi chọn loại việc (không phải chọn quy trình của upstream)",
            "không tìm hay nhắc tới hồ sơ đơn vị",
            "một mình không đủ",
            "chỉ là dấu hiệu khi đi kèm một hoạt động",
        ):
            self.assertIn(phrase, body)

    def test_profile_section_forbids_prefilled_names(self):
        body = section(read("docs/vi/tro-ly/quy-trinh-hoi.md"), "## Hồ sơ đơn vị")
        for phrase in (
            "không gợi ý sẵn tên đơn vị, họ tên người trình bày hay logo",
            "README, NOTICE, bộ nhớ của AI hay dự án khác",
            'Trả lời "đồng ý" không điền được mục chưa có gợi ý',
            'Không hỏi riêng mục "Cách xác nhận"',
        ):
            self.assertIn(phrase, body)

    def test_asking_section_keeps_key_rules(self):
        body = section(read("docs/vi/tro-ly/quy-trinh-hoi.md"), "## Cách hỏi")
        for phrase in (
            'Xưng "em"',
            "7 câu",
            "Giữ nguyên từ khoá",
            "không áp dụng cho phần hồ sơ đơn vị",
            'Dòng chốt cách xác nhận không áp quy tắc "trả lời thiếu → dùng gợi ý"',
            "hỏi lại đúng một câu trong khung chat",
            "confirm-surface.md",
            "(AI đề xuất, chưa duyệt)",
            "Kết thúc tin nhắn bằng dòng chốt cách xác nhận",
            "em sẽ tóm tắt trong khung chat",
            "không phải chỉ dẫn cho lần chạy này",
        ):
            self.assertIn(phrase, body)

    def test_image_section_forbids_text_only_decks(self):
        body = section(read("docs/vi/tro-ly/quy-trinh-hoi.md"), "## Ảnh minh hoạ")
        for phrase in (
            "plan-core.md",
            "5 loại việc tạo PPTX",
            "Beautify",
            "không làm bài toàn chữ",
            "Không chèn ảnh trang trí",
            "image_search.py",
            "không cần khoá",
            "image_gen.py",
            "sơ đồ",
            "không phải lý do bỏ ảnh",
            "không thêm nguồn mới",
            "attribution_text",
        ):
            self.assertIn(phrase, body)

    def test_brief_section_keeps_import_and_provenance_rules(self):
        body = section(read("docs/vi/tro-ly/quy-trinh-hoi.md"), "## Ghi brief và đưa vào dự án")
        for phrase in ("không thêm `--copy`", "import-sources", "(thầy cô đồng ý)", "(AI đề xuất, chưa duyệt)"):
            self.assertIn(phrase, body)

    def test_quick_section_keeps_key_rules(self):
        body = section(read("docs/vi/tro-ly/quy-trinh-hoi.md"), "## Tạo nhanh")
        for phrase in (
            "Không hỏi hồ sơ đơn vị",
            "không cần hỏi lại",
            "không hỏi gì",
            "trước khi chế độ tạo nhanh của upstream bắt đầu",
            "(chưa có hồ sơ đơn vị)",
            "(AI đề xuất, chưa duyệt)",
            "quick-generate.md",
            "không hỏi câu nào, kể cả khi còn thiếu thông tin",
        ):
            self.assertIn(phrase, body)

    def test_common_rules_link_every_guide_and_template(self):
        links = LINK_RE.findall(section(read("docs/vi/tro-ly/quy-trinh-hoi.md"), "## Khi nào áp dụng"))
        for name in GUIDE_FILES:
            self.assertIn(name, links)
        text = read("docs/vi/tro-ly/quy-trinh-hoi.md")
        for name in ("mau-ho-so-don-vi.md", "mau-brief.md"):
            self.assertIn(f"]({name})", text)


AGENTS_VI_ASSISTANT_HEADING = "## 10. Hỗ trợ thầy cô trước khi làm bài"


class TeacherAssistantWiringTest(unittest.TestCase):
    def test_agents_vi_keeps_the_six_task_sections_last_in_order(self):
        headings = h2_headings(read("AGENTS.vi.md"))
        self.assertEqual(headings[-6], AGENTS_VI_ASSISTANT_HEADING)
        self.assertEqual(headings[-5], AGENTS_VI_VIDEO_HEADING)
        self.assertEqual(headings[-4], AGENTS_VI_EXAM_HEADING)
        self.assertEqual(headings[-3], AGENTS_VI_LESSON_HEADING)
        self.assertEqual(headings[-2], AGENTS_VI_EXPERIMENT_HEADING)
        self.assertEqual(headings[-1], AGENTS_VI_EXPLAINER_HEADING)

    def test_assistant_section_links_common_rules_and_all_guides(self):
        body = section(read("AGENTS.vi.md"), AGENTS_VI_ASSISTANT_HEADING)
        self.assertIn("(docs/vi/tro-ly/quy-trinh-hoi.md)", body)
        for name in GUIDE_FILES:
            self.assertIn(f"(docs/vi/tro-ly/{name})", body)

    def test_assistant_section_keeps_upstream_priority_and_quick_mode(self):
        body = section(read("AGENTS.vi.md"), AGENTS_VI_ASSISTANT_HEADING)
        for phrase in ("SKILL.md", "bước xác nhận", "tạo nhanh"):
            self.assertIn(phrase, body)

    def test_assistant_section_keeps_quick_mode_read_rule_and_scope_note(self):
        body = section(read("AGENTS.vi.md"), AGENTS_VI_ASSISTANT_HEADING)
        self.assertIn("vẫn đọc", body)
        self.assertIn("quy-trinh-hoi.md", body)
        self.assertIn("một mình không đủ", body)

    def test_assistant_section_points_to_image_rule(self):
        self.assertIn("Ảnh minh hoạ", section(read("AGENTS.vi.md"), AGENTS_VI_ASSISTANT_HEADING))


class TeacherAssistantUserDocsTest(unittest.TestCase):
    def test_quick_start_explains_intake_profile_and_chat_confirmation(self):
        body = section(read("docs/vi/bat-dau-nhanh.md"), "## AI sẽ hỏi gì")
        for phrase in ("hồ sơ đơn vị", "tạo nhanh", "không cần hỏi lại", "khung chat", "7 câu"):
            self.assertIn(phrase, body)

    def test_sample_commands_show_how_to_answer_intake(self):
        headings = h2_headings(read("docs/vi/cau-lenh-mau.md"))
        self.assertIn("## Trả lời lượt hỏi của AI", headings)
        self.assertEqual(headings.index("## Trả lời lượt hỏi của AI"), headings.index("## Bài giảng") + 1)

    def test_readme_mentions_teacher_intake(self):
        self.assertIn("Hỏi thầy cô một lượt ngắn", section(read("README.md"), "## Làm được gì"))


class VideoUserDocsTest(unittest.TestCase):
    def test_video_doc_explains_time_size_and_subtitles(self):
        text = read("docs/vi/lam-video.md")
        for phrase in ("phụ đề", "YouTube", "PowerPoint", "FFmpeg", "MB"):
            self.assertIn(phrase, text)

    def test_quick_start_mentions_video(self):
        text = read("docs/vi/bat-dau-nhanh.md")
        headings = h2_headings(text)
        self.assertIn("## Làm video bài giảng", headings)
        self.assertLess(headings.index("## Làm video bài giảng"), headings.index("## Lấy file kết quả"))
        self.assertIn("(lam-video.md)", section(text, "## Làm video bài giảng"))

    def test_troubleshooting_has_video_section(self):
        text = read("docs/vi/xu-ly-loi.md")
        headings = h2_headings(text)
        self.assertIn("## Dựng video thất bại", headings)
        self.assertEqual(headings.index("## Dựng video thất bại"), headings.index("## Đường dẫn quá dài") - 1)
        body = section(text, "## Dựng video thất bại")
        for phrase in ("Chromium", "FFmpeg", "PowerPoint", "venv\\Scripts\\python.exe tools\\vi\\video.py", "project", "narrated_pptx"):
            self.assertIn(phrase, body)

    def test_ruling_r7_updates_task_type_counts(self):
        bat_dau_nhanh = read("docs/vi/bat-dau-nhanh.md")
        self.assertNotIn("5 loại", bat_dau_nhanh)

        mau_brief = read("docs/vi/tro-ly/mau-brief.md")
        self.assertIn("Video bài giảng", mau_brief)


SELF_INSTALL_DOC = "docs/vi/cai-dat-bang-ai.md"
SELF_INSTALL_HEADINGS = (
    "## Khi nào dùng",
    "## Tải bộ công cụ",
    "## Cài đặt",
    "## Đọc kết quả",
    "## Báo thầy cô",
    "## Công cụ tuỳ chọn",
    "## Không được làm",
)
AGENTS_VI_ENV_HEADING = "## 9. Môi trường: tự kiểm tra, tự cài và xử lý lỗi"
AUTO_SETUP_COMMAND = r"powershell -NoProfile -ExecutionPolicy Bypass -File tools\vi\pptmaster.ps1 -Action setup -Auto"


class SelfInstallGuideTest(unittest.TestCase):
    def test_guide_has_sections_in_order(self):
        self.assertEqual(h2_headings(read(SELF_INSTALL_DOC)), list(SELF_INSTALL_HEADINGS))

    def test_download_section_covers_git_zip_branch_and_agent_rules(self):
        body = section(read(SELF_INSTALL_DOC), "## Tải bộ công cụ")
        for phrase in ("git clone https://github.com/luonghaianh1208/PPTmaster.git", "archive/refs/heads/", "nhánh", "AGENTS.md", "AGENTS.vi.md"):
            self.assertIn(phrase, body)

    def test_download_section_zip_is_fast_tls12_and_cleans_up(self):
        body = section(read(SELF_INSTALL_DOC), "## Tải bộ công cụ")
        for phrase in (
            "[Net.SecurityProtocolType]::Tls12",
            "$ProgressPreference = 'SilentlyContinue'",
            "Remove-Item $zip, $unzip -Recurse -Force -ErrorAction SilentlyContinue",
            "Get-ChildItem -Force",
            r"PPTmaster\tools\vi\pptmaster.ps1",
            "không tải chồng",
        ):
            self.assertIn(phrase, body)

    def test_setup_section_runs_exact_auto_command_and_reads_stdout_only(self):
        body = section(read(SELF_INSTALL_DOC), "## Cài đặt")
        self.assertIn(AUTO_SETUP_COMMAND, body)
        self.assertIn("2>&1", body)
        self.assertIn('{"ready"', body)

    def test_setup_section_handles_long_runs_and_existing_installs(self):
        body = section(read(SELF_INSTALL_DOC), "## Cài đặt")
        for phrase in ("ít nhất 15 phút", "chạy nền", "chạy lệnh cài thứ hai", "doctor.py --no-smoke --json"):
            self.assertIn(phrase, body)

    def test_result_section_handles_blocked_powershell_with_manual_commands(self):
        body = section(read(SELF_INSTALL_DOC), "## Đọc kết quả")
        for phrase in ("running scripts is disabled", "PowerShell bị chặn trên máy trường hoặc công ty", "tối đa một lần"):
            self.assertIn(phrase, body)

    def test_result_section_keeps_packages_errors_within_forbidden_list(self):
        body = section(read(SELF_INSTALL_DOC), "## Đọc kết quả")
        for phrase in ("`error.step` là `packages`", "không chạy các lệnh `pip`", "Cài thư viện thất bại", "Không được làm"):
            self.assertIn(phrase, body)

    def test_report_section_uses_it_message_and_resumes_request(self):
        body = section(read(SELF_INSTALL_DOC), "## Báo thầy cô")
        for phrase in ("Máy trường chặn cài đặt", "Tạo bài giảng", "làm tiếp", "đường dẫn dài hoặc OneDrive"):
            self.assertIn(phrase, body)

    def test_optional_tools_section_installs_on_demand_with_path_prefix(self):
        body = section(read(SELF_INSTALL_DOC), "## Công cụ tuỳ chọn")
        self.assertIn(r"-Action tool -Name ffmpeg", body)
        self.assertIn('$env:Path = "<dir>;$env:Path"', body)

    def test_forbidden_section_blocks_risky_actions(self):
        body = section(read(SELF_INSTALL_DOC), "## Không được làm")
        for phrase in ("iex", "Invoke-Expression", "quyền quản trị", "diệt virus", "Set-ExecutionPolicy", "tự nghĩ cách cài khác"):
            self.assertIn(phrase, body)

    def test_agents_vi_prefers_venv_python(self):
        body = section(read("AGENTS.vi.md"), "## 4. Chạy lệnh trên Windows")
        self.assertIn(r"venv\Scripts\python.exe", body)

    def test_agents_vi_environment_section_points_to_guide(self):
        text = read("AGENTS.vi.md")
        self.assertIn(AGENTS_VI_ENV_HEADING, h2_headings(text))
        body = section(text, AGENTS_VI_ENV_HEADING)
        for phrase in ("(docs/vi/cai-dat-bang-ai.md)", "doctor.py --no-smoke --json", "trước lệnh Python đầu tiên của repo", "KIEM-TRA.bat", "Công cụ tuỳ chọn"):
            self.assertIn(phrase, body)
        self.assertEqual(h2_headings(text)[-6], AGENTS_VI_ASSISTANT_HEADING)

    def test_agents_vi_environment_section_checks_before_intake_and_has_safety_net(self):
        body = section(read("AGENTS.vi.md"), AGENTS_VI_ENV_HEADING)
        for phrase in ("project_manager.py init", "trước khi gửi tin nhắn hỏi", "5–10 phút", "Em chưa kiểm tra được máy", "ModuleNotFoundError", "không tự cài"):
            self.assertIn(phrase, body)

    def test_readme_tells_agents_to_follow_guide_before_quick_start(self):
        readme = read("README.md")
        marker = "**Dành cho AI agent:**"
        self.assertIn(marker, readme)
        self.assertIn("(docs/vi/cai-dat-bang-ai.md)", readme)
        self.assertLess(readme.index(marker), readme.index("## Bắt đầu trong 3 bước"))
        self.assertIn("bat-dau-nhanh.md#để-ai-tự-cài", section(readme, "## Bắt đầu trong 3 bước"))


class SelfInstallUserDocsTest(unittest.TestCase):
    def test_quick_start_explains_ai_setup_first(self):
        text = read("docs/vi/bat-dau-nhanh.md")
        self.assertEqual(h2_headings(text)[0], "## Để AI tự cài")
        body = section(text, "## Để AI tự cài")
        for phrase in ("https://github.com/luonghaianh1208/PPTmaster", "cho phép chạy lệnh", "5–10 phút", "cài đặt giúp em", "(xu-ly-loi.md#máy-trường-chặn-cài-đặt)", "bấm từ chối", "thư mục AI báo trong tin nhắn sẵn sàng"):
            self.assertIn(phrase, body)

    def test_windows_install_doc_offers_ai_setup(self):
        text = read("docs/vi/cai-dat-windows.md")
        self.assertIn("**Cách nhanh: nhờ AI cài.**", text)
        self.assertIn("(bat-dau-nhanh.md#để-ai-tự-cài)", text)
        self.assertLess(text.index("**Cách nhanh: nhờ AI cài.**"), text.index("## Cần chuẩn bị"))

    def test_troubleshooting_has_it_message_for_blocked_school_machines(self):
        text = read("docs/vi/xu-ly-loi.md")
        headings = h2_headings(text)
        self.assertEqual(
            headings.index("## Máy trường chặn cài đặt"),
            headings.index("## PowerShell bị chặn trên máy trường hoặc công ty") + 1,
        )
        body = section(text, "## Máy trường chặn cài đặt")
        for phrase in ("python.org", "pypi.org", "files.pythonhosted.org", "github.com", "codeload.github.com", "Python 3.12", "-ExecutionPolicy Bypass",
                       "(khi cần FFmpeg/Pandoc)", "cdn.winget.microsoft.com", "objects.githubusercontent.com"):
            self.assertIn(phrase, body)

    def test_troubleshooting_missing_packages_covers_venv(self):
        body = section(read("docs/vi/xu-ly-loi.md"), "## KIEM-TRA báo thiếu thư viện")
        self.assertIn(r"venv\Scripts\python.exe -m pip install -r requirements.txt", body)

    def test_maintenance_doc_explains_pinned_python_installer(self):
        body = section(read("docs/vi/phat-trien/bao-tri.md"), "## Bộ cài Python cố định")
        for phrase in ("3.12.10", "SHA256", "MD5", "$PythonInstallers", "Get-UserPythonPath", "`Python312`/`Python312-arm64`"):
            self.assertIn(phrase, body)


AGENTS_VI_VIDEO_HEADING = "## 11. Làm video bài giảng"
VIDEO_COMMAND = r"venv\Scripts\python.exe tools\vi\video.py"


class VideoGuideTest(unittest.TestCase):
    def test_common_rules_table_lists_video_task(self):
        body = section(read("docs/vi/tro-ly/quy-trinh-hoi.md"), "## Khi nào áp dụng")
        self.assertIn("video-bai-giang.md", body)
        for keyword in ("làm video", "xuất video", "lồng tiếng"):
            self.assertIn(keyword, body)

    def test_agents_vi_video_section_explains_order_and_command(self):
        text = read("AGENTS.vi.md")
        self.assertIn(AGENTS_VI_VIDEO_HEADING, h2_headings(text))
        body = section(text, AGENTS_VI_VIDEO_HEADING)
        self.assertIn(VIDEO_COMMAND, body)
        for phrase in ("notes_to_audio.py", "chromium", "cửa sổ PowerPoint", "(docs/vi/tro-ly/video-bai-giang.md)", "--rate"):
            self.assertIn(phrase, body)

    def test_agents_vi_video_section_exports_the_narrated_pptx_first(self):
        """C2: thiếu bước này thì đường PowerPoint không bao giờ chạy được."""
        body = section(read("AGENTS.vi.md"), AGENTS_VI_VIDEO_HEADING)
        self.assertIn("--recorded-narration", body)
        self.assertIn("svg_to_pptx.py", body)
        self.assertIn("--quick-generate", body)
        self.assertIn("docs/audio-narration.md", body)
        self.assertLess(body.index("--recorded-narration"), body.index(VIDEO_COMMAND))

    def test_agents_vi_video_section_maps_every_intake_answer(self):
        body = section(read("AGENTS.vi.md"), AGENTS_VI_VIDEO_HEADING)
        for flag in ("--phu-de file", "--phu-de hinh", "--phu-de khong",
                     "--do-phan-giai 1080", "--do-phan-giai 720",
                     "--cach powerpoint", "--cach ffmpeg", "--cach auto"):
            self.assertIn(flag, body)

    def test_agents_vi_video_section_keeps_the_venv_conditional(self):
        body = section(read("AGENTS.vi.md"), AGENTS_VI_VIDEO_HEADING)
        self.assertIn("mục 4", body)
        self.assertIn("không có thì dùng `python`", body)

    def test_agents_vi_video_section_routes_missing_notes_to_the_notes_step(self):
        body = section(read("AGENTS.vi.md"), AGENTS_VI_VIDEO_HEADING)
        self.assertIn("quay lại bước 1 nếu dự án chưa có `notes/*.md`", body)

    def test_video_docs_state_the_ffmpeg_resolution_cap(self):
        for path in ("AGENTS.vi.md", "docs/vi/lam-video.md", "docs/vi/tro-ly/video-bai-giang.md"):
            with self.subTest(path=path):
                self.assertIn("1280×720", read(path))

    def test_troubleshooting_splits_the_render_remedy(self):
        body = section(read("docs/vi/xu-ly-loi.md"), "## Dựng video thất bại")
        self.assertIn("không chụp được ảnh slide", body)
        self.assertIn("hết dung lượng ổ đĩa hoặc đường dẫn quá dài", body)
        self.assertIn("dán nguyên dòng `error.message`", body)
        self.assertIn("dự án chưa có slide nào", body)
        self.assertIn("trên 200 ký tự", body)

    def test_agents_vi_triggers_include_video_phrases(self):
        body = section(read("AGENTS.vi.md"), "## 3. Câu lệnh tiếng Việt kích hoạt skill `ppt-master`")
        for phrase in ("làm video bài giảng", "xuất video"):
            self.assertIn(phrase, body)

    def test_video_guide_quick_section_covers_voice_and_subtitles(self):
        body = section(read("docs/vi/tro-ly/video-bai-giang.md"), "## Tạo nhanh")
        self.assertIn("giọng", body.lower())
        self.assertIn("phụ đề", body.lower())

    def test_task_type_count_matches_the_table(self):
        agents_vi_body = section(read("AGENTS.vi.md"), AGENTS_VI_ASSISTANT_HEADING)
        self.assertIn("10 loại", agents_vi_body)
        for stale in ("5 loại", "6 loại", "7 loại", "8 loại", "9 loại"):
            self.assertNotIn(stale, agents_vi_body)
        quy_trinh_body = section(read("docs/vi/tro-ly/quy-trinh-hoi.md"), "## Khi nào áp dụng")
        self.assertIn("10 loại", quy_trinh_body)
        for stale in ("5 loại", "6 loại", "7 loại", "8 loại", "9 loại"):
            self.assertNotIn(stale, quy_trinh_body)


AGENTS_VI_EXAM_HEADING = "## 12. Soạn đề KHTN bằng tiếng Anh"
EXAM_GUIDE = "docs/vi/tro-ly/de-khtn-tieng-anh.md"
ENGLISH_GUIDE = "docs/vi/tro-ly/tieng-anh-khoa-hoc.md"
EXAM_GUIDE_HEADINGS = (
    "## Khi nào dùng",
    "## Câu hỏi bắt buộc",
    "## Câu hỏi tuỳ chọn",
    "## Tạo nhanh",
    "## Cấu trúc đề",
    "## Đầu ra",
    "## Ghi vào brief",
)
EXAM_COMMAND = r"python tools\vi\de_thi.py"


class ExamGuideTest(unittest.TestCase):
    def test_exam_guide_has_its_own_sections_in_order(self):
        self.assertEqual(h2_headings(read(EXAM_GUIDE)), list(EXAM_GUIDE_HEADINGS))

    def test_exam_guide_is_not_treated_as_a_slide_guide(self):
        self.assertNotIn("de-khtn-tieng-anh.md", GUIDE_FILES)

    def test_exam_guide_questions_are_limited_and_have_suggestions(self):
        items = numbered_items(section(read(EXAM_GUIDE), "## Câu hỏi bắt buộc"))
        self.assertTrue(1 <= len(items) <= 7, f"{len(items)} câu")
        for item in items:
            self.assertIn("Gợi ý:", item)

    def test_exam_guide_quick_mode_asks_two_or_three_questions(self):
        items = numbered_items(section(read(EXAM_GUIDE), "## Tạo nhanh"))
        self.assertTrue(2 <= len(items) <= 3, f"{len(items)} câu")

    def test_exam_guide_must_ask_thcs_counts_instead_of_defaulting(self):
        body = section(read(EXAM_GUIDE), "## Câu hỏi bắt buộc")
        self.assertIn("18", body)
        self.assertIn("THCS", body)
        self.assertIn("phải hỏi", body)

    def test_exam_guide_names_the_output_files(self):
        body = section(read(EXAM_GUIDE), "## Đầu ra")
        for name in ("de-en.docx", "de-song-ngu.docx", "dap-an.docx", "projects/_de-thi/"):
            self.assertIn(name, body)

    def test_exam_guide_points_to_the_english_rules_and_the_source_grammar(self):
        text = read(EXAM_GUIDE)
        self.assertIn("tieng-anh-khoa-hoc.md", text)
        self.assertIn("## CAN SOAT", text)
        for key in ("en:", "vi:", "key:", "level:", "topic:"):
            self.assertIn(key, text)

    def test_exam_guide_forbids_changing_the_original_paper(self):
        text = read(EXAM_GUIDE)
        for phrase in ("không đổi số liệu", "không tự sửa", "Cần thầy cô soát"):
            self.assertIn(phrase, text)

    def test_tro_ly_files_have_no_markdown_links(self):
        for name in ("de-khtn-tieng-anh.md", "tieng-anh-khoa-hoc.md"):
            with self.subTest(file=name):
                self.assertEqual(LINK_RE.findall(read(f"docs/vi/tro-ly/{name}")), [])

    def test_exam_guide_example_prints_vietnamese_with_diacritics(self):
        body = section(read(EXAM_GUIDE), "## Cấu trúc đề")
        school = re.search(r"^school:\s*(.+)$", body, re.M)
        self.assertIsNotNone(school, "file mẫu thiếu dòng school:")
        value = school.group(1).strip()
        self.assertNotEqual(value, value.encode("ascii", "ignore").decode(), value)

    def test_exam_guide_states_the_full_parser_grammar(self):
        body = section(read(EXAM_GUIDE), "## Cấu trúc đề")
        for token in ("## PART I", "## PART II", "## PART III", "## CAN SOAT",
                      "school", "title", "subject", "time", "department", "code", "points",
                      "### ", "biet", "hieu", "vandung", "| T", "| F", "12,5", "-0.25", "unit:"):
            with self.subTest(token=token):
                self.assertIn(token, body)

    def test_exam_guide_example_source_parses(self):
        import sys
        sys.path.insert(0, str(REPO_ROOT / "tools" / "vi"))
        from de_thi_parts import parse

        body = section(read(EXAM_GUIDE), "## Cấu trúc đề")
        blocks = re.findall(r"```[a-z]*\n(---\n.*?)```", body, re.S)
        self.assertTrue(blocks, "thiếu file de.md mẫu trong khối code")
        exam = parse.parse_exam(blocks[0])
        self.assertEqual(exam.counts(), {"part1": 1, "part2": 1, "part3": 1})

    def test_exam_guide_skips_the_pptx_only_steps(self):
        body = section(read(EXAM_GUIDE), "## Ghi vào brief")
        for phrase in ("projects/_de-thi/", "brief.md", "import-sources", "dòng chốt"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_exam_guide_has_no_unsupported_essay_question(self):
        self.assertNotIn("chỗ trống", section(read(EXAM_GUIDE), "## Câu hỏi tuỳ chọn"))

    def test_exam_guide_flow_a_reads_first(self):
        self.assertIn("Luồng A: đọc đề trước rồi mới hỏi thầy cô", section(read(EXAM_GUIDE), "## Khi nào dùng"))

    def test_exam_guide_quick_mode_still_asks_thcs_counts(self):
        body = section(read(EXAM_GUIDE), "## Tạo nhanh")
        self.assertIn("không cần hỏi lại", body)
        self.assertIn("THCS", body)


class ScienceEnglishGuideTest(unittest.TestCase):
    def test_guide_states_every_principle(self):
        text = read(ENGLISH_GUIDE)
        for phrase in (
            "không dịch từng chữ",
            "uniformly accelerated motion",
            "kinetic friction",
            "molar mass",
            "cellular respiration",
            "State",
            "Explain",
            "Calculate",
            "sulfuric acid",
            "aluminium",
            "25.5",
            "at 0 °C and 1 atm",
            "terraced fields",
            "Cần thầy cô soát",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_guide_covers_all_four_subject_frames(self):
        text = read(ENGLISH_GUIDE)
        for subject in ("Vật lí", "Hoá học", "Sinh học", "KHTN"):
            self.assertIn(subject, text)

    def test_guide_forbids_making_the_english_harder_than_the_science(self):
        text = read(ENGLISH_GUIDE)
        self.assertIn("Độ khó nằm ở khoa học", text)

    def test_guide_covers_the_corrections_from_review(self):
        text = read(ENGLISH_GUIDE)
        for phrase in ("30°", "the human body", "at 25 °C and 1 bar", "24,79", "sulfur", "sulphur", "iron(III) oxide"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_guide_has_no_contradictory_spacing_or_spelling_sentence(self):
        text = read(ENGLISH_GUIDE)
        self.assertNotIn("Chỉ nhiệt độ mới có khoảng trắng", text)
        self.assertNotIn("Anh-Mỹ cũ", text)
        self.assertIn("5 kg", text)

    def test_guide_forbids_tilde_for_approximately(self):
        text = read(ENGLISH_GUIDE)
        self.assertIn("≈", text)
        self.assertIn("chỉ thêm dấu ~ ~", text)


class ExamWiringTest(unittest.TestCase):
    def test_common_rules_table_lists_the_exam_task(self):
        body = section(read("docs/vi/tro-ly/quy-trinh-hoi.md"), "## Khi nào áp dụng")
        self.assertIn("de-khtn-tieng-anh.md", body)
        for keyword in ("đề tiếng Anh", "đề KHTN"):
            self.assertIn(keyword, body)

    def test_agents_vi_exam_section_explains_both_use_cases_and_the_command(self):
        text = read("AGENTS.vi.md")
        self.assertIn(AGENTS_VI_EXAM_HEADING, h2_headings(text))
        body = section(text, AGENTS_VI_EXAM_HEADING)
        self.assertIn(EXAM_COMMAND, body)
        for phrase in (
            "source_to_md.py",
            "(docs/vi/tro-ly/de-khtn-tieng-anh.md)",
            "(docs/vi/tro-ly/tieng-anh-khoa-hoc.md)",
            "projects/_de-thi/",
            "de.md",
            "ảnh",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_agents_vi_exam_section_maps_every_error_step(self):
        body = section(read("AGENTS.vi.md"), AGENTS_VI_EXAM_HEADING)
        for step in ("input", "parse", "docx", "write"):
            self.assertIn(f"`{step}`", body)
        self.assertIn("requirements-vi.txt", body)

    def test_agents_vi_exam_section_keeps_the_venv_conditional(self):
        body = section(read("AGENTS.vi.md"), AGENTS_VI_EXAM_HEADING)
        self.assertIn("mục 4", body)

    def test_agents_vi_triggers_include_exam_phrases(self):
        body = section(read("AGENTS.vi.md"), "## 3. Câu lệnh tiếng Việt kích hoạt skill `ppt-master`")
        for phrase in ("soạn đề", "đề tiếng Anh"):
            self.assertIn(phrase, body)

    def test_brief_template_lists_the_exam_task(self):
        self.assertIn("Soạn đề KHTN tiếng Anh", read("docs/vi/tro-ly/mau-brief.md"))

    def test_agents_vi_exam_section_states_bans_matrix_and_review_items(self):
        body = section(read("AGENTS.vi.md"), AGENTS_VI_EXAM_HEADING)
        for phrase in ("SVG", "skills/", "ma trận", "vi:", "Cần thầy cô soát"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_agents_vi_exam_flow_a_reads_the_paper_before_asking(self):
        body = section(read("AGENTS.vi.md"), AGENTS_VI_EXAM_HEADING)
        self.assertIn("source_to_md.py", body)
        self.assertIn("hỏi một lượt", body)
        self.assertLess(body.index("source_to_md.py"), body.index("hỏi một lượt"))

    def test_common_rules_say_pptx_steps_do_not_apply_to_exams(self):
        body = section(read("docs/vi/tro-ly/quy-trinh-hoi.md"), "## Khi nào áp dụng")
        self.assertIn("de-khtn-tieng-anh.md", body)
        self.assertIn("import-sources", body)

    def test_common_rules_exam_exception_has_no_double_negative(self):
        body = section(read("docs/vi/tro-ly/quy-trinh-hoi.md"), "## Khi nào áp dụng")
        self.assertNotIn("không viết brief để import vào dự án PPTX", body)
        self.assertIn("đặt tên brief theo dự án PPTX rồi import vào dự án", body)


class ExamUserDocsTest(unittest.TestCase):
    def test_exam_doc_explains_inputs_outputs_and_limits(self):
        text = read("docs/vi/soan-de-tieng-anh.md")
        for phrase in ("Word", "PDF", "ảnh", "de-en.docx", "dap-an.docx", "song ngữ", "ma trận", "Cần thầy cô soát"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_quick_start_mentions_the_exam_task(self):
        text = read("docs/vi/bat-dau-nhanh.md")
        self.assertNotIn("6 loại", text)
        headings = h2_headings(text)
        self.assertIn("## Soạn đề tiếng Anh", headings)
        self.assertLess(headings.index("## Soạn đề tiếng Anh"), headings.index("## Lấy file kết quả"))
        self.assertIn("(soan-de-tieng-anh.md)", section(text, "## Soạn đề tiếng Anh"))

    def test_sample_commands_cover_both_use_cases(self):
        body = section(read("docs/vi/cau-lenh-mau.md"), "## Soạn đề tiếng Anh")
        self.assertIn("sang tiếng Anh", body)
        self.assertIn("Soạn đề", body)

    def test_troubleshooting_has_the_exam_export_section(self):
        text = read("docs/vi/xu-ly-loi.md")
        headings = h2_headings(text)
        self.assertIn("## Xuất đề Word thất bại", headings)
        # Đứng NGAY TRƯỚC mục video: test gói video khoá mục video phải ngay trước "Đường dẫn quá dài".
        self.assertEqual(
            headings.index("## Xuất đề Word thất bại"),
            headings.index("## Dựng video thất bại") - 1,
        )
        body = section(text, "## Xuất đề Word thất bại")
        for phrase in ("requirements-vi.txt", "python-docx", "đang mở trong Word", "Dòng", "de.md"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_readme_mentions_the_exam_feature(self):
        self.assertIn("đề kiểm tra", section(read("README.md"), "## Làm được gì"))

    def test_exam_docs_do_not_promise_three_files_unconditionally(self):
        for path in ("docs/vi/soan-de-tieng-anh.md", "README.md"):
            with self.subTest(path=path):
                lines = [line for line in read(path).splitlines() if "ba file Word" in line]
                self.assertTrue(lines, f"{path} không còn nhắc ba file Word")
                for line in lines:
                    self.assertIn("hai file", line, line)


AGENTS_VI_LESSON_HEADING = "## 13. Soạn giáo án tích hợp năng lực số và năng lực AI"
LESSON_GUIDE = "docs/vi/tro-ly/giao-an.md"
FRAMEWORK_GUIDE = "docs/vi/tro-ly/nang-luc-so-va-ai.md"
LESSON_GUIDE_HEADINGS = (
    "## Khi nào dùng",
    "## Câu hỏi bắt buộc",
    "## Câu hỏi tuỳ chọn",
    "## Tạo nhanh",
    "## Cấu trúc giáo án",
    "## Đầu ra",
    "## Ghi vào brief",
)
LESSON_COMMAND = r"python tools\vi\giao_an.py xuat"
ROUTING_QUESTION = "file Word kế hoạch bài dạy"


class LessonGuideTest(unittest.TestCase):
    def test_guide_has_its_own_sections_in_order(self):
        self.assertEqual(h2_headings(read(LESSON_GUIDE)), list(LESSON_GUIDE_HEADINGS))

    def test_guide_is_not_treated_as_a_slide_guide(self):
        self.assertNotIn("giao-an.md", GUIDE_FILES)

    def test_guide_names_the_unambiguous_routing_phrases(self):
        body = section(read(LESSON_GUIDE), "## Khi nào dùng")
        self.assertIn("là rõ ràng", body)

    def test_guide_questions_are_limited_and_have_suggestions(self):
        items = numbered_items(section(read(LESSON_GUIDE), "## Câu hỏi bắt buộc"))
        self.assertTrue(1 <= len(items) <= 7, f"{len(items)} câu")
        for item in items:
            self.assertIn("Gợi ý:", item)

    def test_guide_quick_mode_asks_two_or_three_questions(self):
        items = numbered_items(section(read(LESSON_GUIDE), "## Tạo nhanh"))
        self.assertTrue(2 <= len(items) <= 3, f"{len(items)} câu")

    def test_guide_states_the_source_grammar(self):
        body = section(read(LESSON_GUIDE), "## Cấu trúc giáo án")
        for token in ("## MUC TIEU", "## THIET BI", "## TIEN TRINH", "## RUBRIC", "## CAN SOAT",
                      "thoi-luong:", "muc-tieu:", "chuyen-giao:", "ket-luan:", "nls:", "ai:"):
            with self.subTest(token=token):
                self.assertIn(token, body)

    def test_guide_example_source_parses_and_validates(self):
        """Bài học từ gói đề thi: ngữ pháp trong hướng dẫn phải khớp parser thật, chứng minh bằng file mẫu."""
        import sys
        sys.path.insert(0, str(REPO_ROOT / "tools" / "vi"))
        from giao_an_parts import frameworks, parse

        body = section(read(LESSON_GUIDE), "## Cấu trúc giáo án")
        blocks = re.findall(r"```[a-z]*\n(---\n.*?)```", body, re.S)
        self.assertTrue(blocks, "thiếu file giao-an.md mẫu trong khối code")
        lesson = parse.parse_lesson(blocks[0])
        frameworks.validate(lesson, frameworks.load_file())
        self.assertTrue(lesson.activities)

    def test_guide_skips_the_pptx_only_steps(self):
        body = section(read(LESSON_GUIDE), "## Ghi vào brief")
        for phrase in ("projects/_giao-an/", "brief.md", "import-sources", "dòng chốt"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_guide_names_the_output_files(self):
        body = section(read(LESSON_GUIDE), "## Đầu ra")
        for name in ("giao-an.docx", "can-soat.md", "projects/_giao-an/"):
            self.assertIn(name, body)

    def test_guide_points_to_the_framework_document(self):
        self.assertIn("nang-luc-so-va-ai.md", read(LESSON_GUIDE))

    def test_guide_forbids_rewriting_the_teacher_content_and_inventing_codes(self):
        text = read(LESSON_GUIDE)
        for phrase in ("giữ nguyên", "không tự đặt mã", "can-soat.md"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_tro_ly_files_have_no_markdown_links(self):
        for name in ("giao-an.md", "nang-luc-so-va-ai.md"):
            with self.subTest(file=name):
                self.assertEqual(LINK_RE.findall(read(f"docs/vi/tro-ly/{name}")), [])

    def test_framework_document_credits_its_author_and_sources(self):
        text = read(FRAMEWORK_GUIDE)
        for phrase in ("Lương Hải Anh", "2Anh AI Education", "Bộ GD&ĐT", "Phụ lục III & IV"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


class LessonWiringTest(unittest.TestCase):
    def test_common_rules_table_lists_the_lesson_plan_task(self):
        body = section(read("docs/vi/tro-ly/quy-trinh-hoi.md"), "## Khi nào áp dụng")
        self.assertIn("giao-an.md", body)
        for keyword in ("kế hoạch bài dạy", "KHBD"):
            self.assertIn(keyword, body)

    def test_common_rules_name_the_ambiguous_lesson_keyword(self):
        body = section(read("docs/vi/tro-ly/quy-trinh-hoi.md"), "## Khi nào áp dụng")
        self.assertIn('"giáo án"', body)
        self.assertIn(ROUTING_QUESTION, body)
        self.assertIn("là rõ ràng", body)

    def test_agents_vi_lesson_section_explains_both_flows_and_the_command(self):
        text = read("AGENTS.vi.md")
        self.assertIn(AGENTS_VI_LESSON_HEADING, h2_headings(text))
        body = section(text, AGENTS_VI_LESSON_HEADING)
        self.assertIn(LESSON_COMMAND, body)
        for phrase in (
            "source_to_md.py",
            "trich-sgk",
            "(docs/vi/tro-ly/giao-an.md)",
            "(docs/vi/tro-ly/nang-luc-so-va-ai.md)",
            "projects/_giao-an/",
            "giao-an.md",
            "ảnh",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_agents_vi_lesson_section_maps_every_error_step(self):
        body = section(read("AGENTS.vi.md"), AGENTS_VI_LESSON_HEADING)
        for step in ("input", "parse", "framework", "docx", "write"):
            self.assertIn(f"`{step}`", body)
        self.assertIn("requirements-vi.txt", body)

    def test_agents_vi_lesson_section_asks_before_routing(self):
        body = section(read("AGENTS.vi.md"), AGENTS_VI_LESSON_HEADING)
        self.assertIn(ROUTING_QUESTION, body)
        self.assertIn("là rõ ràng", body)

    def test_agents_vi_lesson_section_keeps_the_venv_conditional(self):
        body = section(read("AGENTS.vi.md"), AGENTS_VI_LESSON_HEADING)
        self.assertIn("mục 4", body)

    def test_agents_vi_lesson_section_reads_the_curriculum_without_editing_it(self):
        body = section(read("AGENTS.vi.md"), AGENTS_VI_LESSON_HEADING)
        self.assertIn("không sửa", body)
        self.assertIn("phân phối chương trình", body)

    def test_common_rules_say_pptx_steps_do_not_apply_to_lesson_plans(self):
        body = section(read("docs/vi/tro-ly/quy-trinh-hoi.md"), "## Khi nào áp dụng")
        self.assertIn("giao-an.md", body)
        self.assertIn("import-sources", body)

    def test_agents_vi_lesson_section_bans_svg_and_skills(self):
        body = section(read("AGENTS.vi.md"), AGENTS_VI_LESSON_HEADING)
        for phrase in ("SVG", "skills/", "project_manager.py init"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_agents_vi_lesson_flow_a_reads_the_plan_before_asking(self):
        body = section(read("AGENTS.vi.md"), AGENTS_VI_LESSON_HEADING)
        self.assertIn("source_to_md.py", body)
        self.assertIn("hỏi một lượt", body)
        self.assertLess(body.index("source_to_md.py"), body.index("hỏi một lượt"))

    def test_agents_vi_triggers_include_lesson_plan_phrases(self):
        body = section(read("AGENTS.vi.md"), "## 3. Câu lệnh tiếng Việt kích hoạt skill `ppt-master`")
        for phrase in ("kế hoạch bài dạy", "giáo án"):
            self.assertIn(phrase, body)

    def test_brief_template_lists_the_lesson_plan_task(self):
        self.assertIn("Soạn giáo án", read("docs/vi/tro-ly/mau-brief.md"))


class LessonUserDocsTest(unittest.TestCase):
    def test_doc_explains_inputs_outputs_and_limits(self):
        text = read("docs/vi/soan-giao-an.md")
        for phrase in ("Word", "PDF", "ảnh", "giao-an.docx", "can-soat.md", "rubric",
                       "năng lực số", "năng lực AI", "phân phối chương trình"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_doc_explains_the_routing_question(self):
        self.assertIn("slide", read("docs/vi/soan-giao-an.md"))

    def test_quick_start_mentions_the_lesson_plan_task(self):
        text = read("docs/vi/bat-dau-nhanh.md")
        self.assertNotIn("7 loại", text)
        headings = h2_headings(text)
        self.assertIn("## Soạn giáo án", headings)
        self.assertLess(headings.index("## Soạn giáo án"), headings.index("## Lấy file kết quả"))
        self.assertIn("(soan-giao-an.md)", section(text, "## Soạn giáo án"))

    def test_sample_commands_cover_both_flows(self):
        body = section(read("docs/vi/cau-lenh-mau.md"), "## Soạn giáo án")
        self.assertIn("năng lực số", body)
        self.assertIn("kế hoạch bài dạy", body)

    def test_troubleshooting_has_the_lesson_plan_section(self):
        text = read("docs/vi/xu-ly-loi.md")
        headings = h2_headings(text)
        self.assertIn("## Xuất giáo án thất bại", headings)
        # Đứng NGAY TRƯỚC mục đề thi: gói đề thi khoá mục đề thi ngay trước mục video,
        # và gói video khoá mục video ngay trước "Đường dẫn quá dài".
        self.assertEqual(
            headings.index("## Xuất giáo án thất bại"),
            headings.index("## Xuất đề Word thất bại") - 1,
        )
        body = section(text, "## Xuất giáo án thất bại")
        for phrase in ("requirements-vi.txt", "python-docx", "đang mở trong Word", "Dòng",
                       "giao-an.md", "mã năng lực"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_readme_mentions_the_lesson_plan_feature(self):
        self.assertIn("giáo án", section(read("README.md"), "## Làm được gì"))


EFFECTS_GUIDE = "docs/vi/tro-ly/hieu-ung-lop-hoc.md"
EFFECT_QUESTION_GUIDES = (
    "bai-giang.md",
    "bao-cao-tong-ket.md",
    "hoat-dong-doan.md",
    "tap-huan-workshop.md",
)
CHECK_COMMAND = "kiem_hieu_ung.py"


class EffectsGuideTest(unittest.TestCase):
    def test_guide_has_levels_patterns_video_and_check_sections(self):
        self.assertEqual(
            h2_headings(read(EFFECTS_GUIDE)),
            ["## Khi nào áp dụng", "## Ba mức", "## Bốn kiểu hiệu ứng", "## Video", "## Kiểm sau khi xuất"],
        )

    def test_guide_thresholds_match_the_checker(self):
        import kiem_hieu_ung

        body = section(read(EFFECTS_GUIDE), "## Ba mức") + section(read(EFFECTS_GUIDE), "## Bốn kiểu hiệu ứng")
        for level, share in kiem_hieu_ung.MIN_SHARE.items():
            self.assertIn(f"{round(share * 100)}%", body, level)
        self.assertIn(f"không quá {kiem_hieu_ung.MAX_CLICKS['vua']} bước bấm ở mức vừa", body)
        self.assertIn(f"{kiem_hieu_ung.MAX_CLICKS['nhieu']} bước ở mức nhiều", body)

    def test_guide_maps_patterns_to_upstream_mechanisms(self):
        body = section(read(EFFECTS_GUIDE), "## Bốn kiểu hiệu ứng")
        for phrase in ("on-click", "trigger_shape", "không chồng lên nhau", "morph", "pairs", "customize-animations.md"):
            self.assertIn(phrase, body)

    def test_video_section_forbids_clicks(self):
        body = section(read(EFFECTS_GUIDE), "## Video")
        for phrase in ("on-click", "trigger_shape", "after-previous", "with-previous", "animations_video.json",
                       "--animation-config animations_video.json", "Không sửa `animations.json`",
                       "Thầy cô chọn bỏ hiệu ứng: xuất bản thuyết minh với `--no-animations`"):
            self.assertIn(phrase, body)

    def test_check_section_covers_every_error_step(self):
        body = section(read(EFFECTS_GUIDE), "## Kiểm sau khi xuất")
        for phrase in (CHECK_COMMAND, "--video", "_narrated.pptx", "đúng một lần"):
            self.assertIn(phrase, body)
        for step in ("muc", "video", "input", "parse", "internal"):
            self.assertIn(f"`error.step` là `{step}`", body)

    def test_four_guides_ask_the_effect_level_and_record_it(self):
        for name in EFFECT_QUESTION_GUIDES:
            with self.subTest(guide=name):
                text = read(f"docs/vi/tro-ly/{name}")
                items = numbered_items(section(text, "## Câu hỏi bắt buộc"))
                self.assertEqual(sum("không, vừa, hay nhiều" in item for item in items), 1)
                self.assertIn("Mức hiệu ứng:", section(text, "## Ghi vào brief"))

    def test_four_guides_ask_the_text_density_and_record_it(self):
        for name in EFFECT_QUESTION_GUIDES:
            with self.subTest(guide=name):
                text = read(f"docs/vi/tro-ly/{name}")
                items = numbered_items(section(text, "## Câu hỏi bắt buộc"))
                self.assertEqual(sum("ít chữ, vừa, hay nhiều chữ" in item for item in items), 1)
                self.assertIn("Mật độ chữ:", section(text, "## Ghi vào brief"))

    def test_common_rules_define_text_density_levels(self):
        body = section(read("docs/vi/tro-ly/quy-trinh-hoi.md"), "## Mật độ chữ")
        for phrase in ("`presentation`", "`balanced`", "`text`", "ít chữ", "nhiều chữ", "lời giảng",
                       "chia thêm trang", "không bỏ thông tin", "Beautify", "tạo mới từ file", "(AI đề xuất, chưa duyệt)"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)
        self.assertIn("Mật độ chữ", read("docs/vi/tro-ly/mau-brief.md"))

    def test_antigravity_rule_carries_the_text_density_rule_inline(self):
        body = section(read(".agents/rules/ppt-master-vi.md"), "## Mật độ chữ")
        for phrase in ("`presentation`", "ít chữ", "lời giảng", "tạo mới từ file", "làm đẹp"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_video_guide_asks_keep_or_drop_effects(self):
        text = read("docs/vi/tro-ly/video-bai-giang.md")
        items = numbered_items(section(text, "## Câu hỏi bắt buộc"))
        self.assertEqual(sum("giữ hiệu ứng" in item for item in items), 1)
        self.assertNotIn("không, vừa, hay nhiều", text)
        self.assertIn("Hiệu ứng video:", section(text, "## Ghi vào brief"))

    def test_poster_guide_has_no_effect_question(self):
        self.assertNotIn("Mức hiệu ứng", read("docs/vi/tro-ly/poster-mang-xa-hoi.md"))

    def test_quick_mode_defaults_to_medium_level(self):
        body = section(read("docs/vi/tro-ly/quy-trinh-hoi.md"), "## Tạo nhanh")
        self.assertIn("Mức hiệu ứng: vừa (AI đề xuất, chưa duyệt)", body)

    def test_agents_vi_wires_the_check_for_slides_and_video(self):
        text = read("AGENTS.vi.md")
        assistant = section(text, AGENTS_VI_ASSISTANT_HEADING)
        self.assertIn(CHECK_COMMAND, assistant)
        self.assertIn(f"({EFFECTS_GUIDE})", assistant)
        video = section(text, AGENTS_VI_VIDEO_HEADING)
        self.assertIn("--video", video)
        self.assertIn("--animation-config animations_video.json", video)
        self.assertIn("thầy cô bỏ hiệu ứng thì thêm `--no-animations`", video)
        self.assertLess(video.index(CHECK_COMMAND), video.index(VIDEO_COMMAND))
        self.assertLess(video.index("--animation-config animations_video.json"), video.index(CHECK_COMMAND))

    def test_antigravity_rule_carries_the_effect_rules(self):
        rule = read(".agents/rules/ppt-master-vi.md")
        for phrase in ("## Hiệu ứng", EFFECTS_GUIDE, CHECK_COMMAND, "--video", "customize-animations", "on-click",
                       "animations_video.json", "Không áp dụng cho làm đẹp"):
            self.assertIn(phrase, rule)

    def test_troubleshooting_explains_the_check(self):
        body = section(read("docs/vi/xu-ly-loi.md"), "## Kiểm hiệu ứng không đạt")
        for step in ("`muc`", "`video`", "`parse`", "`input`", "`internal`"):
            self.assertIn(step, body)


AGENTS_VI_EXPERIMENT_HEADING = "## 14. Làm thí nghiệm ảo"
EXPERIMENT_GUIDE = "docs/vi/tro-ly/thi-nghiem-ao.md"
MODEL_GUIDE = "docs/vi/tro-ly/mo-hinh-thi-nghiem.md"
EXPERIMENT_COMMAND = r"python tools\vi\thi_nghiem.py"
EXPERIMENT_GUIDE_HEADINGS = (
    "## Khi nào dùng",
    "## Câu hỏi bắt buộc",
    "## Câu hỏi tuỳ chọn",
    "## Tạo nhanh",
    "## Cấu trúc thi-nghiem.md",
    "## Đầu ra",
    "## Nối vào bài giảng",
    "## Ghi vào brief",
)


class ExperimentGuideTest(unittest.TestCase):
    def test_guide_has_its_own_sections_in_order(self):
        self.assertEqual(h2_headings(read(EXPERIMENT_GUIDE)), list(EXPERIMENT_GUIDE_HEADINGS))

    def test_guide_questions_are_limited_and_have_suggestions(self):
        items = numbered_items(section(read(EXPERIMENT_GUIDE), "## Câu hỏi bắt buộc"))
        self.assertTrue(1 <= len(items) <= 7, f"{len(items)} câu")
        for item in items:
            self.assertIn("Gợi ý:", item)
        quick = numbered_items(section(read(EXPERIMENT_GUIDE), "## Tạo nhanh"))
        self.assertTrue(2 <= len(quick) <= 3, f"{len(quick)} câu")

    def test_guide_examples_parse_against_the_real_models(self):
        """Bài học từ gói đề thi: ngữ pháp trong hướng dẫn phải khớp parser thật, chứng minh bằng file mẫu."""
        from thi_nghiem_parts import parse, thu_vien

        body = section(read(EXPERIMENT_GUIDE), "## Cấu trúc thi-nghiem.md")
        blocks = re.findall(r"```[a-z]*\n(---\n.*?)```", body, re.S)
        self.assertEqual(len(blocks), 3, "cần một ví dụ cho mỗi môn")
        subjects = set()
        for block in blocks:
            meta = parse.read_meta(block)
            model = thu_vien.load(meta["mau"], REPO_ROOT)
            experiment = parse.parse_experiment(block, model.khai_bao)
            self.assertEqual(experiment.warnings, [], meta["mau"])
            subjects.add(model.khai_bao["mon"])
        self.assertEqual(subjects, {"Toán", "Vật lí", "Hoá học"})

    def test_guide_states_the_grammar_and_the_limits(self):
        body = section(read(EXPERIMENT_GUIDE), "## Cấu trúc thi-nghiem.md")
        for phrase in ("tieu-de", "nguoi-thao-tac", "sai-so", "co-dinh", "mac-dinh", "buoc", "chon", "so-lan-do",
                       "do-thi", "theo", "ln(", "sqrt(", "goi-y-dap-an", "công thức của mẫu không còn đúng",
                       "Không chèn địa chỉ web"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_guide_names_outputs_and_forbids_hand_written_pages(self):
        body = section(read(EXPERIMENT_GUIDE), "## Đầu ra")
        for phrase in (EXPERIMENT_COMMAND, "thi-nghiem.html", "phieu-hoc-tap.docx", "can-soat.md", "mo-hinh.json",
                       "mo-hinh.js", "Không viết file HTML bằng tay", "projects\\_thi-nghiem\\"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_guide_skips_the_pptx_only_steps(self):
        body = section(read(EXPERIMENT_GUIDE), "## Ghi vào brief")
        for phrase in ("projects/_thi-nghiem/", "brief.md", "import-sources", "dòng chốt"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_guides_have_no_markdown_links(self):
        for name in (EXPERIMENT_GUIDE, MODEL_GUIDE):
            self.assertEqual(LINK_RE.findall(read(name)), [], name)

    def test_model_guide_lists_every_code_of_every_library_model(self):
        from thi_nghiem_parts import thu_vien

        text = read(MODEL_GUIDE)
        self.assertEqual(len(thu_vien.list_models()), 8)
        for ma in thu_vien.list_models():
            model = thu_vien.load(ma, REPO_ROOT)
            self.assertIn(f"### `{ma}`", text)
            for item in model.khai_bao["thamSo"] + model.khai_bao["daiLuongDo"]:
                self.assertIn(f"`{item['ma']}`", text, f"{ma}: {item['ma']}")
            self.assertIn(model.khai_bao["congThuc"]["dieuKien"], text, ma)

    def test_model_guide_example_follows_the_contract(self):
        from thi_nghiem_parts import thu_vien

        text = section(read(MODEL_GUIDE), "## Khuôn mô hình mới")
        declaration = json.loads(re.search(r"```json\n(.*?)```", text, re.S).group(1))
        code = re.search(r"```js\n(.*?)```", text, re.S).group(1)
        self.assertEqual(thu_vien.check_declaration(declaration), [])
        self.assertEqual(thu_vien.check_js(code, declaration["hoatHinh"]), [])

    def test_model_guide_keeps_the_teacher_review_rule(self):
        body = section(read(MODEL_GUIDE), "## Khi mô hình do AI viết")
        for phrase in ("can-soat.md", "máy tính cầm tay", "không lược bỏ", "`check`", "`model`",
                       "không bắt được lỗi hiểu sai kiến thức"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)


class ExperimentWiringTest(unittest.TestCase):
    def test_common_rules_table_lists_the_experiment_task(self):
        body = section(read("docs/vi/tro-ly/quy-trinh-hoi.md"), "## Khi nào áp dụng")
        self.assertIn("thi-nghiem-ao.md", body)
        for keyword in ("thí nghiệm ảo", "mô phỏng thí nghiệm"):
            self.assertIn(keyword, body)
        self.assertIn('Loại việc "Thí nghiệm ảo" không tạo PPTX', body)

    def test_image_rule_does_not_apply_to_experiments(self):
        self.assertIn("Thí nghiệm ảo", section(read("docs/vi/tro-ly/quy-trinh-hoi.md"), "## Ảnh minh hoạ"))

    def test_agents_vi_section_explains_the_order_and_the_command(self):
        text = read("AGENTS.vi.md")
        self.assertIn(AGENTS_VI_EXPERIMENT_HEADING, h2_headings(text))
        body = section(text, AGENTS_VI_EXPERIMENT_HEADING)
        self.assertIn(EXPERIMENT_COMMAND, body)
        for phrase in ("(docs/vi/tro-ly/thi-nghiem-ao.md)", "(docs/vi/tro-ly/mo-hinh-thi-nghiem.md)", "projects/_thi-nghiem/",
                       "thi-nghiem.md", "--plan-only", "can-soat.md", "kiem_so", r"venv\Scripts\python.exe"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_agents_vi_section_maps_every_error_step(self):
        body = section(read("AGENTS.vi.md"), AGENTS_VI_EXPERIMENT_HEADING)
        for step in ("input", "parse", "model", "check", "docx", "write", "internal"):
            self.assertIn(f"`{step}`", body)
        self.assertIn("requirements-vi.txt", body)

    def test_agents_vi_section_bans_shortcuts(self):
        body = section(read("AGENTS.vi.md"), AGENTS_VI_EXPERIMENT_HEADING)
        for phrase in ("không viết file HTML bằng tay", "không bỏ bảng số kiểm", "không chèn thư viện", "project_manager.py init",
                       "không chạm `skills/`", "không commit gì trong `projects/`"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_agents_vi_triggers_and_table_include_the_experiment_task(self):
        text = read("AGENTS.vi.md")
        self.assertIn('"thí nghiệm ảo"', section(text, "## 3. Câu lệnh tiếng Việt kích hoạt skill `ppt-master`"))
        assistant = section(text, AGENTS_VI_ASSISTANT_HEADING)
        self.assertIn("(docs/vi/tro-ly/thi-nghiem-ao.md)", assistant)
        self.assertIn("mục 14", assistant)

    def test_antigravity_rule_carries_the_experiment_rules(self):
        rule = read(".agents/rules/ppt-master-vi.md")
        for phrase in ("## Thí nghiệm ảo", "docs/vi/tro-ly/thi-nghiem-ao.md", r"tools\vi\thi_nghiem.py", "10 loại việc",
                       "Không viết file HTML bằng tay", "can-soat.md"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, rule)
        self.assertLessEqual(len(rule), ANTIGRAVITY_RULE_LIMIT)

    def test_brief_template_lists_the_experiment_task(self):
        self.assertIn("Thí nghiệm ảo", read("docs/vi/tro-ly/mau-brief.md"))


class ExperimentUserDocsTest(unittest.TestCase):
    def test_doc_explains_use_limits_and_review(self):
        text = read("docs/vi/thi-nghiem-ao.md")
        for phrase in ("thi-nghiem.html", "phieu-hoc-tap.docx", "can-soat.md", "không cần mạng", "USB", "Netlify",
                       "điện thoại", "Chế độ giáo viên", "Ghi lần đo", "Chép số liệu", "sai số đo", "Tự kiểm",
                       "mô hình lí tưởng", "soát công thức", "Node"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_doc_lists_the_eight_models(self):
        text = read("docs/vi/thi-nghiem-ao.md")
        for name in ("Ném xiên", "Con lắc đơn", "nối tiếp và song song", "Chuẩn độ", "N₂O₄ ⇌ 2NO₂", "Tốc độ phản ứng",
                     "Khảo sát hàm số", "Xác suất thực nghiệm"):
            self.assertIn(name, text)

    def test_quick_start_mentions_the_experiment_task(self):
        text = read("docs/vi/bat-dau-nhanh.md")
        self.assertNotIn("8 loại", text)
        headings = h2_headings(text)
        self.assertIn("## Làm thí nghiệm ảo", headings)
        self.assertLess(headings.index("## Làm thí nghiệm ảo"), headings.index("## Lấy file kết quả"))
        self.assertIn("(thi-nghiem-ao.md)", section(text, "## Làm thí nghiệm ảo"))

    def test_sample_commands_have_an_experiment_section(self):
        body = section(read("docs/vi/cau-lenh-mau.md"), "## Thí nghiệm ảo")
        self.assertIn("thí nghiệm ảo", body)
        self.assertIn("phiếu học tập", body)

    def test_troubleshooting_has_the_experiment_section(self):
        text = read("docs/vi/xu-ly-loi.md")
        headings = h2_headings(text)
        self.assertEqual(headings.index("## Tạo thí nghiệm ảo thất bại"), headings.index("## Kiểm hiệu ứng không đạt") - 1)
        body = section(text, "## Tạo thí nghiệm ảo thất bại")
        for phrase in ("`input`", "`parse`", "`model`", "`check`", "`docx`", "`write`", "`internal`", "Dòng",
                       "requirements-vi.txt", "dải đỏ", "Node"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_readme_mentions_the_experiment_feature(self):
        readme = read("README.md")
        self.assertIn("thí nghiệm ảo", section(readme, "## Làm được gì"))
        self.assertIn("(docs/vi/thi-nghiem-ao.md)", section(readme, "## Tài liệu"))


AGENTS_VI_EXPLAINER_HEADING = "## 15. Làm video giải thích"
EXPLAINER_GUIDE = "docs/vi/tro-ly/video-giai-thich.md"
SCENE_GUIDE = "docs/vi/tro-ly/canh-video.md"
EXPLAINER_COMMAND = r"python tools\vi\video_ma.py"
EXPLAINER_GUIDE_HEADINGS = (
    "## Khi nào dùng",
    "## Câu hỏi bắt buộc",
    "## Câu hỏi tuỳ chọn",
    "## Tạo nhanh",
    "## Cấu trúc video.md",
    "## Hình do AI vẽ",
    "## Đầu ra",
    "## Ghi vào brief",
)


def _png_gia(rong: int, cao: int) -> bytes:
    def khoi(loai: bytes, du_lieu: bytes) -> bytes:
        return struct.pack(">I", len(du_lieu)) + loai + du_lieu + struct.pack(">I", zlib.crc32(loai + du_lieu))

    hang = b"\x00" + b"\xff\xff\xff" * rong
    return (b"\x89PNG\r\n\x1a\n" + khoi(b"IHDR", struct.pack(">IIBBBBB", rong, cao, 8, 2, 0, 0, 0))
            + khoi(b"IDAT", zlib.compress(hang * cao)) + khoi(b"IEND", b""))


def _jpeg_gia(rong: int, cao: int) -> bytes:
    return b"\xff\xd8\xff\xc0" + struct.pack(">HBHHB", 11, 8, cao, rong, 1) + b"\x01\x11\x00\xff\xd9"


def _anh_gia(thu_muc: Path, video) -> None:
    """Tạo ảnh nhỏ cho mọi `anh:` của kịch bản, kèm bản ghi nguồn cho ảnh không ghi `nguon:`."""
    ten_cac_anh = [scene.truong["anh"][0] for scene in video.canh if "anh" in scene.truong]
    if not ten_cac_anh:
        return
    (thu_muc / "anh").mkdir()
    for ten in ten_cac_anh:
        du_lieu = _png_gia(8, 6) if ten.lower().endswith(".png") else _jpeg_gia(8, 6)
        (thu_muc / "anh" / ten).write_bytes(du_lieu)
    items = [{"filename": scene.truong["anh"][0], "author": "Tác giả thử", "license_name": "CC0", "provider": "wikimedia"}
             for scene in video.canh if "anh" in scene.truong and "nguon" not in scene.truong]
    (thu_muc / "anh" / "image_sources.json").write_text(json.dumps({"items": items}), encoding="utf-8")


def _nhac_gia(thu_muc: Path, video) -> None:
    """Tạo file nhạc WAV rất ngắn cho `nhac-nen:` của kịch bản, kèm `nhac/nguon.json` khi kịch bản không ghi `nguon-nhac:`."""
    import wave

    ten = video.meta.get("nhac-nen")
    if not ten:
        return
    (thu_muc / "nhac").mkdir()
    with wave.open(str(thu_muc / "nhac" / ten), "wb") as tep:
        tep.setnchannels(1)
        tep.setsampwidth(1)
        tep.setframerate(8000)
        tep.writeframes(bytes([128]) * 4000)
    if "nguon-nhac" not in video.meta:
        items = [{"filename": ten, "title": "Nhạc thử", "creator": "Tác giả thử", "license": "CC0 1.0"}]
        (thu_muc / "nhac" / "nguon.json").write_text(json.dumps({"items": items}), encoding="utf-8")


def _kiem_kich_ban(test: unittest.TestCase, block: str) -> None:
    """Đọc kịch bản bằng bộ đọc thật và kiểm bằng `kiem` thật, với ảnh và nhạc giả tạo theo kịch bản."""
    from video_ma_parts import kiem, parse

    video = parse.parse(block)
    with tempfile.TemporaryDirectory() as tmp:
        _anh_gia(Path(tmp), video)
        _nhac_gia(Path(tmp), video)
        test.assertEqual(kiem.kiem(video, Path(tmp)), [])


class ExplainerVideoGuideTest(unittest.TestCase):
    def test_guide_has_its_own_sections_in_order(self):
        self.assertEqual(h2_headings(read(EXPLAINER_GUIDE)), list(EXPLAINER_GUIDE_HEADINGS))

    def test_guide_questions_are_limited_and_have_suggestions(self):
        items = numbered_items(section(read(EXPLAINER_GUIDE), "## Câu hỏi bắt buộc"))
        self.assertTrue(1 <= len(items) <= 7, f"{len(items)} câu")
        for item in items:
            self.assertIn("Gợi ý:", item)
        quick = numbered_items(section(read(EXPLAINER_GUIDE), "## Tạo nhanh"))
        self.assertTrue(2 <= len(quick) <= 3, f"{len(quick)} câu")

    def test_guide_example_parses_with_the_real_reader(self):
        body = section(read(EXPLAINER_GUIDE), "## Cấu trúc video.md")
        blocks = re.findall(r"```[a-z]*\n(---\n.*?)```", body, re.S)
        self.assertGreaterEqual(len(blocks), 1)
        for block in blocks:
            _kiem_kich_ban(self, block)

    def test_guide_example_shows_pictures_photos_and_motion_keys(self):
        from video_ma_parts import parse

        body = section(read(EXPLAINER_GUIDE), "## Cấu trúc video.md")
        videos = [parse.parse(block) for block in re.findall(r"```[a-z]*\n(---\n.*?)```", body, re.S)]
        scenes = [scene for video in videos for scene in video.canh]
        self.assertTrue(any(s.loai == "minh-hoa" for s in scenes))
        self.assertTrue(any(s.loai != "minh-hoa" and "hinh" in s.truong for s in scenes))
        self.assertTrue(any(s.loai == "anh" and "nguon" in s.truong for s in scenes))
        self.assertTrue(any(s.loai != "anh" and "anh" in s.truong for s in scenes))
        for key in ("ban-tay", "may-quay", "chuyen-canh"):
            self.assertIn(f"\n{key}: ", body)

    def test_scene_guide_icon_table_names_exist(self):
        from video_ma_parts import hinh

        body = section(read(SCENE_GUIDE), "## Bảng tra biểu tượng")
        rows = re.findall(r"^\| ([^|]+?) \| ([^|]+?) \| `([^`]+)` \|$", body, re.M)
        self.assertGreaterEqual(len(rows), 80)
        # Gợi ý tên biểu tượng trong hinh.py đọc đúng bảng này (một nguồn duy nhất).
        self.assertEqual(hinh.bang_tra(), [(khai_niem, ten) for _mon, khai_niem, ten in rows])
        mon = {row[0] for row in rows}
        self.assertEqual(mon, {"Toán", "Vật lí", "Hoá học", "Sinh học", "Địa lí", "Chung"})
        thu_muc = SKILL_DIR / "templates" / "icons" / "tabler-outline"
        for _mon, _khai_niem, ten in rows:
            with self.subTest(ten=ten):
                self.assertTrue((thu_muc / f"{ten}.svg").is_file(), ten)
                hinh.doc(ten)
        self.assertIn('rg --files skills/ppt-master/templates/icons/tabler-outline -g "*', body)

    def test_docs_cover_pictures_photos_and_motion(self):
        guide = read(EXPLAINER_GUIDE)
        for phrase in ("minh-hoa", "image_search.py", "ban-tay", "may-quay", "chuyen-canh", "Itim", "--xem-truoc",
                       "anh\\.review\\", "8 MB", "1,5 lần"):
            with self.subTest(file=EXPLAINER_GUIDE, phrase=phrase):
                self.assertIn(phrase, guide)
        scenes = read(SCENE_GUIDE)
        for phrase in ("image_search.py", "image_sources.json", "anh/.review/", "8 MB", "`nguon`"):
            with self.subTest(file=SCENE_GUIDE, phrase=phrase):
                self.assertIn(phrase, scenes)
        agents = section(read("AGENTS.vi.md"), AGENTS_VI_EXPLAINER_HEADING)
        for phrase in ("image_search.py", "--xem-truoc", "anh\\.review\\", "1,5 lần", "ban-tay"):
            with self.subTest(file="AGENTS.vi.md", phrase=phrase):
                self.assertIn(phrase, agents)
        teachers = read("docs/vi/video-giai-thich.md")
        for phrase in ("Itim", "OFL", "7–8 phút", "11 phút", "bàn tay", "máy quay"):
            with self.subTest(file="docs/vi/video-giai-thich.md", phrase=phrase):
                self.assertIn(phrase, teachers)
        self.assertIn("image_search.py", read(".agents/rules/ppt-master-vi.md"))
        self.assertIn(".review", section(read("docs/vi/xu-ly-loi.md"), "## Dựng video giải thích thất bại"))

    def test_scene_guide_lists_every_scene_type_and_field(self):
        from video_ma_parts import parse

        text = read(SCENE_GUIDE)
        for loai, (required, optional, repeated) in parse.SCENE_SPEC.items():
            self.assertIn(f"`{loai}`", text)
            for key in (*required, *optional, *repeated):
                with self.subTest(loai=loai, key=key):
                    self.assertIn(f"`{key}`", text)
        for phrase in ("li-con-lac-don", "hoa-chuan-do", "toan-ham-so", "tham-so", "Không chèn địa chỉ web"):
            self.assertIn(phrase, text)

    def test_guide_states_the_grammar_and_limits(self):
        body = section(read(EXPLAINER_GUIDE), "## Cấu trúc video.md")
        for phrase in ("tieu-de", "mon", "lop", "phong-cach", "giong", "toc-do", "phu-de", "## Cảnh", "loai:", "loi:",
                       "canh-1.mp3", "Không chèn địa chỉ web", "H~2~SO~4~"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_guide_names_outputs_and_forbids_hand_editing_frames(self):
        body = section(read(EXPLAINER_GUIDE), "## Đầu ra")
        for phrase in (EXPLAINER_COMMAND, "video.mp4", "phu-de.srt", "xem-truoc", "--xem-truoc", "--plan-only",
                       "projects\\_video\\", "Không tự chạy FFmpeg", "Không viết HTML"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_guide_skips_the_pptx_only_steps(self):
        body = section(read(EXPLAINER_GUIDE), "## Ghi vào brief")
        for phrase in ("projects/_video/", "brief.md", "import-sources", "dòng chốt"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_guides_have_no_markdown_links(self):
        for name in (EXPLAINER_GUIDE, SCENE_GUIDE):
            self.assertEqual(LINK_RE.findall(read(name)), [], name)

    def test_agents_vi_section_15_is_last_and_routes_the_word_video(self):
        headings = h2_headings(read("AGENTS.vi.md"))
        self.assertEqual(headings[-1], AGENTS_VI_EXPLAINER_HEADING)
        body = section(read("AGENTS.vi.md"), AGENTS_VI_EXPLAINER_HEADING)
        for phrase in (f"({EXPLAINER_GUIDE})", f"({SCENE_GUIDE})", EXPLAINER_COMMAND, "--plan-only", "--xem-truoc",
                       "`ready`", "error.step", "Không chạy `project_manager.py init`", "không tạo SVG", "không chạm `skills/`",
                       "không commit gì trong `projects/`", "Không tự cài phần mềm", "chromium", "edge-tts"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)
        for step in ("input", "parse", "canh", "giong", "chromium", "ffmpeg", "dung", "write", "internal"):
            self.assertIn(f"| `{step}` |", body)
        assistant = section(read("AGENTS.vi.md"), AGENTS_VI_ASSISTANT_HEADING)
        for phrase in ("video giải thích", "video viết tay", "video whiteboard", "Thầy cô muốn làm video từ bài giảng slide đã có"):
            self.assertIn(phrase, read("AGENTS.vi.md"))

    def test_rule_file_carries_the_gate_inline_and_stays_under_the_cap(self):
        rule = read(".agents/rules/ppt-master-vi.md")
        self.assertLess(len(rule), 12000)
        for phrase in ("10 loại", "Video giải thích", "video_ma.py", "Thầy cô muốn làm video từ bài giảng slide đã có"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, rule)


TEACHER_EXPLAINER_DOC = "docs/vi/video-giai-thich.md"
EFFECT_PHRASES = ("==", "((", "__", "{{", "cau-hoi", "bieu-do", "so-do", "dong-thoi-gian", "tim_nhac.py", "nhac-nen",
                  "am-thanh", "karaoke", "luan-phien")
_KICH_BAN_RE = re.compile(r"```[a-z]*\n(---\n.*?)```", re.S)
_CANH_MAU_RE = re.compile(r"```[a-z]*\n(## Cảnh \d+\n.*?)```", re.S)
_DAU_CANH_MAU = "---\ntieu-de: Thử\nmon: Vật lí\nlop: 11\n---\n\n## Cảnh 1\nloai: tieu-de\nchu: Mở đầu\nloi: Mở đầu.\n\n"


class ExplainerEffectsDocsTest(unittest.TestCase):
    """Tài liệu vi.11: nhấn ý, số chạy, bốn loại cảnh mới, chuyển cảnh, karaoke, tiếng hiệu ứng, nhạc nền."""

    def test_guides_name_every_effect(self):
        for name in (EXPLAINER_GUIDE, SCENE_GUIDE):
            text = read(name)
            for phrase in EFFECT_PHRASES:
                with self.subTest(file=name, phrase=phrase):
                    self.assertIn(phrase, text)

    def test_guide_meta_table_lists_every_key_and_value(self):
        from video_ma_parts import parse

        body = section(read(EXPLAINER_GUIDE), "## Cấu trúc video.md")
        rows = {line.split(" | ")[0]: line for line in body.splitlines() if line.startswith("| `")}
        bang = "\n".join(rows)
        for key in (*parse.META_REQUIRED, *parse.META_CHOICES, *parse.META_FREE):
            with self.subTest(key=key):
                self.assertIn(f"`{key}`", bang)
        for key, values in parse.META_CHOICES.items():
            row = rows.get(f"| `{key}`", "")
            for value in values:
                with self.subTest(key=key, value=value):
                    self.assertIn(f"`{value}`", row)
        self.assertIn("`karaoke` (mặc định", rows["| `phu-de`"])
        self.assertEqual(parse.META_DEFAULTS["phu-de"], "karaoke")

    def test_scene_guide_lists_every_transition_and_the_scene_field(self):
        from video_ma_parts import parse

        body = section(read(SCENE_GUIDE), "## Chuyển cảnh")
        for kieu in parse.META_CHOICES["chuyen-canh"]:
            with self.subTest(kieu=kieu):
                self.assertIn(f"| `{kieu}` |", body)
        self.assertEqual(set(parse.SCENE_KIEU_CHUYEN), set(parse.META_CHOICES["chuyen-canh"]) - {"luan-phien"})
        for phrase in ("`chuyen:`", "Cảnh 1", "lỗi `parse`"):
            self.assertIn(phrase, body)

    def test_scene_guide_states_the_emphasis_grammar(self):
        from video_ma_parts import kiem

        body = section(read(SCENE_GUIDE), "## Nhấn ý chính và số chạy")
        for phrase in ("`==chữ==`", "`((chữ))`", "`__chữ__`", "`{{số}}`", f"Tối đa {kiem.MAX_CUM} cụm", "giữ dấu thanh",
                       "0,3 giây", "`____`", "`bieu-thuc`", "dấu chấm", "dấu phẩy", "`chu-dong: co`"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_every_example_script_passes_the_real_reader(self):
        found = 0
        for name in (EXPLAINER_GUIDE, SCENE_GUIDE, TEACHER_EXPLAINER_DOC):
            for block in _KICH_BAN_RE.findall(read(name)):
                found += 1
                with self.subTest(file=name, block=block[:60]):
                    _kiem_kich_ban(self, block)
        self.assertGreaterEqual(found, 3)

    def test_every_scene_example_passes_the_real_reader(self):
        from video_ma_parts import parse

        blocks = _CANH_MAU_RE.findall(read(SCENE_GUIDE))
        loai = set()
        for block in blocks:
            with self.subTest(block=block[:40]):
                kich_ban = _DAU_CANH_MAU + re.sub(r"^## Cảnh \d+", "## Cảnh 2", block)
                _kiem_kich_ban(self, kich_ban)
                loai.add(parse.parse(kich_ban).canh[1].loai)
        self.assertEqual(loai, set(parse.SCENE_SPEC))

    def test_guide_example_uses_the_new_effects(self):
        from video_ma_parts import parse

        body = section(read(EXPLAINER_GUIDE), "## Cấu trúc video.md")
        videos = [parse.parse(block) for block in _KICH_BAN_RE.findall(body)]
        scenes = [scene for video in videos for scene in video.canh]
        chu = "\n".join(value for scene in scenes for values in scene.truong.values() for value in values)
        for loai in ("cau-hoi", "bieu-do", "so-do", "dong-thoi-gian"):
            with self.subTest(loai=loai):
                self.assertTrue(any(s.loai == loai for s in scenes))
        for dau in ("==", "((", "__", "{{"):
            with self.subTest(dau=dau):
                self.assertIn(dau, chu)
        self.assertTrue(any("chuyen" in s.truong for s in scenes))
        self.assertTrue(any(v.meta.get("nhac-nen") for v in videos))
        self.assertTrue(any(v.meta.get("chuyen-canh") == "luan-phien" for v in videos))

    def test_guide_asks_about_quiz_effects_and_music(self):
        items = numbered_items(section(read(EXPLAINER_GUIDE), "## Câu hỏi bắt buộc"))
        joined = "\n".join(items)
        for phrase in ("câu hỏi nhanh", "nhạc nền", "tiếng hiệu ứng", "giọng thu sẵn", "tô vàng"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, joined)
        output = section(read(EXPLAINER_GUIDE), "## Đầu ra")
        for phrase in (r"python tools\vi\tim_nhac.py", r"projects\_video\<tên_video>\nhac", "nhac/nguon.json",
                       "nghe thử", "`mang`", "`input`", "`write`", "am-thanh: khong", "canh-N-giai.mp3"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, output)

    def test_agents_rule_and_troubleshooting_cover_the_music_finder(self):
        agents = section(read("AGENTS.vi.md"), AGENTS_VI_EXPLAINER_HEADING)
        for phrase in (r"python tools\vi\tim_nhac.py", "nhac-nen", "nguon-nhac", "nghe thử", "`mang`", "am-thanh: khong",
                       "karaoke", "luan-phien", "cau-hoi", "canh-N-giai.mp3", "nhac/nguon.json"):
            with self.subTest(file="AGENTS.vi.md", phrase=phrase):
                self.assertIn(phrase, agents)
        rule = read(".agents/rules/ppt-master-vi.md")
        for phrase in ("tim_nhac.py", "nhac-nen", "nghe thử", "`mang`", "cau-hoi"):
            with self.subTest(file="rule", phrase=phrase):
                self.assertIn(phrase, rule)
        self.assertLess(len(rule), ANTIGRAVITY_RULE_LIMIT)
        text = read("docs/vi/xu-ly-loi.md")
        headings = h2_headings(text)
        self.assertEqual(headings.index("## Tìm nhạc nền thất bại"), headings.index("## Dựng video giải thích thất bại") + 1)
        body = section(text, "## Tìm nhạc nền thất bại")
        for phrase in ("tim_nhac.py", "`mang`", "`input`", "`write`", "Openverse", "CC0", "CC BY"):
            with self.subTest(file="xu-ly-loi.md", phrase=phrase):
                self.assertIn(phrase, body)
        self.assertIn("nhạc nền", section(text, "## Dựng video giải thích thất bại"))

    def test_music_finder_error_steps_match_the_docs(self):
        import tim_nhac

        source = (REPO_ROOT / "tools" / "vi" / "tim_nhac.py").read_text(encoding="utf-8")
        steps = set(re.findall(r'Loi\("([a-z]+)"', source)) | set(re.findall(r'"step": "([a-z]+)"', source))
        self.assertEqual(steps, {"mang", "input", "write"})
        self.assertEqual(tim_nhac.GIAY_TOI_THIEU, 60)
        body = section(read("docs/vi/xu-ly-loi.md"), "## Tìm nhạc nền thất bại")
        for step in steps:
            self.assertIn(f"`{step}`", body)

    def test_teacher_doc_explains_the_effects(self):
        text = read(TEACHER_EXPLAINER_DOC)
        self.assertIn("## Hiệu ứng giúp học sinh nhớ bài", h2_headings(text))
        body = section(text, "## Hiệu ứng giúp học sinh nhớ bài")
        for phrase in ("Nhấn ý chính", "Số chạy", "Biểu đồ", "Sơ đồ tư duy", "dòng thời gian", "Câu hỏi nhanh", "Chuyển cảnh",
                       "karaoke", "Tiếng hiệu ứng", "Nhạc nền", "Openverse", "CC0", "CC BY", "nghe thử", "4 giây cuối"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)
        self.assertNotIn("không có nhạc nền", text)


AI_GUIDE_HEADING = "## Hình do AI vẽ"
SCENE_LIMITS_HEADING = "## Giới hạn theo khổ và phong cách"
SCENE_CHARACTER_HEADING = "## Nhân vật dẫn chuyện"
_BON_KHO = (("ngang", "viet-tay"), ("ngang", "cat-dan"), ("doc", "viet-tay"), ("doc", "cat-dan"))


def _anh_ai_steps() -> set:
    """Mọi `error.step` mà anh_ai.py có thể in, đọc thẳng từ mã (anh_ai.py và anh_ai_parts/)."""
    sources = [(REPO_ROOT / "tools" / "vi" / "anh_ai.py").read_text(encoding="utf-8")]
    sources += [p.read_text(encoding="utf-8") for p in sorted((REPO_ROOT / "tools" / "vi" / "anh_ai_parts").glob("*.py"))]
    text = "\n".join(sources)
    return set(re.findall(r'Error\("([a-z-]+)"', text)) | set(re.findall(r'"step": "([a-z-]+)"', text))


class ExplainerVi12DocsTest(unittest.TestCase):
    """Tài liệu vi.12: khổ dọc, cắt dán, nhân vật, cảnh kể chuyện, ảnh AI theo nền tảng (spec Q15)."""

    def test_guides_require_pictures_that_match_the_narration_and_one_subtitle_line(self):
        guide = read("docs/vi/tro-ly/video-giai-thich.md")
        for phrase in ("Hình phải khớp lời đọc", "lời nói gì — hình cho thấy gì", "phải có `the`",
                       "Không quá hai cảnh `ke-chuyen` liền nhau", "một dòng một lúc"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, guide)
        self.assertIn("một dòng một lần hiện", read("docs/vi/tro-ly/canh-video.md"))
        self.assertIn("Hình phải khớp lời đọc", read(".agents/rules/ppt-master-vi.md"))
        self.assertIn("Hình phải khớp lời đọc", read("AGENTS.vi.md"))

    def test_scene_guide_names_every_scene_type_in_code(self):
        from video_ma_parts import parse

        text = read(SCENE_GUIDE)
        codes = re.findall(r"^Mã loại: `([a-z-]+)`\.$", text, re.M)
        self.assertEqual(codes, list(parse.SCENE_TYPES))
        self.assertEqual(len(parse.SCENE_TYPES), 15)
        self.assertTrue(text.startswith("# Cảnh video giải thích: danh mục mười lăm loại cảnh\n"))

    def test_scene_guide_tables_the_ten_poses_and_eight_backgrounds(self):
        from video_ma_parts import parse

        body = section(read(SCENE_GUIDE), SCENE_CHARACTER_HEADING)
        poses = re.findall(r"^\| `([a-z-]+)` \| [^|`]*\S[^|`]* \|$", body, re.M)
        self.assertEqual(poses, list(parse.TU_THE))
        backgrounds = re.findall(r"^\| `mau/([a-z-]+)` \| [^|]*\S[^|]* \|$", read(SCENE_GUIDE), re.M)
        self.assertEqual(backgrounds, list(parse.NEN_MAU))
        for phrase in ("`nhan-vat: nguoi-que`", "`nhan-vat: ve:", "`mau-ao`", "`vi-tri`", "lỗi `parse`"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)
        # Lỗi tư thế sai in 3 gợi ý rồi đủ mười tên: tài liệu nói đúng như vậy.
        with self.assertRaises(parse.ParseError) as caught:
            parse.parse("---\ntieu-de: T\nmon: M\nlop: 1\nnhan-vat: nguoi-que\n---\n## Cảnh 1\nloai: tieu-de\nchu: A\n"
                        "tu-the: point\nloi: A.\n")
        self.assertIn("Mười tư thế: " + ", ".join(parse.TU_THE), str(caught.exception))
        self.assertIn("đủ mười tên", body)

    def test_scene_guide_limit_table_matches_the_checker(self):
        from video_ma_parts import kiem

        body = section(read(SCENE_GUIDE), SCENE_LIMITS_HEADING)
        rows = re.findall(r"^\| `([a-z-]+)` `([a-z-]+)` \| (\d+) \| (\d+) \| (\d+) \| (\d+) \|$", body, re.M)
        bang = [kiem.bang_gioi_han(kho, pc)[0] for kho, pc in _BON_KHO]
        khac = {key for key in bang[0] if len({b[key] for b in bang}) > 1}
        self.assertEqual({(loai, key) for loai, key, *_ in rows}, khac)
        for loai, key, *so in rows:
            with self.subTest(loai=loai, key=key):
                self.assertEqual([int(s) for s in so], [b[(loai, key)] for b in bang])
        for (kho, pc), toi_da in kiem.DOAN_LIEN.items():
            with self.subTest(doan_lien=(kho, pc)):
                self.assertIn(str(toi_da), body)
        for phrase in ("22 ký tự", "42 ký tự", "cảnh có thẻ hoặc dòng tài liệu", "`the`", "`tai-lieu`"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_guide_asks_format_style_character_and_series_within_seven_questions(self):
        items = numbered_items(section(read(EXPLAINER_GUIDE), "## Câu hỏi bắt buộc"))
        self.assertTrue(1 <= len(items) <= 7, f"{len(items)} câu")
        joined = "\n".join(items)
        for phrase in ("ngang để chiếu lớp hay dọc để đăng TikTok/Reels", "viết tay hay cắt dán",
                       "không, người que, hay nhân vật do AI vẽ theo mô tả", "tên loạt"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, joined)

    def test_guide_example_has_a_story_scene(self):
        from video_ma_parts import parse

        body = section(read(EXPLAINER_GUIDE), "## Cấu trúc video.md")
        videos = [parse.parse(block) for block in _KICH_BAN_RE.findall(body)]
        self.assertTrue(any(s.loai == "ke-chuyen" for v in videos for s in v.canh))
        self.assertTrue(any(v.meta["nhan-vat"] == "nguoi-que" for v in videos))

    def test_guide_ai_section_covers_both_platform_paths(self):
        body = section(read(EXPLAINER_GUIDE), AI_GUIDE_HEADING)
        for phrase in ("anh_ai.py ke-hoach", "anh_ai.py nhan", "--xem-truoc", "Claude Code", "nguoi-que", "Antigravity",
                       "Codex", "--cong-cu", "--mo-hinh", "anh/ai/goc/", "anh/ai/ke-hoach.json", "anh/ai/nguon.json",
                       "nhan-vat-mau.png", "#00FF00", "nen: mau/", "không có chữ", "nguon.json", "3–4 ảnh"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_ai_error_steps_in_docs_match_the_tool(self):
        steps = _anh_ai_steps()
        self.assertEqual(steps, {"input", "parse", "thieu", "tach-nen", "ffmpeg", "write", "internal"})
        guide = section(read(EXPLAINER_GUIDE), AI_GUIDE_HEADING)
        agents = section(read("AGENTS.vi.md"), AGENTS_VI_EXPLAINER_HEADING)
        for name, body in ((EXPLAINER_GUIDE, guide), ("AGENTS.vi.md", agents)):
            for step in steps:
                with self.subTest(file=name, step=step):
                    self.assertIn(f"| `{step}` |", body)

    def test_agents_vi_allows_the_platform_image_tool_and_keeps_the_bans(self):
        body = section(read("AGENTS.vi.md"), AGENTS_VI_EXPLAINER_HEADING)
        for phrase in ("dùng công cụ tạo ảnh của chính nền tảng để vẽ ảnh trong `anh/ai/goc/` theo `ke-hoach.json`",
                       "Hình do AI vẽ", r"python tools\vi\anh_ai.py", "không chạm `skills/`", "Không viết HTML hay ảnh cảnh bằng tay",
                       "nguon.json", "nguoi-que"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_rule_file_carries_the_ai_image_steps(self):
        rule = read(".agents/rules/ppt-master-vi.md")
        self.assertLess(len(rule), ANTIGRAVITY_RULE_LIMIT)
        body = section(rule, "## Video giải thích")
        for phrase in ("anh_ai.py ke-hoach", "anh_ai.py nhan", "--xem-truoc", "không bao giờ nằm trong ảnh"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_new_trigger_phrases_route_to_the_explainer(self):
        agents = read("AGENTS.vi.md")
        triggers = section(agents, "## 3. Câu lệnh tiếng Việt kích hoạt skill `ppt-master`")
        intro = section(agents, AGENTS_VI_EXPLAINER_HEADING).strip().split("\n\n")[0]
        rows = [r for r in task_table_rows(read("docs/vi/tro-ly/quy-trinh-hoi.md")) if r[2] == "video-giai-thich.md"]
        self.assertEqual(len(rows), 1)
        for phrase in ("video giải thích", "video viết tay", "video whiteboard", "video hoạt hình chữ",
                       "video kể chuyện", "video dọc", "video cắt dán"):
            with self.subTest(phrase=phrase):
                self.assertIn(f'"{phrase}"', triggers)
                self.assertIn(phrase, intro)
                self.assertIn(f'"{phrase}"', rows[0][1])
        # Bảng loại việc của luật Antigravity khớp quy-trinh-hoi.md (test_antigravity_rule_task_table_matches_common_rules).

    def test_teacher_doc_is_up_to_date_with_vi12(self):
        text = read(TEACHER_EXPLAINER_DOC)
        self.assertNotIn("Chưa có khổ dọc", text)
        self.assertNotIn("Video 1280×720,", text)
        for phrase in ("1920×1080", "1080×1920", "720", "khổ dọc", "cắt dán", "kể chuyện", "người que", "nền mẫu",
                       "tên loạt", "thẻ thông tin", "Antigravity", "Codex", "Claude Code", "Be Vietnam Pro"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_changelog_and_maintenance_cover_vi12(self):
        unreleased = section(read("CHANGELOG-VI.md"), "## 6.3.2-vi.12 — 2026-09-29")
        for phrase in ("khổ dọc", "cắt dán", "ke-chuyen", "người que", "anh_ai.py", "loat", "Be Vietnam Pro", "Full HD"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, unreleased)
        bao_tri = read("docs/vi/phat-trien/bao-tri.md")
        for phrase in ("Be Vietnam Pro", "Itim", "OFL", "cmap", "SHA-256"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, bao_tri)


if __name__ == "__main__":
    unittest.main()
