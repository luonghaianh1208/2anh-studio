'use strict';
// Runtime Vox (runtime/vox.js): hàm thuần đặt ô, xếp chồng, kiểu vào, camera, rung máy và chuyển lia.
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
  assert.deepStrictEqual(V.oCua('hai-ben', 'trai', NGANG), { x: 80, y: 120, w: 520, h: 420 });
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

test('kiểu vào: bắt đầu ngoài, kết thúc đúng chỗ, có nảy', function () {
  ['anh-cat', 'anh-khung', 'the', 'nhan', 'dau', 'chu', 'so', 'mui-ten'].forEach(function (vat) {
    var cuoi = V.vao(vat, 1);
    assert.deepStrictEqual([cuoi.dx, cuoi.dy, cuoi.s, cuoi.goc, cuoi.a], [0, 0, 1, cuoi.goc, 1], vat);
    assert.strictEqual(cuoi.goc, vat === 'dau' ? -4 : 0, vat);
    assert.ok(V.vao(vat, 0).a <= 1);
  });
  var vuot = Math.max.apply(null, [0.6, 0.7, 0.8].map(function (p) { return V.vao('anh-cat', p).s; }));
  assert.ok(vuot > 1, 'easeOutBack phải vượt quá 1 rồi về 1');
  assert.ok(V.vao('anh-cat', 0).dy <= -400, 'ảnh cắt rơi từ trên xuống');
});

test('camera đẩy vào chậm, tối đa 1,06 và ±4°', function () {
  var c0 = V.camera(0, 8, 2), c1 = V.camera(8, 8, 2);
  assert.strictEqual(c0.s, 1);
  assert.ok(Math.abs(c1.s - 1.06) < 1e-9);
  for (var t = 0; t <= 8; t += 0.5) {
    var c = V.camera(t, 8, 2);
    assert.ok(Math.abs(c.ry) <= 4);
    assert.ok(Math.abs(c.rx) <= 1.6 + 1e-9);
  }
  assert.ok(Object.is(c0.ry, 0) && Object.is(c0.tx, 0), 'không có -0');
});

test('lớp sâu: đẩy vào bằng zoom theo bước 0,002 (gần đủ, giữa 75 %, xa không), dời theo bước điểm ảnh', function () {
  var cam = V.camera(8, 8, 2);
  var khong = { x: 0, y: 0 };
  var gan = V.lopCamera('gan', cam, khong, 1.5), giua = V.lopCamera('giua', cam, khong, 1.5), xa = V.lopCamera('xa', cam, khong, 1.5);
  [gan, giua, xa].forEach(function (l) { assert.deepStrictEqual(Object.keys(l).sort(), ['x', 'y', 'z']); });
  assert.ok(Math.abs(gan.z - 1.06) < 1e-9);
  assert.ok(giua.z > 1 && giua.z < gan.z);
  assert.strictEqual(xa.z, 1);
  [0, 1.3, 2.7, 4.1, 6.6].forEach(function (t) {
    var z = V.lopCamera('gan', V.camera(t, 8, 2), khong, 1.5).z;
    assert.ok(Math.abs(z * 500 - Math.round(z * 500)) < 1e-6, 'bước 0,002: ' + z);
  });
  // Gốc đẩy vào ở giữa vạch phụ đề: điểm đó đứng yên (độ dời bù đúng phần phóng, sai không quá nửa điểm ảnh).
  var NG = { ten: 'ngang', rong: 1280, cao: 720, day: 620 };
  var l = V.lopCamera('gan', V.camera(8, 8, 2), khong, 1.5, NG);
  assert.ok(Math.abs(l.x + 640 * l.z - 640) <= 1 / 3 + 1e-9 && Math.abs(l.y + 620 * l.z - 620) <= 1 / 3 + 1e-9);
  assert.ok(cam.ry !== 0);
  assert.strictEqual(gan.x, 0);
  assert.ok(Math.abs(xa.x) > Math.abs(giua.x) && Math.abs(giua.x) > 0, 'thị sai: lớp càng xa càng dời nhiều');
  assert.ok(xa.x * giua.x > 0);
  [gan, giua, xa].forEach(function (l) {
    assert.ok(Math.abs(l.x * 1.5 - Math.round(l.x * 1.5)) < 1e-9 && Math.abs(l.y * 1.5 - Math.round(l.y * 1.5)) < 1e-9);
  });
  assert.deepStrictEqual(V.lopCamera('giua', V.camera(0, 8, 2), khong, 1), { x: 0, y: 0, z: 1 });
  // Rung máy dời mọi lớp như nhau.
  assert.strictEqual(V.lopCamera('gan', V.camera(0, 8, 2), { x: 3, y: -2 }, 1).x, 3);
});

test('số chạy: hàng nghìn dấu chấm, thập phân dấu phẩy', function () {
  assert.strictEqual(V.dinhDangSo(1250.5, 1), '1.250,5');
  assert.strictEqual(V.dinhDangSo(1000000, 0), '1.000.000');
  assert.strictEqual(V.dinhDangSo(85, 0), '85');
});

test('rung máy ngắn sau mỗi cú đập, tối đa 6 px', function () {
  assert.deepStrictEqual(V.rung(1.0, [2.0], 1), { x: 0, y: 0 });
  var r = V.rung(2.05, [2.0], 1);
  assert.ok(Math.hypot(r.x, r.y) > 0 && Math.hypot(r.x, r.y) <= 6);
  assert.deepStrictEqual(V.rung(2.2, [2.0], 1), { x: 0, y: 0 });
});

test('chuyển lia: trượt hết khung trong 0,35 giây', function () {
  assert.strictEqual(V.chuyenLia(0, NGANG).dx, 0);
  assert.strictEqual(V.chuyenLia(1, NGANG).dx, -1280);
  assert.strictEqual(V.chuyenLia(1, DOC).dx, -720);
  assert.ok(V.chuyenLia(0.5, NGANG).mo > 20);
});
