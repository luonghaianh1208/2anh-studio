'use strict';
// Biểu đồ, sơ đồ tư duy, dòng thời gian và công thức từng phần: hàm thuần theo t (Node, không DOM).
var test = require('node:test');
var assert = require('node:assert');
var path = require('node:path');

var RT = path.join(__dirname, '..', '..', 'video_ma_parts', 'runtime');
require(path.join(RT, 'kho.js'));
require(path.join(RT, 'dong.js'));
require(path.join(RT, 'khung-video.js'));
['bieu-do', 'so-do', 'dong-thoi-gian', 'cong-thuc'].forEach(function (l) { require(path.join(RT, 'canh', l + '.js')); });
var V = globalThis.THI_VIDEO;
var C = globalThis.THI_CANH;
var BD = C['bieu-do'];

function du(loai, gh, moc, truong, them) {
  var d = { so: 2, loai: loai, thoiLuong: gh, danDau: 1.0, moc: moc, truong: truong, co: { banTay: true, mayQuay: true } };
  Object.keys(them || {}).forEach(function (k) { d[k] = them[k]; });
  return d;
}
function mocDeu(n, gh) {
  return Array.apply(null, Array(n)).map(function (_, k) { return Math.round((1.0 + k * (gh - 1.6) / n) * 1000) / 1000; });
}
function bieuDo(kieu, duLieu, gh, them) {
  var truong = { 'tieu-de': ['Sản lượng'], kieu: [kieu], 'du-lieu': duLieu.map(function (d) { return d[0] + ' | ' + d[1]; }) };
  Object.keys(them || {}).forEach(function (k) { truong[k] = them[k]; });
  return du('bieu-do', gh, mocDeu(duLieu.length, gh), truong,
    { duLieu: duLieu.map(function (d) { return [d[0], Number(d[1])]; }) });
}
function x16(k) { return ('Nhờ ướt nhẫm ' + k + 'xyzw').slice(0, 16); }
function tamBo(gh) {
  var tam = Array.apply(null, Array(8)).map(function (_, k) { return [x16(k), ['12.5', '-40', '0', '100000', '1', '-7.25', '3000', '99999.99'][k]]; });
  var nhanh = Array.apply(null, Array(6)).map(function (_, k) { return ('Nhánh ' + k + ' của sơ đồ tư duy rất dài nhé các em ơi').slice(0, 40); });
  var moc = Array.apply(null, Array(6)).map(function (_, k) {
    return (190 + k) + '0 năm | ' + ('Sự kiện ' + k + ' mô tả dài đúng sáu mươi ký tự cho dòng thời gian này nhé các em').slice(0, 60);
  });
  return {
    cot: bieuDo('cot', tam, gh, { 'truc-ngang': ['Cây trồng'], 'truc-doc': ['Sản lượng'], 'don-vi': ['tấn'] }),
    duong: bieuDo('duong', tam, gh),
    tron: bieuDo('tron', tam.map(function (d, k) { return [d[0], ['12.5', '40', '0.5', '100000', '1', '7.25', '3000', '2'][k]]; }), gh),
    'so-do': du('so-do', gh, mocDeu(6, gh), { 'trung-tam': ['Trung tâm của sơ đồ tư duy ba mươi'], nhanh: nhanh }),
    'dong-thoi-gian': du('dong-thoi-gian', gh, mocDeu(6, gh), { 'tieu-de': ['Tiến trình'], moc: moc }),
    'cong-thuc': du('cong-thuc', gh, mocDeu(5, gh), { 'bieu-thuc': ['T = 2π√(l/g) | = 2π√(1/9.8) | ≈ {{2.0}} s'], 'giai-thich': ['l là chiều dài', 'g là gia tốc'] })
  };
}
function tim(ds, id) { return ds.filter(function (m) { return m.id === id; })[0]; }
function toaDo(d) { return d.match(/-?\d+(\.\d+)?/g).map(Number); }
function day(m) {
  if (m.kieu === 'net') { return Math.max.apply(null, toaDo(m.d).filter(function (_, i) { return i % 2 === 1; })); }
  if (m.kieu === 'hinh') { return m.y + m.kich; }
  return m.y + m.cao;
}

test('thang so tron: 1, 2, 5 x 10^n, 4-6 vach, phu het so lieu', function () {
  var kiem = function (so, kieu, mong) {
    var th = BD.thang(so, kieu);
    if (mong) { assert.deepStrictEqual(th.vach, mong, JSON.stringify(so)); }
    assert.ok(th.vach.length >= 4 && th.vach.length <= 6, JSON.stringify([so, th.vach]));
    assert.ok(th.lo <= Math.min.apply(null, so) && th.hi >= Math.max.apply(null, so), JSON.stringify([so, th.vach]));
    var mu = Math.pow(10, Math.floor(Math.log10(th.buoc)));
    assert.ok([1, 2, 5].some(function (m) { return Math.abs(th.buoc - m * mu) < 1e-9 * mu; }), 'buoc ' + th.buoc);
    th.vach.forEach(function (v, i) { if (i) { assert.ok(Math.abs(v - th.vach[i - 1] - th.buoc) < 1e-9 * th.buoc, String(th.vach)); } });
    return th;
  };
  kiem([0.3, 7.2], 'cot', [0, 2, 4, 6, 8]);
  kiem([-40, 25], 'cot', [-40, -20, 0, 20, 40]);
  kiem([1, 100000], 'cot', [0, 20000, 40000, 60000, 80000, 100000]);
  kiem([0.3, 7.2], 'duong', [0, 2, 4, 6, 8]);
  kiem([20, 25], 'duong', [20, 21, 22, 23, 24, 25]);
  kiem([0, 0], 'cot');
  kiem([5, 5], 'duong');
  kiem([-3, -3], 'cot');
  kiem([-5, 4.25], 'cot', [-10, -5, 0, 5]);
  kiem([0.001, 0.0042], 'duong');
  // Quét nhiều khoảng: luôn 4–6 vạch.
  for (var a = -7; a <= 7; a++) {
    [0.013, 0.3, 1, 2.5, 7.9, 13, 99, 1234, 5e6].forEach(function (s) {
      kiem([a * s, a * s + s * 3.7], 'duong');
      kiem([a * s, a * s + s * 3.7], 'cot');
    });
  }
});

test('phan tu k bat dau tai moc cau k', function () {
  var bo = tamBo(20);
  [['cot', 'cot-'], ['duong', 'diem-'], ['tron', 'lat-'], ['so-do', 'nhanh-'], ['dong-thoi-gian', 'cham-']].forEach(function (c) {
    var d = bo[c[0]];
    var ds = C[d.loai].muc(d);
    d.moc.forEach(function (m, k) { assert.strictEqual(tim(ds, c[1] + k).batDau, m, c[0] + ' ' + k); });
  });
  var ct = bo['cong-thuc'];
  var bt = tim(C['cong-thuc'].muc(ct), 'bieu-thuc');
  assert.strictEqual(bt.phan.length, 3);
  bt.phan.forEach(function (p, k) { assert.strictEqual(p.batDau, ct.moc[k], 'phan ' + k); });
});

test('moi loai canh moi: 2,5 s va 20 s, co chuyen canh: xac dinh, khong muc nao vuot cuoi, trong day 620', function () {
  [2.5, 2.5667, 20].forEach(function (gh) {
    [null, 'lat-trang'].forEach(function (chuyen) {
      var bo = tamBo(gh);
      Object.keys(bo).forEach(function (ten) {
        var d = bo[ten];
        d.co.chuyen = chuyen;
        var ds = C[d.loai].muc(d);
        assert.deepStrictEqual(ds, C[d.loai].muc(d), ten + ' xac dinh');
        var ids = ds.map(function (m) { return m.id; });
        assert.strictEqual(new Set(ids).size, ids.length, ten + ' id trung');
        ds.forEach(function (m) {
          var ma = ten + '@' + gh + ':' + m.id;
          assert.ok(m.batDau >= (chuyen ? 0.55 - 1e-9 : 0.1), ma + ' bat dau ' + m.batDau);
          assert.ok(m.batDau + m.thoiLuong <= gh - 0.2 + 1e-9, ma + ' xong ' + (m.batDau + m.thoiLuong));
          (m.phan || []).forEach(function (p) { assert.ok(p.batDau + p.thoiLuong <= gh - 0.2 + 1e-9, ma + ' phan'); });
          assert.ok(day(m) <= 620, ma + ' xuong toi ' + day(m));
          if (m.kieu === 'chu') { assert.ok(m.x >= 0 && m.x + m.rong <= 1280 && m.y >= 0, ma + ' ngoai khung'); }
        });
      });
    });
  });
});

test('cot am moc xuong duoi truc, cot duong moc len; nhan gia tri la so chay giu dung chuoi so', function () {
  var d = bieuDo('cot', [['A', '12.5'], ['B', '-40'], ['C', '0'], ['D', '25']], 12);
  var ds = BD.muc(d);
  [0, 1, 2, 3].forEach(function (k) {
    var to = tim(ds, 'cot-' + k).to;
    var v = d.duLieu[k][1];
    if (v > 0) { assert.ok(to.y < to.y0, 'cot duong di len ' + k); }
    if (v < 0) { assert.ok(to.y > to.y0, 'cot am di xuong ' + k); }
    if (v === 0) { assert.strictEqual(to.y, to.y0); }
  });
  assert.deepStrictEqual([0, 1, 2, 3].map(function (k) { return tim(ds, 'so-' + k).chu; }), ['{{12.5}}', '{{-40}}', '{{0}}', '{{25}}']);
  // Nhãn giá trị: cột dương ở trên đầu cột, cột âm ở dưới đáy cột; không đè nhãn loại.
  var am = tim(ds, 'so-1');
  assert.ok(am.y >= tim(ds, 'cot-1').to.y);
  assert.ok(am.y + am.cao <= tim(ds, 'nhan-1').y, 'nhan gia tri cot am khong de nhan loai');
  var duong = tim(ds, 'so-3');
  assert.ok(duong.y + duong.cao <= tim(ds, 'cot-3').to.y);
  assert.ok(duong.y >= 202, 'khong de ten truc doc');
});

test('nhan gia tri va nhan loai cua 8 cot nam gon trong o cua cot, khong chong nhau', function () {
  var d = tamBo(20).cot;
  var ds = BD.muc(d);
  for (var k = 0; k < 8; k++) {
    ['so-', 'nhan-'].forEach(function (tt) {
      var a = tim(ds, tt + k), b = tim(ds, tt + (k + 1));
      if (b) { assert.ok(a.x + a.rong <= b.x, tt + k + ' cham ' + (k + 1)); }
    });
  }
  assert.ok(tim(ds, 'so-0').co >= 16, 'so 9 ky tu van du lon: ' + tim(ds, 'so-0').co);
});

test('bieu do tron: phan tram cong lai 100, nhan hai ben khong chong nhau, lat noi tiep kin vong', function () {
  var d = tamBo(20).tron;
  var ds = BD.muc(d);
  var nhan = ds.filter(function (m) { return /^nhan-/.test(m.id); });
  assert.strictEqual(nhan.length, 8);
  var tong = nhan.reduce(function (s, m) { return s + Number(/\{\{([\d.]+)\}\}%$/.exec(m.chu)[1]); }, 0);
  assert.ok(Math.abs(tong - 100) < 0.5, String(tong));
  nhan.forEach(function (a) {
    assert.ok(a.y >= 170 && a.y + a.cao <= 620, a.id + ' ' + a.y);
    nhan.forEach(function (b) {
      if (a !== b && a.x === b.x) { assert.ok(a.y + a.cao <= b.y || b.y + b.cao <= a.y, a.id + ' de ' + b.id); }
    });
  });
  var lat = ds.filter(function (m) { return /^lat-/.test(m.id); }).map(function (m) { return m.to; });
  assert.strictEqual(lat[0].a0, -90);
  lat.forEach(function (l, k) { if (k) { assert.strictEqual(l.a0, lat[k - 1].a1); } });
  assert.ok(Math.abs(lat[7].a1 - 270) < 0.1);
});

test('so do: moi so nhanh 2-6 co goc co dinh, o nhan khong chong nhau va khong de nut trung tam', function () {
  [false, true].forEach(function (coHinh) {
    for (var n = 2; n <= 6; n++) {
      var nhanh = Array.apply(null, Array(n)).map(function (_, k) { return 'Nhánh ' + k; });
      var d = du('so-do', 20, mocDeu(n, 20), { 'trung-tam': ['Tâm'], nhanh: nhanh },
        coHinh ? { hinh: { viewBox: '0 0 24 24', phanTu: [{ the: 'path', thuocTinh: { d: 'M1 1l2 2' } }] } } : {});
      var ds = C['so-do'].muc(d);
      assert.strictEqual(C['so-do'].GOC[n].length, n);
      var o = ds.filter(function (m) { return /^o-/.test(m.id); }).map(function (m) {
        var s = toaDo(m.d);
        var xs = s.filter(function (_, i) { return i % 2 === 0; }), ys = s.filter(function (_, i) { return i % 2 === 1; });
        return [Math.min.apply(null, xs), Math.min.apply(null, ys), Math.max.apply(null, xs), Math.max.apply(null, ys)];
      });
      var tam = tim(ds, 'vong-tam');
      var st = toaDo(tam.d);
      var tx = st.filter(function (_, i) { return i % 2 === 0; }), ty = st.filter(function (_, i) { return i % 2 === 1; });
      var hopTam = [Math.min.apply(null, tx), Math.min.apply(null, ty), Math.max.apply(null, tx), Math.max.apply(null, ty)];
      o.forEach(function (a, i) {
        assert.ok(a[0] >= 0 && a[2] <= 1280 && a[1] >= 100 && a[3] <= 620, n + ' o ' + i + ' ' + a);
        o.forEach(function (b, j) {
          if (i < j) { assert.ok(a[2] <= b[0] || b[2] <= a[0] || a[3] <= b[1] || b[3] <= a[1], n + ': o ' + i + ' cham o ' + j); }
        });
        // Góc ô nằm ngoài elip trung tâm.
        [[a[0], a[1]], [a[2], a[1]], [a[0], a[3]], [a[2], a[3]], [(a[0] + a[2]) / 2, a[1]], [(a[0] + a[2]) / 2, a[3]]].forEach(function (p) {
          var rx = (hopTam[2] - hopTam[0]) / 2, ry = (hopTam[3] - hopTam[1]) / 2;
          var q = Math.pow((p[0] - C['so-do'].TAM.x) / rx, 2) + Math.pow((p[1] - C['so-do'].TAM.y) / ry, 2);
          assert.ok(q > 1, n + ' o ' + i + ' de nut trung tam ' + p);
        });
      });
    }
  });
});

test('so do: may quay khong day o nhanh da ve xuong vung phu de (day <= 620) o moi thoi diem', function () {
  require(path.join(RT, 'may-quay.js'));
  var Q = globalThis.THI_MAY_QUAY;
  function hop(m) {
    if (m.kieu === 'chu') { return { x: m.x, y: m.y, w: m.rong, h: m.cao }; }
    if (m.kieu === 'hinh') { return { x: m.x, y: m.y, w: m.kich, h: m.kich }; }
    var s = toaDo(m.d);
    var xs = s.filter(function (_, i) { return i % 2 === 0; }), ys = s.filter(function (_, i) { return i % 2 === 1; });
    var x0 = Math.min.apply(null, xs), y0 = Math.min.apply(null, ys);
    return { x: x0, y: y0, w: Math.max.apply(null, xs) - x0, h: Math.max.apply(null, ys) - y0 };
  }
  [2, 3, 4, 5, 6].forEach(function (n) {
    var gh = 16;
    var nhanh = Array.apply(null, Array(n)).map(function (_, k) { return 'Nhánh số ' + k; });
    var ds = C['so-do'].muc(du('so-do', gh, mocDeu(n, gh), { 'trung-tam': ['Chu kì con lắc đơn'], nhanh: nhanh }));
    var cacHop = {};
    ds.forEach(function (m) { cacHop[m.id] = hop(m); });
    for (var i = 0; i <= 320; i++) {
      var t = gh * i / 320;
      var s = Q.tinh(ds, cacHop, t, gh, {});
      ds.forEach(function (m) {
        if (m.batDau > t) { return; }
        var b = cacHop[m.id];
        assert.ok(s.z * (b.y + b.h) + s.ty <= 620 + 1e-6, n + ' nhanh, t=' + t.toFixed(2) + ': ' + m.id + ' xuong vung phu de');
      });
    }
  });
});

test('dong thoi gian: truc ve truoc 0,6 s; tren 4 moc thi xen ke cao thap, o cung phia khong cham', function () {
  [2, 4, 5, 6].forEach(function (n) {
    var moc = Array.apply(null, Array(n)).map(function (_, k) { return (1900 + k) + ' | Mô tả ' + k; });
    var d = du('dong-thoi-gian', 20, mocDeu(n, 20), { 'tieu-de': ['T'], moc: moc });
    var ds = C['dong-thoi-gian'].muc(d);
    var truc = tim(ds, 'truc');
    assert.strictEqual(truc.thoiLuong, 0.6);
    assert.ok(truc.batDau + truc.thoiLuong <= d.moc[0] + 1e-9, 'truc xong truoc moc dau');
    var hop = [];
    for (var k = 0; k < n; k++) {
      var nh = tim(ds, 'nhan-' + k), mt = tim(ds, 'mo-ta-' + k);
      assert.strictEqual(nh.chu, String(1900 + k));
      assert.strictEqual(mt.chu, 'Mô tả ' + k);
      var tren = nh.y + nh.cao <= 400;
      assert.strictEqual(tren, n <= 4 || k % 2 === 0, n + ' moc ' + k);
      assert.strictEqual(mt.y + mt.cao <= 400, n > 4 && k % 2 === 0, n + ' mo ta ' + k);
      assert.ok(mt.batDau >= nh.batDau + nh.thoiLuong - 1e-9);
      hop.push(nh, mt);
    }
    hop.forEach(function (a) {
      hop.forEach(function (b) {
        if (a !== b) { assert.ok(a.x + a.rong <= b.x || b.x + b.rong <= a.x || a.y + a.cao <= b.y || b.y + b.cao <= a.y, n + ': ' + a.id + ' cham ' + b.id); }
      });
    });
  });
});

test('cong thuc tung phan: phan noi tiep, but dung giua hai phan; khong co | thi nhu cu', function () {
  var ct = tamBo(20)['cong-thuc'];
  var ds = C['cong-thuc'].muc(ct);
  var bt = tim(ds, 'bieu-thuc');
  assert.strictEqual(bt.chu, 'T = 2π√(l/g) = 2π√(1/9.8) ≈ {{2.0}} s');
  var tong = V.demKyTu(bt.chu, true);
  assert.strictEqual(bt.phan.reduce(function (s, p) { return s + p.ky; }, 0), tong);
  bt.phan.forEach(function (p, k) {
    if (k) { assert.ok(p.batDau >= bt.phan[k - 1].batDau + bt.phan[k - 1].thoiLuong - 1e-9, 'noi tiep'); }
  });
  // Số ký tự hiện: 0 trước phần đầu, dừng ở cuối phần 0 trong khoảng nghỉ, đủ ở cuối.
  var p0 = bt.phan[0], p1 = bt.phan[1];
  assert.strictEqual(V.kyTuHien(bt, p0.batDau - 0.01, tong), 0);
  assert.strictEqual(V.kyTuHien(bt, (p0.batDau + p0.thoiLuong + p1.batDau) / 2, tong), p0.ky);
  assert.strictEqual(V.kyTuHien(bt, 1e6, tong), tong);
  // Số chạy {{2.0}} ở phần 2 chạy khi phần 2 được viết.
  var vt = V.viTriSo(bt.chu, true)[0].viTri;
  assert.ok(V.lucKyTu(bt, vt, tong) >= bt.phan[2].batDau);
  // Giải thích k ở mốc (số phần + k), sau khi viết xong biểu thức.
  [0, 1].forEach(function (k) {
    var g = tim(ds, 'giai-thich-' + k);
    assert.ok(g.batDau >= ct.moc[3 + k] - 1e-9 && g.batDau >= bt.batDau + bt.thoiLuong);
  });
  // Bàn tay và máy quay thấy mỗi phần là một mục riêng.
  var ve = V.tachPhan(ds).filter(function (m) { return m.id === 'bieu-thuc'; });
  assert.deepStrictEqual(ve.map(function (m) { return [m.batDau, m.thoiLuong]; }), bt.phan.map(function (p) { return [p.batDau, p.thoiLuong]; }));
  // Không có ` | `: một mục như cũ.
  ct.truong['bieu-thuc'] = ['|x| = 2'];
  var cu = tim(C['cong-thuc'].muc(ct), 'bieu-thuc');
  assert.strictEqual(cu.phan, undefined);
  assert.strictEqual(cu.chu, '|x| = 2');
  assert.strictEqual(V.tachPhan([cu])[0], cu);
});
