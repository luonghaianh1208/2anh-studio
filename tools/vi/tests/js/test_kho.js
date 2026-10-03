'use strict';
var test = require('node:test');
var assert = require('node:assert');
var path = require('node:path');

var RT = path.join(__dirname, '..', '..', 'video_ma_parts', 'runtime');
require(path.join(RT, 'kho.js'));
require(path.join(RT, 'ban-tay.js'));
require(path.join(RT, 'may-quay.js'));
require(path.join(RT, 'chuyen-canh.js'));
var K = globalThis.THI_KHO;
var T = globalThis.THI_BAN_TAY;
var Q = globalThis.THI_MAY_QUAY;
var C = globalThis.THI_CHUYEN;

var NGANG = { ten: 'ngang', rong: 1280, cao: 720, day: 620, tamX: 640, tamY: 310 };
var DOC = { ten: 'doc', rong: 720, cao: 1280, day: 1080, tamX: 360, tamY: 540 };

function gan(a, b, sai) { return Math.abs(a - b) < (sai || 1e-6); }
function muc(id, batDau, thoiLuong) { return { id: id, kieu: 'chu', batDau: batDau, thoiLuong: thoiLuong }; }

test('kho: mac dinh la kho ngang cu; dat() gan V.kho', function () {
  globalThis.THI_VIDEO = {};
  assert.deepStrictEqual(K.dat(undefined), K.NGANG);
  assert.deepStrictEqual(K.NGANG, NGANG);
  assert.strictEqual(K.dat(DOC), globalThis.THI_VIDEO.kho);
  assert.deepStrictEqual(K.lay(), DOC);
  K.dat(null);
  assert.deepStrictEqual(K.lay(), NGANG);
  delete globalThis.THI_VIDEO;
});

var TEN_O = ['tieu-de', 'noi-dung', 'noi-dung-hep', 'cot-phu', 'anh-lon', 'hai-cot-trai', 'hai-cot-phai', 'bieu-do', 'so-do',
  'dong-thoi-gian', 'cau-hoi', 'thi-nghiem', 'the', 'tai-lieu', 'nhan-vat'];

test('o bo cuc: kho ngang du ten, moi o nam trong 1280x720 va day o <= vach phu de', function () {
  K.dat(NGANG);
  var bang = require(path.join(RT, 'o-bo-cuc.json'));
  assert.deepStrictEqual(Object.keys(bang), ['ngang', 'doc']);
  TEN_O.forEach(function (ten) { assert.ok(bang.ngang[ten], 'thieu o ' + ten); });
  Object.keys(bang.ngang).forEach(function (ten) {
    var o = K.o(ten);
    assert.deepStrictEqual(o, bang.ngang[ten]);
    assert.deepStrictEqual(Object.keys(o).sort(), ['h', 'w', 'x', 'y'], ten);
    assert.ok(o.x >= 0 && o.y >= 0 && o.w > 0 && o.h > 0 && o.x + o.w <= 1280 && o.y + o.h <= 720, ten + ' ' + JSON.stringify(o));
    // Ô chú thích ảnh giữ đúng toạ độ vi.11 (đáy 625, lố vạch 5; chữ một dòng nằm trên vạch) để hình không đổi.
    if (phuKin(ten)) { assert.deepStrictEqual(o, { x: 0, y: 0, w: 1280, h: 720 }, ten); return; }
    assert.ok(o.y + o.h <= NGANG.day + (ten === 'chu-thich' ? 5 : 0), ten + ' xuong vung phu de ' + JSON.stringify(o));
  });
});

test('o bo cuc: gia tri ngang chep dung toa do vi.11', function () {
  K.dat(NGANG);
  assert.deepStrictEqual(K.o('cot-phu'), { x: 900, y: 200, w: 320, h: 380 });
  assert.deepStrictEqual(K.o('anh-lon'), { x: 80, y: 70, w: 1120, h: 490 });
  assert.deepStrictEqual(K.o('tieu-de'), { x: 60, y: 30, w: 1160, h: 116 });
  assert.deepStrictEqual(K.o('noi-dung'), { x: 60, y: 190, w: 1160, h: 430 });
  assert.deepStrictEqual(K.o('noi-dung-hep'), { x: 60, y: 190, w: 800, h: 430 });
});

test('o bo cuc: ten la thi bao loi; ban tra ve la ban sao', function () {
  K.dat(NGANG);
  assert.throws(function () { K.o('cot-phai-khong-co'); }, /cot-phai-khong-co/);
  var o = K.o('cot-phu');
  o.x = 0;
  assert.strictEqual(K.o('cot-phu').x, 900);
});

// Ô nền toàn cảnh của Vox cố ý phủ kín khung (nằm dưới phụ đề); ô hai bên của Vox ở khổ dọc xếp trên/dưới nên khác tên.
function phuKin(ten) { return /^vox-.*-nen$/.test(ten); }
var VOX_HAI_BEN = { ngang: ['vox-hai-ben-trai', 'vox-hai-ben-phai'], doc: ['vox-hai-ben-tren', 'vox-hai-ben-duoi'] };

function chong(a, b) { return a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h; }

test('o bo cuc doc: cung ten voi kho ngang, moi o trong 720x1280, day o <= 1080, le 48 hoac rong hon', function () {
  var bang = require(path.join(RT, 'o-bo-cuc.json'));
  function boHaiBen(kho) { return Object.keys(bang[kho]).filter(function (t) { return VOX_HAI_BEN[kho].indexOf(t) < 0; }).sort(); }
  assert.deepStrictEqual(boHaiBen('doc'), boHaiBen('ngang'));
  ['ngang', 'doc'].forEach(function (kho) {
    VOX_HAI_BEN[kho].forEach(function (t) { assert.ok(bang[kho][t], kho + ' thieu ' + t); });
  });
  K.dat(DOC);
  Object.keys(bang.doc).forEach(function (ten) {
    var o = K.o(ten);
    assert.deepStrictEqual(o, bang.doc[ten]);
    assert.ok(o.x >= 0 && o.y >= 0 && o.w > 0 && o.h > 0 && o.x + o.w <= 720, ten + ' ' + JSON.stringify(o));
    if (phuKin(ten)) { assert.deepStrictEqual(o, { x: 0, y: 0, w: 720, h: 1280 }, ten); return; }
    assert.ok(o.y + o.h <= DOC.day, ten + ' xuong vung phu de ' + JSON.stringify(o));
  });
  K.dat(NGANG);
});

test('o bo cuc doc: quy tac cua ban thiet ke', function () {
  K.dat(DOC);
  var td = K.o('tieu-de'), nd = K.o('noi-dung'), hep = K.o('noi-dung-hep'), cot = K.o('cot-phu');
  assert.strictEqual(td.y, 110);
  assert.strictEqual(td.x, 48);
  assert.strictEqual(td.x + td.w, 720 - 48);
  assert.deepStrictEqual(cot, { x: 160, y: 640, w: 400, h: 380 });
  // Nội dung hẹp là ô nội dung, chiều cao tới y 620 (cột phụ thành khối dưới nội dung).
  assert.deepStrictEqual([hep.x, hep.y, hep.w, hep.y + hep.h], [nd.x, nd.y, nd.w, 620]);
  assert.ok(!chong(hep, cot) && !chong(td, nd));
  // Hai cột xếp chồng: trên rồi dưới, cùng bề rộng.
  var a = K.o('hai-cot-trai'), b = K.o('hai-cot-phai');
  assert.ok(a.y + a.h <= b.y && a.x === b.x && a.w === b.w, JSON.stringify([a, b]));
  // Biểu đồ, sơ đồ, dòng thời gian dùng gần hết bề rộng (từ lề 48 trở ra).
  ['bieu-do', 'so-do', 'dong-thoi-gian'].forEach(function (ten) {
    assert.ok(K.o(ten).w >= 720 - 2 * 48 - 48, ten + ' ' + JSON.stringify(K.o(ten)));
  });
  // Dòng tài liệu không đè ô nội dung hẹp. Thẻ nằm ở đỉnh ô nội dung, ngay dưới tiêu đề: cảnh có thẻ dời nội dung
  // xuống dưới thẻ (khung-video B.o), nên thẻ chỉ cần không đè tiêu đề và cột phụ (test_the.js).
  assert.ok(!chong(K.o('tai-lieu'), hep));
  assert.ok(!chong(K.o('the'), td) && !chong(K.o('the'), cot));
  assert.strictEqual(K.o('the').y, nd.y);
  K.dat(NGANG);
});

test('o bo cuc: kho doc khong bao gio doc o ngang; kho la thi bao loi', function () {
  var bang = require(path.join(RT, 'o-bo-cuc.json'));
  K.dat(DOC);
  Object.keys(bang.doc).forEach(function (ten) { assert.deepStrictEqual(K.o(ten), bang.doc[ten], ten); });
  assert.notDeepStrictEqual(K.o('cot-phu'), bang.ngang['cot-phu']);
  K.dat({ ten: 'vuong', rong: 1080, cao: 1080, day: 980, tamX: 540, tamY: 490 });
  assert.throws(function () { K.o('tieu-de'); }, /vuong/);
  K.dat(NGANG);
});

test('ban tay: gie lau bang o giua vung noi dung theo kho (kho ngang y 380 nhu cu)', function () {
  K.dat(NGANG);
  var v = T.viTri([], 0.25, function () { return { x: 0, y: 0 }; }, T.NGHI, { chuyen: 'lau-bang', giayLau: 0.5 });
  assert.strictEqual(v.y, 380);
  K.dat(DOC);
  v = T.viTri([], 0.25, function () { return { x: 0, y: 0 }; }, T.NGHI, { chuyen: 'lau-bang', giayLau: 0.5 });
  assert.strictEqual(v.y, 610);
  K.dat(NGANG);
});

test('kho ngang: may quay dua tam hop nho ve (640, 310)', function () {
  K.dat(NGANG);
  var hop = { a: { x: 600, y: 290, w: 80, h: 40 } };
  var s = Q.tinh([muc('a', 1, 3)], hop, 3, 10, {});
  assert.ok(gan(s.z * 640 + s.tx, 640) && gan(s.z * 310 + s.ty, 310), JSON.stringify(s));
});

test('kho doc: tam la (360, 540), khung nhin luon nam trong [0,720]x[0,1280]', function () {
  K.dat(DOC);
  var hop = { a: { x: 320, y: 520, w: 80, h: 40 } };
  var s = Q.tinh([muc('a', 1, 3)], hop, 3, 10, {});
  assert.ok(gan(s.z * 360 + s.tx, 360) && gan(s.z * 540 + s.ty, 540), JSON.stringify(s));
  var cacHop = [];
  for (var x = 0; x <= 640; x += 160) {
    for (var y = 0; y <= 1180; y += 118) { cacHop.push({ x: x, y: y, w: 80, h: 60 }); }
  }
  cacHop.push({ x: 0, y: 0, w: 720, h: 1000 }, { x: 600, y: 1000, w: 120, h: 60 });
  cacHop.forEach(function (h) {
    for (var t = 0; t < 10; t += 0.25) {
      var c = Q.tinh([muc('a', 1, 3)], { a: h }, t, 10, {});
      var trai = -c.tx / c.z, tren = -c.ty / c.z;
      var phai = (720 - c.tx) / c.z, duoi = (1280 - c.ty) / c.z;
      var tt = JSON.stringify({ h: h, t: t, c: c });
      assert.ok(trai >= -1e-6 && tren >= -1e-6 && phai <= 720 + 1e-6 && duoi <= 1280 + 1e-6, tt);
    }
  });
  // Cảnh thí nghiệm: đẩy nhẹ quanh tâm khung dọc.
  var d = Q.tinh([], {}, 5, 10, { day: true });
  assert.ok(gan(d.tx, 360 * (1 - d.z)) && gan(d.ty, 640 * (1 - d.z)), JSON.stringify(d));
  K.dat(NGANG);
});

test('ban tay: cho nghi va gie lau bang theo kho', function () {
  K.dat(NGANG);
  assert.deepStrictEqual(T.NGHI, { x: 1220, y: 760 });
  var v = T.viTri([], 0.25, function () { return { x: 0, y: 0 }; }, T.NGHI, { chuyen: 'lau-bang', giayLau: 0.5 });
  assert.ok(gan(v.x, -120 + 1400 * 0.5), JSON.stringify(v));
  K.dat(DOC);
  assert.deepStrictEqual(T.NGHI, { x: 660, y: 1320 });
  v = T.viTri([], 0.5, function () { return { x: 0, y: 0 }; }, T.NGHI, { chuyen: 'lau-bang', giayLau: 0.5 });
  assert.ok(gan(v.x, 720), JSON.stringify(v));
  v = T.viTri([], 0.25, function () { return { x: 0, y: 0 }; }, T.NGHI, { chuyen: 'lau-bang', giayLau: 0.5 });
  assert.ok(gan(v.x, -120 + 840 * 0.5), JSON.stringify(v));
  K.dat(NGANG);
});

test('chuyen canh: mep lau va hai nua man theo be rong kho', function () {
  K.dat(DOC);
  assert.strictEqual(C.trangThai('lau-bang', 0.5, 0.5).nen.clipPath, 'inset(0 0 0 720px)');
  assert.strictEqual(C.trangThai('mo-man', 0, 0.5).nen.clipPath, 'inset(0 360px 0 0)');
  assert.ok(C.trangThai('phong', 0.25, 0.5).nen.transform.indexOf('translate(360px,640px)') === 0);
  K.dat(NGANG);
  assert.strictEqual(C.trangThai('mo-man', 0, 0.5).nen.clipPath, 'inset(0 640px 0 0)');
});
