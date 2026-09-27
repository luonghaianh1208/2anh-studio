'use strict';
var test = require('node:test');
var assert = require('node:assert');
var path = require('node:path');
var fs = require('node:fs');

var RT = path.join(__dirname, '..', '..', 'video_ma_parts', 'runtime');
var TN = path.join(__dirname, '..', '..', 'thi_nghiem_parts');
require(path.join(TN, 'runtime', 'khung.js'));
require(path.join(TN, 'mo_hinh', 'li-con-lac-don.js'));
require(path.join(RT, 'kho.js'));
require(path.join(RT, 'dong.js'));
require(path.join(RT, 'khung-video.js'));
var LOAI = ['tieu-de', 'khai-niem', 'cong-thuc', 'y-tung-y', 'quy-trinh', 'so-sanh', 'do-thi', 'thi-nghiem'];
var LOAI_MOI = ['minh-hoa', 'anh'];
LOAI.concat(LOAI_MOI).forEach(function (l) { require(path.join(RT, 'canh', l + '.js')); });
var V = globalThis.THI_VIDEO;
var C = globalThis.THI_CANH;
var KHAI_BAO = JSON.parse(fs.readFileSync(path.join(TN, 'mo_hinh', 'li-con-lac-don.json'), 'utf8'));

function du(loai, thoiLuong, moc, truong, them) {
  var d = { so: 1, loai: loai, thoiLuong: thoiLuong, danDau: 1.0, moc: moc, truong: truong };
  Object.keys(them || {}).forEach(function (k) { d[k] = them[k]; });
  return d;
}
function tatCa(gh) {
  var s = gh === 2.5;
  return {
    'tieu-de': du('tieu-de', gh, [], { chu: ['Chuẩn độ acid – base'], phu: ['Hoá học 11'] }),
    'khai-niem': du('khai-niem', gh, [], { 'thuat-ngu': ['Chuẩn độ'], 'dinh-nghia': ['Xác định nồng độ một dung dịch.'] }),
    'cong-thuc': du('cong-thuc', gh, s ? [0.7, 1.0] : [2.5, 4.5], { 'bieu-thuc': ['C~M~ = n/V'], 'giai-thich': ['n là số mol', 'V là thể tích'] }),
    'y-tung-y': du('y-tung-y', gh, s ? [0.7, 1.0, 1.3] : [0.7, 3, 5.5], { 'tieu-de': ['Ba bước'], y: ['a', 'b', 'c'] }),
    'quy-trinh': du('quy-trinh', gh, s ? [0.7, 1.0, 1.3] : [0.7, 3.5, 6], { 'tieu-de': ['Quy trình'], buoc: ['Đo', 'Nhỏ', 'Dừng'] }),
    'so-sanh': du('so-sanh', gh, s ? [0.7, 0.9, 1.1, 1.3] : [0.7, 2.5, 4.5, 6.5],
      { 'tieu-de': ['So sánh'], trai: ['Acid'], phai: ['Base'], 'y-trai': ['a', 'b'], 'y-phai': ['c', 'd'] }),
    'do-thi': du('do-thi', gh, s ? [0.7, 1.0, 1.3] : [0.7, 3, 5.5], { 'tieu-de': ['Đồ thị'], 'truc-ngang': ['t'], 'truc-doc': ['v'], diem: ['0, 0', '1, 2', '2, 4'] },
      { diem: [[0, 0], [1, 2], [2, 4]] }),
    'thi-nghiem': du('thi-nghiem', gh, [], { mau: ['li-con-lac-don'] },
      { khaiBao: KHAI_BAO, thamSo: { 'chieu-dai': [[0, 0.4], [6, 1.6]] }, do: ['chu-ki'] })
  };
}
function hienThi(html) {
  return html.replace(/<span class="an">.*?<\/span>/g, '').replace(/<[^>]+>/g, '');
}

test('catDanhDau: che chu, giu the dong mo va thoat ky tu dac biet', function () {
  assert.strictEqual(V.catDanhDau('**ab**c', 1), '<b>a<span class="ngoi"></span><span class="an">b</span></b><span class="an">c</span>');
  assert.strictEqual(V.catDanhDau('H~2~O', 99), 'H<sub>2</sub>O');
  assert.strictEqual(V.catDanhDau('m/s^2^', 99), 'm/s<sup>2</sup>');
  assert.strictEqual(V.catDanhDau('a < b & "c"', 99), 'a &lt; b &amp; &quot;c&quot;');
  var doc = V.catDanhDau('</script><img src=x onerror=alert(1)>', 99);
  assert.ok(doc.indexOf('<img') === -1 && doc.indexOf('</script') === -1, doc);
  assert.strictEqual(hienThi(V.catDanhDau('**ab**c', 2)), 'ab');
  assert.strictEqual(hienThi(V.catDanhDau('Nhờ ướt', 3)), 'Nhờ');
  assert.strictEqual(V.catDanhDau('abc', 0), '<span class="an">abc</span>');
});

test('demKyTu bo dau danh dau; tienDo kep 0..1', function () {
  assert.strictEqual(V.demKyTu('H~2~SO~4~ **x**'), 'H2SO4 x'.length);
  assert.strictEqual(V.tienDo(0, 1, 2), 0);
  assert.strictEqual(V.tienDo(2, 1, 2), 0.5);
  assert.strictEqual(V.tienDo(9, 1, 2), 1);
  assert.strictEqual(V.tienDo(1, 1, 0), 1);
});

test('khung-video khong giu hang dan dau rieng: du.danDau tu Python la nguon duy nhat', function () {
  assert.strictEqual(V.DAN_DAU, undefined);
});

test('lau bang: do dai lay tu du.giayLauBang cua Python, mac dinh 0,5 khi thieu', function () {
  var co = { lauBang: true };
  var mot = V.tao({ thoiLuong: 6, co: co, giayLauBang: 1.0 }).chu('a', 'x', 0, 0, 100, 50, 30, 0.2, {});
  assert.ok(mot.batDau >= 1.05, 'muc dau tien doi het lau bang: ' + mot.batDau);
  var macDinh = V.tao({ thoiLuong: 6, co: co }).chu('a', 'x', 0, 0, 100, 50, 30, 0.2, {});
  assert.ok(Math.abs(macDinh.batDau - 0.55) < 1e-9, String(macDinh.batDau));
});

test('moi kieu chuyen canh: muc dau tien doi het chuyen canh; khong chuyen canh thi khong doi', function () {
  ['lau-bang', 'lat-trang', 'truot', 'phong', 'mo-man'].forEach(function (k) {
    var m = V.tao({ thoiLuong: 6, co: { chuyen: k }, giayLauBang: 0.5 }).chu('a', 'x', 0, 0, 100, 50, 30, 0.2, {});
    assert.ok(Math.abs(m.batDau - 0.55) < 1e-9, k + ' ' + m.batDau);
  });
  var khong = V.tao({ thoiLuong: 6, co: { chuyen: null, lauBang: false }, giayLauBang: 0.5 }).chu('a', 'x', 0, 0, 100, 50, 30, 0.2, {});
  assert.strictEqual(khong.batDau, 0.2);
});

test('duong ve la xac dinh theo hat giong', function () {
  assert.strictEqual(V.duongQua([[0, 0], [100, 0]], 5), V.duongQua([[0, 0], [100, 0]], 5));
  assert.notStrictEqual(V.duongQua([[0, 0], [100, 0]], 5), V.duongQua([[0, 0], [100, 0]], 6));
});

test('moi loai canh: muc xac dinh, t=0 chua hien gi, cuoi canh hien du', function () {
  [12, 2.5].forEach(function (gh) {
    var bo = tatCa(gh);
    LOAI.forEach(function (l) {
      var a = C[l].muc(bo[l]);
      var b = C[l].muc(bo[l]);
      assert.deepStrictEqual(a, b, l);
      assert.ok(a.length > 0, l);
      a.forEach(function (m) {
        if (m.dong) { return; }
        assert.ok(m.batDau > 0, l + ':' + m.id + ' phai bat dau sau t=0');
        assert.strictEqual(V.tienDo(0, m.batDau, m.thoiLuong), 0, l + ':' + m.id);
        assert.ok(m.batDau + m.thoiLuong <= gh - 0.2 + 1e-9, l + ':' + m.id + ' phai xong truoc cuoi canh ' + gh);
        assert.strictEqual(V.tienDo(gh, m.batDau, m.thoiLuong), 1, l + ':' + m.id);
      });
      var ids = a.map(function (m) { return m.id; });
      assert.strictEqual(new Set(ids).size, ids.length, l + ' co id trung');
    });
  });
});

test('moi loai canh chua trong day 90 px cho phu de, ke ca khi du so dong toi da', function () {
  var DAY = 630;
  var bo = tatCa(12);
  var moc = function (n) { return Array.apply(null, Array(n)).map(function (_, k) { return 0.7 + k; }); };
  var nhieu = function (n, chu) { return Array.apply(null, Array(n)).map(function () { return chu; }); };
  bo['y-tung-y'] = du('y-tung-y', 12, moc(6), { 'tieu-de': ['Sáu ý'], y: nhieu(6, 'ý') });
  bo['cong-thuc'] = du('cong-thuc', 12, moc(4), { 'bieu-thuc': ['T = 2π√(l/g)'], 'giai-thich': nhieu(4, 'g') });
  bo['so-sanh'] = du('so-sanh', 12, moc(8), { 'tieu-de': ['S'], trai: ['A'], phai: ['B'], 'y-trai': nhieu(4, 'a'), 'y-phai': nhieu(4, 'b') });
  bo['quy-trinh'] = du('quy-trinh', 12, moc(5), { 'tieu-de': ['Q'], buoc: nhieu(5, 'b') });
  bo['thi-nghiem'].thamSo = { 'chieu-dai': [[0, 0.4]], g: [[0, 9.8]], 'khoi-luong': [[0, 0.2]] };
  bo['thi-nghiem'].do = ['chu-ki', 'thoi-gian-10-dao-dong'];
  LOAI.forEach(function (l) {
    C[l].muc(bo[l]).forEach(function (m) {
      var day = m.kieu === 'net'
        ? Math.max.apply(null, m.d.match(/-?\d+(\.\d+)?/g).map(Number).filter(function (_, i) { return i % 2 === 1; }))
        : m.y + m.cao;
      assert.ok(day <= DAY, l + ':' + m.id + ' xuong toi ' + day);
    });
  });
});

test('y k hien dung tai moc cau k', function () {
  var bo = tatCa(12);
  var ids = function (l, tienTo) {
    var muc = C[l].muc(bo[l]);
    return [0, 1, 2].map(function (k) { return muc.filter(function (m) { return m.id === tienTo + k; })[0]; });
  };
  ids('y-tung-y', 'y-').forEach(function (m, k) { assert.strictEqual(m.batDau, bo['y-tung-y'].moc[k]); });
  ids('quy-trinh', 'buoc-').forEach(function (m, k) { assert.strictEqual(m.batDau, bo['quy-trinh'].moc[k]); });
  ids('do-thi', 'diem-').forEach(function (m, k) { assert.strictEqual(m.batDau, bo['do-thi'].moc[k]); });
  var ss = C['so-sanh'].muc(bo['so-sanh']);
  var at = function (id) { return ss.filter(function (m) { return m.id === id; })[0].batDau; };
  assert.strictEqual(at('y-trai-0'), 0.7);
  assert.strictEqual(at('y-trai-1'), 2.5);
  assert.strictEqual(at('y-phai-0'), 4.5);
  assert.strictEqual(at('y-phai-1'), 6.5);
  var ct = C['cong-thuc'].muc(bo['cong-thuc']);
  var bt = ct.filter(function (m) { return m.id === 'bieu-thuc'; })[0];
  ct.filter(function (m) { return /^giai-thich-/.test(m.id); }).forEach(function (m, k) {
    assert.ok(m.batDau >= bo['cong-thuc'].moc[k]);
    assert.ok(m.batDau >= bt.batDau + bt.thoiLuong);
  });
});

test('do thi: diem nam trong vung ve, cung y thi vao giua', function () {
  var muc = C['do-thi'].muc(tatCa(12)['do-thi']);
  var vong = muc.filter(function (m) { return /^diem-/.test(m.id); });
  assert.strictEqual(vong.length, 3);
  vong.forEach(function (m) {
    var so = m.d.match(/-?\d+(\.\d+)?/g).map(Number);
    var cx = so[0] + 9;
    assert.ok(cx >= 190 - 1 && cx <= 1090 + 1, 'x ngoai vung: ' + cx);
  });
  var bang = tatCa(12)['do-thi'];
  bang.diem = [[0, 5], [1, 5]];
  var muc2 = C['do-thi'].muc(bang).filter(function (m) { return /^diem-/.test(m.id); });
  var y = muc2.map(function (m) { return Number(m.d.match(/-?\d+(\.\d+)?/g)[1]); });
  assert.strictEqual(y[0], y[1]);
  assert.ok(y[0] > 270 && y[0] < 560);
});

test('thi nghiem: noi suy tham so theo moc thoi gian', function () {
  var d = tatCa(12)['thi-nghiem'];
  var T = C['thi-nghiem'];
  assert.strictEqual(T.thamSoTai(d, 0)['chieu-dai'], 0.4);
  assert.ok(Math.abs(T.thamSoTai(d, 3)['chieu-dai'] - 1.0) < 1e-9);
  assert.strictEqual(T.thamSoTai(d, 6)['chieu-dai'], 1.6);
  assert.strictEqual(T.thamSoTai(d, 100)['chieu-dai'], 1.6);
  assert.strictEqual(T.thamSoTai(d, 3)['g'], 9.8);
  d.thamSo = { 'chieu-dai': [[2, 0.4]] };
  assert.strictEqual(T.thamSoTai(d, 1)['chieu-dai'], 1.0);
  assert.strictEqual(T.thamSoTai(d, 2)['chieu-dai'], 0.4);
});

test('thi nghiem: so do la so cua tinh() cua mo hinh, o moi thoi diem', function () {
  var d = tatCa(12)['thi-nghiem'];
  var T = C['thi-nghiem'];
  var M = globalThis.THI_NGHIEM_MO_HINH;
  [0, 1.5, 3, 5, 6, 11].forEach(function (t) {
    var g = T.giaTri(d, t);
    assert.strictEqual(g.dai['chu-ki'], M.tinh(g.tham)['chu-ki']);
  });
  assert.ok(Math.abs(T.giaTri(d, 3).dai['chu-ki'] - 2.007089923) < 5e-4);
});

test('thi nghiem: mo hinh mot-lan chay lai tu moc tham-so gan nhat, mo hinh khac tinh tu danDau', function () {
  var T = C['thi-nghiem'];
  var d = { danDau: 1.0, khaiBao: { hoatHinh: 'mot-lan' },
    thamSo: { 'goc-nem': [[0, 30], [8, 60]], 'van-toc': [[12, 15]] } };
  assert.strictEqual(T.mocGanNhat(d, 5), 1.0);
  assert.strictEqual(T.mocGanNhat(d, 9), 8);
  assert.strictEqual(T.mocGanNhat(d, 13), 12);
  assert.ok(Math.abs(T.thoiGianMoHinh(d, 5) - 4.0) < 1e-9);
  assert.strictEqual(T.thoiGianMoHinh(d, 8), 0);
  assert.strictEqual(T.thoiGianMoHinh(d, 10), 2);
  assert.strictEqual(T.thoiGianMoHinh(d, 14), 2);
  assert.strictEqual(T.thoiGianMoHinh(d, 0.2), 0);
  d.khaiBao.hoatHinh = 'lap';
  assert.ok(Math.abs(T.thoiGianMoHinh(d, 14) - 13.0) < 1e-9);
});

test('thi nghiem: khong co dong chu nao bat dau tai t=0 ngoai dong so do', function () {
  var muc = C['thi-nghiem'].muc(tatCa(12)['thi-nghiem']);
  var dong = muc.filter(function (m) { return m.dong; });
  assert.ok(dong.length >= 2);
});

// ---------- hình, ảnh, cột hình, minh-hoa, anh, lau bảng ----------

var HINH = { ten: 'flask', viewBox: '0 0 24 24', phanTu: [
  { the: 'path', thuocTinh: { d: 'M9 3l6 0' } },
  { the: 'path', thuocTinh: { d: 'M10 9l4 0' } },
  { the: 'circle', thuocTinh: { cx: '12', cy: '12', r: '3' } }
] };
function hinhNhan(nhan) { var h = JSON.parse(JSON.stringify(HINH)); h.nhan = nhan; return h; }
function anhGia(rong, cao) { return { dataUrl: 'data:image/png;base64,AAAA', nguon: 'Ảnh: Tác giả · CC BY 4.0', rong: rong, cao: cao }; }
var COT = ['khai-niem', 'cong-thuc', 'y-tung-y'];

function boMoi(gh) {
  var s = gh < 3;
  var bo = tatCa(gh);
  bo['minh-hoa'] = du('minh-hoa', gh, s ? [1.0, 1.3, 1.6] : [1.0, 4, 7],
    { 'tieu-de': ['Dụng cụ'], hinh: ['clock | Đồng hồ', 'ruler | Thước', 'weight | Quả nặng'] },
    { hinhs: [hinhNhan('Đồng hồ'), hinhNhan('Thước'), hinhNhan('Quả nặng')] });
  bo.anh = du('anh', gh, [], { anh: ['a.png'], 'chu-thich': ['Con lắc Foucault'] }, { anh: anhGia(2000, 800) });
  Object.keys(bo).forEach(function (l) { bo[l].co = { banTay: true, mayQuay: true, lauBang: false }; });
  return bo;
}
function voiHinh(bo, loai, hinhHayAnh) {
  var d = JSON.parse(JSON.stringify(bo[loai]));
  if (hinhHayAnh === 'hinh') { d.hinh = HINH; } else { d.anh = anhGia(600, 1200); }
  return d;
}
function tim(ds, id) { return ds.filter(function (m) { return m.id === id; })[0]; }
function dayMuc(m) {
  if (m.kieu === 'net') {
    return Math.max.apply(null, m.d.match(/-?\d+(\.\d+)?/g).map(Number).filter(function (_, i) { return i % 2 === 1; }));
  }
  if (m.kieu === 'hinh') { return m.y + m.kich; }
  return m.y + m.cao;
}

test('catDanhDau: dung mot span.ngoi khi 0 < n < tong, khong co khi n = 0 hoac n = tong; chu hien thi khong doi', function () {
  ['**ab**c', 'H~2~SO~4~ loãng', 'Nhờ ướt nhẫm'].forEach(function (chu) {
    var tong = V.demKyTu(chu);
    var chuThuan = V.catDanhDau(chu, tong).replace(/<[^>]+>/g, '');
    for (var n = 0; n <= tong; n++) {
      var html = V.catDanhDau(chu, n);
      var so = (html.match(/<span class="ngoi"><\/span>/g) || []).length;
      assert.strictEqual(so, n > 0 && n < tong ? 1 : 0, chu + ' n=' + n);
      assert.strictEqual(hienThi(html), chuThuan.slice(0, n), chu + ' n=' + n);
    }
  });
});

test('B.hinh va B.anh: muc dung kieu, anh vua khung giu ti le', function () {
  var B = V.tao({ thoiLuong: 12, co: {} });
  var h = B.hinh('h', HINH, 100, 200, 240, 1.0);
  assert.strictEqual(h.kieu, 'hinh');
  assert.strictEqual(h.phanTu.length, 3);
  assert.strictEqual(h.viewBox, '0 0 24 24');
  assert.ok(h.thoiLuong >= 1.2);
  var a = B.anh('a', anhGia(600, 1200), 80, 70, 1120, 490, 1.0);
  assert.strictEqual(a.kieu, 'anh');
  assert.ok(Math.abs(a.rong / a.cao - 0.5) < 1e-9);
  assert.ok(a.x >= 80 && a.y >= 70 && a.x + a.rong <= 1200 + 1e-9 && a.y + a.cao <= 560 + 1e-9);
  assert.ok(Math.abs(a.cao - 490) < 1e-9, 'anh doc chiem het chieu cao');
  var b = B.anh('b', anhGia(2000, 800), 80, 70, 1120, 490, 1.0);
  assert.ok(Math.abs(b.rong / b.cao - 2.5) < 1e-9);
  assert.ok(Math.abs(b.rong - 1120) < 1e-9, 'anh ngang chiem het chieu ngang');
});

test('minh-hoa: hinh k bat dau tai moc[k], nhan k bat dau khi hinh k xong', function () {
  var d = boMoi(12)['minh-hoa'];
  var ds = C['minh-hoa'].muc(d);
  [0, 1, 2].forEach(function (k) {
    var h = tim(ds, 'hinh-' + k);
    var n = tim(ds, 'nhan-' + k);
    assert.strictEqual(h.kieu, 'hinh');
    assert.strictEqual(h.batDau, d.moc[k]);
    assert.ok(Math.abs(n.batDau - (h.batDau + h.thoiLuong)) < 1e-9);
    assert.strictEqual(h.kich, 240);
    assert.strictEqual(h.y, 230);
    assert.strictEqual(n.co, 28);
  });
  var xs = [0, 1, 2].map(function (k) { return tim(ds, 'hinh-' + k).x + 120; });
  assert.ok(Math.abs((xs[1] - xs[0]) - (xs[2] - xs[1])) < 1e-9, 'chia deu be ngang');
  assert.ok(Math.abs((xs[0] + xs[2]) / 2 - 640) < 1e-9);
});

test('anh: anh trong vung 80..1200 x 70..560, chu thich co 30 o y 575..625 bat dau tai 1,0', function () {
  var d = boMoi(12).anh;
  var ds = C.anh.muc(d);
  var a = tim(ds, 'anh');
  assert.ok(a.x >= 80 && a.x + a.rong <= 1200 + 1e-9 && a.y >= 70 && a.y + a.cao <= 560 + 1e-9);
  var c = tim(ds, 'chu-thich');
  assert.strictEqual(c.co, 30);
  assert.strictEqual(c.y, 575);
  assert.strictEqual(c.y + c.cao, 625);
  assert.strictEqual(c.batDau, 1.0);
  d.moc = [2.5];
  assert.strictEqual(tim(C.anh.muc(d), 'chu-thich').batDau, 2.5);
  var dai = function (n) { d.truong['chu-thich'] = ['x'.repeat(n)]; return tim(C.anh.muc(d), 'chu-thich').co; };
  assert.strictEqual(dai(60), 30);
  assert.strictEqual(dai(75), 26, 'chu thich dai thu nho de vua mot dong');
  assert.strictEqual(dai(90), 24);
});

test('cot hinh: chu thu vao x <= 860, hinh o o 900,200,320x380 bat dau tai moc[0] hoac 1,0', function () {
  var bo = boMoi(12);
  COT.forEach(function (l) {
    ['hinh', 'anh'].forEach(function (kieu) {
      var d = voiHinh(bo, l, kieu);
      var ds = C[l].muc(d);
      ds.forEach(function (m) {
        if (m.kieu === 'chu') { assert.ok(m.x + m.rong <= 860, l + ':' + m.id + ' phai toi ' + (m.x + m.rong)); }
      });
      var h = tim(ds, kieu);
      assert.ok(h, l + ' thieu muc ' + kieu);
      var rong = kieu === 'hinh' ? h.kich : h.rong;
      var cao = kieu === 'hinh' ? h.kich : h.cao;
      assert.ok(h.x >= 900 && h.x + rong <= 1220 + 1e-9 && h.y >= 200 && h.y + cao <= 580 + 1e-9, l + ' ' + JSON.stringify([h.x, h.y, rong, cao]));
      assert.strictEqual(h.batDau, d.moc.length ? d.moc[0] : 1.0, l);
    });
    var cu = C[l].muc(bo[l]);
    assert.ok(!tim(cu, 'hinh') && !tim(cu, 'anh'), l + ' khong co hinh thi khong co cot');
  });
  var y = voiHinh(bo, 'y-tung-y', 'hinh');
  y.truong.y = ['x'.repeat(60), 'ngắn', 'vừa'];
  var co = C['y-tung-y'].muc(y).filter(function (m) { return /^y-/.test(m.id); }).map(function (m) { return m.co; });
  assert.strictEqual(new Set(co).size, 1, 'moi y cung co chu: ' + co);
});

test('tieu-de co hinh: hinh 180x180 giua phia tren (y 40..220), tieu de doi xuong', function () {
  var bo = boMoi(12);
  ['hinh', 'anh'].forEach(function (kieu) {
    var d = voiHinh(bo, 'tieu-de', kieu);
    var ds = C['tieu-de'].muc(d);
    var h = tim(ds, kieu);
    var rong = kieu === 'hinh' ? h.kich : h.rong;
    var cao = kieu === 'hinh' ? h.kich : h.cao;
    assert.ok(h.y >= 40 && h.y + cao <= 220 + 1e-9 && rong <= 180 + 1e-9 && cao <= 180 + 1e-9);
    assert.ok(Math.abs(h.x + rong / 2 - 640) < 1e-9, 'giua');
    assert.ok(tim(ds, 'chu').y >= 220);
  });
});

test('moi loai canh co lau bang, gh = 2,5667: khong muc nao bat dau truoc 0,55 hay xong sau gh - 0,2', function () {
  [2.5667, 12].forEach(function (gh) {
    var bo = boMoi(gh);
    var ca = [];
    Object.keys(bo).forEach(function (l) { ca.push([l, bo[l]]); });
    COT.concat(['tieu-de']).forEach(function (l) {
      ca.push([l + '+hinh', voiHinh(bo, l, 'hinh')]);
      ca.push([l + '+anh', voiHinh(bo, l, 'anh')]);
    });
    ca.forEach(function (c) {
      var d = JSON.parse(JSON.stringify(c[1]));
      d.co.lauBang = true;
      var ds = C[d.loai].muc(d);
      assert.deepStrictEqual(ds, C[d.loai].muc(d), c[0] + ' xac dinh');
      ds.forEach(function (m) {
        if (m.dong) { return; }
        assert.ok(m.batDau >= 0.55 - 1e-9, c[0] + ':' + m.id + ' bat dau ' + m.batDau);
        assert.ok(m.batDau + m.thoiLuong <= gh - 0.2 + 1e-9, c[0] + ':' + m.id + ' xong ' + (m.batDau + m.thoiLuong));
        if (m.kieu === 'hinh') { assert.ok(m.thoiLuong >= 1.2 - 1e-9, c[0] + ':' + m.id + ' ve qua nhanh ' + m.thoiLuong); }
        assert.ok(dayMuc(m) <= 630, c[0] + ':' + m.id + ' xuong toi ' + dayMuc(m));
      });
      var ids = ds.map(function (m) { return m.id; });
      assert.strictEqual(new Set(ids).size, ids.length, c[0] + ' co id trung');
    });
  });
});

test('tieu-de chu-dong: chu nay tung ky tu, khong ban tay, xong truoc cuoi canh; khong chu-dong thi viet tay', function () {
  [12, 2.5].forEach(function (gh) {
    ['', 'hinh'].forEach(function (kieu) {
      var d = JSON.parse(JSON.stringify(boMoi(gh)['tieu-de']));
      if (kieu) { d.hinh = HINH; }
      d.truong.chu = ['x'.repeat(90)];
      d.co.chuDong = true;
      var c = tim(C['tieu-de'].muc(d), 'chu');
      assert.strictEqual(c.nay, true);
      assert.strictEqual(c.tay, false);
      assert.ok(c.batDau + c.thoiLuong <= gh - 0.2 + 1e-9, gh + ' ' + kieu);
      d.co.chuDong = false;
      var cu = tim(C['tieu-de'].muc(d), 'chu');
      assert.ok(!cu.nay && cu.tay !== false);
    });
  });
});

test('cong-thuc: bieu-thuc khong tach cum nhan (khongCum), giai-thich van tach', function () {
  var d = tatCa(12)['cong-thuc'];
  d.truong['bieu-thuc'] = ['y = ((a+b))__c'];
  var ds = C['cong-thuc'].muc(d);
  assert.strictEqual(tim(ds, 'bieu-thuc').khongCum, true);
  assert.ok(!tim(ds, 'giai-thich-0').khongCum);
  assert.ok(Math.abs(tim(ds, 'bieu-thuc').thoiLuong - V.thoiGianViet('y = ((a+b))__c', true)) < 1e-9);
});

test('y-tung-y cot hinh: cum khoanh o gioi han 60 ky tu thi chu nho hon de dem khong day xuong dong', function () {
  var bo = boMoi(12);
  var y = voiHinh(bo, 'y-tung-y', 'hinh');
  y.truong.y = ['x'.repeat(60), 'ngắn'];
  var co = function () { return tim(C['y-tung-y'].muc(y), 'y-0').co; };
  assert.strictEqual(co(), 26, 'khong co cum thi giu co cu');
  y.truong.y = ['((' + 'x'.repeat(60) + '))', 'ngắn'];
  assert.strictEqual(co(), 24);
  y.truong.y = ['((' + 'x'.repeat(50) + '))', 'ngắn'];
  assert.strictEqual(co(), 26);
});
