"""Kiểm tra mã ND30 nhúng nguyên trạng trong tools/vi/nd30/."""

import hashlib
import re
import shutil
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ND30_DIR = REPO_ROOT / "tools" / "vi" / "nd30"
NGUON_MD = ND30_DIR / "NGUON.md"

TABLE_ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([0-9a-f]{64})\s*\|\s*$")


def parse_sha_table(text: str) -> dict:
    """Đọc bảng `| đường dẫn tương đối | sha256 |` trong NGUON.md."""
    table = {}
    for line in text.splitlines():
        match = TABLE_ROW_RE.match(line.strip())
        if match is None:
            continue
        path, sha = match.groups()
        if path in ("đường dẫn tương đối", ":---", "---"):
            continue
        table[path] = sha
    return table


def list_embedded_files(base_dir: Path) -> set:
    """Mọi file trong base_dir trừ NGUON.md và __pycache__, đường dẫn tương đối dùng dấu /."""
    files = set()
    for path in base_dir.rglob("*"):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(base_dir).as_posix()
        if rel == "NGUON.md":
            continue
        files.add(rel)
    return files


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_embed(base_dir: Path, nguon_md: Path) -> dict:
    """So bảng SHA-256 trong nguon_md với các file thật dưới base_dir.

    Trả về {"missing": [...], "mismatched": [...], "untabled": [...]}.
    - missing: có trong bảng nhưng không tồn tại trên đĩa.
    - mismatched: tồn tại nhưng SHA-256 khác bảng.
    - untabled: có trên đĩa (không phải NGUON.md/__pycache__) nhưng không có trong bảng.
    """
    table = parse_sha_table(nguon_md.read_text(encoding="utf-8"))
    disk_files = list_embedded_files(base_dir)

    missing = []
    mismatched = []
    for rel, expected_sha in table.items():
        full = base_dir / rel
        if not full.is_file():
            missing.append(rel)
            continue
        actual_sha = sha256_of(full)
        if actual_sha != expected_sha:
            mismatched.append(rel)

    untabled = sorted(disk_files - set(table.keys()))

    return {"missing": missing, "mismatched": mismatched, "untabled": untabled}


class Nd30EmbedIntegrityTest(unittest.TestCase):
    def test_nguon_md_exists(self):
        self.assertTrue(NGUON_MD.is_file(), "Thiếu tools/vi/nd30/NGUON.md")

    def test_table_is_not_empty(self):
        table = parse_sha_table(NGUON_MD.read_text(encoding="utf-8"))
        self.assertGreater(len(table), 0, "Bảng SHA-256 trong NGUON.md rỗng hoặc không đọc được")

    def test_every_table_entry_exists_and_matches_sha256(self):
        result = verify_embed(ND30_DIR, NGUON_MD)
        self.assertEqual(result["missing"], [], f"File thiếu trên đĩa: {result['missing']}")
        self.assertEqual(result["mismatched"], [], f"SHA-256 lệch bảng: {result['mismatched']}")

    def test_every_disk_file_is_listed_in_the_table(self):
        result = verify_embed(ND30_DIR, NGUON_MD)
        self.assertEqual(result["untabled"], [], f"File trên đĩa chưa có trong bảng NGUON.md: {result['untabled']}")

    def test_table_sorted_by_path_with_forward_slashes(self):
        table = parse_sha_table(NGUON_MD.read_text(encoding="utf-8"))
        paths = list(table.keys())
        self.assertEqual(paths, sorted(paths))
        for path in paths:
            self.assertNotIn("\\", path)

    def test_files_match_upstream_git_blobs(self):
        """SHA-256 của blob ở commit b683ff9a (LF, `git show`): bản nhúng phải giống từng byte."""
        upstream = {
            "LICENSE": "8c618bd499a693bbbf905a4dc4c276db6a09a9abb190e05a2e2b2b978fb6cc3a",
            "scripts/_common.py":
                "baecd402e84f9dd992d5a3aa7b610cb2871b54f440d1eec8283db995bc972c16",
            "scripts/validate_docx.py":
                "b5fb9bc5054a540c1dee1709a2cde2615dfe78a105f0b40d36c29310e0fc9976",
            "examples/cong_van.json":
                "97dac5c34dea0796016c9084b06814ec1a1b6ccfe5077d357056b9bc3d967864",
            "templates/cong-van.docx":
                "5816ead12bd2cfd889163cf8cd209e2f1c478b26affc799f3f24a7bea1e44863",
        }
        for rel, expected in upstream.items():
            with self.subTest(path=rel):
                self.assertEqual(sha256_of(ND30_DIR / rel), expected)
                self.assertNotIn(b"\r\n", (ND30_DIR / rel).read_bytes()[:4096]
                                 if rel.endswith((".py", ".json")) or rel == "LICENSE" else b"")

    def test_license_is_mit_and_credits_the_author(self):
        license_text = (ND30_DIR / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("MIT License", license_text)
        self.assertIn("Nguyễn Minh Phát", license_text)

    def test_tampering_one_byte_is_detected_in_an_isolated_copy(self):
        """Sửa 1 byte trong bản sao tạm (không đụng repo thật): hàm kiểm phải nêu đúng tên file lệch."""
        with tempfile.TemporaryDirectory() as tmp_name:
            tmp_dir = Path(tmp_name) / "nd30"
            shutil.copytree(ND30_DIR, tmp_dir)
            target = tmp_dir / "scripts" / "_common.py"
            data = bytearray(target.read_bytes())
            data[0] ^= 0xFF
            target.write_bytes(bytes(data))

            result = verify_embed(tmp_dir, tmp_dir / "NGUON.md")
            self.assertEqual(result["mismatched"], ["scripts/_common.py"])
            self.assertEqual(result["missing"], [])


if __name__ == "__main__":
    unittest.main()
