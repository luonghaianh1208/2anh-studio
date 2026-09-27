'use strict';
// Cảnh câu hỏi nhanh: mục, lịch viết, đồng hồ đếm ngược, hiện đáp án, máy quay — hàm thuần theo t (Node, không DOM).
var test = require('node:test');
var assert = require('node:assert');
var path = require('node:path');

var RT = path.join(__dirname, '..', '..', 'video_ma_parts', 'runtime');
require(path.join(RT, 'kho.js'));
require(path.join(RT, 'dong.js'));
require(path.join(RT, 'khung-video.js'));
require(path.join(RT, 'ban-tay.js'));
require(path.join(RT, 'canh', 'cau-hoi.js'));
var V = globalThis.THI_VIDEO;
var T = globalThis.THI_BAN_TAY;
var D = globalThis.THI_DONG;
var CH = globalThis.THI_CANH['cau-hoi'];

// giayHoi: giọng câu hỏi; cho: đếm ngược; giayGiai: giọng lời giải (như lich.py: dẫn đầu 1,0, nghỉ 0,4, đuôi 0,6).
function du(n, giayHoi, cho, giayGiai, them) {
  var dem = 1.0 + giayHoi;
  var giai = Math.round((dem + cho + 0.4) * 1000) / 1000;
  var gh = Math.ceil((giai + giayGiai + 0.6) * 30 - 1e-9) / 30;
  var lc = ['Tăng gấp đôi', 'Giảm một nửa', 'Không đổi', 'Tăng gấp bốn'].slice(0, n);
  var moc = [];
  for (var k = 0; k <= n; k++) { moc.push(Math.round((1.0 + k * giayHoi / (n + 1)) * 1000) / 1000); }
  var d = { so: 2, loai: 'cau-hoi', thoiLuong: gh, danDau: 1.0, giayLauBang: 0.5, moc: moc, tu: [],
    truong: { 'cau-hoi': ['Khi dây dài gấp bốn thì chu kì con lắc thay đổi thế nào?'], 'lua-chon': lc,
      'dap-an': [n > 2 ? 'C' : 'B'], 'giai-thich': ['Chu kì tỉ lệ với căn bậc hai của chiều dài.'], cho: [String(cho)] },
    cauHoi: { batDauDem: Math.round(dem * 1000) / 1000, cho: cho, batDauGiai: giai, dapAn: n > 2 ? 'C' : 'B' },
    co: { banTay: true, mayQuay: true, chuyen: 'lau-bang' } };
  Object.keys(them || {}).forEach(function (k2) { d[k2] = them[k2]; });
  return d;
}
function tim(ds, id) { return ds.filter(function (m) { return m.id === id; })[0]; }
function day(m) {
  if (m.kieu === 'net') {
    return Math.max.apply(null, m.d.match(/-?\d+(\.\d+)?/g).map(Number).filter(function (_, i) { return i % 2 === 1; }));
  }
  return m.y + m.cao;
}
function boCanh() {
  var kq = [];
  [2, 3, 4].forEach(function (n) {
    [[12, 5, 6], [2.5, 3, 1.2], [30, 10, 20]].forEach(function (g) { kq.push([n + ':' + g.join('/'), du(n, g[0], g[1], g[2])]); });
  });
  return kq;
}

test('muc xac dinh, id khong trung, moi muc trong canh va tren y = 620', function () {
  boCanh().forEach(function (c) {
    var d = c[1];
    var ds = CH.muc(d);
    assert.deepStrictEqual(ds, CH.muc(d), c[0]);
    var ids = ds.map(function (m) { return m.id; });
    assert.strictEqual(new Set(ids).size, ids.length, c[0] + ' id trung');
    ds.forEach(function (m) {
      assert.ok(m.batDau >= 0.55 - 1e-9, c[0] + ':' + m.id + ' bat dau truoc khi lau bang xong ' + m.batDau);
      assert.ok(m.thoiLuong > 0, c[0] + ':' + m.id);
      assert.ok(m.batDau + m.thoiLuong <= d.thoiLuong - 0.2 + 1e-9, c[0] + ':' + m.id + ' xong sau cuoi canh');
      assert.ok(day(m) <= 620, c[0] + ':' + m.id + ' xuong toi ' + day(m));
    });
  });
});

test('cau hoi va lua chon viet xong truoc dem nguoc 0,4 s (tay kip roi bang); lua chon k bat dau tu moc cau k+1', function () {
  boCanh().forEach(function (c) {
    var d = c[1];
    var ds = CH.muc(d);
    ds.filter(function (m) { return m.id !== 'giai-thich'; }).forEach(function (m) {
      assert.ok(m.batDau + m.thoiLuong <= d.cauHoi.batDauDem - 0.4 + 1e-9, c[0] + ':' + m.id + ' viet vao luc dem nguoc');
    });
  });
  var d = du(4, 20, 5, 6);
  var ds = CH.muc(d);
  assert.strictEqual(tim(ds, 'cau-hoi').batDau, d.moc[0]);
  [0, 1, 2, 3].forEach(function (k) {
    assert.strictEqual(tim(ds, 'o-' + k).batDau, d.moc[k + 1], 'o hop k bat dau o moc cau k+1 khi du thoi gian');
    assert.ok(tim(ds, 'lc-' + k).batDau >= tim(ds, 'o-' + k).batDau);
  });
  // Viết lần lượt, không chồng nhau (bàn tay chỉ viết một mục mỗi lúc).
  var viet = ds.filter(function (m) { return m.id !== 'giai-thich'; });
  viet.forEach(function (m, i) {
    if (i) { assert.ok(m.batDau >= viet[i - 1].batDau + viet[i - 1].thoiLuong - 1e-9, m.id); }
  });
});

test('khong co ban tay trong luc dem nguoc; giai thich viet sau khi hien dap an', function () {
  boCanh().forEach(function (c) {
    var d = c[1];
    var ds = V.tachPhan(CH.muc(d));
    var ngoi = function () { return { x: 500, y: 300 }; };
    for (var t = d.cauHoi.batDauDem; t <= d.cauHoi.batDauGiai + 1e-9; t += 1 / 30) {
      var v = T.viTri(ds, t, ngoi, T.NGHI, { chuyen: 'lau-bang', giayLau: 0.5, gh: d.thoiLuong });
      assert.strictEqual(v.hien, false, c[0] + ' tay hien luc ' + t);
    }
    var gt = tim(CH.muc(d), 'giai-thich');
    assert.ok(gt.batDau >= d.cauHoi.batDauGiai + 0.3, c[0] + ' giai thich ' + gt.batDau);
  });
});

test('dap an hien tai batDauGiai, khong som hon', function () {
  var d = du(4, 8, 5, 6);
  var g = d.cauHoi.batDauGiai;
  [0, d.cauHoi.batDauDem, d.cauHoi.batDauDem + 4.9, g - 1 / 30, g - 0.001, g].forEach(function (t) {
    var s = CH.trangThai(d, t);
    assert.strictEqual(s.vien, 0, 't=' + t);
    assert.strictEqual(s.dau.a, 0, 't=' + t);
    s.lo.forEach(function (o, k) { assert.deepStrictEqual([o.a, o.s], [1, 1], 't=' + t + ' lua chon ' + k); });
  });
  var sau = CH.trangThai(d, g + 1 / 30);
  assert.ok(sau.vien > 0, 'vien xanh bat dau ve');
  assert.strictEqual(sau.dung, 2);
  var cuoi = CH.trangThai(d, d.thoiLuong - 0.2);
  assert.strictEqual(cuoi.vien, 1);
  assert.strictEqual(cuoi.dau.a, 1);
  assert.strictEqual(cuoi.dau.s, 1);
  cuoi.lo.forEach(function (o, k) {
    assert.strictEqual(o.a, k === 2 ? 1 : 0.35, 'lua chon ' + k);
    assert.strictEqual(o.s, 1, 'nay xong thi ve dung co');
  });
  // Lựa chọn đúng nảy (to hơn 1 một lúc) rồi về 1; lựa chọn khác không nảy.
  var to = 0;
  for (var t = g; t < g + 1; t += 1 / 30) { to = Math.max(to, CH.trangThai(d, t).lo[2].s); }
  assert.ok(to > 1.05, 'nay ' + to);
  assert.deepStrictEqual(CH.trangThai(d, g + 0.37), CH.trangThai(d, g + 0.37));
});

test('dong ho dem nguoc: an truoc dem, so lon giam tu cho ve 1, cung giam dan, tat truoc khi hien dap an', function () {
  var d = du(3, 6, 5, 4);
  var q = d.cauHoi;
  assert.strictEqual(CH.trangThai(d, q.batDauDem - 0.01).dem.a, 0);
  assert.strictEqual(CH.trangThai(d, q.batDauDem + 0.01).dem.so, 5);
  assert.strictEqual(CH.trangThai(d, q.batDauDem + 1.01).dem.so, 4);
  assert.strictEqual(CH.trangThai(d, q.batDauDem + 4.99).dem.so, 1);
  assert.strictEqual(CH.trangThai(d, q.batDauDem + 2.5).dem.a, 1);
  var truoc = 2;
  for (var t = q.batDauDem; t < q.batDauDem + 5; t += 0.1) {
    var f = CH.trangThai(d, t).dem.f;
    assert.ok(f <= truoc + 1e-12 && f >= 0 && f <= 1, 'cung giam dan ' + f);
    truoc = f;
  }
  assert.ok(Math.abs(CH.trangThai(d, q.batDauDem + 2.5).dem.f - 0.5) < 1e-9);
  assert.strictEqual(CH.trangThai(d, q.batDauGiai).dem.a, 0);
  assert.strictEqual(CH.trangThai(d, q.batDauGiai + 2).dem.a, 0);
  assert.deepStrictEqual(CH.trangThai(d, q.batDauDem + 1.234), CH.trangThai(d, q.batDauDem + 1.234));
});

test('bo cuc: o lua chon khong chong nhau, khong chong cau hoi hay giai thich, dong ho nam trong vung giai thich', function () {
  [2, 3, 4].forEach(function (n) {
    var d = du(n, 12, 5, 6);
    var ds = CH.muc(d);
    var hop = CH.bo(d);
    assert.strictEqual(hop.length, n);
    var q = tim(ds, 'cau-hoi');
    var gt = tim(ds, 'giai-thich');
    hop.forEach(function (a, i) {
      assert.ok(a.x >= 40 && a.x + a.w <= 1240, 'ngang ' + JSON.stringify(a));
      assert.ok(a.y >= q.y + q.cao + 10 && a.y + a.h <= gt.y - 10, n + ' doc ' + JSON.stringify(a));
      hop.slice(i + 1).forEach(function (b) {
        var giao = a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;
        assert.ok(!giao, n + ' chong ' + JSON.stringify([a, b]));
      });
    });
    var dh = CH.DONG_HO;
    assert.ok(dh.y - dh.r - 8 >= gt.y && dh.y + dh.r + 8 <= 620, 'dong ho');
  });
});

test('may quay: dung yen truoc dem, day nhe trong luc dem, ve goc truoc cuoi canh', function () {
  var d = du(4, 8, 5, 6);
  var q = d.cauHoi;
  var goc = { z: 1, tx: 0, ty: 0 };
  assert.deepStrictEqual(CH.mayQuay(d, q.batDauDem - 0.5, goc), goc);
  var giua = CH.mayQuay(d, q.batDauDem + 4, goc);
  assert.ok(giua.z > 1.02 && giua.z <= 1.06, 'day nhe ' + giua.z);
  assert.ok(CH.mayQuay(d, q.batDauDem + 2, goc).z < giua.z, 'day cham dan');
  assert.deepStrictEqual(CH.mayQuay(d, d.thoiLuong - 0.2, goc), goc);
  // Toàn cảnh vẫn nằm trong khung và trên vạch phụ đề khi đẩy tối đa.
  var z = giua.z;
  assert.ok(giua.tx + z * 40 >= 0 && giua.tx + z * 1240 <= 1280, 'ngang');
  assert.ok(giua.ty + z * 30 >= 0 && giua.ty + z * 600 <= 620, 'doc ' + (giua.ty + z * 600));
  var ngan = du(2, 2.5, 3, 0.3);
  assert.deepStrictEqual(CH.mayQuay(ngan, ngan.thoiLuong - 0.2, goc), goc);
});

test('nayDanHoi: 1 tai 0 va 1, vuot len roi ve, xac dinh', function () {
  assert.strictEqual(D.nayDanHoi(0, 0.2), 1);
  assert.strictEqual(D.nayDanHoi(1, 0.2), 1);
  assert.strictEqual(D.nayDanHoi(5, 0.2), 1);
  var dinh = 0;
  for (var p = 0; p <= 1; p += 0.01) { dinh = Math.max(dinh, D.nayDanHoi(p, 0.2)); }
  assert.ok(dinh > 1.08 && dinh < 1.2, String(dinh));
});
