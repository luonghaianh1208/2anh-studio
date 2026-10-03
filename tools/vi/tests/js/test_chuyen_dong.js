'use strict';
var test = require('node:test');
var assert = require('node:assert');
var path = require('node:path');

var RT = path.join(__dirname, '..', '..', 'video_ma_parts', 'runtime');
require(path.join(RT, 'kho.js'));
require(path.join(RT, 'ban-tay.js'));
require(path.join(RT, 'may-quay.js'));
var T = globalThis.THI_BAN_TAY;
var Q = globalThis.THI_MAY_QUAY;
var NGHI = { x: 1220, y: 760 };

// Ngòi giả: mỗi mục có đoạn thẳng riêng; điểm ngòi chạy từ đầu tới cuối đoạn theo p.
var DUONG = { a: [[100, 100], [300, 100]], b: [[100, 300], [500, 300]], c: [[700, 200], [900, 400]] };
function ngoi(m, p) {
  var d = DUONG[m.id];
  return { x: d[0][0] + (d[1][0] - d[0][0]) * p, y: d[0][1] + (d[1][1] - d[0][1]) * p };
}
function muc(id, batDau, thoiLuong, tuy) {
  var m = { id: id, kieu: 'chu', batDau: batDau, thoiLuong: thoiLuong };
  Object.keys(tuy || {}).forEach(function (k) { m[k] = tuy[k]; });
  return m;
}
function gan(a, b, sai) { return Math.abs(a - b) < (sai || 1e-9); }

test('ban tay: xac dinh theo t', function () {
  var ds = [muc('a', 1, 1), muc('b', 2.4, 1), muc('c', 5, 1)];
  for (var t = 0; t < 8; t += 0.137) {
    assert.deepStrictEqual(T.viTri(ds, t, ngoi, NGHI), T.viTri(ds, t, ngoi, NGHI));
  }
});

test('ban tay: dang ve thi o dung ngoi cua muc do', function () {
  var ds = [muc('a', 1, 1), muc('b', 2.4, 1)];
  var v = T.viTri(ds, 1.5, ngoi, NGHI);
  assert.strictEqual(v.hien, true);
  assert.strictEqual(v.kieu, 'but');
  assert.ok(gan(v.x, 200) && gan(v.y, 100), JSON.stringify(v));
});

test('ban tay: khoang trong 0,4 s thi noi suy tuyen tinh tu cuoi muc truoc toi dau muc sau', function () {
  var ds = [muc('a', 1, 1), muc('b', 2.4, 1)];
  var v = T.viTri(ds, 2.2, ngoi, NGHI);
  assert.strictEqual(v.hien, true);
  assert.ok(gan(v.x, (300 + 100) / 2) && gan(v.y, (100 + 300) / 2), JSON.stringify(v));
  var dau = T.viTri(ds, 2.0, ngoi, NGHI);
  assert.ok(gan(dau.x, 300) && gan(dau.y, 100));
});

test('ban tay va may quay: hai muc cung bat dau thi uu tien hinh, roi chu, roi net', function () {
  var ds = [muc('a', 1, 0.3, { kieu: 'net' }), muc('b', 1, 2.5), muc('c', 1, 1.4, { kieu: 'hinh' })];
  var v = T.viTri(ds, 1.2, ngoi, NGHI);
  assert.ok(gan(v.x, ngoi(ds[2], 0.2 / 1.4).x), 've hinh truoc: ' + JSON.stringify(v));
  var sau = T.viTri(ds, 2.6, ngoi, NGHI);
  assert.ok(gan(sau.x, ngoi(ds[1], 1.6 / 2.5).x), 'hinh xong thi viet tiep chu: ' + JSON.stringify(sau));
  var ds2 = [muc('a', 1, 0.3, { kieu: 'net' }), muc('b', 1, 1.5)];
  assert.ok(gan(T.viTri(ds2, 1.2, ngoi, NGHI).x, ngoi(ds2[1], 0.2 / 1.5).x), 'chu truoc net');
  var hop = { a: HOP_TAM, b: HOP_TAM, c: HOP_TAM };
  assert.strictEqual(Q.mucTieu(ds, hop, 1.2), 'c');
  assert.strictEqual(Q.mucTieu(ds, hop, 2.6), 'b');
  assert.strictEqual(Q.mucTieu(ds2, hop, 1.2), 'b');
});
var HOP_TAM = { x: 100, y: 100, w: 100, h: 100 };

test('ban tay va may quay: gach chan (quay: false) bat dau muon hon van nhuong tay cho muc may quay dang nhin', function () {
  // Cảnh minh-hoa thật: tiêu đề viết 0,55–1,4 s, gạch chân 1,4–1,8 s, hình đầu tiên vẽ 1,0–2,8 s.
  var ds = [muc('a', 0.55, 0.85), muc('b', 1.4, 0.4, { kieu: 'net', quay: false }), muc('c', 1.0, 1.8, { kieu: 'hinh' })];
  var hop = { a: HOP_TAM, b: HOP_TAM, c: HOP_TAM };
  var v = T.viTri(ds, 1.6, ngoi, NGHI);
  assert.strictEqual(Q.mucTieu(ds, hop, 1.6), 'c');
  assert.ok(gan(v.x, ngoi(ds[2], 0.6 / 1.8).x) && gan(v.y, ngoi(ds[2], 0.6 / 1.8).y), 'tay o hinh may quay dang nhin: ' + JSON.stringify(v));
  // Chỉ còn gạch chân đang vẽ thì tay vẫn vẽ gạch chân.
  var ds2 = [muc('a', 0.55, 0.85), muc('b', 1.4, 0.4, { kieu: 'net', quay: false })];
  var v2 = T.viTri(ds2, 1.6, ngoi, NGHI);
  assert.ok(gan(v2.x, ngoi(ds2[1], 0.5).x), 'chi con gach chan: ' + JSON.stringify(v2));
  // Mọi t: mục máy quay nhắm, nếu đang vẽ, chính là mục tay đang vẽ.
  for (var t = 0; t < 3; t += 1 / 30) {
    var id = Q.mucTieu(ds, hop, t);
    var m = ds.filter(function (x) { return x.id === id; })[0];
    if (!m || t < m.batDau || t >= m.batDau + m.thoiLuong) { continue; }
    var p = (t - m.batDau) / m.thoiLuong;
    var tay = T.viTri(ds, t, ngoi, NGHI);
    assert.ok(gan(tay.x, ngoi(m, p).x) && gan(tay.y, ngoi(m, p).y), 't = ' + t + ': ' + JSON.stringify(tay));
  }
});

test('ban tay: bo qua muc dong va muc anh', function () {
  var ds = [muc('a', 1, 1), muc('b', 1.2, 1, { dong: true }), muc('c', 1.3, 0.4, { kieu: 'anh' })];
  var v = T.viTri(ds, 1.5, ngoi, NGHI);
  assert.ok(gan(v.x, 200) && gan(v.y, 100), JSON.stringify(v));
});

test('ban tay: ranh 2 s thi nghi o goc va an', function () {
  var ds = [muc('a', 1, 1), muc('c', 5, 1)];
  var v = T.viTri(ds, 3.5, ngoi, NGHI);
  assert.strictEqual(v.hien, false);
  assert.ok(gan(v.x, NGHI.x) && gan(v.y, NGHI.y));
  var luot = T.viTri(ds, 2.2, ngoi, NGHI);
  assert.strictEqual(luot.hien, true, 'dang luot ve goc nghi');
  assert.ok(luot.x > 300 && luot.x < NGHI.x);
  assert.strictEqual(T.viTri(ds, 2.4, ngoi, NGHI).hien, false, 'luot ve nghi xong trong 0,4 s');
});

test('ban tay: truoc muc dau tien tay luot vao tu goc nghi, bat dau khong som hon t = 0', function () {
  var ds = [muc('a', 0.2, 1)];
  var v0 = T.viTri(ds, 0, ngoi, NGHI);
  assert.ok(gan(v0.x, NGHI.x) && gan(v0.y, NGHI.y), JSON.stringify(v0));
  var v1 = T.viTri(ds, 0.1, ngoi, NGHI);
  assert.ok(gan(v1.x, (NGHI.x + 100) / 2) && gan(v1.y, (NGHI.y + 100) / 2), JSON.stringify(v1));
  var ds2 = [muc('a', 3, 1)];
  assert.strictEqual(T.viTri(ds2, 1, ngoi, NGHI).hien, false);
  var v2 = T.viTri(ds2, 2.8, ngoi, NGHI);
  assert.ok(v2.hien && gan(v2.x, NGHI.x + (100 - NGHI.x) * 0.5));
});

test('ban tay: lau bang dung gie, x tang dan theo t, y = 380', function () {
  var ds = [muc('a', 0.55, 1)];
  var truoc = -Infinity;
  for (var i = 0; i <= 10; i++) {
    var t = 0.5 * i / 10;
    var v = T.viTri(ds, t, ngoi, NGHI, { lauBang: true });
    assert.strictEqual(v.kieu, 'gie');
    assert.strictEqual(v.hien, true);
    assert.strictEqual(v.y, 380);
    assert.ok(gan(v.x, -120 + 1400 * t / 0.5));
    assert.ok(v.x > truoc);
    truoc = v.x;
  }
  assert.strictEqual(T.viTri(ds, 0.3, ngoi, NGHI).kieu, 'but', 'khong lau bang thi khong co gie');
});

test('ban tay: do dai lau bang theo tuy.giayLau (tu du.giayLauBang)', function () {
  var ds = [muc('a', 1.05, 1)];
  var v = T.viTri(ds, 0.8, ngoi, NGHI, { lauBang: true, giayLau: 1.0 });
  assert.strictEqual(v.kieu, 'gie');
  assert.ok(gan(v.x, -120 + 1400 * 0.8 / 1.0));
  assert.strictEqual(T.viTri(ds, 0.8, ngoi, NGHI, { lauBang: true }).kieu, 'but', 'mac dinh 0,5 giay');
});

test('ban tay: o khung cuoi canh ngan tay da nghi', function () {
  var gh = 2.5667;
  var ds = [muc('a', 0.55, gh - 0.2 - 0.55)];
  var v = T.viTri(ds, gh - 1 / 30, ngoi, NGHI, { lauBang: true, gh: gh });
  assert.strictEqual(v.hien, false);
  assert.strictEqual(T.viTri(ds, gh - 0.2, ngoi, NGHI, { gh: gh }).hien, false);
});

test('ban tay: chuyen canh khac lau bang thi khong co gie va tay an, but vao sau khi chuyen xong', function () {
  var ds = [muc('a', 0.55, 1)];
  ['lat-trang', 'truot', 'phong', 'mo-man'].forEach(function (k) {
    for (var i = 0; i <= 10; i++) {
      var v = T.viTri(ds, 0.5 * i / 10, ngoi, NGHI, { chuyen: k, giayLau: 0.5 });
      assert.strictEqual(v.hien, false, k + ' t=' + 0.05 * i + ' ' + JSON.stringify(v));
      assert.strictEqual(v.kieu, 'but', k);
    }
    assert.strictEqual(T.viTri(ds, 0.52, ngoi, NGHI, { chuyen: k, giayLau: 0.5 }).hien, true, k + ': but luot vao sau chuyen canh');
  });
  var v = T.viTri(ds, 0.25, ngoi, NGHI, { chuyen: 'lau-bang', giayLau: 0.5 });
  assert.strictEqual(v.kieu, 'gie');
  assert.ok(gan(v.x, -120 + 1400 * 0.5));
});

// ---------- chuyển cảnh ----------

require(path.join(RT, 'cat-dan.js'));
require(path.join(RT, 'chuyen-canh.js'));
var CH = globalThis.THI_CHUYEN;
var KIEU = ['lau-bang', 'lat-trang', 'truot', 'phong', 'mo-man'];
var LOP = ['nen', 'moi'];
function laDongNhat(tf) { return tf === 'none'; }

test('chuyen canh: nam kieu, xac dinh theo t', function () {
  assert.deepStrictEqual(CH.KIEU, KIEU);
  KIEU.forEach(function (k) {
    for (var t = -0.1; t < 0.8; t += 0.013) {
      assert.deepStrictEqual(CH.trangThai(k, t, 0.5), CH.trangThai(k, t, 0.5), k + ' t=' + t);
    }
  });
});

test('chuyen canh: t = 0 la nen cu nguyen ven, lop moi chua bien doi', function () {
  KIEU.forEach(function (k) {
    var s = CH.trangThai(k, 0, 0.5);
    assert.strictEqual(s.nen.opacity, 1, k);
    assert.ok(laDongNhat(s.nen.transform), k + ' ' + s.nen.transform);
    assert.strictEqual(s.nen.filter, '', k + ': khong bong');
    assert.strictEqual(s.nen.phu, '', k + ': khong lop phu');
    assert.strictEqual(s.loe, 0, k);
    assert.deepStrictEqual(s.moi, { transform: 'none', opacity: 1, clipPath: 'none' }, k);
    if (k === 'lau-bang') {
      assert.strictEqual(s.nen.clipPath, 'inset(0 0 0 0px)');
    } else if (k === 'mo-man') {
      // Hai nửa ghép khít: nửa trái cắt bỏ 640 px bên phải, nửa phải cắt bỏ 640 px bên trái.
      assert.strictEqual(s.nen.clipPath, 'inset(0 640px 0 0)');
      assert.strictEqual(s.nen2.clipPath, 'inset(0 0 0 640px)');
      assert.strictEqual(s.nen2.opacity, 1);
      assert.ok(laDongNhat(s.nen2.transform), s.nen2.transform);
    } else {
      assert.strictEqual(s.nen.clipPath, 'none', k);
    }
    if (k !== 'mo-man') { assert.strictEqual(s.nen2, null, k); }
  });
});

test('chuyen canh: tu t >= dai khong con nen cu, lop moi ve nguyen trang', function () {
  KIEU.forEach(function (k) {
    [0.5, 0.55, 1, 30].forEach(function (t) {
      var s = CH.trangThai(k, t, 0.5);
      assert.strictEqual(s.nen.opacity, 0, k + ' t=' + t);
      if (s.nen2) { assert.strictEqual(s.nen2.opacity, 0, k + ' t=' + t); }
      assert.deepStrictEqual(s.moi, { transform: 'none', opacity: 1, clipPath: 'none' }, k + ' t=' + t);
      assert.strictEqual(s.loe, 0, k + ' t=' + t);
    });
  });
});

test('chuyen canh: do dai theo dai (du.giayLauBang)', function () {
  var a = CH.trangThai('truot', 0.5, 1.0);
  var b = CH.trangThai('truot', 0.25, 0.5);
  assert.deepStrictEqual(a, b);
  assert.notStrictEqual(a.nen.opacity, 0);
});

test('chuyen canh: loe trong [0, 1]; phong loe dinh 0,6 o giua, kieu khac khong loe', function () {
  KIEU.forEach(function (k) {
    var lon = 0;
    for (var i = 0; i <= 100; i++) {
      var s = CH.trangThai(k, 0.5 * i / 100, 0.5);
      assert.ok(s.loe >= 0 && s.loe <= 1, k + ' ' + s.loe);
      LOP.forEach(function (l) { assert.ok(s[l].opacity >= 0 && s[l].opacity <= 1, k + ' ' + l); });
      lon = Math.max(lon, s.loe);
    }
    if (k === 'phong') {
      assert.ok(gan(lon, 0.6, 1e-9), 'dinh ' + lon);
      assert.ok(gan(CH.trangThai(k, 0.25, 0.5).loe, 0.6, 1e-9));
    } else {
      assert.strictEqual(lon, 0, k);
    }
  });
});

function so(chuoi, ten) {
  var m = new RegExp(ten + '\\((-?[\\d.]+)').exec(chuoi);
  return m ? Number(m[1]) : null;
}

test('chuyen canh: lau bang giu dung duong lau cua vi.10', function () {
  for (var i = 0; i <= 10; i++) {
    var t = 0.05 * i;
    var s = CH.trangThai('lau-bang', t, 0.5);
    var x = Math.min(1280, Math.max(0, -120 + 1400 * t / 0.5));
    assert.strictEqual(s.nen.clipPath, 'inset(0 0 0 ' + x + 'px)', 't=' + t);
  }
});

test('chuyen canh: lat trang xoay quanh mep trai 0 -> -100 do, toi dan', function () {
  var truocGoc = 1;
  var truocToi = 0;
  for (var i = 1; i < 10; i++) {
    var s = CH.trangThai('lat-trang', 0.05 * i, 0.5);
    var goc = so(s.nen.transform, 'rotateY');
    assert.ok(goc < truocGoc && goc > -100, 'goc ' + goc);
    // Độ tối ở mép tự do (điểm dừng cuối của lớp phủ) tăng dần; có bóng đổ.
    var toi = Number(/rgba\(0,0,0,([\d.]+)\)\)$/.exec(s.nen.phu)[1]);
    assert.ok(toi > truocToi && toi <= 1, 'toi ' + toi);
    assert.ok(/drop-shadow/.test(s.nen.filter), s.nen.filter);
    truocGoc = goc;
    truocToi = toi;
  }
  assert.ok(gan(so(CH.trangThai('lat-trang', 0.4999999, 0.5).nen.transform, 'rotateY'), -100, 1e-3));
});

test('chuyen canh: truot, nen sang trai 0 -> -1280, moi tu +1280 -> 0, khit nhau', function () {
  for (var i = 1; i < 10; i++) {
    var s = CH.trangThai('truot', 0.05 * i, 0.5);
    var a = so(s.nen.transform, 'translateX');
    var b = so(s.moi.transform, 'translateX');
    assert.ok(a < 0 && a > -1280, String(a));
    assert.ok(gan(b - a, 1280, 1e-6), a + ' ' + b);
  }
});

test('chuyen canh: phong, nen phong 1 -> 1,6 va mo dan', function () {
  var truoc = 1;
  for (var i = 1; i < 10; i++) {
    var s = CH.trangThai('phong', 0.05 * i, 0.5);
    var k = so(s.nen.transform, 'scale');
    assert.ok(k > truoc && k < 1.6, String(k));
    assert.ok(s.nen.opacity < 1 && s.nen.opacity > 0);
    truoc = k;
  }
});

test('chuyen canh: mo man, hai nua tach doi xung sang hai ben', function () {
  for (var i = 1; i < 10; i++) {
    var s = CH.trangThai('mo-man', 0.05 * i, 0.5);
    var a = so(s.nen.transform, 'translateX');
    var b = so(s.nen2.transform, 'translateX');
    assert.ok(a < 0 && gan(a, -b, 1e-9), a + ' ' + b);
    assert.strictEqual(s.nen.clipPath, 'inset(0 640px 0 0)');
    assert.strictEqual(s.nen2.clipPath, 'inset(0 0 0 640px)');
  }
});

test('chuyen canh: kieu la hoac null thi nem loi', function () {
  assert.throws(function () { CH.trangThai('xoay', 0.1, 0.5); });
  assert.throws(function () { CH.trangThai(null, 0.1, 0.5); });
});

// ---------- xé giấy (cat-dan) ----------

test('chuyen canh: xe-giay khong nam trong KIEU/luan phien nhung trangThai van nhan', function () {
  assert.deepStrictEqual(CH.KIEU, KIEU, 'KIEU van dung 5 kieu cu');
  assert.doesNotThrow(function () { CH.trangThai('xe-giay', 0.1, 0.5); });
});

test('chuyen canh: xe-giay tai t=0 che kin (opacity 1, polygon), tu t >= dai thi het (opacity 0)', function () {
  var s0 = CH.trangThai('xe-giay', 0, 0.5);
  assert.strictEqual(s0.nen.opacity, 1);
  assert.ok(/^polygon\(/.test(s0.nen.clipPath), s0.nen.clipPath);
  assert.strictEqual(s0.nen.filter, '', 'chua chay thi chua co bong');
  [0.5, 0.55, 1, 30].forEach(function (t) {
    var s = CH.trangThai('xe-giay', t, 0.5);
    assert.strictEqual(s.nen.opacity, 0, 't=' + t);
  });
});

test('chuyen canh: xe-giay dang chay thi co bong doc mep, moi ve nguyen trang', function () {
  for (var i = 1; i < 10; i++) {
    var t = 0.05 * i;
    var s = CH.trangThai('xe-giay', t, 0.5);
    assert.ok(/drop-shadow/.test(s.nen.filter), s.nen.filter);
    assert.ok(/^polygon\(/.test(s.nen.clipPath), s.nen.clipPath);
    assert.deepStrictEqual(s.moi, { transform: 'none', opacity: 1, clipPath: 'none' }, 't=' + t);
    assert.strictEqual(s.nen2, null, 't=' + t);
    assert.strictEqual(s.loe, 0, 't=' + t);
  }
});

test('chuyen canh: xe-giay polygon co don vi px o moi toa do (CSS bo qua polygon so tran, vet xe se khong hien)', function () {
  var s = CH.trangThai('xe-giay', 0.2, 0.5, 2);
  var diem = s.nen.clipPath.replace(/^polygon\(|\)$/g, '').split(', ');
  assert.ok(diem.length > 3, s.nen.clipPath);
  diem.forEach(function (d) {
    assert.ok(/^-?\d+(\.\d+)?px -?\d+(\.\d+)?px$/.test(d), 'diem sai cu phap CSS: ' + d);
  });
});

test('chuyen canh: xe-giay xac dinh theo t va hat (cung t, cung hat ra cung hinh)', function () {
  for (var t = -0.1; t < 0.8; t += 0.013) {
    assert.deepStrictEqual(CH.trangThai('xe-giay', t, 0.5, 3), CH.trangThai('xe-giay', t, 0.5, 3), 't=' + t);
  }
});

test('chuyen canh: xe-giay hat = so canh - hai canh khac nhau ra mep khac nhau, cung canh thi giong het', function () {
  var a2 = CH.trangThai('xe-giay', 0.25, 0.5, 2);
  var a2b = CH.trangThai('xe-giay', 0.25, 0.5, 2);
  var a3 = CH.trangThai('xe-giay', 0.25, 0.5, 3);
  assert.deepStrictEqual(a2, a2b, 'cung so canh (hat) thi ra cung mep');
  assert.notStrictEqual(a2.nen.clipPath, a3.nen.clipPath, 'khac so canh (hat) thi mep phai khac nhau');
  // Thiếu hat (kiểu chuyển khác không cần) vẫn ra một hình hợp lệ, không lỗi.
  assert.ok(/^polygon\(/.test(CH.trangThai('xe-giay', 0.25, 0.5).nen.clipPath));
});

test('ban tay: xe-giay cung khong co gie, tay an toi khi chuyen xong', function () {
  var ds = [muc('a', 0.55, 1)];
  for (var i = 0; i <= 10; i++) {
    var v = T.viTri(ds, 0.5 * i / 10, ngoi, NGHI, { chuyen: 'xe-giay', giayLau: 0.5 });
    assert.strictEqual(v.hien, false, 't=' + 0.05 * i + ' ' + JSON.stringify(v));
    assert.strictEqual(v.kieu, 'but');
  }
  assert.strictEqual(T.viTri(ds, 0.52, ngoi, NGHI, { chuyen: 'xe-giay', giayLau: 0.5 }).hien, true, 'but luot vao sau chuyen canh');
});

// ---------- máy quay ----------

var HOP = {
  a: { x: 60, y: 30, w: 1160, h: 116 },
  b: { x: 900, y: 240, w: 300, h: 300 },
  c: { x: 124, y: 400, w: 400, h: 40 },
  d: { x: 480, y: 560, w: 200, h: 58 }
};
var DS = [muc('a', 0.55, 1.2), muc('b', 1.0, 1.5), muc('c', 3, 1), muc('d', 3.3, 0.8), muc('e', 4, 1, { dong: true })];
var GH = 7;

function bienDoi(s, h) { return { x: s.z * h.x + s.tx, y: s.z * h.y + s.ty, w: s.z * h.w, h: s.z * h.h }; }
function phuKin(s) {
  return s.tx <= 1e-6 && s.ty <= 1e-6 && s.tx + 1280 * s.z >= 1280 - 1e-6 && s.ty + 720 * s.z >= 720 - 1e-6;
}

test('may quay: xac dinh theo t', function () {
  for (var t = 0; t < GH; t += 0.173) {
    assert.deepStrictEqual(Q.tinh(DS, HOP, t, GH, {}), Q.tinh(DS, HOP, t, GH, {}));
  }
});

test('may quay: z trong [1; 1,35] tai 200 diem va ve {1,0,0} tai cuoi canh', function () {
  for (var i = 0; i < 200; i++) {
    var s = Q.tinh(DS, HOP, GH * i / 199, GH, {});
    assert.ok(s.z >= 1 - 1e-9 && s.z <= 1.35 + 1e-9, 'z = ' + s.z);
  }
  assert.deepStrictEqual(Q.tinh(DS, HOP, GH, GH, {}), { z: 1, tx: 0, ty: 0 });
  assert.deepStrictEqual(Q.tinh(DS, HOP, GH - 0.2, GH, {}), { z: 1, tx: 0, ty: 0 });
});

test('may quay: moi diem lop bang phu kin khung va hop muc tieu nam trong khung, day <= 620', function () {
  var coPhong = false;
  for (var i = 0; i < 400; i++) {
    var t = GH * i / 399;
    var s = Q.tinh(DS, HOP, t, GH, {});
    assert.ok(phuKin(s), 't=' + t + ' ' + JSON.stringify(s));
    var id = Q.mucTieu(DS, HOP, t);
    if (!id) { continue; }
    var b = bienDoi(s, HOP[id]);
    assert.ok(b.y + b.h <= 620 + 1e-6, 't=' + t + ' ' + id + ' day ' + (b.y + b.h));
    assert.ok(b.x >= -1e-6 && b.y >= -1e-6 && b.x + b.w <= 1280 + 1e-6, 't=' + t + ' ' + id + ' ' + JSON.stringify(b));
    if (s.z > 1.05) { coPhong = true; }
  }
  assert.ok(coPhong, 'may quay phai co luc phong vao muc nho');
});

test('may quay: muc tieu la muc dang ve, khong co thi muc vua xong; bo qua muc dong', function () {
  assert.strictEqual(Q.mucTieu(DS, HOP, 0.2), null);
  assert.strictEqual(Q.mucTieu(DS, HOP, 0.8), 'a');
  assert.strictEqual(Q.mucTieu(DS, HOP, 1.2), 'b');
  assert.strictEqual(Q.mucTieu(DS, HOP, 2.8), 'b');
  assert.strictEqual(Q.mucTieu(DS, HOP, 3.5), 'd');
  assert.strictEqual(Q.mucTieu(DS, HOP, 4.5), 'd');
  assert.strictEqual(Q.mucTieu(DS, HOP, 4.05), 'd', 'c xong truoc, d con dang ve');
});

test('may quay: hop sat vach phu de van duoc nang len tren 620', function () {
  var hop = { y: { x: 124, y: 556, w: 700, h: 72 } };
  var ds = [muc('y', 1, 1)];
  var s = Q.tinh(ds, hop, 3, 8, {});
  var b = bienDoi(s, hop.y);
  assert.ok(b.y + b.h <= 620 + 1e-6, JSON.stringify(s));
  assert.ok(phuKin(s));
});

test('may quay: hop noi dung dien hinh khong vuot vach phu de o ca hai kho (ngam theo canh, khong hang so kho ngang)', function () {
  var CAC_KHO = {
    ngang: { ten: 'ngang', rong: 1280, cao: 720, day: 620, tamX: 640, tamY: 310 },
    doc: { ten: 'doc', rong: 720, cao: 1280, day: 1080, tamX: 360, tamY: 540 }
  };
  Object.keys(CAC_KHO).forEach(function (ten) {
    var k = CAC_KHO[ten];
    globalThis.THI_KHO.dat(k);
    // Hộp nội dung điển hình: gần hết bề ngang, cao bằng 28% chiều cao vùng nội dung, sát đáy.
    var hop = { a: { x: k.rong * 0.08, y: k.day - 0.28 * k.day, w: k.rong * 0.84, h: 0.28 * k.day } };
    var ds = [muc('a', 0.5, 2)];
    for (var i = 0; i <= 60; i++) {
      var t = 3 * i / 60;
      var s = Q.tinh(ds, hop, t, 3, {});
      var day = s.z * (hop.a.y + hop.a.h) + s.ty;
      assert.ok(day <= k.day + 1e-6, ten + ' t=' + t + ' day=' + day);
    }
  });
  globalThis.THI_KHO.dat(globalThis.THI_KHO.NGANG);
});

test('may quay: canh thi nghiem chi day cham tu 1 len 1,06, giu tam', function () {
  var s0 = Q.tinh(DS, HOP, 0, GH, { day: true });
  var s1 = Q.tinh(DS, HOP, GH, GH, { day: true });
  assert.ok(gan(s0.z, 1));
  assert.ok(gan(s1.z, 1.06, 1e-6));
  assert.ok(gan(s1.tx, 640 * (1 - s1.z), 1e-6) && gan(s1.ty, 360 * (1 - s1.z), 1e-6));
  assert.ok(phuKin(s1));
});

test('may quay: tat may quay thi luon {1,0,0}', function () {
  [0, 1.2, 3.5, GH].forEach(function (t) {
    assert.deepStrictEqual(Q.tinh(DS, HOP, t, GH, { mayQuay: false }), { z: 1, tx: 0, ty: 0 });
  });
});

test('may quay: chuyen muc tieu muot, khong nhay qua 0,1 giua hai khung 1/30 s ngoai luc bat buoc', function () {
  var truoc = Q.tinh(DS, HOP, 0, GH, {});
  for (var i = 1; i <= GH * 30; i++) {
    var s = Q.tinh(DS, HOP, i / 30, GH, {});
    assert.ok(Math.abs(s.z - truoc.z) < 0.1, 't=' + i / 30 + ' dz=' + (s.z - truoc.z));
    truoc = s;
  }
});

test('may quay: canh ngan 2,5667 s co hinh va o chu day 628 van giu rang buoc, ve dung {1,0,0}', function () {
  var gh = 2.5667;
  var hop = { hinh: { x: 910, y: 240, w: 300, h: 300 }, y: { x: 124, y: 556, w: 700, h: 72 } };
  var ds = [muc('hinh', 0.55, 1.2, { kieu: 'hinh' }), muc('y', 1.0, gh - 0.2 - 1.0)];
  var veNha = gh - 1.2;
  for (var i = 0; i <= 240; i++) {
    var t = gh * i / 240;
    var s = Q.tinh(ds, hop, t, gh, {});
    assert.ok(phuKin(s), 't=' + t + ' ' + JSON.stringify(s));
    assert.ok(s.z >= 1 - 1e-9 && s.z <= 1.35 + 1e-9, 't=' + t + ' z=' + s.z);
    var id = Q.mucTieu(ds, hop, t);
    if (id && t < veNha) {
      var b = bienDoi(s, hop[id]);
      assert.ok(b.y + b.h <= 620 + 1e-6, 't=' + t + ' ' + id + ' day ' + (b.y + b.h));
    }
  }
  assert.deepStrictEqual(Q.tinh(ds, hop, gh - 1 / 30, gh, {}), { z: 1, tx: 0, ty: 0 });
  assert.deepStrictEqual(Q.tinh(ds, hop, gh - 0.2, gh, {}), { z: 1, tx: 0, ty: 0 });
});

test('ban tay va may quay: cung ranh gioi bat dau (t = batDau la dang ve)', function () {
  var ds = [muc('a', 1, 1)];
  var v = T.viTri(ds, 1, ngoi, NGHI);
  assert.ok(v.hien && gan(v.x, 100) && gan(v.y, 100), JSON.stringify(v));
  assert.strictEqual(T.dangVe(ds, 1), ds[0]);
  assert.strictEqual(Q.mucTieu(ds, { a: HOP_TAM }, 1), 'a');
});

test('ban tay: muc tay:false khong duoc ve (tieu de nay chu)', function () {
  var ds = [muc('a', 1, 1, { tay: false }), muc('c', 5, 1)];
  assert.strictEqual(T.viTri(ds, 1.5, ngoi, NGHI).hien, false);
  assert.strictEqual(T.dangVe(ds, 1.5), null);
  assert.strictEqual(T.viTri(ds, 5.5, ngoi, NGHI).hien, true);
});

// ---------- thu tu xuat hien o canh cat-dan xe-giay (dau() kep batDau >= giayLau + 0,05) ----------

require(path.join(RT, 'dong.js'));
require(path.join(RT, 'khung-video.js'));
require(path.join(RT, 'canh', 'y-tung-y.js'));
var CANH = globalThis.THI_CANH;

test('thu tu xuat hien: canh 2 cat-dan xe-giay - moi muc >= giayLau + 0,05, nen truoc hinh truoc nhan truoc chu', function () {
  var du = {
    so: 2, loai: 'y-tung-y', thoiLuong: 12, danDau: 1.0, giayLauBang: 0.5,
    moc: [3.0, 5.0],
    truong: { 'tieu-de': ['Ba y'], y: ['Mot', 'Hai'] },
    hinh: { phanTu: [{ the: 'circle', thuocTinh: { cx: '12', cy: '12', r: '9' } }], viewBox: '0 0 24 24' },
    co: { chuyen: 'xe-giay', banTay: false, mayQuay: false, chuDong: false, lauBang: false },
    chuDe: { ten: 'cat-dan', font: 'BeVietnamPro', hienChu: 'truot', net: 'nhanh',
             mauNhan: ['#e8a33d', '#1f6f78', '#c8452f', '#2f4f9e'], giay: '#f3ead7' }
  };
  var ds = CANH['y-tung-y'].muc(du);
  var sau = 0.5 + 0.05;
  var boi = {};
  ds.forEach(function (m) {
    assert.ok(m.batDau >= sau - 1e-9, m.id + ' batDau=' + m.batDau + ' < giayLau + 0,05');
    boi[m.id] = m;
  });
  // Nền (mép xé) chạy suốt [0, giayLau]; mọi mục chỉ vẽ từ sau khi mép xé xong nên luôn sau nền.
  assert.ok(boi.hinh.batDau <= boi['tieu-de'].batDau, 'hinh chinh truoc nhan tieu de: ' + JSON.stringify(boi));
  assert.ok(boi['tieu-de'].batDau <= boi['y-0'].batDau, 'nhan tieu de truoc chu y: ' + JSON.stringify(boi));
  assert.ok(boi['y-0'].batDau <= boi['y-1'].batDau, 'chu y-0 truoc y-1 theo moc: ' + JSON.stringify(boi));
  // Chấm tròn đầu mỗi ý (cham-k) và chữ ý (y-k) cùng nhận batDau = du.moc[k] (dau() kẹp cả hai như nhau), nên thứ tự
  // thật là "cùng lúc", không phải chấm hẳn trước chữ: chấm không bao giờ đến trước hình chính, và không bao giờ đến
  // sau đúng chữ ý nó đứng cạnh.
  [0, 1].forEach(function (k) {
    var cham = boi['cham-' + k], y = boi['y-' + k];
    assert.ok(cham.batDau >= boi.hinh.batDau, 'cham-' + k + ' khong duoc den truoc hinh chinh: ' + JSON.stringify(boi));
    assert.ok(cham.batDau <= y.batDau, 'cham-' + k + ' khong duoc den sau chu y-' + k + ' no dung canh: ' + JSON.stringify(boi));
  });
});

// Hộp giữ (tiêu đề, thẻ, dòng tài liệu): luôn nằm trọn trong khung, đỉnh không cao hơn `tren` (dưới khung loạt),
// cùng mục tiêu; máy quay vẫn phóng khi còn chỗ.
test('may quay: hop giu (the, tieu de, tai lieu) luon trong khung va duoi khung loat', function () {
  globalThis.THI_KHO.dat(null);
  [{ hop: { x: 880, y: 40, w: 340, h: 140 }, tren: 40 },            // thẻ góc phải trên
    { hop: { x: 60, y: 40, w: 1160, h: 576 }, tren: 40 },            // tiêu đề trái trên tới tài liệu phải dưới
    { hop: { x: 300, y: 90, w: 200, h: 60 }, tren: 0 },
    { hop: { x: 100, y: 190, w: 1120, h: 426 }, tren: 0 }].forEach(function (giu) {   // khung công thức + tài liệu
    var coPhong = false;
    for (var i = 0; i < 300; i++) {
      var t = GH * i / 299;
      var s = Q.tinh(DS, HOP, t, GH, { giu: giu });
      assert.ok(phuKin(s), JSON.stringify([t, s]));
      var b = bienDoi(s, giu.hop);
      assert.ok(b.x >= -1e-6 && b.x + b.w <= 1280 + 1e-6 && b.y >= giu.tren - 1e-6 && b.y + b.h <= 620 + 1e-6,
        JSON.stringify([giu, t, b]));
      // Lề hai bên 24 (LE_GIU) khi đang phóng: nét vẽ tay ngoài hộp đo không bị cắt ở mép khung.
      if (s.z > 1 + 1e-9) { assert.ok(b.x >= 24 - 1e-6 && b.x + b.w <= 1280 - 24 + 1e-6, JSON.stringify([giu, t, s, b])); }
      if (s.z > 1.02) { coPhong = true; }
    }
    if (giu.hop.w < 400) { assert.ok(coPhong, 'hop giu nho thi van phong: ' + JSON.stringify(giu)); }
  });
});
