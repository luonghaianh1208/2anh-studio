# Video Vox — kế hoạch triển khai (6.3.2-vi.15)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Thêm `phong-cach: vox` cho video giải thích: cảnh tả bằng nhịp gắn lời thoại, ảnh AI qua API kiểu OpenAI (9router), lớp dựng giấy cắt dán 2,5D, kiểm thời lượng; hướng dẫn và luật chỉ dạy lối Vox.

**Architecture:** Đọc `video.md` Vox bằng mô-đun mới `video_ma_parts/vox.py` (parse.py chỉ rẽ nhánh). Ảnh tạo và xử lý trước bằng `tools/vi/anh_vox.py` (ảnh gốc, ảnh cắt nền có viền xé, ảnh khung); `video_ma.py` chỉ đọc file đã xử lý theo tên tất định. Trang mỗi cảnh Vox dùng runtime riêng `runtime/vox.js` + `vox.css`, giữ đúng hợp đồng trang hiện có (`datThoiDiem`, `THI_VIDEO.san/thoiDiemCuoi/kiemTran/suKien`), nên `chup.py` (beginFrame) và `ghep.py` (karaoke, âm thanh) dùng lại nguyên.

**Tech Stack:** Python 3.10+ thư viện chuẩn, Pillow, numpy (có sẵn qua `skills/ppt-master/requirements.txt`), Playwright Chromium, FFmpeg, JavaScript ES5 trong trang (như runtime hiện có), Node `node --test` cho test JS.

**Spec:** `docs/vi/phat-trien/2026-10-01-video-vox-design.md`

## Global Constraints

- Không sửa gì trong `skills/` (chỉ được chạy `skills/ppt-master/scripts/image_search.py`), `LICENSE`, `SPONSORS*`, `attribution_guard.py`, `tools/vi/nd30/`, `tools/vi/thi_nghiem_parts/`; không sửa `requirements.txt` ở gốc và của skill.
- Không thêm thư viện Python ngoài: chỉ thư viện chuẩn, Pillow, numpy, playwright, edge-tts.
- Kịch bản `viet-tay`, `cat-dan` cũ dựng ra như trước; toàn bộ test hiện có (1420) vẫn qua, trừ các test tài liệu Task 8 chuyển đích có chủ đích.
- Khoá API (`ANH_AI_KEY`) không bao giờ nằm trong repo, log, stderr hay JSON đầu ra.
- Mọi khung hình là hàm thuần của t; ngẫu nhiên đều có seed (mulberry32 `THI_CAT_DAN.prng`, Python `random.Random(seed)`).
- Chữ hiển thị dùng Be Vietnam Pro đóng gói ở `runtime/fonts/` (không tải font ngoài, không địa chỉ web trong trang).
- Lệnh mới in đúng một dòng JSON ra stdout; lỗi có `error.step`, `error.message`, `error.fix`; tiến trình ghi ra stderr.
- Ngôn ngữ: code, tên hàm theo kiểu tiếng Việt không dấu như mã hiện có; tài liệu trong `docs/vi/` viết tiếng Việt; commit message tiếng Anh kiểu `feat(vi): …`, kèm dòng `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`; commit bằng `git commit -F <file>`; `git add` đường dẫn tường minh.
- Chạy test từ gốc repo: `venv\Scripts\python.exe -m unittest discover -s tools/vi/tests -t tools/vi` không dùng được; dùng `cd tools/vi; ..\..\venv\Scripts\python.exe -m unittest discover -s tests` (toàn bộ) hoặc `..\..\venv\Scripts\python.exe -m unittest tests.<tên_file>` (một file).
- Luật Antigravity `.agents/rules/ppt-master-vi.md` ≤ 12 000 byte tính UTF-8 với CRLF.
- Mặc định nguồn vẽ: `ANH_AI_URL=http://localhost:20128/v1`, `ANH_AI_MO_HINH=ag/gemini-3.1-flash-image`.

## Hợp đồng dùng chung (mọi task đọc)

**Scene Vox** (`parse.Scene`): `loai == "vox"`, `truong` có `bo-cuc` (list một phần tử), `nhip` (list chuỗi gốc), tuỳ chọn `chuyen`, `nguon`; thêm thuộc tính mới `Scene.nhip: list[vox.Nhip] | None = None`.

**`vox.Nhip`** (dataclass, `video_ma_parts/vox.py`):
```python
@dataclass
class Nhip:
    cum: str            # cụm từ trong lời, hoặc "@dau"
    vat: str            # anh | the | chu | nhan | dau | mui-ten | so
    noi_dung: str       # phần sau "vat:" đã strip
    o: str | None       # ô; None = công cụ chọn ô trống kế tiếp
    tuy_chon: tuple     # tập con của ("khung", "duotone", "halftone", "xa", "gan")
    dong: int           # số dòng trong video.md
    chi_so: int         # thứ tự nhịp trong cảnh, từ 0
```

**Tên file ảnh tất định** (`anh_vox_parts/ke_hoach.py`, video_ma import lại):
- `ma_anh(prompt: str, kich_thuoc: str) -> str` = 16 ký tự hex đầu của SHA-256 của `f"{prompt}\n{kich_thuoc}"`.
- Ảnh gốc AI: `anh/ai/goc/<ma>.png`. Ảnh thật `tim:`: `anh/tim-<sha256(từ khoá)[:10]>.jpg`.
- Ảnh đã xử lý: `anh/ai/xu-ly/<ma>-<hat>-<kieu>.png`, `kieu ∈ {"cat", "khung", "phu"}` (`phu` cho `toan-canh` ô `nen`), `hat = so_canh * 100 + chi_so`. Hậu tố thêm `-duotone` hoặc `-halftone` nếu có tuỳ chọn đó, theo thứ tự đó, ví dụ `…-khung-duotone.png`.
- `anh/ai/nguon.json`: list `{file, cong_cu, mo_hinh, prompt, ngay, ma}` (cùng dạng `anh_ai.py` đang ghi, thêm `ma`). Ảnh thật: nguồn trong `anh/image_sources.json` như hiện nay.

**Dữ liệu cảnh Vox cho trang** (`du`, do `vox.du_lieu_canh` dựng):
```python
{
  "so": int, "loai": "vox", "thoiLuong": float, "danDau": lich.DAN_DAU,
  "kho": Kho.du_lieu(), "chuDe": phong.chu_de("vox"),
  "boCuc": "mot|hai-ben|dan-hang|chong|toan-canh", "hat": int,            # hat = so cảnh
  "bangMau": "kem|bao-cu|dem|tuoi",
  "nhip": [ { "batDau": float, "vat": str, "o": str, "tuyChon": [str],
              "chu": str | None,                       # chu/nhan/dau/so (đã bỏ dấu nhấn), mui-ten: "a -> b"
              "the": {"nhan","giaTri","chuThich"} | None,
              "anh": {"dataUrl","rong","cao","kieu": "cat|khung|phu","nguon": str|None} | None,
              "so": {"giaTri": float, "truoc": str, "sau": str, "thapPhan": int} | None } ],
  "nguon": str | None,                                   # dòng nguồn số liệu của cảnh
  "co": {"chuyen": "xe-giay|lia" | None},
  "nenTruoc": None, "dongNguon": [], "loat": None,
}
```

**Hợp đồng trang** (giữ như runtime cũ): sau `khoiDong(du)` đặt `THI_VIDEO.san = true`; `window.datThoiDiem(t)`; `THI_VIDEO.thoiDiemCuoi() -> du.thoiLuong - 1/30`; `THI_VIDEO.kiemTran() -> [id]`; `THI_VIDEO.suKien() -> [{t, loai, dai}]` với `loai ∈ {chuyen, ting, nhan, dung}`.

## Review Focus

1. Cụm từ trong `nhip` viết khác lời một chút (hoa thường, dấu câu, "chu kì"/"chu kỳ") → so theo `lich.khoa_so_khop` từng từ; khác chữ thật thì lỗi `parse` nêu cụm và câu lời. Test ở Task 1.
2. Cùng một cụm xuất hiện hai lần trong lời, hai nhịp dùng nó → nhịp sau lấy lần xuất hiện sau. Test ở Task 1 và Task 5.
3. Mô hình ảnh trả khổ khác khổ xin (1024×1024 khi xin 1536×1024) hoặc trả `url` thay `b64_json` → vẫn ra ảnh đúng tỉ lệ ô. Test ở Task 3 và Task 4.
4. Chạy lại `anh_vox.py` sau khi sửa một nhịp → chỉ vẽ ảnh đổi; đổi mô hình → vẽ lại. Test ở Task 3.
5. Ảnh AI nền không thuần xanh (xanh đậm, có bóng) → tách nền vẫn ra alpha sạch hoặc tự chuyển `khung` kèm cảnh báo, không ra ảnh có viền xanh. Test ở Task 4.

---

### Task 1: Đọc `video.md` Vox (khối thông tin và nhịp)

**Files:**
- Create: `tools/vi/video_ma_parts/vox.py`
- Modify: `tools/vi/video_ma_parts/parse.py` (`META_CHOICES["phong-cach"]`, `META_FREE`, `_read_meta`, `_finish`, `parse`, dataclass `Scene`)
- Test: `tools/vi/tests/test_video_ma_vox_parse.py`

**Interfaces:**
- Produces: `vox.Nhip`; `vox.BO_CUC: dict[str, dict[str, tuple]]` (bố cục → {"ngang": ô, "doc": ô}); `vox.VAT`; `vox.VOX_META_CHOICES`; `vox.VOX_CAM`; `vox.doc_nhip(value: str, no: int, chi_so: int) -> Nhip`; `vox.kiem_canh(scene: parse.Scene, kho: str) -> None` (raise `parse.ParseError`); `vox.tim_cum(tokens: list[str], cum: str, tu_vi_tri: int) -> int` (chỉ số token đầu, -1 nếu không có); `vox.khoa_tu(text: str) -> list[str]`.
- `parse.Scene` thêm `nhip: list | None = None`.

- [ ] **Step 1: Viết test hỏng**

```python
# tools/vi/tests/test_video_ma_vox_parse.py
"""Đọc video.md kiểu Vox: khối thông tin, nhịp, ô theo bố cục."""
import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from video_ma_parts import parse, vox  # noqa: E402

DAU = "---\ntieu-de: Giao tiếp\nphong-cach: vox\n---\n\n"


def doc(canh: str, dau: str = DAU):
    return parse.parse(dau + canh)


CANH_HAI_BEN = ("## Cảnh 1\nbo-cuc: hai-ben\n"
                "loi: Bạn nói \"để mai tính\", đồng nghiệp lại hiểu là \"không làm\".\n"
                "nhip: để mai tính | anh: ve: nhân viên nhún vai | trai\n"
                "nhip: không làm | anh: ve: đồng nghiệp khoanh tay | phai\n"
                "nhip: hiểu | dau: HIỂU LẦM\n")


class MetaTest(unittest.TestCase):
    def test_vox_does_not_need_subject_or_grade(self):
        v = doc(CANH_HAI_BEN)
        self.assertEqual(v.meta["phong-cach"], "vox")
        self.assertNotIn("mon", v.meta)

    def test_other_styles_still_need_subject_and_grade(self):
        with self.assertRaises(parse.ParseError) as c:
            parse.parse("---\ntieu-de: T\n---\n\n## Cảnh 1\nloai: tieu-de\nchu: A\nloi: Chào.\n")
        self.assertIn("`mon`", str(c.exception))

    def test_vox_meta_values(self):
        v = doc(CANH_HAI_BEN, "---\ntieu-de: T\nphong-cach: vox\nthoi-luong: 60\nphong-anh: minh-hoa\n"
                              "bang-mau: dem\nchuyen-canh: lia\n---\n\n")
        self.assertEqual((v.meta["thoi-luong"], v.meta["phong-anh"], v.meta["bang-mau"], v.meta["chuyen-canh"]),
                         ("60", "minh-hoa", "dem", "lia"))
        v2 = doc(CANH_HAI_BEN)
        self.assertEqual((v2.meta["phong-anh"], v2.meta["bang-mau"], v2.meta["chuyen-canh"]), ("chup-that", "kem", "xen-ke"))

    def test_bad_duration(self):
        for gt in ("5", "601", "một phút", "60.5"):
            with self.subTest(gt=gt), self.assertRaises(parse.ParseError) as c:
                doc(CANH_HAI_BEN, f"---\ntieu-de: T\nphong-cach: vox\nthoi-luong: {gt}\n---\n\n")
            self.assertIn("thoi-luong", str(c.exception))

    def test_duration_allowed_for_old_styles_too(self):
        v = parse.parse("---\ntieu-de: T\nmon: Toán\nlop: 8\nthoi-luong: 90\n---\n\n## Cảnh 1\nloai: tieu-de\nchu: A\nloi: Chào.\n")
        self.assertEqual(v.meta["thoi-luong"], "90")

    def test_vox_rejects_handwriting_only_keys(self):
        for dong in ("ban-tay: co", "nhan-vat: nguoi-que", "mau-ao: do", "chu-dong: co", "may-quay: co"):
            with self.subTest(dong=dong), self.assertRaises(parse.ParseError) as c:
                doc(CANH_HAI_BEN, f"---\ntieu-de: T\nphong-cach: vox\n{dong}\n---\n\n")
            self.assertIn("vox", str(c.exception))

    def test_vox_values_only_for_vox(self):
        with self.assertRaises(parse.ParseError):
            parse.parse("---\ntieu-de: T\nmon: A\nlop: 1\nphong-anh: minh-hoa\n---\n\n## Cảnh 1\nloai: tieu-de\nchu: A\nloi: B.\n")


class NhipTest(unittest.TestCase):
    def test_beats_are_parsed(self):
        c = doc(CANH_HAI_BEN).canh[0]
        self.assertEqual(c.loai, "vox")
        self.assertEqual([(n.cum, n.vat, n.o) for n in c.nhip],
                         [("để mai tính", "anh", "trai"), ("không làm", "anh", "phai"), ("hiểu", "dau", None)])
        self.assertEqual(c.nhip[0].noi_dung, "ve: nhân viên nhún vai")
        self.assertEqual(c.nhip[2].chi_so, 2)

    def test_options(self):
        c = doc("## Cảnh 1\nbo-cuc: mot\nloi: Đây là Hà Nội.\nnhip: Hà Nội | anh: tim: hanoi old quarter | giua | khung duotone\n").canh[0]
        self.assertEqual(c.nhip[0].tuy_chon, ("khung", "duotone"))

    def test_loai_is_not_allowed_in_vox(self):
        with self.assertRaises(parse.ParseError) as c:
            doc("## Cảnh 1\nloai: tieu-de\nbo-cuc: mot\nloi: A.\nnhip: @dau | chu: A\n")
        self.assertIn("loai", str(c.exception))

    def test_phrase_must_be_in_narration(self):
        with self.assertRaises(parse.ParseError) as c:
            doc("## Cảnh 1\nbo-cuc: mot\nloi: Hôm nay trời đẹp.\nnhip: trời mưa | chu: Mưa\n")
        self.assertIn("trời mưa", str(c.exception))

    def test_phrase_matching_ignores_case_and_punctuation(self):
        c = doc("## Cảnh 1\nbo-cuc: mot\nloi: \"Để mai tính\", anh ấy nói.\nnhip: để MAI tính | chu: Để mai\n").canh[0]
        self.assertEqual(c.nhip[0].cum, "để MAI tính")

    def test_beats_follow_the_narration_order(self):
        with self.assertRaises(parse.ParseError) as c:
            doc("## Cảnh 1\nbo-cuc: hai-ben\nloi: Một hai ba.\nnhip: ba | chu: Ba | trai\nnhip: một | chu: Một | phai\n")
        self.assertIn("thứ tự", str(c.exception))

    def test_repeated_phrase_takes_the_next_occurrence(self):
        c = doc("## Cảnh 1\nbo-cuc: hai-ben\nloi: Tiền nhiều, tiền ít.\nnhip: tiền | chu: A | trai\nnhip: tiền | chu: B | phai\n").canh[0]
        self.assertEqual(len(c.nhip), 2)

    def test_scene_needs_at_least_one_beat_and_at_most_six(self):
        with self.assertRaises(parse.ParseError):
            doc("## Cảnh 1\nbo-cuc: mot\nloi: A.\n")
        nhip = "".join(f"nhip: @dau | nhan: N{k}\n" for k in range(7))
        with self.assertRaises(parse.ParseError) as c:
            doc("## Cảnh 1\nbo-cuc: mot\nloi: A.\n" + nhip)
        self.assertIn("6", str(c.exception))

    def test_slot_must_belong_to_the_layout(self):
        with self.assertRaises(parse.ParseError) as c:
            doc("## Cảnh 1\nbo-cuc: mot\nloi: A b.\nnhip: A | chu: X | trai\n")
        self.assertIn("giua", str(c.exception))

    def test_portrait_slots(self):
        dau = "---\ntieu-de: T\nphong-cach: vox\nkho: doc\n---\n\n"
        doc("## Cảnh 1\nbo-cuc: hai-ben\nloi: A b.\nnhip: A | chu: X | tren\n", dau)
        with self.assertRaises(parse.ParseError):
            doc("## Cảnh 1\nbo-cuc: hai-ben\nloi: A b.\nnhip: A | chu: X | trai\n", dau)

    def test_unknown_object_and_bad_contents(self):
        cases = [
            "nhip: A | video: x\n",                          # vật lạ
            "nhip: A | the: chỉ một phần\n",                 # thẻ sai dạng
            "nhip: A | so: không có số\n",                   # so thiếu {{…}}
            "nhip: A | mui-ten: giua\n",                     # mũi tên thiếu ->
            "nhip: A | anh: \n",                             # ảnh trống
            "nhip: A | chu: " + "x" * 41 + "\n",             # chữ quá 40
            "nhip: A | dau: " + "X" * 17 + "\n",             # dấu quá 16
            "nhip: A | chu: X | giua | nhay-mua\n",          # tuỳ chọn lạ
        ]
        for nhip in cases:
            with self.subTest(nhip=nhip), self.assertRaises(parse.ParseError):
                doc("## Cảnh 1\nbo-cuc: mot\nloi: A b.\n" + nhip)

    def test_at_most_two_big_lines(self):
        with self.assertRaises(parse.ParseError) as c:
            doc("## Cảnh 1\nbo-cuc: chong\nloi: A b c.\nnhip: A | chu: X\nnhip: b | chu: Y\nnhip: c | chu: Z\n")
        self.assertIn("chu", str(c.exception))

    def test_full_frame_photo_only_in_nen_slot(self):
        doc("## Cảnh 1\nbo-cuc: toan-canh\nloi: Phố cổ.\nnhip: @dau | anh: tim: hanoi street | nen\nnhip: Phố cổ | nhan: Hà Nội | duoi\n")
        with self.assertRaises(parse.ParseError):
            doc("## Cảnh 1\nbo-cuc: toan-canh\nloi: Phố cổ.\nnhip: @dau | chu: X | nen\n")

    def test_source_line_and_transition(self):
        v = doc("## Cảnh 1\nbo-cuc: mot\nloi: A.\nnhip: @dau | chu: A\n\n"
                "## Cảnh 2\nbo-cuc: mot\nchuyen: lia\nnguon: Gallup 2023\nloi: B.\nnhip: @dau | chu: B\n")
        self.assertEqual(v.canh[1].truong["nguon"], ["Gallup 2023"])
        with self.assertRaises(parse.ParseError):
            doc("## Cảnh 1\nbo-cuc: mot\nchuyen: lau-bang\nloi: A.\nnhip: @dau | chu: A\n")


class KhoaTuTest(unittest.TestCase):
    def test_tokens(self):
        self.assertEqual(vox.khoa_tu("\"Để mai tính\", anh ấy nói!"), ["để", "mai", "tính", "anh", "ấy", "nói"])

    def test_find_phrase(self):
        t = vox.khoa_tu("tiền nhiều, tiền ít")
        self.assertEqual(vox.tim_cum(t, "tiền", 0), 0)
        self.assertEqual(vox.tim_cum(t, "tiền", 1), 2)
        self.assertEqual(vox.tim_cum(t, "tiền ít", 0), 2)
        self.assertEqual(vox.tim_cum(t, "bạc", 0), -1)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Chạy test, xác nhận hỏng**

Run: `cd tools/vi; ..\..\venv\Scripts\python.exe -m unittest tests.test_video_ma_vox_parse`
Expected: lỗi `ImportError: cannot import name 'vox'`.

- [ ] **Step 3: Viết `vox.py`**

```python
# tools/vi/video_ma_parts/vox.py
"""Cảnh kiểu Vox: nhịp gắn cụm từ trong lời, bố cục và ô. Ngữ pháp ở docs/vi/tro-ly/nhip-vox.md."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

# Khoá đầu chỉ có ở Vox; giá trị đầu tiên là mặc định.
VOX_META_CHOICES = {
    "phong-anh": ("chup-that", "minh-hoa"),
    "bang-mau": ("kem", "bao-cu", "dem", "tuoi"),
    "chuyen-canh": ("xen-ke", "xe-giay", "lia", "khong"),
}
# Khoá đầu của kiểu viết tay, không dùng ở Vox.
VOX_CAM = ("ban-tay", "nhan-vat", "mau-ao", "chu-dong", "may-quay")
CHUYEN_CANH = ("xe-giay", "lia", "khong")
THOI_LUONG = (15, 600)
NHIP_TOI_DA = 6
CHU_TOI_DA = 2
CHONG_TOI_DA = 5
NGUON_DAI = 90
# bố cục -> {khổ: các ô}; `None` (không ghi ô) được phép với mọi bố cục.
BO_CUC = {
    "mot": {"ngang": ("giua", "tren", "duoi"), "doc": ("giua", "tren", "duoi")},
    "hai-ben": {"ngang": ("trai", "phai", "giua"), "doc": ("tren", "duoi", "giua")},
    "dan-hang": {"ngang": ("1", "2", "3", "4"), "doc": ("1", "2", "3", "4")},
    "chong": {"ngang": (), "doc": ()},
    "toan-canh": {"ngang": ("nen", "giua", "duoi"), "doc": ("nen", "giua", "duoi")},
}
# vật -> giới hạn ký tự hiện (None: không đếm)
VAT = {"anh": None, "the": None, "chu": 40, "nhan": 30, "dau": 16, "mui-ten": None, "so": 24}
GIOI_HAN_THE = (24, 16, 60)
ANH_MO_TA = 300
TUY_CHON = ("khung", "duotone", "halftone", "xa", "gan")
_SO_RE = re.compile(r"\{\{(-?\d+(?:\.\d+)?)\}\}")
_NHAN_RE = re.compile(r"==|\(\(|\)\)|__")


@dataclass
class Nhip:
    cum: str
    vat: str
    noi_dung: str
    o: str | None
    tuy_chon: tuple
    dong: int
    chi_so: int


def khoa_tu(text: str) -> list:
    """Từ đã chuẩn hoá để so cụm với lời: NFC, chữ thường, bỏ dấu câu (giữ dấu thanh) — như lich.khoa_so_khop."""
    s = unicodedata.normalize("NFC", text).lower()
    return re.sub(r"[^\w\s]", " ", s).split()


def tim_cum(tokens: list, cum: str, tu_vi_tri: int) -> int:
    can = khoa_tu(cum)
    if not can:
        return -1
    for i in range(max(tu_vi_tri, 0), len(tokens) - len(can) + 1):
        if tokens[i:i + len(can)] == can:
            return i
    return -1


def hien(chu: str) -> str:
    """Chữ hiện ra: bỏ dấu nhấn, số chạy hiện bằng con số."""
    return _SO_RE.sub(lambda m: m.group(1).replace(".", ","), _NHAN_RE.sub("", chu))


def _loi(no: int, message: str):
    from .parse import ParseError  # tránh vòng import
    return ParseError(no, message)


def doc_nhip(value: str, no: int, chi_so: int) -> Nhip:
    phan = [p.strip() for p in value.split(" | ")]
    if len(phan) < 2 or not phan[0]:
        raise _loi(no, "`nhip` phải có dạng `<cụm từ trong lời> | <vật>: <nội dung> | <ô> | <tuỳ chọn>`, "
                       "ví dụ `nhip: để mai tính | anh: ve: nhân viên nhún vai | trai`.")
    cum, vat_noi = phan[0], phan[1]
    m = re.match(r"^([a-z-]+):\s*(.*)$", vat_noi)
    if m is None or m.group(1) not in VAT:
        raise _loi(no, f"Vật của nhịp phải là một trong: {', '.join(VAT)} (dạng `vat: nội dung`).")
    vat, noi_dung = m.group(1), m.group(2).strip()
    # Với `the`, chính nội dung chứa " | ": gộp lại 3 phần sau vật.
    du = phan[2:]
    if vat == "the":
        the = [noi_dung] + du
        cat = 3 if len(the) >= 3 and the[2] not in TUY_CHON and not _la_o(the[2]) else 2
        noi_dung, du = " | ".join(the[:cat]), the[cat:]
    o = du[0] if du and du[0] and not set(du[0].split()) <= set(TUY_CHON) else None
    tuy = tuple((du[1] if o is not None and len(du) > 1 else (du[0] if o is None and du else "")).split())
    for t in tuy:
        if t not in TUY_CHON:
            raise _loi(no, f"Tuỳ chọn `{t}` không có; tuỳ chọn của nhịp: {', '.join(TUY_CHON)}.")
    _kiem_noi_dung(vat, noi_dung, no)
    return Nhip(cum=cum, vat=vat, noi_dung=noi_dung, o=o, tuy_chon=tuy, dong=no, chi_so=chi_so)


def _la_o(chu: str) -> bool:
    return any(chu in o for b in BO_CUC.values() for o in b.values())


def _kiem_noi_dung(vat: str, nd: str, no: int) -> None:
    if not nd:
        raise _loi(no, f"Nhịp `{vat}` chưa có nội dung.")
    if vat == "anh":
        if nd.startswith("ve:"):
            mo_ta = nd[3:].strip()
            if not mo_ta or len(mo_ta) > ANH_MO_TA:
                raise _loi(no, f"`anh: ve:` cần mô tả từ 1 đến {ANH_MO_TA} ký tự.")
        elif nd.startswith("tim:"):
            if not nd[4:].strip():
                raise _loi(no, "`anh: tim:` cần từ khoá tiếng Anh để tìm ảnh thật.")
        elif not nd.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            raise _loi(no, "`anh` là `ve: <mô tả>`, `tim: <từ khoá tiếng Anh>` hoặc tên file ảnh trong `anh/`.")
        return
    if vat == "the":
        p = [x.strip() for x in nd.split(" | ")]
        if len(p) not in (2, 3) or not p[0] or not p[1]:
            raise _loi(no, "`the` phải có dạng `<nhãn> | <giá trị> | <chú thích>` (chú thích bỏ trống được).")
        for chu, toi_da, ten in zip(p, GIOI_HAN_THE, ("nhãn", "giá trị", "chú thích")):
            if len(hien(chu)) > toi_da:
                raise _loi(no, f"{ten} của `the` dài {len(hien(chu))} ký tự, tối đa {toi_da}.")
        return
    if vat == "mui-ten":
        if not re.match(r"^\S+\s*->\s*\S+$", nd):
            raise _loi(no, "`mui-ten` phải có dạng `<ô> -> <ô>`, ví dụ `trai -> phai`.")
        return
    if vat == "so" and not _SO_RE.search(nd):
        raise _loi(no, "`so` cần một số chạy `{{…}}`, ví dụ `{{85}}% người được hỏi`.")
    toi_da = VAT[vat]
    if toi_da is not None and len(hien(nd)) > toi_da:
        raise _loi(no, f"Chữ của `{vat}` dài {len(hien(nd))} ký tự, tối đa {toi_da}. Rút gọn chữ; ý dài để ở lời.")


def kiem_canh(scene, kho: str) -> None:
    """Kiểm nhịp của một cảnh Vox đã đọc (bố cục, ô, cụm từ, thứ tự). Raise ParseError."""
    bo_cuc = scene.truong["bo-cuc"][0]
    no_bc = scene.dong_truong["bo-cuc"][0]
    if bo_cuc not in BO_CUC:
        raise _loi(no_bc, f"`bo-cuc` phải là một trong: {', '.join(BO_CUC)}.")
    o_hop_le = BO_CUC[bo_cuc][kho]
    tokens = khoa_tu(scene.loi)
    vi_tri = 0
    so_chu = 0
    for n in scene.nhip:
        if n.o is not None:
            if bo_cuc == "chong":
                raise _loi(n.dong, "Bố cục `chong` tự xếp các vật; bỏ ô ở nhịp này.")
            if n.o not in o_hop_le:
                raise _loi(n.dong, f"Ô `{n.o}` không có ở bố cục `{bo_cuc}` khổ {kho}; ô đúng: {', '.join(o_hop_le)}.")
        if n.o == "nen" and n.vat != "anh":
            raise _loi(n.dong, "Ô `nen` chỉ dành cho ảnh phủ kín khung (`anh`).")
        if n.vat == "chu":
            so_chu += 1
            if so_chu > CHU_TOI_DA:
                raise _loi(n.dong, f"Mỗi cảnh tối đa {CHU_TOI_DA} dòng `chu`; ý còn lại để ở lời hoặc tách cảnh.")
        if n.cum == "@dau":
            continue
        i = tim_cum(tokens, n.cum, vi_tri)
        if i < 0:
            co_truoc = tim_cum(tokens, n.cum, 0) >= 0
            if co_truoc:
                raise _loi(n.dong, f"Cụm \"{n.cum}\" nằm trước cụm của nhịp trước trong lời; viết các nhịp theo đúng "
                                   "thứ tự lời đọc.")
            raise _loi(n.dong, f"Cụm \"{n.cum}\" không có trong lời của Cảnh {scene.so}: \"{scene.loi}\". "
                               "Chép đúng vài từ liền nhau trong lời.")
        vi_tri = i + len(khoa_tu(n.cum))
    if bo_cuc == "chong" and len(scene.nhip) > CHONG_TOI_DA:
        raise _loi(scene.nhip[CHONG_TOI_DA].dong, f"Bố cục `chong` tối đa {CHONG_TOI_DA} vật.")
```

Ghi chú cho người làm: nhịp sau dùng cùng cụm thì `vi_tri` đã nằm sau lần trước nên `tim_cum` tìm lần sau. Câu "thứ tự" trong thông báo khớp test `test_beats_follow_the_narration_order`. Trong `doc_nhip`, cách tách ô và tuỳ chọn: phần thứ 3 là ô nếu nó không chỉ gồm từ tuỳ chọn; phần thứ 4 là tuỳ chọn. Viết lại cho gọn nếu cần, nhưng giữ đúng các test.

- [ ] **Step 4: Rẽ nhánh trong `parse.py`**

1. `META_CHOICES["phong-cach"] = ("viet-tay", "cat-dan", "vox")`.
2. `META_FREE` thêm `"thoi-luong"`; thêm import `from . import vox` ở đầu file sau các import chuẩn, và `from .vox import VOX_META_CHOICES`.
3. Trong `_read_meta`:
   - khoá hợp lệ thêm `VOX_META_CHOICES`;
   - với khoá thuộc `VOX_META_CHOICES` mà phong cách (đọc sau vòng lặp) khác `vox`: lỗi ``f"`{key}` chỉ dùng với `phong-cach: vox`."``;
   - `chuyen-canh` khi `vox`: kiểm theo `VOX_META_CHOICES["chuyen-canh"]` thay cho `META_CHOICES` (kiểm giá trị sau vòng lặp, khi đã biết phong cách; giá trị `chuyen-canh` của kiểu cũ vẫn kiểm như cũ);
   - khoá trong `vox.VOX_CAM` có mặt khi `vox`: lỗi ``f"`{key}` là khoá của kiểu viết tay, không dùng với `phong-cach: vox`; bỏ dòng này."``;
   - `thoi-luong`: phải là số nguyên trong `vox.THOI_LUONG`, nếu không lỗi ``"`thoi-luong` là số giây của video, số nguyên từ 15 đến 600, ví dụ `thoi-luong: 60`."``;
   - khoá bắt buộc: `("tieu-de",)` khi `vox`, `META_REQUIRED` cho kiểu khác;
   - khi `vox`, `setdefault` giá trị đầu của mỗi khoá trong `VOX_META_CHOICES` (kể cả `chuyen-canh: xen-ke`), và không `setdefault` các khoá trong `VOX_CAM` (bỏ chúng khỏi `meta` sau vòng `META_DEFAULTS`).
4. `Scene` thêm trường `nhip: list | None = None` (cuối dataclass).
5. `_finish(so, dong0, fields)` nhận thêm tham số `vox_kho: str | None` (None với kiểu cũ). Khi `vox_kho`:
   - `loai` có mặt: lỗi ``"Cảnh Vox không có `loai`; tả cảnh bằng `bo-cuc` và các dòng `nhip`."``;
   - khoá cho phép: `{"loi", "bo-cuc", "nhip", "chuyen", "nguon"}`; khoá khác: ``f"Cảnh Vox không có trường `{key}`."``;
   - `loi`, `bo-cuc` bắt buộc, không lặp; `nhip` 1–`vox.NHIP_TOI_DA` dòng; `chuyen` ∈ `vox.CHUYEN_CANH`, không ở Cảnh 1; `nguon` ≤ `vox.NGUON_DAI` ký tự;
   - `nhip = [vox.doc_nhip(v, no, k) for k, (v, no) in enumerate(zip(truong["nhip"], dong_truong["nhip"]))]`;
   - trả `Scene(so, dong0, "vox", loi, truong, dong_truong, nhip=nhip)` rồi gọi `vox.kiem_canh(scene, vox_kho)`.
6. Trong `parse`: `vox_kho = meta["kho"] if meta["phong-cach"] == "vox" else None`, truyền vào cả hai chỗ gọi `_finish`. Bỏ qua kiểm `tu-the`/`vi-tri` và `giai_nen` cho cảnh `vox` (chúng không có các trường này nên vòng cũ không chạm; giữ nguyên).

- [ ] **Step 5: Chạy test**

Run: `cd tools/vi; ..\..\venv\Scripts\python.exe -m unittest tests.test_video_ma_vox_parse tests.test_video_ma_parse`
Expected: PASS hết. Nếu test của `test_video_ma_parse` liệt kê đúng `META_CHOICES["phong-cach"]` thì cập nhật kỳ vọng thêm `vox`.

- [ ] **Step 6: Commit**

```bash
git add tools/vi/video_ma_parts/vox.py tools/vi/video_ma_parts/parse.py tools/vi/tests/test_video_ma_vox_parse.py
git commit -F <file>   # feat(vi): read Vox scenes with narration-anchored beats
```

---

### Task 2: Kiểm thời lượng (`thoi-luong`)

**Files:**
- Create: `tools/vi/video_ma_parts/thoi_luong.py`
- Modify: `tools/vi/video_ma.py` (`chay`, `_dung`)
- Test: `tools/vi/tests/test_video_ma_thoi_luong.py`

**Interfaces:**
- Consumes: `parse.Video`, `lich.CanhLich.thoi_luong`.
- Produces: `thoi_luong.uoc_tinh(video) -> float`; `thoi_luong.canh_bao(muc_tieu: int, giay: float, toc_do: str, uoc: bool) -> str | None`; `thoi_luong.dem_tu(text) -> int`; hằng `TOC_DO = {"cham": 2.4, "vua": 2.7, "nhanh": 3.1}`, `MOI_CANH = 1.1`, `VUOT = 0.15`, `THIEU = 0.25`.

- [ ] **Step 1: Viết test hỏng**

```python
# tools/vi/tests/test_video_ma_thoi_luong.py
"""Ước tính và cảnh báo thời lượng so với `thoi-luong`."""
import json, subprocess, sys, tempfile, unittest
from pathlib import Path

TOOLS_VI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_VI))
from video_ma_parts import parse, thoi_luong  # noqa: E402


def video(so_canh: int, so_tu: int, them: str = "") -> parse.Video:
    loi = " ".join(["từ"] * (so_tu - 1)) + " cuối."
    canh = "".join(f"## Cảnh {k}\nbo-cuc: mot\nloi: {loi}\nnhip: @dau | chu: A\n\n" for k in range(1, so_canh + 1))
    return parse.parse(f"---\ntieu-de: T\nphong-cach: vox\n{them}---\n\n{canh}")


class UocTinhTest(unittest.TestCase):
    def test_word_count_ignores_markup(self):
        self.assertEqual(thoi_luong.dem_tu("Tiền ==nhiều== lên {{85}} lần, ((rất)) __nhanh__."), 7)

    def test_estimate_matches_the_measured_video(self):
        # Số đo spec mục 7: 9 cảnh, 288 từ → video 115 giây.
        v = video(9, 32)
        self.assertAlmostEqual(thoi_luong.uoc_tinh(v), 288 / 2.7 + 9 * 1.1, places=3)

    def test_speed_changes_the_estimate(self):
        nhanh = video(2, 54, "toc-do: nhanh\n")
        self.assertAlmostEqual(thoi_luong.uoc_tinh(nhanh), 108 / 3.1 + 2.2, places=3)


class CanhBaoTest(unittest.TestCase):
    def test_within_band_is_silent(self):
        self.assertIsNone(thoi_luong.canh_bao(60, 66.0, "vua", True))
        self.assertIsNone(thoi_luong.canh_bao(60, 46.0, "vua", True))

    def test_too_long_names_words_to_cut(self):
        w = thoi_luong.canh_bao(60, 115.0, "vua", True)
        self.assertIn("115", w)
        self.assertIn("60", w)
        self.assertIn("bớt khoảng 150 từ", w)   # (115-60)*2.7 = 148.5 → làm tròn chục: 150

    def test_too_short_names_words_to_add(self):
        w = thoi_luong.canh_bao(60, 40.0, "vua", False)
        self.assertIn("thêm khoảng 50 từ", w)   # 20*2.7 = 54 → 50

    def test_measured_vs_estimated_wording(self):
        self.assertIn("ước", thoi_luong.canh_bao(60, 115.0, "vua", True))
        self.assertIn("dài", thoi_luong.canh_bao(60, 115.0, "vua", False))


class CliTest(unittest.TestCase):
    def test_plan_only_reports_the_estimate(self):
        with tempfile.TemporaryDirectory() as tmp:
            loi = " ".join(["từ"] * 99) + " cuối."
            canh = "".join(f"## Cảnh {k}\nbo-cuc: mot\nloi: {loi}\nnhip: @dau | chu: A\n\n" for k in (1, 2, 3))
            (Path(tmp) / "video.md").write_text(f"---\ntieu-de: T\nphong-cach: vox\nthoi-luong: 60\n---\n\n{canh}",
                                                encoding="utf-8")
            r = subprocess.run([sys.executable, str(TOOLS_VI / "video_ma.py"), tmp, "--plan-only"],
                               capture_output=True, text=True, encoding="utf-8")
            out = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertTrue(out["ready"])
        self.assertTrue(any("bớt khoảng" in w for w in out["warnings"]), out["warnings"])
        self.assertAlmostEqual(out["thoi_luong_uoc"], round(300 / 2.7 + 3.3, 1))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Chạy test, xác nhận hỏng** — `ImportError: thoi_luong`.

- [ ] **Step 3: Viết `thoi_luong.py`**

```python
# tools/vi/video_ma_parts/thoi_luong.py
"""Ước tính thời lượng video từ số từ của lời, và cảnh báo khi lệch `thoi-luong` (spec Vox mục 7)."""

from __future__ import annotations

import re

# Từ/giây của giọng edge-tts tiếng Việt; đo trên video 9 cảnh, 288 từ (105 giây tiếng) ở tốc độ vừa.
TOC_DO = {"cham": 2.4, "vua": 2.7, "nhanh": 3.1}
# Đoạn dẫn đầu (lich.DAN_DAU 1,0 s) và đuôi mỗi cảnh, trung bình đo được.
MOI_CANH = 1.1
VUOT, THIEU = 0.15, 0.25
_DAU = re.compile(r"==|\(\(|\)\)|__|\{\{|\}\}")


def dem_tu(text: str) -> int:
    return len(re.sub(r"[^\w\s]", " ", _DAU.sub("", text)).split())


def uoc_tinh(video) -> float:
    toc = TOC_DO[video.meta["toc-do"]]
    tu = sum(dem_tu(c.loi) + sum(dem_tu(x) for x in c.truong.get("loi-giai", [])) for c in video.canh)
    cho = sum(int(c.truong.get("cho", ["5"])[0]) + 0.4 for c in video.canh if c.loai == "cau-hoi")
    return tu / toc + MOI_CANH * len(video.canh) + cho


def _chuc(x: float) -> int:
    return max(10, int(round(x / 10.0)) * 10)


def canh_bao(muc_tieu: int, giay: float, toc_do: str, uoc: bool) -> str | None:
    if muc_tieu * (1 - THIEU) <= giay <= muc_tieu * (1 + VUOT):
        return None
    dong_tu = f"ước {giay:.0f} giây" if uoc else f"dài {giay:.0f} giây"
    so_tu = _chuc(abs(giay - muc_tieu) * TOC_DO[toc_do])
    viec = f"bớt khoảng {so_tu} từ lời" if giay > muc_tieu else f"thêm khoảng {so_tu} từ lời"
    return (f"Video {dong_tu}, mục tiêu `thoi-luong: {muc_tieu}` giây: {viec} (hoặc bớt/thêm cảnh) "
            "rồi chạy lại trước khi dựng thật.")
```

- [ ] **Step 4: Nối vào `video_ma.py`**

- `chay`: sau `canh_bao_hinh_khop_loi`, tính `uoc = thoi_luong.uoc_tinh(video)`; nếu `"thoi-luong" in video.meta`, thêm `thoi_luong.canh_bao(int(video.meta["thoi-luong"]), uoc, video.meta["toc-do"], True)` vào `warnings` nếu khác None. Kết quả `--plan-only` thêm khoá `"thoi_luong_uoc": round(uoc, 1)`; `base` trong `main` thêm `"thoi_luong_uoc": None`.
- `_dung`: sau `lich.dung_lich`, nếu có `thoi-luong`, tính lại với `sum(cl.thoi_luong for cl in cac_lich)` và `uoc=False`; xoá cảnh báo ước tính cũ (giữ một cảnh báo thời lượng duy nhất, cảnh báo đo thật thay cảnh báo ước).
- Import `thoi_luong` cùng dòng import `video_ma_parts`.
- `kiem.kiem`: ngay sau phần đọc nhạc nền, thêm `if video.meta["phong-cach"] == "vox": return warnings` (các kiểm theo loại cảnh cũ không áp cho cảnh Vox; Task 5 thay dòng này bằng `return warnings + vox.kiem(video, thu_muc)`). Thêm test trong `test_video_ma_thoi_luong.py`: `kiem.kiem(video(2, 10), Path("."))` trả `[]`.

- [ ] **Step 5: Chạy test** — `tests.test_video_ma_thoi_luong tests.test_video_ma_cong_cu` PASS (cập nhật `test_video_ma_cong_cu` nếu nó so khớp đúng tập khoá JSON: thêm `thoi_luong_uoc`).

- [ ] **Step 6: Commit** — `feat(vi): estimate video length and warn against thoi-luong`.

---

### Task 3: `anh_vox.py` — lập danh sách, nguồn vẽ, lưu đệm, nguồn ảnh

**Files:**
- Create: `tools/vi/anh_vox.py`, `tools/vi/anh_vox_parts/__init__.py`, `tools/vi/anh_vox_parts/ke_hoach.py`, `tools/vi/anh_vox_parts/nguon_ve.py`
- Test: `tools/vi/tests/test_anh_vox.py`

**Interfaces:**
- Consumes: `parse.parse`, `vox.Nhip`.
- Produces:
  - `ke_hoach.ma_anh(prompt, kich_thuoc) -> str`; `ke_hoach.Muc` dataclass `{ma, canh, chi_so, kieu: "cat"|"khung"|"phu", nguon: "ve"|"tim"|"file", prompt|tu_khoa|file, kich_thuoc, tuy_chon}`; `ke_hoach.lap(video) -> list[Muc]`; `ke_hoach.file_goc(thu_muc, muc) -> Path`; `ke_hoach.file_xu_ly(thu_muc, muc) -> Path`; `ke_hoach.hat(muc) -> int`.
  - `nguon_ve.CauHinh(url, khoa, mo_hinh)`; `nguon_ve.doc_cau_hinh(env=os.environ, home=Path.home()) -> CauHinh`; `nguon_ve.ve(cau_hinh, prompt, kich_thuoc, timeout=120, mo=urllib.request.urlopen) -> bytes` (PNG/JPEG bytes); `nguon_ve.VeError(step, message, fix)`.
  - CLI `anh_vox.py <thư mục> [--chi-ke-hoach] [--toi-da N]`, JSON `{ready, files, so_anh, da_ve, dung_lai, ke_hoach, warnings, error}`; `ERROR_STEPS = ("input", "parse", "cau-hinh", "mang", "nha-cung-cap", "tach-nen", "write", "internal")`.

- [ ] **Step 1: Viết test hỏng** (máy chủ HTTP giả lập bằng `http.server` trong luồng; không gọi mạng thật)

```python
# tools/vi/tests/test_anh_vox.py
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

    def do_POST(self):
        than = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        _May.goi.append({"auth": self.headers.get("Authorization"), **than})
        if _May.tra == "loi":
            self.send_response(429)
            self.end_headers()
            self.wfile.write(b'{"error":{"message":"quota exceeded"}}')
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

    def test_steps_are_the_documented_ones(self):
        import anh_vox
        self.assertEqual(anh_vox.ERROR_STEPS, ("input", "parse", "cau-hinh", "mang", "nha-cung-cap", "tach-nen", "write", "internal"))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Chạy test, xác nhận hỏng** — `ModuleNotFoundError: anh_vox_parts`.

- [ ] **Step 3: Viết `ke_hoach.py`**

```python
# tools/vi/anh_vox_parts/ke_hoach.py
"""Danh sách ảnh của video Vox và tên file tất định (video_ma đọc lại cùng tên)."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

DUOI_PHONG = {
    "chup-that": "ảnh chụp thật, ánh sáng tự nhiên, chi tiết sắc nét",
    "minh-hoa": "tranh minh hoạ phẳng, nét gọn, màu tươi",
}
DUOI_CAT = "một vật duy nhất ở giữa, nền xanh lá thuần #00FF00 phẳng, không bóng đổ, không viền"
DUOI_CHUNG = "không có chữ, không có chữ cái, không có logo"
KHO_ANH = {"cat": "1024x1024", ("khung", "ngang"): "1536x1024", ("khung", "doc"): "1024x1536",
           ("phu", "ngang"): "1536x1024", ("phu", "doc"): "1024x1536"}


@dataclass
class Muc:
    ma: str
    canh: int
    chi_so: int
    kieu: str          # cat | khung | phu
    nguon: str         # ve | tim | file
    prompt: str        # ve: câu lệnh đầy đủ; tim: từ khoá; file: tên file
    kich_thuoc: str
    tuy_chon: tuple


def ma_anh(prompt: str, kich_thuoc: str) -> str:
    return hashlib.sha256(f"{prompt}\n{kich_thuoc}".encode("utf-8")).hexdigest()[:16]


def hat(m: Muc) -> int:
    return m.canh * 100 + m.chi_so


def _kieu(n, nguon: str) -> str:
    if n.o == "nen":
        return "phu"
    if nguon != "ve" or "khung" in n.tuy_chon:
        return "khung"   # ảnh thật và ảnh có sẵn luôn là khung (spec 4.6)
    return "cat"


def lap(video) -> list:
    kho = video.meta["kho"]
    ds = []
    for c in video.canh:
        for n in c.nhip or []:
            if n.vat != "anh":
                continue
            nd = n.noi_dung
            nguon = "ve" if nd.startswith("ve:") else ("tim" if nd.startswith("tim:") else "file")
            kieu = _kieu(n, nguon)
            kt = KHO_ANH["cat"] if kieu == "cat" else KHO_ANH[(kieu, kho)]
            if nguon == "ve":
                phan = [nd[3:].strip(), DUOI_PHONG[video.meta["phong-anh"]]]
                if kieu == "cat":
                    phan.append(DUOI_CAT)
                phan.append(DUOI_CHUNG)
                prompt = ", ".join(phan)
            else:
                prompt = nd[4:].strip() if nguon == "tim" else nd
            ma = ma_anh(prompt, kt) if nguon == "ve" else hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:10]
            ds.append(Muc(ma, c.so, n.chi_so, kieu, nguon, prompt, kt, n.tuy_chon))
    return ds


def file_goc(thu_muc: Path, m: Muc) -> Path:
    if m.nguon == "ve":
        return thu_muc / "anh" / "ai" / "goc" / f"{m.ma}.png"
    if m.nguon == "tim":
        return thu_muc / "anh" / f"tim-{m.ma}.jpg"
    return thu_muc / "anh" / m.prompt


def file_xu_ly(thu_muc: Path, m: Muc) -> Path:
    duoi = "".join(f"-{t}" for t in ("duotone", "halftone") if t in m.tuy_chon)
    return thu_muc / "anh" / "ai" / "xu-ly" / f"{m.ma}-{hat(m)}-{m.kieu}{duoi}.png"
```

Ghi chú: test `test_processed_file_names` dùng `Path("x")` nên chỉ so `.name`.

- [ ] **Step 4: Viết `nguon_ve.py`**

```python
# tools/vi/anh_vox_parts/nguon_ve.py
"""Gọi API tạo ảnh kiểu OpenAI (9router mặc định). Khoá không bao giờ đi vào thông báo lỗi."""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

URL_MAC_DINH = "http://localhost:20128/v1"
MO_HINH_MAC_DINH = "ag/gemini-3.1-flash-image"
FIX_KHOA = ("Đặt khoá API của 9router: `setx ANH_AI_KEY \"<khoá>\"` (lấy ở trang quản trị 9router) rồi mở lại cửa sổ "
            "lệnh; hoặc dùng `anh: tim:` (ảnh thật), hoặc thay ảnh bằng `chu`, `the`.")
FIX_MANG = "Kiểm tra 9router đang chạy (`9router` mở ở cổng 20128) hoặc địa chỉ `ANH_AI_URL`, rồi chạy lại."
FIX_NCC = "Đọc thông báo của nhà cung cấp: hết hạn mức thì chờ hoặc đổi `ANH_AI_MO_HINH`; câu lệnh bị từ chối thì sửa mô tả `ve:`."


class VeError(Exception):
    """`thu_lai`: lỗi tạm (mạng, 5xx) — anh_vox thử lại tối đa 2 lần trước khi báo."""

    def __init__(self, step: str, message: str, fix: str, thu_lai: bool = False) -> None:
        super().__init__(message)
        self.step, self.message, self.fix, self.thu_lai = step, message, fix, thu_lai


@dataclass
class CauHinh:
    url: str
    khoa: str | None
    mo_hinh: str


def doc_cau_hinh(env=os.environ, home: Path | None = None) -> CauHinh:
    tep = {}
    f = (home or Path.home()) / ".2anh-studio" / "anh-ai.json"
    if f.is_file():
        try:
            tep = json.loads(f.read_text(encoding="utf-8"))
        except ValueError as exc:
            raise VeError("cau-hinh", f"File cấu hình {f} hỏng: {exc}", "Sửa hoặc xoá file đó rồi chạy lại.") from None
    return CauHinh(url=(env.get("ANH_AI_URL") or tep.get("url") or URL_MAC_DINH).rstrip("/"),
                   khoa=env.get("ANH_AI_KEY") or tep.get("khoa"),
                   mo_hinh=env.get("ANH_AI_MO_HINH") or tep.get("mo_hinh") or MO_HINH_MAC_DINH)


def _an(chu: str, khoa: str | None) -> str:
    return chu.replace(khoa, "***") if khoa else chu


def ve(ch: CauHinh, prompt: str, kich_thuoc: str, timeout: float = 120, mo=urllib.request.urlopen) -> bytes:
    than = json.dumps({"model": ch.mo_hinh, "prompt": prompt, "size": kich_thuoc, "n": 1}).encode("utf-8")
    dau = {"Content-Type": "application/json"}
    if ch.khoa:
        dau["Authorization"] = f"Bearer {ch.khoa}"
    req = urllib.request.Request(f"{ch.url}/images/generations", data=than, headers=dau)
    try:
        with mo(req, timeout=timeout) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as exc:
        chu = exc.read()[:500].decode("utf-8", "replace")
        if exc.code == 401:
            raise VeError("cau-hinh", _an(f"Nguồn vẽ từ chối khoá (401): {chu}", ch.khoa), FIX_KHOA) from None
        raise VeError("nha-cung-cap", _an(f"Nguồn vẽ báo lỗi {exc.code}: {chu}", ch.khoa), FIX_NCC,
                      thu_lai=exc.code >= 500) from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise VeError("mang", _an(f"Không gọi được {ch.url}: {exc}", ch.khoa), FIX_MANG, thu_lai=True) from None
    try:
        muc = data["data"][0]
    except (KeyError, IndexError, TypeError):
        raise VeError("nha-cung-cap", _an(f"Nguồn vẽ không trả ảnh: {str(data)[:300]}", ch.khoa), FIX_NCC) from None
    if muc.get("b64_json"):
        return base64.b64decode(muc["b64_json"])
    if muc.get("url"):
        try:
            with mo(urllib.request.Request(muc["url"]), timeout=timeout) as r:
                return r.read()
        except (urllib.error.URLError, OSError) as exc:
            raise VeError("mang", f"Không tải được ảnh từ địa chỉ nguồn vẽ trả về: {exc}", FIX_MANG) from None
    raise VeError("nha-cung-cap", "Nguồn vẽ trả kết quả không có ảnh.", FIX_NCC)
```

- [ ] **Step 5: Viết `anh_vox.py` (CLI, chưa xử lý ảnh — Task 4 thêm)**

Luồng `chay(thu_muc, chi_ke_hoach, toi_da, warnings) -> dict`:
1. Đọc `video.md` (`parse.parse`); không phải `phong-cach: vox` → lỗi `input` "anh_vox.py chỉ dùng cho video `phong-cach: vox`."
2. `ds = ke_hoach.lap(video)`; ghi `anh/ai/ke-hoach.json` = `{"mo_hinh": ch.mo_hinh, "muc": [asdict(m) + {"file_goc": rel}]}`.
3. `--chi-ke-hoach`: trả `{files: ["anh/ai/ke-hoach.json"], so_anh: len(ds), da_ve: 0, dung_lai: 0, ke_hoach: "anh/ai/ke-hoach.json"}`.
4. Đọc `anh/ai/nguon.json` (list; hỏng thì đổi tên sang `nguon.hong.json` như `anh_ai._ghi_nguon` và coi như rỗng). Một mục `ve` **dùng lại** khi `file_goc` tồn tại và (nguon.json có bản ghi `ma` đó với `mo_hinh == ch.mo_hinh`, hoặc không có bản ghi nào cho `ma` đó — ảnh do nền tảng tự vẽ, ghi bản ghi `cong_cu: "nen-tang"`, `mo_hinh: "không rõ"` và cảnh báo "ảnh <file> do nền tảng vẽ, chưa rõ mô hình").
5. Cần vẽ = mục `ve` không dùng lại được. Quá `toi_da` (mặc định 20) → lỗi `input` "Cần vẽ N ảnh, quá giới hạn M", fix "Bớt nhịp `anh: ve:` hoặc chạy lại với `--toi-da N`.". `ch.khoa` None và URL mặc định → vẫn thử (9router có thể không cần khoá); 401 → `cau-hinh`.
6. Vẽ song song tối đa 3 (`concurrent.futures.ThreadPoolExecutor(3)`), mỗi ảnh thử tối đa 3 lần khi `VeError.thu_lai`; lỗi khác dừng ngay. Thêm test với máy chủ giả trả 503 hai lần rồi 200: ảnh vẫn ra, máy chủ nhận 3 lần gọi. Ghi `goc/<ma>.png` (nếu nhận JPEG/WebP thì đổi sang PNG bằng Pillow). In tiến độ ra stderr: "Vẽ ảnh k/N (cảnh c)...".
7. Ghi `nguon.json` nguyên tử (temp + `os.replace`): mỗi ảnh vẽ thêm/ghi đè bản ghi `{file: "ai/goc/<ma>.png", cong_cu: "api", mo_hinh, prompt, ngay: date.today().isoformat(), ma}`.
8. Trả `{files: [...các file goc...], so_anh: len(ds), da_ve, dung_lai, ke_hoach: "anh/ai/ke-hoach.json"}`.

`main` giống `anh_ai.py`: một dòng JSON, `base = {ready, files, so_anh, da_ve, dung_lai, ke_hoach, warnings, error}`, bắt `parse.ParseError` → `parse`, `VeError` → `step` của nó, `OSError` → `write`, khác → `internal`.

- [ ] **Step 6: Chạy test** — `tests.test_anh_vox` PASS.

- [ ] **Step 7: Commit** — `feat(vi): anh_vox draws Vox images through an OpenAI-style API`.

---

### Task 4: `anh_vox.py` — ảnh thật, tách nền, viền xé, khung, duotone/halftone

**Files:**
- Create: `tools/vi/anh_vox_parts/xu_ly.py`
- Modify: `tools/vi/anh_vox.py` (gọi tìm ảnh thật và xử lý sau bước vẽ)
- Test: `tools/vi/tests/test_anh_vox_xu_ly.py`

**Interfaces:**
- Consumes: `ke_hoach.Muc`, `ke_hoach.file_goc/file_xu_ly/hat`; `anh_ai_parts.xu_ly.LOC_TACH` (chuỗi bộ lọc FFmpeg đang dùng).
- Produces: `xu_ly.tach_nen(goc: Path, run=subprocess.run) -> PIL.Image (RGBA)`; `xu_ly.alpha_sach(im) -> bool`; `xu_ly.cat_phu(im, ti_le: float) -> Image`; `xu_ly.vien_xe(im_rgba, hat: int) -> Image` (cắt nền + viền giấy + bóng); `xu_ly.khung_xe(im_rgb, hat: int) -> Image`; `xu_ly.duotone(im, mau_toi, mau_sang) -> Image`; `xu_ly.halftone(im, buoc=8) -> Image`; `xu_ly.xu_ly_muc(thu_muc, muc, run=subprocess.run) -> list[str]` (cảnh báo).

- [ ] **Step 1: Viết test hỏng**

```python
# tools/vi/tests/test_anh_vox_xu_ly.py
"""Xử lý ảnh Vox: tách nền xanh, viền xé, khung xé, cắt phủ, in chấm. Cần FFmpeg cho tách nền."""
import shutil, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image  # noqa: E402
from anh_vox_parts import xu_ly  # noqa: E402

CO_FFMPEG = shutil.which("ffmpeg") is not None


def vat_tren_nen(mau_nen=(0, 255, 0), w=200, h=200) -> Image.Image:
    im = Image.new("RGB", (w, h), mau_nen)
    for x in range(60, 140):
        for y in range(50, 160):
            im.putpixel((x, y), (180, 70, 40))
    return im


class CatPhuTest(unittest.TestCase):
    def test_cover_crop_keeps_the_ratio(self):
        im = xu_ly.cat_phu(Image.new("RGB", (1024, 1024)), 1.5)
        self.assertAlmostEqual(im.width / im.height, 1.5, places=2)
        im = xu_ly.cat_phu(Image.new("RGB", (1536, 1024)), 1 / 1.5)
        self.assertAlmostEqual(im.width / im.height, 1 / 1.5, places=2)


@unittest.skipUnless(CO_FFMPEG, "cần FFmpeg")
class TachNenTest(unittest.TestCase):
    def test_pure_green_is_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "g.png"
            vat_tren_nen().save(p)
            im = xu_ly.tach_nen(p)
        self.assertEqual(im.mode, "RGBA")
        self.assertEqual(im.getpixel((5, 5))[3], 0)
        self.assertEqual(im.getpixel((100, 100))[3], 255)
        self.assertTrue(xu_ly.alpha_sach(im))

    def test_not_green_background_is_not_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "g.png"
            vat_tren_nen((240, 240, 240)).save(p)
            im = xu_ly.tach_nen(p)
        self.assertFalse(xu_ly.alpha_sach(im))


class VienXeTest(unittest.TestCase):
    def setUp(self):
        self.vat = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
        for x in range(60, 140):
            for y in range(50, 160):
                self.vat.putpixel((x, y), (180, 70, 40, 255))

    def test_rim_is_paper_coloured_around_the_object_and_deterministic(self):
        a = xu_ly.vien_xe(self.vat, 101)
        b = xu_ly.vien_xe(self.vat, 101)
        self.assertEqual(a.tobytes(), b.tobytes())
        self.assertNotEqual(a.tobytes(), xu_ly.vien_xe(self.vat, 102).tobytes())
        # Có lề trong suốt để bóng đổ không bị cắt, viền giấy sáng ngay ngoài vật.
        self.assertGreater(a.width, self.vat.width)
        lech = (a.width - self.vat.width) // 2
        r, g, bl, al = a.getpixel((lech + 55, lech + 100))
        self.assertGreater(min(r, g, bl), 200)
        self.assertEqual(al, 255)

    def test_frame_has_torn_edges(self):
        k = xu_ly.khung_xe(Image.new("RGB", (300, 200), (90, 120, 160)), 7)
        self.assertEqual(k.mode, "RGBA")
        canh = [k.getpixel((x, 2))[3] for x in range(20, k.width - 20, 3)]
        self.assertIn(0, canh)
        self.assertIn(255, [k.getpixel((x, k.height // 2))[3] for x in range(20, k.width - 20, 3)])


class InTest(unittest.TestCase):
    def test_duotone_uses_two_colours(self):
        im = xu_ly.duotone(Image.linear_gradient("L").convert("RGB"), (30, 40, 90), (240, 220, 180))
        self.assertEqual(im.getpixel((0, 0))[:3], (30, 40, 90))
        self.assertEqual(im.getpixel((0, 255))[:3], (240, 220, 180))

    def test_halftone_makes_dots(self):
        im = xu_ly.halftone(Image.new("RGB", (64, 64), (128, 128, 128)), buoc=8)
        mau = {im.getpixel((x, y))[:3] for x in range(64) for y in range(64)}
        self.assertLessEqual(len(mau), 6)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Chạy test, xác nhận hỏng.**

- [ ] **Step 3: Viết `xu_ly.py`**

Cài đặt (Pillow + numpy):
- `tach_nen`: chạy `ffmpeg -v error -y -i <goc> -vf "<anh_ai_parts.xu_ly.LOC_TACH>" <tmp>.png`, mở RGBA. Sau đó gỡ quầng xanh: điểm có alpha < 255 và G > max(R,B)+20 thì đặt G = max(R,B).
- `alpha_sach(im)`: 4 vùng góc 16×16 có alpha trung bình < 10 **và** tỉ lệ điểm alpha=255 nằm trong 5–90% diện tích.
- `cat_phu(im, ti_le)`: cắt giữa về tỉ lệ `ti_le` (rộng/cao), không phóng.
- `vien_xe(rgba, hat)`:
  1. `m = alpha > 128`; giãn `m` bán kính `r = max(8, round(0.035 * max(w, h)))` (numpy, đĩa tròn qua `scipy`-free: lặp `np.maximum` các bản dịch trong đĩa).
  2. Mép răng cưa: nhiễu giá trị 1D theo góc quanh tâm vật, `random.Random(hat)`, 64 mốc nội suy tuyến tính, biên độ ±0,45 r; giữ điểm của vùng giãn có khoảng cách tới mép `m` ≤ r·(1 + nhiễu(góc)).
  3. Tô vùng viền màu giấy `(247, 242, 230)` với thớ: cộng nhiễu ±6 theo `Random(hat+1)`.
  4. Đặt vật lên trên viền, thêm lề trong suốt `pad = 2r`, bóng đổ: alpha của (viền ∪ vật) làm mờ Gauss bán kính `r` (Pillow `ImageFilter.GaussianBlur`), độ đục 0,35, lệch (r/2, r) xuống dưới phải, đặt dưới cùng.
- `khung_xe(rgb, hat)`: RGBA cùng kích thước + lề 2%; hai cạnh do `Random(hat)` chọn (luôn có cạnh trên hoặc dưới) có mép răng cưa (polygon răng cưa bước 6–14 px, sâu 3–9 px), hai cạnh còn lại thẳng; viền giấy trắng 1,5% quanh ảnh; bóng như trên.
- `duotone(im, toi, sang)`: chuyển L, nội suy tuyến tính giữa hai màu theo độ sáng.
- `halftone(im, buoc=8)`: lưới chấm tròn đen trên nền sáng (màu giấy), bán kính tỉ lệ độ tối trung bình ô; tối đa vài màu (đen, giấy, khử răng cưa nhẹ bằng supersample 2× rồi thu nhỏ → test cho phép ≤ 6 màu; nếu khử răng cưa sinh nhiều màu hơn thì lượng tử về 4 mức).
- `xu_ly_muc(thu_muc, muc, run)`:
  - `cat`: `tach_nen(goc)`; không sạch → cảnh báo "Cảnh c, nhịp k: ảnh tách nền không sạch, đã chuyển sang `khung`." và xử lý như `khung` (không vẽ lại ở đây — bước vẽ lại một lần nằm trong `anh_vox.chay`, xem Step 4); sạch → `vien_xe`.
  - `khung`: `cat_phu(goc, 1.5 hoặc 1/1.5 theo khổ)` → `khung_xe`.
  - `phu`: `cat_phu(goc, rong/cao của khổ)` lưu thẳng (không viền).
  - Sau đó `duotone` (màu theo `bang-mau`, bảng `MAU_DUOTONE = {"kem": ((38,52,94),(244,236,214)), "bao-cu": ((60,48,40),(236,226,204)), "dem": ((16,22,40),(120,180,220)), "tuoi": ((120,30,60),(255,214,120))}`) và/hoặc `halftone` nếu có tuỳ chọn, giữ alpha.
  - Thu nhỏ để cạnh dài ≤ 1400 px, lưu PNG vào `ke_hoach.file_xu_ly`.

- [ ] **Step 4: Nối vào `anh_vox.chay`**

- Sau bước vẽ: với mục `tim`, chạy `venv`-Python hiện tại `sys.executable skills/ppt-master/scripts/image_search.py "<từ khoá>" --filename tim-<ma>.jpg --orientation landscape|portrait -o <thu_muc>/anh` (đường dẫn script tính từ `Path(__file__).resolve().parents[2]`), bỏ qua nếu file đã có; lỗi (mã khác 0 hoặc không ra file) → `VeError("mang", "Không tìm được ảnh thật cho \"<từ khoá>\" (cảnh c).", "Đổi từ khoá `tim:` (tiếng Anh, cụ thể hơn) hoặc dùng `anh: ve:`.")`.
- Xử lý mọi mục bằng `xu_ly.xu_ly_muc`; mục `cat` tách không sạch và nguồn `ve` (do API vẽ) → vẽ lại đúng một lần với câu lệnh thêm "nền xanh lá #00FF00 tuyệt đối đồng màu, không gradient, không bóng" (mã băm theo câu lệnh mới, ghi `nguon.json` cho file mới), xử lý lại; vẫn không sạch → chuyển `khung` kèm cảnh báo. Ghi nhớ: file xử lý chọn theo `kieu` cuối cùng, nên `anh/ai/xu-ly/` chứa đúng tên mà Task 5 đọc; để Task 5 biết kiểu cuối, ghi `anh/ai/vox.json` = `{"<canh>-<chi_so>": {"file": "ai/xu-ly/<…>.png", "kieu": "cat|khung|phu", "ma": "<ma>", "mo_hinh": "<mô hình hoặc null>", "nguon": "<dòng nguồn ảnh thật hoặc null>"}}`. Đây là bảng duy nhất video_ma đọc.
- Ảnh thật: `nguon` lấy từ `anh/image_sources.json` theo tên file (cùng cách `anh._nguon_tu_manifest` đang làm); không có nguồn → lỗi `nha-cung-cap` "Ảnh thật chưa có nguồn".
- Trả thêm `"files"` gồm `anh/ai/vox.json` và các file xử lý.

Test bổ sung trong `tests/test_anh_vox.py` (`CliTest`), dùng máy chủ giả trả ảnh `png_xanh(256,256)`:

```python
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
```

(Bỏ qua khi không có FFmpeg: `@unittest.skipUnless(shutil.which("ffmpeg"), "cần FFmpeg")`.)

- [ ] **Step 5: Chạy test** — `tests.test_anh_vox_xu_ly tests.test_anh_vox` PASS.

- [ ] **Step 6: Commit** — `feat(vi): process Vox images into torn-paper cutouts and frames`.

---

### Task 5: Dữ liệu cảnh Vox, mốc nhịp, tài nguyên, chủ đề và phụ đề

**Files:**
- Modify: `tools/vi/video_ma_parts/vox.py` (thêm `du_lieu_canh`, `moc_nhip`, `tai_nguyen`, `kiem`), `tools/vi/video_ma_parts/lich.py` (`du_lieu_canh` rẽ nhánh, `mac_dinh`, `kieu_chuyen`), `tools/vi/video_ma_parts/phong.py` (`CHU_DE["vox"]`, `font_css`), `tools/vi/video_ma_parts/karaoke.py` (`kieu_phu_de`: hộp nền như `cat-dan`), `tools/vi/video_ma_parts/kiem.py` (`kiem`: rẽ sang `vox.kiem`), `tools/vi/video_ma.py` (`_tai_nguyen`, `_cac_du` ghi công AI)
- Test: `tools/vi/tests/test_video_ma_vox_du_lieu.py`

**Interfaces:**
- Consumes: `vox.Nhip`, `lich.CanhLich.moc_tu` (`[{t, d, chu, khoa}]`, `t` đã cộng `DAN_DAU`), bảng `anh/ai/vox.json` (Task 4), `anh.doc` (đọc ảnh thành dataUrl).
- Produces: `vox.moc_nhip(nhips, moc_tu, dan_dau) -> list[float]`; `vox.tai_nguyen(scene, thu_muc) -> dict` → `{"anh": {chi_so: {dataUrl, rong, cao, kieu, nguon, moHinh}}}`; `vox.du_lieu_canh(scene, cl, tai_nguyen, meta) -> dict` (dạng ở "Hợp đồng dùng chung"); `vox.kiem(video, thu_muc) -> list[str]` (raise `kiem.CanhError` khi thiếu ảnh); `vox.CHUYEN_XEN_KE = ("xe-giay", "lia")`.

- [ ] **Step 1: Viết test hỏng**

```python
# tools/vi/tests/test_video_ma_vox_du_lieu.py
"""Dữ liệu trang của cảnh Vox: mốc nhịp theo mốc từ, ô tự chọn, chuyển cảnh xen kẽ, ảnh từ vox.json."""
import base64, io, json, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from video_ma_parts import kiem, lich, parse, phong, vox  # noqa: E402


def moc(loi: str, buoc=0.4):
    return [{"t": lich.DAN_DAU + i * buoc, "d": buoc, "chu": w, "khoa": lich.khoa_so_khop(w)}
            for i, w in enumerate(loi.split())]


VID = ("---\ntieu-de: T\nphong-cach: vox\n---\n\n"
       "## Cảnh 1\nbo-cuc: hai-ben\nloi: Tiền nhiều, tiền ít, rồi hết.\n"
       "nhip: @dau | nhan: Tiền | giua\nnhip: tiền | chu: Nhiều\nnhip: tiền ít | chu: Ít\n\n"
       "## Cảnh 2\nbo-cuc: mot\nloi: Hai.\nnhip: @dau | dau: XONG\n\n"
       "## Cảnh 3\nbo-cuc: mot\nloi: Ba.\nnhip: @dau | so: {{85.5}}% người\n")


class MocTest(unittest.TestCase):
    def test_beat_times_follow_the_words(self):
        v = parse.parse(VID)
        c = v.canh[0]
        t = vox.moc_nhip(c.nhip, moc(c.loi), lich.DAN_DAU)
        self.assertEqual(t, [lich.DAN_DAU, lich.DAN_DAU + 0.0, lich.DAN_DAU + 0.8])

    def test_unmatched_estimated_word_falls_back_to_order(self):
        c = parse.parse(VID).canh[0]
        t = vox.moc_nhip(c.nhip, [], lich.DAN_DAU)   # chưa có mốc từ: rải đều theo vị trí từ trong lời
        self.assertEqual(len(t), 3)
        self.assertTrue(t[0] <= t[1] <= t[2])


class DuLieuTest(unittest.TestCase):
    def du(self, k=0, meta_them=""):
        v = parse.parse(VID.replace("phong-cach: vox\n", "phong-cach: vox\n" + meta_them))
        plan, _ = lich.dung_lich(v.canh, [lich.GiongInfo(None, 3.0, [0.0], False, "may", moc_tu=moc(c.loi)) for c in v.canh])
        return [vox.du_lieu_canh(c, cl, {"anh": {}}, v.meta) for c, cl in zip(v.canh, plan)][k], v

    def test_shape(self):
        du, _ = self.du()
        self.assertEqual(du["loai"], "vox")
        self.assertEqual(du["boCuc"], "hai-ben")
        self.assertEqual([n["o"] for n in du["nhip"]], ["giua", "trai", "phai"])   # ô trống kế tiếp theo thứ tự ô
        self.assertEqual(du["chuDe"]["ten"], "vox")
        self.assertIsNone(du["co"]["chuyen"])

    def test_counter_and_text(self):
        du, _ = self.du(2)
        self.assertEqual(du["nhip"][0]["so"], {"giaTri": 85.5, "truoc": "", "sau": "% người", "thapPhan": 1})

    def test_transitions_alternate(self):
        self.assertEqual(self.du(1)[0]["co"]["chuyen"], "xe-giay")
        self.assertEqual(self.du(2)[0]["co"]["chuyen"], "lia")
        self.assertEqual(self.du(2, "chuyen-canh: khong\n")[0]["co"]["chuyen"], None)


class ChuDeTest(unittest.TestCase):
    def test_theme_and_fonts(self):
        self.assertEqual(phong.chu_de("vox")["ten"], "vox")
        self.assertIn("Be Vietnam Pro", phong.font_css("vox"))

    def test_subtitles_get_the_dark_box(self):
        from video_ma_parts import karaoke
        self.assertEqual(karaoke.kieu_phu_de("vox", "ngang"), karaoke.kieu_phu_de("cat-dan", "ngang"))


class KiemTest(unittest.TestCase):
    def test_missing_processed_image_is_a_scene_error_with_the_fix(self):
        md = ("---\ntieu-de: T\nphong-cach: vox\n---\n\n## Cảnh 1\nbo-cuc: mot\nloi: Cốc.\n"
              "nhip: Cốc | anh: ve: cốc sứ | giua\n")
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(kiem.CanhError) as c:
                kiem.kiem(parse.parse(md), Path(tmp))
        self.assertIn("anh_vox.py", c.exception.fix)

    def test_resources_read_from_the_index(self):
        from PIL import Image
        md = ("---\ntieu-de: T\nphong-cach: vox\n---\n\n## Cảnh 1\nbo-cuc: mot\nloi: Cốc.\n"
              "nhip: Cốc | anh: ve: cốc sứ | giua\n")
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "anh" / "ai" / "xu-ly"
            d.mkdir(parents=True)
            Image.new("RGBA", (40, 30), (1, 2, 3, 255)).save(d / "a-100-cat.png")
            (Path(tmp) / "anh" / "ai" / "vox.json").write_text(json.dumps(
                {"1-0": {"file": "ai/xu-ly/a-100-cat.png", "kieu": "cat", "ma": "a", "mo_hinh": "m", "nguon": None}}),
                encoding="utf-8")
            v = parse.parse(md)
            self.assertEqual(kiem.kiem(v, Path(tmp)), [])
            tn = vox.tai_nguyen(v.canh[0], Path(tmp))
        a = tn["anh"][0]
        self.assertEqual((a["rong"], a["cao"], a["kieu"], a["moHinh"]), (40, 30, "cat", "m"))
        self.assertTrue(a["dataUrl"].startswith("data:image/png;base64,"))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Chạy test, xác nhận hỏng.**

- [ ] **Step 3: Cài đặt**

`vox.moc_nhip(nhips, moc_tu, dan_dau)`:
```python
def moc_nhip(nhips: list, moc_tu: list, dan_dau: float) -> list:
    khoa = [w["khoa"] for w in moc_tu]
    ra, vi_tri = [], 0
    for n in nhips:
        if n.cum == "@dau":
            ra.append(dan_dau)
            continue
        can = khoa_tu(n.cum)
        i = next((j for j in range(vi_tri, len(khoa) - len(can) + 1) if khoa[j:j + len(can)] == can), -1)
        if i < 0:   # mốc từ thiếu (giọng chưa có, hay không khớp): nhịp theo nhịp trước, cách 0,6 s
            ra.append((ra[-1] + 0.6) if ra else dan_dau)
            continue
        ra.append(moc_tu[i]["t"])
        vi_tri = i + len(can)
    return [max(dan_dau, t) for t in ra]
```
Ghi chú: `lich.khoa_so_khop` giữ dấu thanh và bỏ dấu câu như `khoa_tu` — kiểm bằng test `test_beat_times_follow_the_words`; nếu `khoa_so_khop` của một từ có dấu câu dính liền (ví dụ "nhiều,") trả "nhiều" thì so khớp đúng.

`vox.du_lieu_canh(scene, cl, tai_nguyen, meta)`:
- `o` của nhịp không ghi: ô đầu tiên của `BO_CUC[bo_cuc][kho]` chưa có vật (trừ `nen`); hết ô thì dùng lại ô cuối; `chong` → `"chong-<k>"` (runtime tự xếp).
- `chu`: `vox.hien(noi_dung)` cho `chu`, `nhan`, `dau`; `mui-ten` giữ nguyên; `so`: tách `truoc`, `{{x}}`, `sau`, `thapPhan` = số chữ số sau dấu chấm.
- `the`: tách 3 phần như `parse.tach_the`.
- `anh`: `tai_nguyen["anh"].get(chi_so)`.
- `co.chuyen`: Cảnh 1 → None; trường `chuyen` của cảnh nếu có (`khong` → None); không thì theo `meta["chuyen-canh"]`: `xen-ke` → `CHUYEN_XEN_KE[(so - 2) % 2]`, `khong` → None, còn lại là chính nó.
- `nguon`: `truong["nguon"][0]` hoặc None; `hat = so`; `bangMau = meta["bang-mau"]`; `kho = Kho.du_lieu()` qua `kho.tu_meta(meta)`; `chuDe = phong.chu_de("vox")`; `thoiLuong = cl.thoi_luong`; `danDau = lich.DAN_DAU`; `nenTruoc = None`; `dongNguon = []`; `loat = None`; `tu = cl.moc_tu` (runtime không cần, nhưng giữ để gỡ lỗi).

`lich.du_lieu_canh`: dòng đầu thân hàm `if scene.loai == "vox": return vox.du_lieu_canh(scene, cl, tai_nguyen or {"anh": {}}, (tai_nguyen or {}).get("meta", {}))` (import `vox` trong hàm để tránh vòng import).

`lich.mac_dinh`: `phong-cach: vox` → `ban-tay: khong`, `chuyen-canh: xen-ke` (dùng khi khoá không có trong meta; thực ra parse đã setdefault, giữ cho đủ). `lich.kieu_chuyen` không dùng cho Vox (dữ liệu Vox tự tính).

`phong.CHU_DE["vox"] = {"ten": "vox", "font": "Be Vietnam Pro", "hienChu": "truot", "net": "nhanh"}`; `font_css`: điều kiện thêm Be Vietnam Pro đổi từ `== "cat-dan"` thành `in ("cat-dan", "vox")`.

`karaoke.kieu_phu_de`: chỗ `chu_de == "cat-dan"` (font và hộp) đổi thành `chu_de in ("cat-dan", "vox")`.

`kiem.kiem`: ngay đầu thân sau `warnings = []` và phần nhạc nền: `if video.meta["phong-cach"] == "vox": return warnings + vox.kiem(video, thu_muc)`. `vox.kiem`:
- Đọc `anh/ai/vox.json` (thiếu hoặc hỏng → coi như rỗng).
- Mỗi nhịp `anh`: khoá `f"{so}-{chi_so}"` phải có và file tồn tại; không → `kiem.CanhError(so, f"nhịp {chi_so + 1} chưa có ảnh đã xử lý.", "Chạy `python tools\\vi\\anh_vox.py <thư mục video>` để tạo và xử lý ảnh, rồi chạy lại.")`.
- Ảnh thật (`nguon` khác None) giữ dòng nguồn; ảnh AI (`mo_hinh`) ghi công cuối video.
- Lời dài quá 700 ký tự → cảnh báo như kiểu cũ.
- Trả list cảnh báo.

`vox.tai_nguyen(scene, thu_muc)`: đọc `vox.json`; với từng nhịp `anh` tự đọc file PNG đã xử lý (`base64` → `data:image/png;base64,…`, kích thước bằng Pillow `Image.open(...).size`), **không** qua `anh.doc` (luật nguồn của `anh.doc` dành cho ảnh trong `anh/`; nguồn ảnh Vox đã kiểm ở `anh_vox.py` và nằm trong `vox.json`). Trả `{"anh": {chi_so: {dataUrl, rong, cao, kieu, nguon: bang["nguon"], moHinh: bang["mo_hinh"]}}}`. Runtime chỉ hiện `nguon` khi có (ảnh thật).

Vòng import: `kiem.py` import `vox` ở đầu file; `vox.kiem` import `kiem` **trong thân hàm** (`from . import kiem as _kiem`) để lấy `CanhError`.

`video_ma._tai_nguyen`: `if scene.loai == "vox": return vox.tai_nguyen(scene, thu_muc)`. `_cac_du`: thêm mô hình AI từ ảnh Vox: `mo_hinh += [a["moHinh"] for tn in cac_tn for a in tn.get("anh", {}).values() if isinstance(tn.get("anh"), dict) and a.get("moHinh")]` — chú ý `tn["anh"]` của kiểu cũ là `None` hoặc dict ảnh đơn; chỉ cảnh Vox có `tn["anh"]` là dict theo chỉ số, phân biệt bằng `scene.loai`.

- [ ] **Step 4: Chạy test** — `tests.test_video_ma_vox_du_lieu tests.test_video_ma_lich tests.test_video_ma_phong tests.test_video_ma_karaoke tests.test_video_ma_parse` PASS.

- [ ] **Step 5: Commit** — `feat(vi): build Vox scene data with beat times from word timestamps`.

---

### Task 6: Runtime Vox (`vox.js`, `vox.css`) và ghép trang

**Files:**
- Create: `tools/vi/video_ma_parts/runtime/vox.js`, `tools/vi/video_ma_parts/runtime/vox.css`, `tools/vi/tests/js/test_vox.js`
- Modify: `tools/vi/video_ma_parts/trang.py` (`dung_trang` rẽ nhánh `vox`), `tools/vi/video_ma_parts/runtime/o-bo-cuc.json` (ô Vox), `tools/vi/tests/test_video_ma_canh.py` (thêm `js/test_vox.js` vào danh sách `node --test`)
- Test: `tools/vi/tests/test_video_ma_vox_trang.py` (Chromium)

**Interfaces:**
- Consumes: dữ liệu `du` Vox (hợp đồng chung), `THI_KHO`, `THI_CAT_DAN.prng`, `THI_CAT_DAN.giayXe`.
- Produces: `window.THI_VOX` (hàm thuần cho test Node): `oCua(boCuc, o, kho) -> {x,y,w,h}`, `xepChong(k, n, hat, kho) -> {x,y,w,h,goc}`, `vao(vat, p) -> {dx, dy, s, goc, a}` (p ∈ [0,1] tiến độ vào), `camera(t, thoiLuong, hat) -> {s, rx, ry, tx, ty}`, `rung(t, cacMocDap, hat) -> {x, y}`, `chuyenLia(p, kho) -> {dx, mo}`; và hợp đồng trang (`THI_VIDEO.khoiDong/san/thoiDiemCuoi/kiemTran/suKien`, `window.datThoiDiem`).

**Ô Vox** thêm vào `o-bo-cuc.json` dưới khoá `"ngang"` và `"doc"`, tên tiền tố `vox-` (toạ độ CSS điểm, khung ngang 1280×720, dọc 720×1280; vạch phụ đề ngang y ≥ 620, dọc y ≥ 1080):

| Ô | Ngang `{x,y,w,h}` | Dọc `{x,y,w,h}` |
|---|---|---|
| `vox-mot-giua` | 340,110,600,440 | 90,300,540,560 |
| `vox-mot-tren` | 240,60,800,110 | 60,120,600,150 |
| `vox-mot-duoi` | 240,520,800,90 | 60,900,600,150 |
| `vox-hai-ben-trai` / `-tren` | 80,120,520,420 | 60,140,600,420 |
| `vox-hai-ben-phai` / `-duoi` | 680,120,520,420 | 60,600,600,420 |
| `vox-hai-ben-giua` | 490,250,300,160 | 210,470,300,160 |
| `vox-dan-hang-1..4` | x = 70 + k·290, y 170, w 270, h 340 | x 60, y = 120 + k·235, w 600, h 215 |
| `vox-toan-canh-nen` | 0,0,1280,720 | 0,0,720,1280 |
| `vox-toan-canh-giua` | 240,200,800,240 | 60,420,600,320 |
| `vox-toan-canh-duoi` | 160,480,960,120 | 40,860,640,180 |

(Tên cho dọc của `hai-ben` là `vox-hai-ben-tren` và `vox-hai-ben-duoi`; ô `trai`/`phai` không có ở dọc — Task 1 đã chặn.)

- [ ] **Step 1: Viết test Node hỏng** (`tools/vi/tests/js/test_vox.js`, cùng khuôn với `js/test_cat_dan.js`: nạp `kho.js`, `cat-dan.js`, `vox.js` bằng `vm` với `window` giả)

```javascript
// tools/vi/tests/js/test_vox.js
const test = require('node:test');
const assert = require('node:assert');
const { napRuntime } = require('./nap_runtime');   // dùng helper sẵn có; nếu chưa có, chép cách nạp của test_cat_dan.js

const R = napRuntime(['kho.js', 'cat-dan.js', 'vox.js']);
const V = R.THI_VOX;
const NGANG = { ten: 'ngang', rong: 1280, cao: 720 };

test('ô theo bố cục', () => {
  assert.deepStrictEqual(V.oCua('hai-ben', 'trai', NGANG), { x: 80, y: 120, w: 520, h: 420 });
});

test('xếp chồng tất định, trong khung, trên vạch phụ đề', () => {
  for (let k = 0; k < 5; k++) {
    const a = V.xepChong(k, 5, 3, NGANG), b = V.xepChong(k, 5, 3, NGANG);
    assert.deepStrictEqual(a, b);
    assert.ok(a.x >= 0 && a.y >= 0 && a.x + a.w <= 1280 && a.y + a.h <= 620);
    assert.ok(Math.abs(a.goc) <= 8);
  }
});

test('kiểu vào: bắt đầu ngoài, kết thúc đúng chỗ, có nảy', () => {
  for (const vat of ['anh-cat', 'anh-khung', 'the', 'nhan', 'dau', 'chu', 'so', 'mui-ten']) {
    const cuoi = V.vao(vat, 1);
    assert.deepStrictEqual([cuoi.dx, cuoi.dy, cuoi.s, cuoi.goc, cuoi.a], [0, 0, 1, cuoi.goc, 1], vat);
    assert.ok(V.vao(vat, 0).a <= 1);
  }
  const vuot = Math.max(...[0.6, 0.7, 0.8].map(p => V.vao('anh-cat', p).s));
  assert.ok(vuot > 1, 'easeOutBack phải vượt quá 1 rồi về 1');
});

test('camera đẩy vào chậm, tối đa 1,06 và ±4°', () => {
  const c0 = V.camera(0, 8, 2), c1 = V.camera(8, 8, 2);
  assert.strictEqual(c0.s, 1);
  assert.ok(Math.abs(c1.s - 1.06) < 1e-9);
  for (let t = 0; t <= 8; t += 0.5) assert.ok(Math.abs(V.camera(t, 8, 2).ry) <= 4);
});

test('rung máy ngắn sau mỗi cú đập, tối đa 6 px', () => {
  assert.deepStrictEqual(V.rung(1.0, [2.0], 1), { x: 0, y: 0 });
  const r = V.rung(2.05, [2.0], 1);
  assert.ok(Math.hypot(r.x, r.y) > 0 && Math.hypot(r.x, r.y) <= 6);
  assert.deepStrictEqual(V.rung(2.2, [2.0], 1), { x: 0, y: 0 });
});

test('chuyển lia: trượt hết khung trong 0,35 giây', () => {
  assert.strictEqual(V.chuyenLia(0, NGANG).dx, 0);
  assert.strictEqual(V.chuyenLia(1, NGANG).dx, -1280);
});
```

- [ ] **Step 2: Chạy, xác nhận hỏng** — `node --test tools/vi/tests/js/test_vox.js`.

- [ ] **Step 3: Viết `vox.js`** (ES5 như runtime cũ, bọc `(function (root) { … })(window)`)

Phần hàm thuần (đúng chữ ký ở Interfaces):
- `oCua(boCuc, o, kho)`: đọc `THI_O_BO_CUC[kho.ten]["vox-" + boCuc + "-" + o]`.
- `xepChong(k, n, hat, kho)`: lưới tự do: `r = THI_CAT_DAN.prng(hat * 31 + k)`; ô cơ sở chia vùng nội dung (ngang 60..1220 × 60..600, dọc 40..680 × 120..1040) thành `n` cột so le; lệch ±40 px, `goc` ±8°; kẹp trong vùng.
- `vao(vat, p)`: `e = easeOutBack(p)` (c1 = 1,70158); theo vật:
  - `anh-cat`: rơi từ trên `dy = -420·(1-p)`, `s = 0.7 + 0.3·e` (vượt 1 rồi về), `goc = 0`, `a = min(1, p·4)`;
  - `anh-khung`: `dy = -300·(1-e)`, `goc = 6·(1-p)`, `s = 1`, `a = min(1, p·3)`;
  - `the`: `dx = 260·(1-e)`, `a = min(1, p·2)`;
  - `nhan`: `s = 1.12 - 0.12·e`, `a = p < 0.15 ? p/0.15 : 1`;
  - `dau`: `s = 2.2 - 1.2·e`, `goc = -8 + 4·e`, `a = min(1, p·5)`;
  - `chu`, `so`, `mui-ten`: `dy = 18·(1-e)`, `a = p`.
  Ở `p = 1` luôn trả `{dx: 0, dy: 0, s: 1, goc: goc_cuối, a: 1}` (`goc_cuối` = 0, trừ `dau` = -4).
- `camera(t, T, hat)`: `u = t/T`, `s = 1 + 0.06·(u·u·(3-2u))`, `ry = 4·sin(2π·(u·0.5 + prng(hat)()·0.3))·(u)` kẹp ±4, `rx = ry·0.4`, `tx, ty` = 0.
- `rung(t, cacMoc, hat)`: với mốc `m` gần nhất mà `0 ≤ t-m ≤ 0.15`: biên độ `6·(1-(t-m)/0.15)`, hướng theo `prng(hat*7 + chỉ số mốc)`; ngoài cửa sổ trả `{x:0, y:0}`.
- `chuyenLia(p, kho)`: `e = p<0.5 ? 2p² : 1-2(1-p)²`, `dx = -kho.rong·e + 0` (cộng 0 để `p = 0` ra `0` chứ không phải `-0`: `assert.strictEqual` của Node phân biệt hai giá trị này), `mo = sin(πp)·24` (px nhoè hướng). Mọi hàm thuần trả số đều tránh `-0` theo cách này.

Phần dựng trang (`khoiDong(du)`):
1. `#khung` (đã có trong HTML) nhận class `vox` và `bang-<bangMau>`; dựng 3 lớp `div.lop` theo `transform-style: preserve-3d` trong `div.san` có `perspective: 1400px`:
   - `.lop-xa` (`translateZ(-220px) scale(1.18)`): nền giấy `THI_CAT_DAN.nenGiay(hat, kho, giay)` của bảng màu + 3–5 mảng giấy xé `giayXe` màu theo bảng, có lớp chấm halftone SVG `pattern`.
   - `.lop-giua` (`translateZ(-80px) scale(1.06)`): 1–2 mảng giấy xé nhỏ và ảnh `toan-canh` ô `nen` (nếu có).
   - `.lop-gan` (`translateZ(0)`): mọi vật của nhịp. Tuỳ chọn `xa` đưa vật vào `.lop-giua`, `gan` giữ ở gần.
2. Mỗi nhịp → một phần tử `div.vat` có `data-id="nhip-<k>"`, đặt theo `oCua`/`xepChong`, nội dung:
   - `anh` kiểu `cat`: `<img>` PNG đã có viền và bóng (Task 4), `object-fit: contain`.
   - `anh` kiểu `khung`: `<img>` khung xé + 1–2 băng dính (`THI_CAT_DAN.bangDinh`) ở góc theo `prng`; có `nguon` thì chữ nguồn nhỏ dưới ảnh (`.nguon-anh`, 13 px).
   - `the`: thẻ giấy trắng viền đậm: nhãn (chữ hoa, màu nhấn), giá trị (ExtraBold 64 px, co theo ô), chú thích.
   - `chu`: Be Vietnam Pro ExtraBold, cỡ lớn nhất vừa ô (đo bằng `scrollWidth`, giảm dần từ 72 px tới 34 px; vẫn tràn → `kiemTran` báo).
   - `nhan`: dải băng dính màu nhấn, chữ hoa ExtraBold 30 px, nghiêng ±3°.
   - `dau`: khung chữ nhật bo tròn viền 6 px màu đỏ con dấu, chữ hoa, `mix-blend-mode: multiply`, hạt nhiễu SVG nhẹ.
   - `so`: như `chu`, số chạy từ 0 tới giá trị trong 1,2 giây từ `batDau`, định dạng dấu phẩy thập phân theo `thapPhan`, hàng nghìn dấu chấm.
   - `mui-ten`: SVG đường cong từ tâm ô đầu tới tâm ô cuối, nét đậm 8 px màu mực, `stroke-dashoffset` vẽ dần 0,5 giây, đầu mũi tên hiện khi vẽ xong.
3. Dòng `nguon` của cảnh (`du.nguon`): `.nguon-canh` góc dưới trái trên vạch phụ đề. `du.dongNguon` (cuối video): như runtime cũ, `#nhac-nguon`. `du.loat`: như `khung-loat.js` (gọi lại `THI_KHUNG_LOAT` nếu có, không viết lại).
4. `datThoiDiem(t)`:
   - Chuyển cảnh: `t < 0.35` và `du.co.chuyen` và `du.nenTruoc`: vẽ ảnh nền cảnh trước (`<img class="nen-truoc">` phủ khung) ở trên cùng; `lia` → dịch theo `chuyenLia(t/0.35)` kèm `filter: blur(mo/6 px)` **chỉ trong 0,35 giây đầu** (không áp blur ở khung khác); `xe-giay` → mặt nạ đa giác xé chạy ngang (dùng lại cách của `chuyen-canh.js`, đọc hàm của nó nếu có, không chép tay).
   - Camera: `.san` nhận `transform: scale(s) rotateX(rx deg) rotateY(ry deg) translate(rung)`.
   - Từng vật: `p = kep((t - batDau) / DAI[vat], 0, 1)` với `DAI = {anh-cat: .55, anh-khung: .5, the: .4, nhan: .3, dau: .35, chu: .45, so: .45, mui-ten: .5}`; `p = 0` → `visibility: hidden`; áp `vao(vat, p)`.
   - Bóng đổ của vật không phải ảnh: `box-shadow` cố định (không đổi theo khung) để khỏi tốn.
5. `kiemTran()`: đặt `datThoiDiem(thoiDiemCuoi())`; trả `id` của: vật `chu`/`the`/`nhan`/`dau`/`so` có `scrollWidth > clientWidth + 1` hoặc `scrollHeight > clientHeight + 1`; vật có bounding box ra ngoài khung (> 1 px) hoặc đè vạch phụ đề (ngang y > 620, dọc y > 1080), trừ ô `nen`; hai vật (không phải `chong`, không phải `nen`) giao nhau quá 30% diện tích vật nhỏ hơn → `"chong:<id1>,<id2>"`; `.nguon-canh` tràn → `"nguon"`; `#nhac-nguon` như cũ.
6. `suKien()`: `[{t: 0, loai: "chuyen", dai: .35}]` nếu có chuyển, và mỗi nhịp: `anh-cat`/`dau` → `{t: batDau + .45, loai: "nhan", dai: .2}` (tiếng đập), các vật khác → `{t: batDau, loai: "ting", dai: .2}`. Danh sách mốc đập (`anh-cat`, `dau`) cũng dùng cho `rung`.
7. Đặt `THI_VIDEO = {khoiDong, san:false, thoiDiemCuoi, kiemTran, suKien}` rồi sau khi dựng xong `datThoiDiem(0)` và `san = true`. Lưu ý: `khung-video.js` không nạp ở trang Vox, nên `vox.js` tự định nghĩa `root.THI_VIDEO`.

`vox.css`: `.vox` dùng `font-family: 'Be Vietnam Pro'`; bảng màu bốn bộ (biến CSS `--giay`, `--muc`, `--nhan`, `--manh1..4`): `kem` (#F4ECD8, #1E2430, #E4572E, #2E86AB #F2A541 #3B8B5A #C8553D), `bao-cu` (#E9DFC8, #2B2620, #B23A2B, #7A8B6F #C9A15B #556270 #A0522D), `dem` (#1B2133, #F4ECD8, #F2C14E, #2E4057 #048A81 #D1495B #6C5B7B), `tuoi` (#FFF3E0, #222222, #FF4F5A, #00A6A6 #FFB400 #7A4EAB #3DDC97). Không dùng `filter` theo khung ngoài lúc chuyển `lia`.

`trang.dung_trang`: nếu `du["loai"] == "vox"`: scripts = `THI_O_BO_CUC`, `kho.js`, `dong.js`, `cat-dan.js`, `chuyen-canh.js`, `khung-loat.js`, `vox.js`, rồi `window.DU_CANH = …; THI_KHO.dat(window.DU_CANH.kho); THI_VIDEO.khoiDong(window.DU_CANH);`; CSS = `phong.font_css("vox")` + `vox.css` (không nạp `viet-tay.css`). Đọc `chuyen-canh.js` và `khung-loat.js` trước: nếu chúng phụ thuộc `khung-video.js` thì không nạp và tự cài phần cần (ghi rõ trong báo cáo).

- [ ] **Step 4: Viết test Chromium** (`tools/vi/tests/test_video_ma_vox_trang.py`, `@unittest.skipUnless(co_chromium(), …)`), dựng `du` bằng `vox.du_lieu_canh` với ảnh PNG tự tạo (Pillow) gắn qua `tai_nguyen`:
  - `test_same_time_same_bytes`: `chup.trang_chup(Kho("ngang", 720))`, hai lần `datThoiDiem(2.0)` → `_anh_khung` bằng nhau từng byte.
  - `test_object_hidden_before_its_beat_and_visible_after`: nhịp `batDau` 2,0: ở t = 1,9 phần tử `[data-id=nhip-1]` có `visibility: hidden`; t = 3,0 hiện, `getBoundingClientRect` nằm trong ô.
  - `test_no_overflow_for_the_example_scenes`: mọi bố cục, cả `ngang` và `doc`, nội dung dài đúng giới hạn (chu 40 ký tự, nhãn 30, dấu 16, thẻ 24/16/60) → `THI_VIDEO.kiemTran()` rỗng.
  - `test_overflowing_text_is_reported`: chữ 40 ký tự toàn "W" ở ô `vox-dan-hang-1` dọc → `kiemTran` có `nhip-0`.
  - `test_full_hd_frame_size`: `Kho("ngang", 1080)` → ảnh 1920×1080; `Kho("doc", 1080)` → 1080×1920.
  - `test_lia_transition_uses_previous_frame`: có `nenTruoc` (PNG đỏ) và `co.chuyen = "lia"`: ở t = 0,1 cột điểm ảnh giữa khung còn đỏ một phần; t = 0,4 không còn đỏ.
  - `test_sound_events`: `suKien()` có một `chuyen` ở 0 và đúng một sự kiện cho mỗi nhịp.

- [ ] **Step 5: Chạy test** — `node --test tools/vi/tests/js/test_vox.js`; `cd tools/vi; ..\..\venv\Scripts\python.exe -m unittest tests.test_video_ma_vox_trang tests.test_video_ma_canh tests.test_video_ma_chup` PASS.

- [ ] **Step 6: Commit** — `feat(vi): render Vox scenes as layered torn-paper collages in 2.5D`.

---

### Task 7: Nối vào `video_ma.py`: xem trước hai khung, dựng thật, tốc độ

**Files:**
- Modify: `tools/vi/video_ma.py` (`_xem_truoc`, `_kiem_tran_tat_ca`, `_dung` không đổi luồng), `tools/vi/video_ma_parts/chup.py` (chỉ thêm `chup_luc(page, html, t, duong_dan)` nếu cần, không đổi beginFrame)
- Test: `tools/vi/tests/test_video_ma_vox_tich_hop.py`

**Interfaces:**
- Consumes: mọi thứ của Task 1–6.
- Produces: `--xem-truoc` với Vox ghi `xem-truoc/canh-N.png` (khung cuối) **và** `xem-truoc/canh-N-giua.png` (khung ở giữa cảnh, t = thời lượng/2); `files` liệt kê cả hai.

- [ ] **Step 1: Viết test hỏng** (cần Chromium và FFmpeg; dùng giọng thu sẵn để không cần mạng: tạo `giong/canh-N.mp3` bằng FFmpeg `anullsrc` 3 giây, như các test tích hợp hiện có làm)

```python
# tools/vi/tests/test_video_ma_vox_tich_hop.py (khung chính; dùng helper tạo mp3 im lặng của test_video_ma_tich_hop.py)
class VoxTichHopTest(unittest.TestCase):
    def test_preview_writes_middle_and_end_frames(self): ...
        # 2 cảnh Vox, ảnh xử lý sẵn trong anh/ai/xu-ly + vox.json; chạy --xem-truoc;
        # expect files == ["xem-truoc/canh-1-giua.png", "xem-truoc/canh-1.png", "xem-truoc/canh-2-giua.png", "xem-truoc/canh-2.png"]
    def test_full_render_produces_a_video_with_the_right_length(self): ...
        # thoi-luong: 6; expect ready, video.mp4 tồn tại, ffprobe duration ≈ tổng thời lượng cảnh ± 0,1;
        # warnings có cảnh báo thời lượng khi lệch, không có khi trong khoảng.
    def test_missing_images_stop_before_capture(self): ...
        # xoá vox.json → error.step == "canh", fix chứa "anh_vox.py".
    def test_old_styles_render_unchanged(self): ...
        # kịch bản viet-tay mẫu của test_video_ma_tich_hop: --plan-only kết quả JSON giống trước (so_canh, warnings).
```

Viết đầy đủ thân các test theo khuôn của `tests/test_video_ma_tich_hop.py` (đọc file đó trước: cách dựng thư mục tạm, tạo mp3 im lặng, gọi CLI, đọc JSON).

- [ ] **Step 2: Cài đặt**
- `_xem_truoc`: với cảnh `vox`, sau `chup_cuoi`, chụp thêm khung giữa: `mo_trang` (đã mở trong `chup_cuoi`), `page.evaluate("(t) => window.datThoiDiem(t)", thoi_luong / 2)`, `page.screenshot(path=…, type="png")`. Giọng giả 8 giây nên `thoi_luong` lấy từ `THI_VIDEO.thoiDiemCuoi()`; dùng `/2` của giá trị đó.
- `_kiem_tran_tat_ca`: thêm nhánh cho mã Vox: `"chong:<a>,<b>"` → `CanhError(so, f"hai vật {a} và {b} đè lên nhau quá nhiều.", "Đổi ô của một nhịp, đổi `bo-cuc` (ví dụ `chong` cho nhiều vật) hoặc bớt nhịp.")`; `nhip-k` tràn → `CanhError(so, f"chữ của nhịp {k+1} tràn ô.", "Rút gọn chữ của nhịp đó (ý dài để ở lời) hoặc đổi sang ô rộng hơn.")`.
- Kiểm tốc độ (ghi số đo vào báo cáo, không phải test): dựng một video Vox 60 giây mẫu (Task 8 có ví dụ) bằng `do3.py`-kiểu đo (`time.perf_counter` quanh `chup_song_song`), so với `in-tien-lam-phat-cat-dan` cùng độ dài; mục tiêu ≤ 1,5 lần thời lượng video trên máy 6 lõi. Không đạt → tìm phần tốn (thường là `filter`, `box-shadow` động, ảnh quá lớn) và sửa trước khi đóng task.

- [ ] **Step 3: Chạy test** — `tests.test_video_ma_vox_tich_hop tests.test_video_ma_tich_hop tests.test_video_ma_cong_cu` PASS.

- [ ] **Step 4: Commit** — `feat(vi): preview and render Vox videos end to end`.

---

### Task 8: Hướng dẫn, luật và test tài liệu

**Files:**
- Rewrite: `docs/vi/tro-ly/video-giai-thich.md` (hướng dẫn Vox cho AI)
- Create: `docs/vi/tro-ly/nhip-vox.md`
- Move: `docs/vi/tro-ly/canh-video.md` → `docs/vi/tham-khao/canh-video.md`; nội dung viết tay cũ của `video-giai-thich.md` (bản trước khi viết lại) → `docs/vi/tham-khao/video-viet-tay.md`; mỗi file đầu trang thêm dòng "Kiểu cũ (viết tay, cắt dán theo loại cảnh). Chỉ dùng khi sửa `video.md` cũ; video mới làm theo `docs/vi/tro-ly/video-giai-thich.md` (kiểu Vox)."
- Modify: `AGENTS.vi.md` §3 (từ kích hoạt "video vox", "kiểu vox"), §10 bảng (giữ tên loại việc "Video giải thích dựng bằng mã"), §15 (viết lại), `docs/vi/tro-ly/quy-trinh-hoi.md` (dòng video giải thích: chỉ hỏi khi thiếu chủ đề/nội dung, không chờ duyệt), `docs/vi/video-giai-thich.md` (cho người dùng), `.agents/rules/ppt-master-vi.md` (mục "Video giải thích"), `docs/vi/xu-ly-loi.md` (bảng lỗi `anh_vox.py`), `CHANGELOG-VI.md` (mục `6.3.2-vi.15`), `docs/vi/phat-trien/bao-tri.md` (nếu test bảo trì đòi), `NOTICE` (không đổi trừ khi thêm bên thứ ba — không có)
- Modify tests: `tools/vi/tests/test_vi_layer.py`

**Interfaces:**
- Consumes: ngữ pháp Task 1, `anh_vox.ERROR_STEPS`, các `error.step` của `video_ma.py`.
- Produces: tài liệu mà AI đọc; test ghim cụm từ mới.

- [ ] **Step 1: Chuyển đích các test tài liệu cũ**

Trong `test_vi_layer.py`, mọi hằng/đường dẫn trỏ `docs/vi/tro-ly/video-giai-thich.md` (biến `EXPLAINER_GUIDE`) và `docs/vi/tro-ly/canh-video.md` (`SCENE_GUIDE`) của các test kiểu cũ đổi sang `docs/vi/tham-khao/video-viet-tay.md` và `docs/vi/tham-khao/canh-video.md` (các test: `test_guide_meta_table_lists_every_key_and_value` — chỉ cho khoá kiểu cũ, xem dưới; `test_scene_guide_*`; `test_every_scene_example_passes_the_real_reader`; `test_guide_example_parses_with_the_real_reader`; `test_every_example_script_passes_the_real_reader`; `test_guide_asks_format_style_character_and_series_within_seven_questions`; `test_guides_name_every_effect`; `test_guide_states_the_grammar_and_limits`; `test_guide_names_outputs_and_forbids_hand_editing_frames`; `test_docs_cover_pictures_photos_and_motion` phần hướng dẫn; `test_guide_ai_section_covers_both_platform_paths`; `test_guides_require_pictures_that_match_the_narration_and_one_subtitle_line` phần hướng dẫn). `test_guide_meta_table_lists_every_key_and_value`: với `META_CHOICES` kiểu cũ kiểm ở file tham khảo (giá trị `vox` của `phong-cach` được miễn ở file tham khảo); `VOX_META_CHOICES` và `phong-cach: vox`, `thoi-luong` kiểm ở hướng dẫn Vox mới.

- [ ] **Step 2: Viết test mới cho hướng dẫn Vox (hỏng trước khi viết tài liệu)**

```python
class VoxGuideTest(unittest.TestCase):
    GUIDE = "docs/vi/tro-ly/video-giai-thich.md"
    NHIP = "docs/vi/tro-ly/nhip-vox.md"

    def test_guide_teaches_the_vox_craft(self):
        g = read(self.GUIDE)
        for phrase in ("Vox", "móc", "lật", "chốt", "130 từ", "phép thử tắt tiếng", "Không bịa số liệu",
                       "6 từ", "thoi-luong", "anh_vox.py", "--xem-truoc", "--plan-only", "ANH_AI_KEY",
                       "nhip-vox.md", "Hôm nay chúng ta"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, g)
        for cam in ("Môn, lớp", "học sinh cần hiểu", "mười lăm loại cảnh"):
            with self.subTest(cam=cam):
                self.assertNotIn(cam, g)

    def test_beat_reference_lists_every_object_layout_and_slot(self):
        from video_ma_parts import vox
        n = read(self.NHIP)
        for vat in vox.VAT:
            self.assertIn(f"`{vat}`", n)
        for bo_cuc, o in vox.BO_CUC.items():
            self.assertIn(f"`{bo_cuc}`", n)
            for ten in set(o["ngang"]) | set(o["doc"]):
                self.assertIn(f"`{ten}`", n)
        for t in vox.TUY_CHON:
            self.assertIn(f"`{t}`", n)

    def test_every_vox_example_passes_the_reader(self):
        # mọi khối ```…``` trong hai file có dòng "phong-cach: vox" phải đọc được và qua vox.kiem_canh;
        # ví dụ 60 giây trong nhip-vox.md ước tính 54–66 giây.
        ...

    def test_meta_table_lists_vox_keys(self):
        from video_ma_parts import vox
        g = read(self.GUIDE)
        for key, values in vox.VOX_META_CHOICES.items():
            row = next(l for l in g.splitlines() if l.startswith(f"| `{key}`"))
            for v in values:
                self.assertIn(f"`{v}`", row)
        self.assertIn("| `thoi-luong`", g)

    def test_anh_vox_error_steps_documented(self):
        import anh_vox
        for doc in ("AGENTS.vi.md", "docs/vi/xu-ly-loi.md"):
            t = read(doc)
            for step in anh_vox.ERROR_STEPS:
                with self.subTest(doc=doc, step=step):
                    self.assertIn(f"`{step}`", t)

    def test_agents_section_15_is_vox_only(self):
        s = section(read("AGENTS.vi.md"), AGENTS_VI_EXPLAINER_HEADING)
        for phrase in ("Vox", "anh_vox.py", "thoi-luong", "không dừng chờ duyệt", "ANH_AI_KEY"):
            self.assertIn(phrase, s)
        self.assertNotIn("nen: mau/", s)

    def test_rule_file_has_the_vox_steps_and_stays_under_the_cap(self):
        r = read(".agents/rules/ppt-master-vi.md")
        for phrase in ("Vox", "anh_vox.py", "thoi-luong", "Không bịa số liệu"):
            self.assertIn(phrase, r)
        # giới hạn 12 000 byte (CRLF) đã có test riêng; chạy lại test đó.
```

(Viết thân `test_every_vox_example_passes_the_reader` đầy đủ: tách khối code bằng regex ```` ```\n(.*?)``` ````, lọc khối chứa `phong-cach: vox`, `parse.parse` từng khối, với ví dụ có `thoi-luong` thì `thoi_luong.uoc_tinh` nằm trong ±10% của `thoi-luong`.)

Các test cũ ghim chữ trong `AGENTS.vi.md` §15 và luật Antigravity mà nói về kiểu cũ (`anh_ai.py ke-hoach`, `nen: mau/`, "phải có `the`", "Không quá hai cảnh `ke-chuyen` liền nhau", "viết tay hay cắt dán") thì sửa kỳ vọng sang câu Vox tương ứng, hoặc chuyển sang file tham khảo. Giữ các test về `tim_nhac.py`, `nhac-nen`, `mang`, câu hỏi phân loại "video từ slide hay video mới", và giới hạn 12 000 byte.

- [ ] **Step 3: Viết tài liệu**

`docs/vi/tro-ly/video-giai-thich.md` (Vox), các mục theo thứ tự: Khi nào dùng · Hỏi gì (chỉ chủ đề, nội dung khi thiếu; mặc định: `thoi-luong: 60`, `kho: ngang`, giọng nữ vừa, phụ đề karaoke, tiếng hiệu ứng có, nhạc nền không; người dùng xin xem kịch bản trước thì dừng) · Nghề viết kịch bản Vox (mạch móc → vấn đề → giải thích 2–4 ý, mỗi ý một hình ví von → lật → chốt; không cảnh tiêu đề riêng, không "Hôm nay chúng ta…", không "thứ nhất, thứ hai"; quỹ từ 30 giây ≈ 65 từ 3–4 cảnh, 60 giây ≈ 130 từ 5–7 cảnh, 2 phút ≈ 270 từ, 3 phút ≈ 410 từ, mỗi cảnh 5–12 giây; câu ngắn ≤ khoảng 15 từ; Không bịa số liệu, số phải có `nguon`) · Hình khớp thoại (mỗi câu ít nhất một nhịp; phép thử tắt tiếng; chữ trên hình tối đa khoảng 6 từ, không chép lời; `ve:` nêu vật, hành động, góc chụp cụ thể; người, địa danh, sự kiện có thật dùng `tim:`) · Chọn bố cục (bảng) · Cấu trúc video.md (bảng khoá đầu, gồm `phong-cach: vox`, `thoi-luong`, `phong-anh`, `bang-mau`, `chuyen-canh`, các khoá giữ nguyên; cảnh: `bo-cuc`, `loi`, `nhip`, `chuyen`, `nguon`; trỏ `nhip-vox.md` cho ngữ pháp đủ) · Ảnh (thứ tự nguồn: công cụ vẽ của nền tảng lưu vào `anh/ai/goc/<mã>.png` theo `anh/ai/ke-hoach.json` → API kiểu OpenAI qua `ANH_AI_URL`, `ANH_AI_KEY`, `ANH_AI_MO_HINH`, mặc định 9router `ag/gemini-3.1-flash-image` → ảnh thật; `anh_vox.py` lưu đệm, giới hạn 20 ảnh, `--toi-da`) · Vòng tự kiểm (`--plan-only` đọc cảnh báo thời lượng → sửa → `anh_vox.py` → `--xem-truoc` xem `canh-N-giua.png` và `canh-N.png` theo danh sách: hình khớp lời, chữ không tràn, vật không chồng, ảnh không có chữ, không sai ý → sửa → dựng thật → gửi video kèm `video.md` và nguyên văn `warnings`) · Đầu ra · Ghi vào brief. Kèm một ví dụ đầy đủ "Giao tiếp với đồng nghiệp" 60 giây (5–6 cảnh, khoảng 130 từ, không số liệu thiếu nguồn).

`docs/vi/tro-ly/nhip-vox.md`: ngữ pháp `nhip`, bảng vật (giới hạn, kiểu vào), bảng bố cục và ô (ngang, dọc), tuỳ chọn, cụm từ và thời điểm (`@dau`, lặp cụm), giới hạn (≤ 6 nhịp, ≤ 2 `chu`, `chong` ≤ 5), ví dụ từng bố cục.

`AGENTS.vi.md` §15 viết lại: đọc hai file trên; quy trình 1–6 (hỏi khi thiếu chủ đề → viết `video.md` → `--plan-only` sửa thời lượng → `anh_vox.py` → `--xem-truoc` tự xem tự sửa → dựng thật, không dừng chờ duyệt trừ khi người dùng xin); bảng `error.step` của `video_ma.py` (giữ) và của `anh_vox.py` (mới: `input`, `parse`, `cau-hinh`, `mang`, `nha-cung-cap`, `tach-nen`, `write`, `internal`, mỗi dòng một cách xử lý); điều cấm (không bịa số liệu; không viết HTML hay ảnh cảnh bằng tay; không tự viết `anh/ai/nguon.json`, `anh/ai/vox.json`; khoá API không ghi vào file nào trong repo; không chạm `skills/` trừ chạy `image_search.py`; không commit `projects/`). Kịch bản cũ (`loai:`) vẫn dựng được, sửa theo `docs/vi/tham-khao/`.

`.agents/rules/ppt-master-vi.md` mục "Video giải thích": thay toàn bộ bằng bản Vox gọn (≤ 1 000 byte): đọc hai file; Vox, không khuôn bài giảng; quỹ từ theo `thoi-luong`; Không bịa số liệu; `--plan-only` → `anh_vox.py` → `--xem-truoc` → dựng; hình khớp lời; khoá ảnh qua `ANH_AI_KEY`. Đo lại ≤ 12 000 byte CRLF.

`docs/vi/video-giai-thich.md` (người dùng): giới thiệu video Vox, câu lệnh mẫu ("Tạo video vox 60 giây về …"), ảnh AI cần 9router và khoá (cách lấy khoá, `setx ANH_AI_KEY`), thời gian dựng, kịch bản cũ vẫn dùng được.

`CHANGELOG-VI.md` mục `## 6.3.2-vi.15 — <ngày phát hành>`: Thêm (Vox, nhịp, `anh_vox.py`, `thoi-luong`), Đổi (hướng dẫn chỉ dạy Vox, `mon`/`lop` không bắt buộc với Vox), Không đổi (kịch bản cũ), Rủi ro (nguồn vẽ phụ thuộc tài khoản; ảnh AI có thể có chữ hoặc sai ý — AI phải xem trước).

- [ ] **Step 4: Chạy toàn bộ test** — `cd tools/vi; ..\..\venv\Scripts\python.exe -m unittest discover -s tests` PASS hết.

- [ ] **Step 5: Commit** — `docs(vi): teach Vox explainer videos; move the handwriting guide to reference`.

---

### Task 9: Kiểm chứng thật (người điều phối làm, không giao subagent)

**Files:** không sửa code; kết quả ghi `docs/vi/phat-trien/2026-10-01-video-vox-kiem-thu.md`.

- [ ] **Step 1:** Đặt khoá cho phiên chạy (chủ repo đã cho phép đọc khoá 9router chỉ đọc): đọc khoá đang hoạt động từ `%APPDATA%\9router\db\data.sqlite` (bảng `apiKeys`, `mode=ro`) vào biến môi trường của tiến trình con, không in, không ghi file.
- [ ] **Step 2:** Làm đúng câu lệnh "Sử dụng 2anh-studio tạo 1 video dạng vox chủ đề giao tiếp với đồng nghiệp dài 60s video ngang 16:9" theo hướng dẫn mới (đọc `video-giai-thich.md`, `nhip-vox.md` như một AI mới), thư mục `projects/_video/giao-tiep-dong-nghiep-vox/`.
- [ ] **Step 3:** Ghi số đo: thời lượng (đạt 54–66 giây), số ảnh, thời gian vẽ ảnh, thời gian dựng, cảnh báo; mở xem 6–8 khung (giữa và cuối mỗi cảnh) và ghi nhận xét thật (khớp lời, chồng, chữ trong ảnh).
- [ ] **Step 4:** Gửi chủ repo đường dẫn video, kịch bản và ảnh ghép các khung; chờ chủ repo đồng ý trước khi gộp nhánh và phát hành vi.15.
- [ ] **Step 5:** Commit file kiểm thử (`docs(vi): record the Vox end-to-end check`); không commit gì trong `projects/`.
