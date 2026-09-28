'use strict';
// Thẻ thông tin (`the`), dòng tài liệu (`tai-lieu`), công thức không ngắt và khung loạt (`loat`): các mục của cảnh
// (hàm thuần muc(du)), chuỗi "0k/N" và HTML khối không ngắt của catDanhDau.
var test = require('node:test');
var assert = require('node:assert');
var path = require('node:path');

var RT = path.join(__dirname, '..', '..', 'video_ma_parts', 'runtime');
require(path.join(RT, 'kho.js'));
require(path.join(RT, 'dong.js'));
require(path.join(RT, 'cat-dan.js'));
require(path.join(RT, 'khung-loat.js'));
require(path.join(RT, 'khung-video.js'));
['tieu-de', 'khai-niem', 'cong-thuc', 'y-tung-y'].forEach(function (l) { require(path.join(RT, 'canh', l + '.js')); });
var K = globalThis.THI_KHO;
var V = globalThis.THI_VIDEO;
var C = globalThis.THI_CANH;
var L = globalThis.THI_KHUNG_LOAT;

var NGANG = { ten: 'ngang', rong: 1280, cao: 720, day: 620, tamX: 640, tamY: 310 };
var DOC = { ten: 'doc', rong: 720, cao: 1280, day: 1080, tamX: 360, tamY: 540 };
var CAT_DAN = { ten: 'cat-dan', font: 'BeVietnamPro', hienChu: 'truot', net: 'nhanh', mauNhan: ['#e8a33d', '#1f6f78', '#c8452f', '#2f4f9e'], giay: '#f3ead7' };
var THE = { nhan: 'Của cải thực sự', giaTri: 'GDP', chuThich: 'Tổng sản lượng hàng hoá và dịch vụ' };
var ANH = { dataUrl: 'data:image/png;base64,AAAA', nguon: 'Ảnh: Tác giả · CC BY 4.0', rong: 600, cao: 400 };

function du(loai, truong, them) {
  var d = { so: 1, loai: loai, thoiLuong: 10, danDau: 1.0, moc: [1.0, 2.0, 3.0, 4.0, 5.0, 6.0], truong: truong, co: {} };
  Object.keys(them || {}).forEach(function (k) { d[k] = them[k]; });
  return d;
}
var TRUONG = {
  'tieu-de': { chu: ['Vì sao in thêm tiền lại gây lạm phát'], phu: ['Kinh tế học nhập môn'] },
  'khai-niem': { 'thuat-ngu': ['Lạm phát'], 'dinh-nghia': ['Mức giá chung tăng liên tục theo thời gian.'] },
  'cong-thuc': { 'bieu-thuc': ['M x V = P x Y'], 'giai-thich': ['M là lượng tiền'] },
  'y-tung-y': { 'tieu-de': ['Ba nguyên nhân'], y: ['Cầu kéo', 'Chi phí đẩy', 'In tiền'] }
};
function tim(ds, id) { return ds.filter(function (m) { return m.id === id; })[0]; }
function giao(a, b) { return a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h; }

test('khung loat: "0k/N" hai chu so, nhieu hon khi tong co ba chu so', function () {
  assert.strictEqual(L.chuoiSo(3, 8), '03/08');
  assert.strictEqual(L.chuoiSo(3, 12), '03/12');
  assert.strictEqual(L.chuoiSo(12, 12), '12/12');
  assert.strictEqual(L.chuoiSo(7, 120), '007/120');
});

test('the: moi loai canh x 2 kho x 2 phong cach co du muc the, nam trong o the va hien sau muc chu dau 0,3 s', function () {
  [NGANG, DOC].forEach(function (kho) {
    K.dat(kho);
    [undefined, CAT_DAN].forEach(function (cd) {
      Object.keys(TRUONG).forEach(function (loai) {
        var d = du(loai, TRUONG[loai], { the: THE, chuDe: cd });
        var ds = C[loai].muc(d);
        var the = ds.filter(function (m) { return m.id.indexOf('the-') === 0; });
        var ten = kho.ten + ' ' + (cd ? 'cat-dan' : 'viet-tay') + ' ' + loai;
        assert.deepStrictEqual(the.map(function (m) { return m.id; }).sort(),
          (cd ? ['the-chu-thich', 'the-gia-tri', 'the-nen', 'the-nhan'] : ['the-chu-thich', 'the-gia-tri', 'the-khung', 'the-nhan']), ten);
        var dau = ds.filter(function (m) { return m.kieu === 'chu' && m.id.indexOf('the-') !== 0; })
          .sort(function (a, b) { return a.batDau - b.batDau; })[0];
        var som = Math.min.apply(null, the.map(function (m) { return m.batDau; }));
        assert.ok(som >= Math.min(dau.batDau + dau.thoiLuong + 0.3, d.thoiLuong - 0.6) - 1e-9, ten + ' ' + som);
        var o = tim(ds, 'the-nhan');
        var gt = tim(ds, 'the-gia-tri');
        assert.deepStrictEqual(gt.khoi, [3], ten);
        assert.ok(gt.co === 44 && gt.khongCum, ten);
        the.filter(function (m) { return m.kieu === 'chu'; }).forEach(function (m) {
          assert.ok(m.y + m.cao <= kho.day, ten + ' ' + m.id);
          assert.ok(m.x >= 0 && m.x + m.rong <= kho.rong, ten + ' ' + m.id);
          assert.ok(m.y >= o.y - 10 - 1e-9, ten + ' ' + m.id);
          // Thẻ không bao giờ là mục tiêu máy quay (máy quay giữ cả thẻ trong khung).
          assert.strictEqual(m.quay, false, ten + ' ' + m.id);
        });
      });
    });
  });
  K.dat(NGANG);
});

test('the: khong co chu thich thi khong co muc chu thich va the thap hon', function () {
  K.dat(NGANG);
  var ds = C['khai-niem'].muc(du('khai-niem', TRUONG['khai-niem'], { the: { nhan: 'Năm', giaTri: '1923', chuThich: '' }, chuDe: CAT_DAN }));
  assert.strictEqual(tim(ds, 'the-chu-thich'), undefined);
  assert.ok(tim(ds, 'the-nen').cao < K.o('the').h);
});

test('the kho ngang: tieu de hep lai, khong de len o the; tieu-de khong hinh co chu hep lai', function () {
  K.dat(NGANG);
  var o = K.o('the');
  var ds = C['y-tung-y'].muc(du('y-tung-y', TRUONG['y-tung-y'], { the: THE }));
  var td = tim(ds, 'tieu-de');
  assert.ok(td.x + td.rong <= o.x - 20 + 1e-9, JSON.stringify(td));
  ['chu', 'phu'].forEach(function (id) {
    var m = tim(C['tieu-de'].muc(du('tieu-de', TRUONG['tieu-de'], { the: THE })), id);
    assert.ok(m.x + m.rong <= o.x - 20 + 1e-9, id);
  });
  // Không có thẻ: bố cục vi.11 giữ nguyên.
  assert.strictEqual(tim(C['y-tung-y'].muc(du('y-tung-y', TRUONG['y-tung-y'])), 'tieu-de').rong, K.o('noi-dung').w);
});

test('the kho doc: noi dung doi xuong duoi the; cot phu thu lai nhung day giu nguyen', function () {
  K.dat(DOC);
  var o = K.o('the');
  ['khai-niem', 'cong-thuc', 'y-tung-y'].forEach(function (loai) {
    [null, 'hinh'].forEach(function (cot) {
      var them = { the: THE };
      if (cot) { them.hinh = { phanTu: [{ the: 'circle', thuocTinh: { cx: '12', cy: '12', r: '9' } }], viewBox: '0 0 24 24' }; }
      var ds = C[loai].muc(du(loai, TRUONG[loai], them));
      ds.forEach(function (m) {
        if (m.id.indexOf('the-') === 0 || m.id === 'tieu-de' || m.id === 'gach' && loai === 'y-tung-y') { return; }
        if (m.kieu === 'chu' || m.kieu === 'hinh') {
          var h = m.kieu === 'hinh' ? m.kich : m.cao;
          assert.ok(m.y >= o.y + o.h, loai + ' ' + cot + ' ' + m.id + ' y ' + m.y);
          assert.ok(m.y + h <= DOC.day, loai + ' ' + cot + ' ' + m.id + ' day ' + (m.y + h));
        }
      });
    });
  });
  K.dat(NGANG);
});

test('tai-lieu: muc kieu nguon trong o tai-lieu; co anh co nguon thi xep chong nguon anh len tren', function () {
  [NGANG, DOC].forEach(function (kho) {
    K.dat(kho);
    var o = K.o('tai-lieu');
    var ds = C['khai-niem'].muc(du('khai-niem', TRUONG['khai-niem'], { taiLieu: 'Nguồn: Giáo trình' }));
    var tl = tim(ds, 'tai-lieu');
    assert.strictEqual(tl.kieu, 'nguon');
    assert.deepStrictEqual(tl.dongs, ['Nguồn: Giáo trình']);
    assert.deepStrictEqual([tl.x, tl.y, tl.rong, tl.cao], [o.x, o.y, o.w, o.h]);
    assert.ok(tl.quay === false && tl.tay === false);
    ds = C['khai-niem'].muc(du('khai-niem', TRUONG['khai-niem'], { taiLieu: 'Nguồn: Giáo trình', anh: ANH }));
    assert.deepStrictEqual(tim(ds, 'tai-lieu').dongs, [ANH.nguon, 'Nguồn: Giáo trình']);
    assert.strictEqual(tim(ds, 'anh').nguonNgoai, true);
    ds = C['khai-niem'].muc(du('khai-niem', TRUONG['khai-niem'], { anh: ANH }));
    assert.strictEqual(tim(ds, 'anh').nguonNgoai, undefined);
    assert.strictEqual(tim(ds, 'tai-lieu'), undefined);
  });
  K.dat(NGANG);
});

test('o the va tai-lieu: khong giao cot phu hay nhan vat, trong khung va tren vach phu de', function () {
  [NGANG, DOC].forEach(function (kho) {
    K.dat(kho);
    ['the', 'tai-lieu'].forEach(function (ten) {
      var o = K.o(ten);
      ['cot-phu', 'nhan-vat', 'noi-dung-hep'].forEach(function (khac) {
        if (ten === 'the' && khac === 'noi-dung-hep' && kho.ten === 'doc') { return; } // khổ dọc: nội dung dời xuống dưới thẻ
        assert.ok(!giao(o, K.o(khac)), kho.ten + ' ' + ten + ' giao ' + khac);
      });
      assert.ok(o.x >= 0 && o.y >= 40 && o.x + o.w <= kho.rong && o.y + o.h <= kho.day, kho.ten + ' ' + ten);
    });
    assert.ok(!giao(K.o('the'), K.o('tai-lieu')));
  });
  K.dat(NGANG);
});

test('loat: o tieu de chua 40 px phia tren chi khi co loat', function () {
  K.dat(NGANG);
  var co = tim(C['y-tung-y'].muc(du('y-tung-y', TRUONG['y-tung-y'], { loat: { ten: 'A', so: 1, tong: 2 } })), 'tieu-de');
  var khong = tim(C['y-tung-y'].muc(du('y-tung-y', TRUONG['y-tung-y'])), 'tieu-de');
  assert.strictEqual(khong.y, K.o('tieu-de').y);
  assert.ok(co.y >= 40);
  K.dat(DOC);
  co = tim(C['y-tung-y'].muc(du('y-tung-y', TRUONG['y-tung-y'], { loat: { ten: 'A', so: 1, tong: 2 } })), 'tieu-de');
  assert.strictEqual(co.y, K.o('tieu-de').y);
  K.dat(NGANG);
});

test('cong-thuc: moi phan la mot khoi khong ngat; html boc span.phan nowrap, khoang trang giua hai phan nam ngoai', function () {
  K.dat(NGANG);
  var bt = tim(C['cong-thuc'].muc(du('cong-thuc', { 'bieu-thuc': ['M x V | = P x Y'] })), 'bieu-thuc');
  assert.deepStrictEqual(bt.khoi, [5, 7]);
  assert.deepStrictEqual(bt.khoiChu, ['M x V', '= P x Y']);
  // Không tách phần: vẫn được xuống dòng trước toán tử quan hệ cấp ngoài cùng, số hạng giữ liền.
  bt = tim(C['cong-thuc'].muc(du('cong-thuc', { 'bieu-thuc': ['M x V = P x Y'] })), 'bieu-thuc');
  assert.deepStrictEqual(bt.khoi, [5, 7]);
  assert.deepStrictEqual(bt.khoiChu, ['M x V', '= P x Y']);
  bt = tim(C['cong-thuc'].muc(du('cong-thuc', { 'bieu-thuc': ['T = 2π√(l/g) | = 2π√(1/9.8) | ≈ {{2.01}} s'] })), 'bieu-thuc');
  assert.deepStrictEqual(bt.khoiChu, ['T', '= 2π√(l/g)', '= 2π√(1/9.8)', '≈ {{2.01}} s']);
  assert.strictEqual(bt.khoiChu.join(' '), bt.chu);
  var PHAN = '<span class="phan" style="white-space:nowrap">';
  assert.strictEqual(V.catDanhDau('M x V = P x Y', 13, null, null, true, [13]), PHAN + 'M x V = P x Y</span>');
  assert.strictEqual(V.catDanhDau('a b c d', 7, null, null, true, [3, 3]), PHAN + 'a b</span> ' + PHAN + 'c d</span>');
  // Viết dở: phần chưa viết ẩn trong span.an, khoảng trắng ngăn cũng ẩn khi chưa tới.
  assert.strictEqual(V.catDanhDau('a b c d', 2, null, null, true, [3, 3]),
    PHAN + 'a <span class="ngoi"></span><span class="an">b</span></span><span class="an"> </span>' + PHAN + '<span class="an">c d</span></span>');
  // Số chạy và chỉ số giữ nguyên trong khối.
  var h = V.catDanhDau('x~2~ | ≈ {{2.01}}'.replace(' | ', ' '), 20, null, null, true, [2, 6]);
  assert.ok(h.indexOf(PHAN + 'x<sub>2</sub></span> ' + PHAN + '≈ <span class="so" data-so="0">2,01</span></span>') === 0, h);
  // Không có khối: HTML như cũ.
  assert.strictEqual(V.catDanhDau('a b', 3, null, null, true), 'a b');
});

test('tachDoanCongThuc: tach truoc toan tu quan he cap ngoai cung; khong tach trong ngoac, dinh dang, so chay', function () {
  var T = V.tachDoanCongThuc;
  assert.deepStrictEqual(T('M x V = P x Y'), ['M x V', '= P x Y']);
  assert.deepStrictEqual(T('a ≈ b ≠ c < d > e ≤ f ≥ g → h ⇒ k'), ['a', '≈ b', '≠ c', '< d', '> e', '≤ f', '≥ g', '→ h', '⇒ k']);
  assert.deepStrictEqual(T('= 2π√(1/9.8)'), ['= 2π√(1/9.8)']);
  assert.deepStrictEqual(T('f(x = 2) = 5'), ['f(x = 2)', '= 5']);
  assert.deepStrictEqual(T('**a = b** = c'), ['**a = b**', '= c']);
  assert.deepStrictEqual(T('x^a = b^ = H~2 = O~'), ['x^a = b^', '= H~2 = O~']);
  assert.deepStrictEqual(T('a == b'), ['a == b']);
  assert.deepStrictEqual(T('a=b'), ['a=b']);
  assert.deepStrictEqual(T('Nhờ ướt nhẫm quyết định'), ['Nhờ ướt nhẫm quyết định']);
});

test('catDanhDau: khoi trong danh sach ngat duoc xuong dong o khoang trang (white-space normal)', function () {
  assert.strictEqual(V.catDanhDau('a b = c', 7, null, null, true, [3, 3], [0]),
    '<span class="phan" style="white-space:normal">a b</span> <span class="phan" style="white-space:nowrap">= c</span>');
});
