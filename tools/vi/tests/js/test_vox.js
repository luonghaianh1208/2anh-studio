'use strict';
// Runtime Vox (runtime/vox.js): hàm thuần đặt ô, xếp chồng, kiểu vào, thị sai và chuyển lia.
var test = require('node:test');
var assert = require('node:assert');
var path = require('node:path');

var RT = path.join(__dirname, '..', '..', 'video_ma_parts', 'runtime');
require(path.join(RT, 'kho.js'));
require(path.join(RT, 'cat-dan.js'));
require(path.join(RT, 'vox.js'));
var V = globalThis.THI_VOX;
var NGANG = { ten: 'ngang', rong: 1280, cao: 720, day: 620 };
var DOC = { ten: 'doc', rong: 720, cao: 1280, day: 1080 };

test('ô theo bố cục', function () {
  assert.deepStrictEqual(V.oCua('hai-ben', 'trai', NGANG), { x: 40, y: 90, w: 580, h: 500 });
  assert.deepStrictEqual(V.oCua('dan-hang', '4', DOC), { x: 60, y: 825, w: 600, h: 215 });
  assert.throws(function () { V.oCua('hai-ben', 'trai', DOC); });
});

test('xếp chồng tất định, trong khung, trên vạch phụ đề', function () {
  [[NGANG, 620], [DOC, 1080]].forEach(function (kd) {
    var kho = kd[0];
    for (var n = 1; n <= 5; n++) {
      for (var k = 0; k < n; k++) {
        var a = V.xepChong(k, n, 3, kho), b = V.xepChong(k, n, 3, kho);
        assert.deepStrictEqual(a, b);
        assert.ok(a.x >= 0 && a.y >= 0 && a.x + a.w <= kho.rong && a.y + a.h <= kd[1], kho.ten + ' ' + JSON.stringify(a));
        assert.ok(Math.abs(a.goc) <= 8);
      }
    }
  });
  assert.notDeepStrictEqual(V.xepChong(0, 3, 3, NGANG), V.xepChong(0, 3, 4, NGANG));
});

test('kiểu vào: êm, trượt ngắn kèm mờ dần, không nảy', function () {
  ['anh-cat', 'anh-khung', 'anh-phu', 'the', 'nhan', 'dau', 'chu', 'so', 'mui-ten'].forEach(function (vat) {
    var cuoi = V.vao(vat, 1);
    assert.deepStrictEqual([cuoi.dx, cuoi.dy, cuoi.s, cuoi.goc, cuoi.a], [0, 0, 1, cuoi.goc, 1], vat);
    assert.strictEqual(cuoi.goc, vat === 'dau' ? -4 : 0, vat);
    assert.strictEqual(V.vao(vat, 0).a, 0, vat + ' bắt đầu trong suốt');
    for (var p = 0; p <= 1.0001; p += 0.05) {
      var v = V.vao(vat, p);
      assert.ok(Math.abs(v.dx) <= 40 && Math.abs(v.dy) <= 36, vat + ' chỉ trượt ngắn');
      assert.ok(v.s >= 1 - 1e-9 && v.s <= 1.15 + 1e-9, vat + ' không nảy quá đích');
      assert.ok(v.a >= 0 && v.a <= 1);
    }
  });
  assert.strictEqual(V.vao('dau', 0).s, 1.15, 'con dấu thu nhỏ nhẹ từ 1,15, không đập');
});

test('máy quay: không phóng, không xoay, không rung; chỉ có thị sai trôi ngang chậm', function () {
  assert.deepStrictEqual(V.camera(0, 8), { u: 0 });
  assert.deepStrictEqual(V.camera(8, 8), { u: 1 });
  assert.strictEqual(V.rung, undefined, 'đã bỏ rung máy');
  var dau = V.lopCamera('xa', V.camera(0, 8), 1.5), cuoi = V.lopCamera('xa', V.camera(8, 8), 1.5);
  assert.deepStrictEqual(Object.keys(dau).sort(), ['x', 'y']);
  assert.strictEqual(dau.x, V.TROI.xa);
  assert.strictEqual(cuoi.x, -V.TROI.xa);
  assert.ok(V.TROI.xa <= 16, 'trôi ít hơn lề nền 16 điểm CSS để không hở mép');
  [0, 1.3, 2.7, 4.1, 6.6, 8].forEach(function (t) {
    var cam = V.camera(t, 8);
    var xa = V.lopCamera('xa', cam, 1.5), giua = V.lopCamera('giua', cam, 1.5), gan = V.lopCamera('gan', cam, 1.5);
    assert.deepStrictEqual(gan, { x: 0, y: 0 }, 'chữ đứng yên');
    assert.ok(Math.abs(xa.x) >= Math.abs(giua.x), 'nền trôi nhiều hơn ảnh');
    assert.strictEqual(xa.y, 0);
    [xa, giua].forEach(function (l) {
      assert.ok(Math.abs(l.x * 1.5 - Math.round(l.x * 1.5)) < 1e-9, 'dời theo bước điểm ảnh thiết bị');
      assert.ok(!Object.is(l.x, -0));
    });
  });
});

test('số chạy: hàng nghìn dấu chấm, thập phân dấu phẩy', function () {
  assert.strictEqual(V.dinhDangSo(1250.5, 1), '1.250,5');
  assert.strictEqual(V.dinhDangSo(1000000, 0), '1.000.000');
  assert.strictEqual(V.dinhDangSo(85, 0), '85');
});

test('chuyển lia: trượt hết khung trong 0,35 giây', function () {
  assert.strictEqual(V.chuyenLia(0, NGANG).dx, 0);
  assert.strictEqual(V.chuyenLia(1, NGANG).dx, -1280);
  assert.strictEqual(V.chuyenLia(1, DOC).dx, -720);
  assert.ok(V.chuyenLia(0.5, NGANG).mo > 20);
});

test('vật nhiều mục: các mục hiện nối nhau, mục cuối xong đúng lúc vật xong', function () {
  [2, 3, 5].forEach(function (n) {
    for (var i = 0; i < n; i++) {
      assert.strictEqual(V.tienDoMuc(0, i, n), 0, 'chưa hiện ở đầu');
      assert.strictEqual(V.tienDoMuc(1, i, n), 1, 'xong hết ở cuối');
    }
    assert.ok(V.tienDoMuc(0.3, 0, n) > V.tienDoMuc(0.3, n - 1, n), 'mục đầu đi trước mục cuối');
    assert.strictEqual(V.tienDoMuc(0.999, n - 1, n) < 1, true);
  });
});

test('kim tự tháp: đỉnh hẹp, đáy rộng đúng bề ngang ô, mép tầng liền nhau', function () {
  var n = 4, w = 600;
  assert.strictEqual(V.tangThap(n - 1, n, w).duoi, w);
  assert.ok(V.tangThap(0, n, w).tren < w * 0.4);
  for (var i = 0; i + 1 < n; i++) { assert.strictEqual(V.tangThap(i, n, w).duoi, V.tangThap(i + 1, n, w).tren); }
});

test('chu trình: điểm đầu ở đỉnh, quay theo chiều kim đồng hồ', function () {
  assert.deepStrictEqual(V.diemTron(100, 100, 50, 0), [100, 50]);
  assert.deepStrictEqual(V.diemTron(100, 100, 50, 90), [150, 100]);
  assert.deepStrictEqual(V.diemTron(100, 100, 50, 180), [100, 150]);
  ['cot', 'chu-trinh', 'moc', 'thap'].forEach(function (vat) { assert.ok(V.DAI[vat] >= 1, vat); });
});
