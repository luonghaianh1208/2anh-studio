'use strict';
// Người que (runtime/nhan-vat.js): mười tư thế, toạ độ khớp thuần theo t, nhún thở, chớp mắt, cử chỉ; và cách
// khung-video.js đặt nhân vật vào cột phụ của tieu-de, khai-niem, y-tung-y.
var test = require('node:test');
var assert = require('node:assert');
var path = require('node:path');

var RT = path.join(__dirname, '..', '..', 'video_ma_parts', 'runtime');
require(path.join(RT, 'kho.js'));
require(path.join(RT, 'dong.js'));
require(path.join(RT, 'cat-dan.js'));
require(path.join(RT, 'nhan-vat.js'));
require(path.join(RT, 'khung-video.js'));
require(path.join(RT, 'nhan.js'));
require(path.join(RT, 'hinh.js'));
['tieu-de', 'khai-niem', 'y-tung-y'].forEach(function (l) { require(path.join(RT, 'canh', l + '.js')); });
var NV = globalThis.THI_NHAN_VAT;
var K = globalThis.THI_KHO;
var C = globalThis.THI_CANH;

var TEN = ['dung', 'chao', 'chi-tay', 'giai-thich', 'suy-nghi', 'ngac-nhien', 'vo-dau', 'dung-lai', 'an-mung', 'buon'];
var KHOP = ['co', 'vaiT', 'vaiP', 'khuyuT', 'khuyuP', 'tayT', 'tayP', 'hong', 'goiT', 'goiP', 'chanT', 'chanP'];
var NGANG = { ten: 'ngang', rong: 1280, cao: 720, day: 620 };
var DOC = { ten: 'doc', rong: 720, cao: 1280, day: 1080 };

test('muoi tu the dung ten va thu tu', function () {
  assert.deepStrictEqual(NV.TU_THE, TEN);
});

test('moi tu the tai t = 0; 0,6; 5: khop trong hop [-150,150]x[-310,0], chan cham dat', function () {
  TEN.forEach(function (ten) {
    [0, 0.6, 5].forEach(function (t) {
      var d = NV.dang(ten, t);
      var k = d.khop;
      KHOP.forEach(function (ma) {
        var p = k[ma];
        assert.ok(p && isFinite(p.x) && isFinite(p.y), ten + ' ' + ma);
        assert.ok(p.x >= -150 && p.x <= 150 && p.y >= -310 && p.y <= 0, ten + '@' + t + ' ' + ma + ' ' + JSON.stringify(p));
      });
      assert.ok(k.dau.y - k.dau.r >= -310 && Math.abs(k.dau.x) + k.dau.r <= 150, ten + '@' + t + ' dau');
      assert.ok(Math.abs(k.chanT.y) <= 0.5 && Math.abs(k.chanP.y) <= 0.5, ten + '@' + t + ' chan');
      assert.ok(['tron', 'cuoi', 'nham', 'xoay', 'to'].indexOf(d.mat.mat) >= 0, ten);
      assert.ok(['cuoi', 'mo', 'ngang', 'meo', 'o'].indexOf(d.mat.mieng) >= 0, ten);
      assert.ok(['ngang', 'nhuong', 'chau'].indexOf(d.mat.may) >= 0, ten);
    });
  });
});

test('moi tu the qua ca canh (buoc 1/30 s): khop trong hop', function () {
  TEN.forEach(function (ten) {
    for (var i = 0; i <= 240; i++) {
      var k = NV.dang(ten, i / 30).khop;
      KHOP.forEach(function (ma) {
        assert.ok(k[ma].x >= -150 && k[ma].x <= 150 && k[ma].y >= -310 && k[ma].y <= 0.5, ten + '@' + i + ' ' + ma);
      });
      assert.ok(k.dau.y - k.dau.r >= -310, ten + '@' + i + ' dau');
    }
  });
});

test('xac dinh: goi hai lan cung ket qua; tu the la thi loi', function () {
  TEN.forEach(function (ten) {
    [0, 0.37, 1.1, 4.2].forEach(function (t) {
      assert.deepStrictEqual(NV.dang(ten, t), NV.dang(ten, t));
    });
  });
  assert.throws(function () { NV.dang('point', 1); });
});

test('tay va chan dai khong doi: canh tay 46 + 44, chan tu hong', function () {
  TEN.forEach(function (ten) {
    [0.6, 5].forEach(function (t) {
      var k = NV.dang(ten, t).khop;
      function d(a, b) { return Math.hypot(a.x - b.x, a.y - b.y); }
      assert.ok(Math.abs(d(k.vaiT, k.khuyuT) - 46) < 0.01, ten);
      assert.ok(Math.abs(d(k.vaiP, k.khuyuP) - 46) < 0.01, ten);
      assert.ok(d(k.khuyuT, k.tayT) <= 44.01 && d(k.khuyuP, k.tayP) <= 44.01, ten);
    });
  });
});

test('chop mat dung moc 1,3 + 3,1k + 0,4((7k) mod 3), dai 0,12 s', function () {
  for (var k = 0; k < 4; k++) {
    var m = 1.3 + 3.1 * k + 0.4 * ((k * 7) % 3);
    assert.strictEqual(NV.dang('dung', m + 0.01).mat.mat, 'nham', 'k=' + k);
    assert.strictEqual(NV.dang('dung', m + 0.11).mat.mat, 'nham', 'k=' + k);
    assert.notStrictEqual(NV.dang('dung', m - 0.02).mat.mat, 'nham', 'k=' + k);
    assert.notStrictEqual(NV.dang('dung', m + 0.13).mat.mat, 'nham', 'k=' + k);
  }
  assert.deepStrictEqual(NV.mocChop(10).map(function (x) { return Math.round(x * 100) / 100; }), [1.3, 4.8, 8.3]);
});

test('nhun tho: khop tren hong dich 3 sin(2 pi t / 2,4), chan dung yen', function () {
  var a = NV.dang('dung', 5).khop, b = NV.dang('dung', 5.6).khop; // 5,6 − 5 = 0,6 = một phần tư chu kì
  var mong = 3 * Math.sin(2 * Math.PI * 5.6 / 2.4) - 3 * Math.sin(2 * Math.PI * 5 / 2.4);
  ['co', 'vaiT', 'dau'].forEach(function (ma) { assert.ok(Math.abs((b[ma].y - a[ma].y) - mong) < 2e-3, ma); }); // khớp làm tròn 3 chữ số
  assert.deepStrictEqual([a.chanT, a.goiP, a.hong], [b.chanT, b.goiP, b.hong]);
});

test('net mat theo tu the', function () {
  var cuoi = function (ten) { return NV.dang(ten, 5).mat; };
  assert.strictEqual(cuoi('ngac-nhien').mat, 'to');
  assert.strictEqual(cuoi('ngac-nhien').mieng, 'o');
  assert.strictEqual(cuoi('vo-dau').mat, 'xoay');
  assert.strictEqual(cuoi('vo-dau').mieng, 'meo');
  assert.strictEqual(cuoi('buon').may, 'chau');
  assert.strictEqual(cuoi('buon').mieng, 'meo');
  assert.strictEqual(cuoi('dung-lai').may, 'chau');
  assert.ok(cuoi('suy-nghi').nhin.y < 0, 'suy-nghi nhìn lên');
});

test('tu the dac trung: suy-nghi tay cham cam, dung-lai tay phai gio cao, an-mung hai tay tren dau, chi-tay duoi ve phia truoc', function () {
  var sn = NV.dang('suy-nghi', 5).khop;
  var cam = { x: sn.dau.x, y: sn.dau.y + sn.dau.r };
  assert.ok(Math.hypot(sn.tayP.x - cam.x, sn.tayP.y - cam.y) < 22, 'suy-nghi: tay ở cằm');
  var dl = NV.dang('dung-lai', 5).khop;
  assert.ok(dl.tayP.y < dl.vaiP.y - 20 && dl.tayP.x > dl.vaiP.x + 50, 'dung-lai: tay phải giơ ra trước');
  assert.strictEqual(NV.dang('dung-lai', 5).tay.P, 'chan');
  var am = NV.dang('an-mung', 5).khop;
  assert.ok(am.tayT.y < am.dau.y && am.tayP.y < am.dau.y, 'an-mung: hai tay trên đầu');
  var ct0 = NV.dang('chi-tay', 0).khop, ct = NV.dang('chi-tay', 5).khop;
  assert.ok(ct.tayP.x > ct.vaiP.x + 75 && Math.abs(ct.tayP.y - ct.vaiP.y) < 25, 'chi-tay: tay duỗi ngang');
  assert.ok(ct0.tayP.x < ct.tayP.x - 30, 'chi-tay: duỗi dần');
  var vd = NV.dang('vo-dau', 5).khop;
  ['tayT', 'tayP'].forEach(function (ma) {
    var r = Math.hypot(vd[ma].x - vd.dau.x, vd[ma].y - vd.dau.y);
    assert.ok(Math.abs(r - vd.dau.r) < 12 && vd[ma].y < vd.vaiT.y - 40, 'vo-dau: hai tay ôm đầu ' + ma);
  });
});

test('cu chi trong 1,2 s dau: chao vay, an-mung bat nhay, vo-dau rung; sau do dung yen (tru nhun tho)', function () {
  function goc(k) { return Math.atan2(k.tayP.y - k.khuyuP.y, k.tayP.x - k.khuyuP.x) * 180 / Math.PI; }
  var cacGoc = [];
  for (var i = 0; i <= 36; i++) { cacGoc.push(goc(NV.dang('chao', i / 30).khop)); }
  var bien = Math.max.apply(null, cacGoc) - Math.min.apply(null, cacGoc);
  assert.ok(bien > 40 && bien < 55, 'chao vẫy ±25°: ' + bien);
  assert.ok(Math.abs(goc(NV.dang('chao', 2).khop) - goc(NV.dang('chao', 3).khop)) < 1e-9);
  var cao = Math.min.apply(null, [0.1, 0.2, 0.3, 0.4, 0.5].map(function (t) { return NV.dang('an-mung', t).khop.chanT.y; }));
  assert.ok(cao < -10 && cao >= -12.01, 'an-mung bật nhảy 12: ' + cao);
  assert.strictEqual(NV.dang('an-mung', 3).khop.chanT.y, 0);
  var a = NV.dang('vo-dau', 0.55).khop, b = NV.dang('vo-dau', 0.65).khop;
  assert.ok(Math.hypot(a.tayT.x - b.tayT.x, a.tayT.y - b.tayT.y) > 1, 'vo-dau rung');
});

test('ve: SVG co dau tron trang vien 4, ao mau theo ten, tay chan net den 7, giay elip xam dam', function () {
  var s = NV.ve(NV.dang('chao', 2), 'xanh-la');
  assert.ok(/<circle[^>]*class="dau"[^>]*fill="#fff"[^>]*stroke-width="4"/.test(s), s.slice(0, 400));
  assert.ok(s.indexOf(NV.MAU_AO['xanh-la']) >= 0);
  assert.ok(/stroke-width="7"/.test(s));
  assert.ok(/<ellipse[^>]*class="giay"/.test(s));
  assert.deepStrictEqual(Object.keys(NV.MAU_AO), ['vang', 'do', 'xanh-duong', 'xanh-la', 'cam', 'tim', 'hong', 'xam']);
  // Viền sticker (cat-dan): cùng hình, nét trắng dày hơn 12.
  var v = NV.ve(NV.dang('chao', 2), 'vang', { vien: 12 });
  assert.ok(/stroke="#fff"/.test(v) && /stroke-width="19"/.test(v));
  assert.throws(function () { NV.ve(NV.dang('dung', 0), 'bac'); });
});

test('hien: bat vao easeOutBack 0,6 -> 1 trong 0,4 s tu 0,2 s', function () {
  assert.strictEqual(NV.hien(0.1).a, 0);
  assert.ok(Math.abs(NV.hien(0.2).k - 0.6) < 1e-9);
  assert.strictEqual(NV.hien(0.6).k, 1);
  assert.ok(NV.hien(0.45).k > 1, 'easeOutBack vượt đích');
  assert.strictEqual(NV.hien(3).a, 1);
});

function du(loai, truong, them) {
  var d = { so: 3, loai: loai, thoiLuong: 8, danDau: 1, truong: truong, moc: [1.5, 2.5, 3.5], tu: [], co: {},
    nhanVat: { kieu: 'nguoi-que', mauAo: 'vang', tuThe: 'giai-thich' } };
  Object.keys(them || {}).forEach(function (k) { d[k] = them[k]; });
  return d;
}
var TRUONG = {
  'tieu-de': { chu: ['Vì sao in thêm tiền'] },
  'khai-niem': { 'thuat-ngu': ['Lạm phát'], 'dinh-nghia': ['Mức giá chung tăng.'] },
  'y-tung-y': { 'tieu-de': ['Ba nguyên nhân'], y: ['Cầu kéo', 'Chi phí đẩy'] }
};
function giao(a, b) { return a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h; }

test('khung: nhan vat trong cot phu, quay ve phia noi dung, khong giao o chu', function () {
  [NGANG, DOC].forEach(function (kho) {
    K.dat(kho);
    Object.keys(TRUONG).forEach(function (loai) {
      var ds = C[loai].muc(du(loai, TRUONG[loai]));
      var nv = ds.filter(function (m) { return m.kieu === 'nhan-vat'; });
      assert.strictEqual(nv.length, 1, kho.ten + ' ' + loai);
      var m = nv[0];
      var cot = K.o('cot-phu');
      assert.ok(m.hop.x >= cot.x - 0.01 && m.hop.y >= cot.y - 0.01 && m.hop.x + m.hop.w <= cot.x + cot.w + 0.01 &&
        m.hop.y + m.hop.h <= cot.y + cot.h + 0.01, kho.ten + ' ' + loai + ' ' + JSON.stringify(m.hop));
      assert.strictEqual(m.lat, kho.ten === 'ngang', 'ngang: lật (nội dung bên trái)');
      assert.strictEqual(m.batDau, 0.2);
      assert.strictEqual(m.tay, false);
      assert.strictEqual(m.quay, false);
      ds.filter(function (c) { return c.kieu === 'chu'; }).forEach(function (c) {
        assert.ok(!giao(m.hop, { x: c.x, y: c.y, w: c.rong, h: c.cao }), kho.ten + ' ' + loai + ' ' + c.id);
      });
    });
  });
  K.dat(NGANG);
});

test('khung: khong co nhanVat thi khong co nhan vat (du lieu cu giu nguyen)', function () {
  K.dat(NGANG);
  Object.keys(TRUONG).forEach(function (loai) {
    var d = du(loai, TRUONG[loai]);
    delete d.nhanVat;
    assert.strictEqual(C[loai].muc(d).filter(function (m) { return m.kieu === 'nhan-vat'; }).length, 0);
  });
});

test('khung cat-dan: nhan vat la sticker, goc xoay +-3 do theo so canh', function () {
  K.dat(NGANG);
  var cd = { ten: 'cat-dan', font: 'BeVietnamPro', hienChu: 'truot', net: 'nhanh', mauNhan: ['#e8a33d'], giay: '#f3ead7' };
  var m = C['khai-niem'].muc(du('khai-niem', TRUONG['khai-niem'], { chuDe: cd })).filter(function (x) { return x.kieu === 'nhan-vat'; })[0];
  assert.strictEqual(m.sticker, true);
  assert.ok(Math.abs(m.goc) <= 3);
  var m2 = C['khai-niem'].muc(du('khai-niem', TRUONG['khai-niem'])).filter(function (x) { return x.kieu === 'nhan-vat'; })[0];
  assert.ok(!m2.sticker);
  assert.strictEqual(m2.goc, 0);
});
