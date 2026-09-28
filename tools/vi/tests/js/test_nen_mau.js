'use strict';
// Kho 8 nền mẫu vẽ bằng mã (runtime/nen-mau.js): đúng tên, SVG kín khổ ở cả hai khổ, không chữ, không tham chiếu
// ngoài, xác định theo hạt giống; tên lạ là lỗi.
var test = require('node:test');
var assert = require('node:assert');
var path = require('node:path');

var RT = path.join(__dirname, '..', '..', 'video_ma_parts', 'runtime');
require(path.join(RT, 'cat-dan.js'));
require(path.join(RT, 'nen-mau.js'));
var N = globalThis.THI_NEN_MAU;

var TEN = ['giay', 'bau-troi', 'vu-tru', 'lop-hoc', 'phong-thi-nghiem', 'thanh-pho', 'dong-que', 'vong-tron'];
var NGANG = { ten: 'ngang', rong: 1280, cao: 720, day: 620, tamX: 640, tamY: 310 };
var DOC = { ten: 'doc', rong: 720, cao: 1280, day: 1080, tamX: 360, tamY: 540 };

test('tam nen dung ten va thu tu', function () {
  assert.deepStrictEqual(N.TEN, TEN);
});

test('moi nen x 2 kho: SVG kin kho, viewBox dung, khong chu, khong tham chieu ngoai', function () {
  TEN.forEach(function (ten) {
    [NGANG, DOC].forEach(function (kho) {
      var s = N.ve(ten, kho, 3);
      var nhan = ten + ' ' + kho.ten;
      assert.ok(/^<svg\b/.test(s) && /<\/svg>$/.test(s), nhan);
      var mo = s.match(/^<svg[^>]*>/)[0];
      assert.ok(mo.indexOf('viewBox="0 0 ' + kho.rong + ' ' + kho.cao + '"') >= 0, nhan + ' viewBox');
      assert.ok(mo.indexOf('width="' + kho.rong + '"') >= 0 && mo.indexOf('height="' + kho.cao + '"') >= 0, nhan + ' kho');
      assert.ok(!/<text\b/.test(s), nhan + ' co <text>');
      assert.ok(!/<image\b|href=|https?:/.test(s.replace('http://www.w3.org/2000/svg', '')), nhan + ' tham chieu ngoai');
      assert.ok(!/NaN|undefined/.test(s), nhan + ' so hong');
      assert.ok(s.length > 500, nhan + ' qua ngan');
    });
  });
});

test('cung hat ra cung chuoi, hat khac ra chuoi khac (nen co PRNG)', function () {
  TEN.forEach(function (ten) {
    [NGANG, DOC].forEach(function (kho) {
      assert.strictEqual(N.ve(ten, kho, 5), N.ve(ten, kho, 5), ten + ' ' + kho.ten);
    });
  });
  TEN.forEach(function (ten) {
    [NGANG, DOC].forEach(function (kho) {
      assert.notStrictEqual(N.ve(ten, kho, 1), N.ve(ten, kho, 2), ten + ' ' + kho.ten);
    });
  });
});

// Vị trí tương đối (x/rộng, y/cao) của phần tử đầu tiên có màu `mau` (circle: tâm; rect: góc trên trái).
function viTri(svg, mau, kho) {
  var m = svg.match(new RegExp('<(circle|rect) ([^>]*)fill="' + mau + '"'));
  assert.ok(m, 'khong thay ' + mau);
  function lay(ten) { return +m[2].match(new RegExp('\\b' + ten + '="([-0-9.]+)"'))[1]; }
  return m[1] === 'circle' ? [lay('cx') / kho.rong, lay('cy') / kho.cao] : [lay('x') / kho.rong, lay('y') / kho.cao];
}

test('kho doc bo tri lai (vi tri tuong doi khac), khong co gian ban kho ngang', function () {
  TEN.forEach(function (ten) {
    var ngang = N.ve(ten, NGANG, 4).replace(/^<svg[^>]*>/, '');
    var doc = N.ve(ten, DOC, 4).replace(/^<svg[^>]*>/, '');
    assert.notStrictEqual(ngang, doc, ten);
  });
  // Mốc nhận ra được: hành tinh, khung bảng, mặt trời, vỉa hè; co giãn thì vị trí tương đối giữ nguyên.
  [['vu-tru', '#eea56a'], ['lop-hoc', '#a9723f'], ['dong-que', '#ffd166'], ['thanh-pho', '#ddd3c4']].forEach(function (c) {
    var a = viTri(N.ve(c[0], NGANG, 4), c[1], NGANG), b = viTri(N.ve(c[0], DOC, 4), c[1], DOC);
    assert.ok(Math.abs(a[0] - b[0]) > 0.02 || Math.abs(a[1] - b[1]) > 0.02, c[0] + ' ' + JSON.stringify([a, b]));
  });
});

test('giay dung lai THI_CAT_DAN.nenGiay', function () {
  assert.strictEqual(N.ve('giay', NGANG, 7), globalThis.THI_CAT_DAN.nenGiay(7, NGANG));
});

test('ten la nem loi', function () {
  assert.throws(function () { N.ve('bien', NGANG, 1); }, /bien/);
  assert.throws(function () { N.ve('', DOC, 1); });
});
