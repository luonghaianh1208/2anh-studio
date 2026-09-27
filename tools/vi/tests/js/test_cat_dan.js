'use strict';
// Phong cách cắt dán (runtime/cat-dan.js): hàm thuần vẽ giấy xé, chấm lưới, băng dính, nền giấy; và cách
// khung-video.js / hinh.js dùng chủ đề `cat-dan` (chữ trượt, nét nhanh, nhãn tiêu đề, sticker).
var test = require('node:test');
var assert = require('node:assert');
var path = require('node:path');

var RT = path.join(__dirname, '..', '..', 'video_ma_parts', 'runtime');
require(path.join(RT, 'kho.js'));
require(path.join(RT, 'dong.js'));
require(path.join(RT, 'cat-dan.js'));
require(path.join(RT, 'khung-video.js'));
require(path.join(RT, 'nhan.js'));
require(path.join(RT, 'hinh.js'));
['tieu-de', 'khai-niem', 'y-tung-y', 'quy-trinh', 'minh-hoa'].forEach(function (l) { require(path.join(RT, 'canh', l + '.js')); });
var C = globalThis.THI_CAT_DAN;
var V = globalThis.THI_VIDEO;
var K = globalThis.THI_CANH;

var MAU = ['#e8a33d', '#1f6f78', '#c8452f', '#2f4f9e'];
var CAT_DAN = { ten: 'cat-dan', font: 'BeVietnamPro', hienChu: 'truot', net: 'nhanh', mauNhan: MAU, giay: '#f3ead7' };
var VIET_TAY = { ten: 'viet-tay', font: 'Itim', hienChu: 'viet', net: 've' };
var NGANG = { ten: 'ngang', rong: 1280, cao: 720, day: 620 };
var DOC = { ten: 'doc', rong: 720, cao: 1280, day: 1080 };

function diem(chuoi) {
  return chuoi.trim().split(/\s+/).map(function (p) { return p.split(',').map(Number); });
}

test('prng la mulberry32: cung hat cung day, khac hat khac day, trong [0, 1)', function () {
  var a = C.prng(7), b = C.prng(7), c = C.prng(8);
  var da = [a(), a(), a()];
  assert.deepStrictEqual(da, [b(), b(), b()]);
  assert.notStrictEqual(da[0], c());
  da.forEach(function (x) { assert.ok(x >= 0 && x < 1); });
  // Cùng thuật toán với rng của khung-video.js (mulberry32).
  var r = V.rng(7);
  assert.strictEqual(C.prng(7)(), r());
});

test('giayXe: cung hat ra cung chuoi, khac hat ra khac chuoi', function () {
  var s1 = C.giayXe(3, 10, 20, 300, 120, 6);
  assert.strictEqual(typeof s1, 'string');
  assert.strictEqual(s1, C.giayXe(3, 10, 20, 300, 120, 6));
  assert.notStrictEqual(s1, C.giayXe(4, 10, 20, 300, 120, 6));
  assert.ok(diem(s1).length >= 12, 'đủ răng cưa');
});

test('giayXe: moi diem nam trong hop cho truoc +- doRang', function () {
  [[1, 0, 0, 200, 100, 5], [2, -40, 30, 500, 60, 12], [9, 700, 400, 90, 260, 8]].forEach(function (a) {
    var x = a[1], y = a[2], w = a[3], h = a[4], r = a[5];
    diem(C.giayXe.apply(null, a)).forEach(function (p) {
      assert.ok(p[0] >= x - r - 1e-6 && p[0] <= x + w + r + 1e-6, 'x ' + p[0]);
      assert.ok(p[1] >= y - r - 1e-6 && p[1] <= y + h + r + 1e-6, 'y ' + p[1]);
    });
  });
});

test('mau nhan canh N la mauNhan[(N-1) % 4]', function () {
  assert.deepStrictEqual([1, 2, 3, 4, 5, 6, 8, 9].map(function (n) { return C.mauCanh(n, MAU); }),
    [MAU[0], MAU[1], MAU[2], MAU[3], MAU[0], MAU[1], MAU[3], MAU[0]]);
});

test('chamLuoi la pattern SVG co id, buoc va ban kinh', function () {
  var p = C.chamLuoi('cham-1', 12, 2.5);
  assert.match(p, /^<pattern id="cham-1"/);
  assert.match(p, /width="12" height="12"/);
  assert.match(p, /patternUnits="userSpaceOnUse"/);
  assert.match(p, /<circle [^>]*r="2.5"/);
  assert.match(p, /<\/pattern>$/);
});

test('bangDinh: xoay trong +-6 do, mep rang, xac dinh theo hat', function () {
  var gocs = [];
  for (var h = 1; h <= 40; h++) {
    var b = C.bangDinh(h, 100, 50, 160);
    assert.deepStrictEqual(b, C.bangDinh(h, 100, 50, 160));
    assert.ok(Math.abs(b.goc) <= 6 + 1e-9, 'góc ' + b.goc);
    assert.ok(diem(b.points).length >= 10, 'hai đầu răng cưa');
    gocs.push(b.goc);
  }
  assert.ok(Math.min.apply(null, gocs) < -2 && Math.max.apply(null, gocs) > 2, 'góc trải cả hai phía');
  // Góc tối đa truyền vào (dải nhãn dài xoay ít hơn).
  assert.ok(Math.abs(C.bangDinh(5, 0, 0, 900, 40, 0.5).goc) <= 0.5);
});

test('nenGiay: giay kem, van feTurbulence seed = hat, 2-4 manh giay xe, cham luoi', function () {
  [1, 2, 3, 4, 5, 6, 7, 8].forEach(function (hat) {
    [NGANG, DOC].forEach(function (kho) {
      var s = C.nenGiay(hat, kho);
      assert.strictEqual(s, C.nenGiay(hat, kho));
      assert.match(s, /^<svg /);
      assert.ok(s.indexOf('viewBox="0 0 ' + kho.rong + ' ' + kho.cao + '"') > 0);
      assert.ok(s.indexOf('#f3ead7') > 0, 'giấy kem');
      assert.ok(s.indexOf('<feTurbulence') > 0 && s.indexOf('seed="' + hat + '"') > 0, 'vân theo hạt');
      assert.ok(s.indexOf('<pattern') > 0, 'chấm lưới');
      assert.ok(!/https?:|www\./.test(s.replace('http://www.w3.org/2000/svg', '')), 'không có địa chỉ web');
      var m = C.cacManh(hat, kho);
      assert.ok(m.length >= 2 && m.length <= 4, 'số mảnh ' + m.length);
    });
  });
  assert.notStrictEqual(C.nenGiay(1, NGANG), C.nenGiay(2, NGANG));
});

test('nenGiay: khong manh nao (ke ca vung cham) che vung noi dung qua 15 %', function () {
  [NGANG, DOC].forEach(function (kho) {
    var v = C.vungNoiDung(kho);
    var dt = v.w * v.h;
    for (var hat = 1; hat <= 60; hat++) {
      C.cacManh(hat, kho).concat([C.vungCham(hat, kho)]).forEach(function (m) {
        var w = Math.max(0, Math.min(m.x + m.w, v.x + v.w) - Math.max(m.x, v.x));
        var h = Math.max(0, Math.min(m.y + m.h, v.y + v.h) - Math.max(m.y, v.y));
        assert.ok(w * h <= 0.15 * dt, kho.ten + ' hạt ' + hat + ': ' + (w * h / dt).toFixed(3));
      });
    }
  });
});

test('bangTieuDe: moi dong mot dai bang dinh, lech dau dong khong qua 4 px', function () {
  var ds = C.bangTieuDe(3, [{ x: 60, y: 30, w: 900, h: 40 }, { x: 60, y: 82, w: 300, h: 40 }]);
  assert.strictEqual(ds.length, 2);
  ds.forEach(function (b, k) {
    var nua = [900, 300][k] / 2 + 14;
    assert.ok(Math.abs(Math.sin(b.goc * Math.PI / 180) * nua) <= 4 + 1e-9);
  });
});

function du(loai, truong, chuDe, them) {
  var d = { so: 3, loai: loai, thoiLuong: 10, danDau: 1.0, moc: [1.2, 3.4, 5.6, 7.0], tu: [], truong: truong,
    co: { banTay: true, mayQuay: true, chuDong: true, chuyen: null } };
  if (chuDe) { d.chuDe = chuDe; }
  Object.keys(them || {}).forEach(function (k) { d[k] = them[k]; });
  return d;
}

test('cat-dan: chu truot 0,35 s, khong som hon 0,6 s, khong ban tay, khong nay', function () {
  var ds = K['tieu-de'].muc(du('tieu-de', { chu: ['Con lắc đơn'], phu: ['Vật lí 11'] }, CAT_DAN));
  ds.filter(function (m) { return m.kieu === 'chu'; }).forEach(function (m) {
    assert.strictEqual(m.truot, true, m.id);
    assert.ok(m.batDau >= 0.6 - 1e-9, m.id + ' ' + m.batDau);
    assert.strictEqual(m.thoiLuong, 0.35);
    assert.strictEqual(m.tay, false);
    assert.ok(!m.nay, 'không nảy chữ');
  });
  // viet-tay giữ nguyên: chữ viết theo tốc độ, tiêu đề nảy.
  var cu = K['tieu-de'].muc(du('tieu-de', { chu: ['Con lắc đơn'], phu: ['Vật lí 11'] }));
  var c = cu.filter(function (m) { return m.id === 'chu'; })[0];
  assert.ok(!c.truot && c.nay && c.batDau === 0.3);
});

test('cat-dan: net nhanh ve trong min(thoiLuong, 0,5) s va day x1,4', function () {
  var B = V.tao(du('khai-niem', {}, CAT_DAN));
  var n = B.net('a', 'M0 0 L10 10', 1, 2);
  assert.strictEqual(n.thoiLuong, 0.5);
  assert.ok(Math.abs(n.day - 5.6) < 1e-9);
  var n2 = B.net('b', 'M0 0 L10 10', 1, 0.3, { day: 5 });
  assert.strictEqual(n2.thoiLuong, 0.3);
  assert.ok(Math.abs(n2.day - 7) < 1e-9);
  var cu = V.tao(du('khai-niem', {})).net('a', 'M0 0 L10 10', 1, 2);
  assert.strictEqual(cu.thoiLuong, 2);
  assert.strictEqual(cu.day, 4);
});

test('cat-dan: tieu de canh la nhan bang dinh o 0,4 s, goc trai tren o tieu-de, khong gach chan', function () {
  var ds = K['quy-trinh'].muc(du('quy-trinh', { 'tieu-de': ['Các bước'], buoc: ['Một', 'Hai'] }, CAT_DAN));
  var td = ds.filter(function (m) { return m.id === 'tieu-de'; })[0];
  var o = V.o('tieu-de');
  assert.strictEqual(td.bang, true);
  assert.strictEqual(td.batDau, 0.4);
  assert.strictEqual(td.x, o.x);
  assert.strictEqual(td.y, o.y);
  assert.ok(!td.day, 'nhãn nằm trên đỉnh ô');
  assert.strictEqual(ds.filter(function (m) { return m.id === 'gach'; }).length, 0);
  // viet-tay: tiêu đề và gạch chân như cũ.
  var cu = K['quy-trinh'].muc(du('quy-trinh', { 'tieu-de': ['Các bước'], buoc: ['Một', 'Hai'] }));
  assert.strictEqual(cu.filter(function (m) { return m.id === 'gach'; }).length, 1);
  assert.ok(!cu[0].bang);
});

test('cat-dan: hinh chinh la sticker o 0,3 s, 0,45 s, xoay (prng(so)()*6-3) do', function () {
  var h = { phanTu: [{ the: 'circle', thuocTinh: { cx: 12, cy: 12, r: 8 } }], viewBox: '0 0 24 24' };
  var ds = K['khai-niem'].muc(du('khai-niem', { 'thuat-ngu': ['A'], 'dinh-nghia': ['B'] }, CAT_DAN, { hinh: h }));
  var m = ds.filter(function (x) { return x.kieu === 'hinh'; })[0];
  assert.strictEqual(m.sticker, true);
  assert.strictEqual(m.batDau, 0.3);
  assert.strictEqual(m.thoiLuong, 0.45);
  assert.strictEqual(m.tay, false);
  assert.ok(Math.abs(m.goc - (C.prng(3)() * 6 - 3)) < 1e-9);
  // minh-hoa: ba sticker, góc lần lượt theo cùng một dãy prng(so).
  var r = C.prng(3);
  var mh = K['minh-hoa'].muc(du('minh-hoa', { 'tieu-de': ['Ba hình'] }, CAT_DAN,
    { hinhs: [{ ten: 'a', nhan: 'A', phanTu: h.phanTu, viewBox: h.viewBox }, { ten: 'b', nhan: 'B', phanTu: h.phanTu, viewBox: h.viewBox }] }));
  mh.filter(function (x) { return x.kieu === 'hinh'; }).forEach(function (x) {
    assert.ok(Math.abs(x.goc - (r() * 6 - 3)) < 1e-9);
  });
});

test('cat-dan: su kien am thanh khong co tieng but cho chu truot va sticker', function () {
  var d = du('y-tung-y', { 'tieu-de': ['Hai ý'], y: ['Một', 'Hai'] }, CAT_DAN);
  var but = V.suKienCua(d).filter(function (e) { return e.loai === 'but'; });
  var nets = K['y-tung-y'].muc(d).filter(function (m) { return m.kieu === 'net'; });
  // Chỉ còn tiếng bút của các nét (chấm đầu ý), không có của chữ.
  but.forEach(function (e) {
    assert.ok(nets.some(function (m) { return Math.abs(m.batDau - e.t) < 0.002; }), 'bút lúc ' + e.t);
  });
});

test('khong co chuDe (du lieu cu) la viet-tay', function () {
  var a = K['y-tung-y'].muc(du('y-tung-y', { 'tieu-de': ['Hai ý'], y: ['Một', 'Hai'] }));
  var b = K['y-tung-y'].muc(du('y-tung-y', { 'tieu-de': ['Hai ý'], y: ['Một', 'Hai'] }, VIET_TAY));
  assert.deepStrictEqual(a, b);
});
