'use strict';
// Sự kiện âm thanh `suKien`: một nguồn thời gian với khung hình (Node, không DOM).
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
require(path.join(RT, 'chuyen-canh.js'));
require(path.join(RT, 'khung-video.js'));
require(path.join(RT, 'nhan.js'));
var LOAI = ['tieu-de', 'khai-niem', 'cong-thuc', 'y-tung-y', 'quy-trinh', 'so-sanh', 'do-thi', 'thi-nghiem', 'minh-hoa', 'anh',
  'bieu-do', 'so-do', 'dong-thoi-gian', 'cau-hoi'];
LOAI.forEach(function (l) { require(path.join(RT, 'canh', l + '.js')); });
var V = globalThis.THI_VIDEO;
var KHAI_BAO = JSON.parse(fs.readFileSync(path.join(TN, 'mo_hinh', 'li-con-lac-don.json'), 'utf8'));
var CAC_LOAI = ['but', 'ting', 'chuyen', 'tictac', 'dung', 'nhan'];
var HINH = { viewBox: '0 0 100 100', phanTu: [{ the: 'path', d: 'M10 10 L90 90' }, { the: 'path', d: 'M90 10 L10 90' }] };
var ANH = { dataUrl: 'data:image/png;base64,AA==', nguon: 'Ảnh: tác giả', rong: 800, cao: 600 };

function mocDeu(n, gh) {
  return Array.apply(null, Array(n)).map(function (_, k) { return Math.round((1.0 + k * Math.max(0.2, gh - 1.6) / n) * 1000) / 1000; });
}
// Mốc từng từ (như lich.py): lời đọc đều từ giây 1,0 tới gh − 0,6.
function tuDeu(loi, gh) {
  var tu = loi.split(' ');
  var buoc = Math.max(0.05, (gh - 1.6) / tu.length);
  return tu.map(function (w, i) { return { t: Math.round((1.0 + i * buoc) * 1000) / 1000, d: buoc, chu: w, khoa: w.toLowerCase() }; });
}
function du(loai, gh, soMuc, truong, them) {
  var d = { so: 2, loai: loai, thoiLuong: gh, danDau: 1.0, giayLauBang: 0.5, moc: mocDeu(soMuc, gh), truong: truong,
    tu: tuDeu('chu kì tăng gấp đôi khi dây dài gấp bốn lần nhé', gh), hinh: null, anh: null, hinhs: [],
    co: { banTay: true, mayQuay: true, chuDong: true, chuyen: 'lat-trang', lauBang: false } };
  Object.keys(them || {}).forEach(function (k) { d[k] = them[k]; });
  return d;
}
function cauHoi(gh) {
  // Cảnh câu hỏi ngắn (câu hỏi đọc 2 s, đếm 3 s, lời giải 0,2 s); mốc câu của lời câu hỏi nằm trong giọng câu hỏi.
  var dem = 3.0;
  var giai = Math.round((dem + 3 + 0.4) * 1000) / 1000;
  gh = Math.max(gh, Math.ceil((giai + 0.2 + 0.6) * 30 - 1e-9) / 30);
  return du('cau-hoi', gh, 5, { 'cau-hoi': ['==Chu kì== thay đổi thế nào?'], 'lua-chon': ['Tăng', 'Giảm', 'Không đổi', '{{2}} lần'],
    'dap-an': ['D'], 'giai-thich': ['((Chu kì)) tỉ lệ căn bậc hai.'], cho: ['3'] },
  { cauHoi: { batDauDem: dem, cho: 3, batDauGiai: giai, dapAn: 'D' },
    moc: [0, 1, 2, 3, 4].map(function (k) { return Math.round((1.0 + k * 0.4) * 1000) / 1000; }) });
}
// Mọi loại cảnh, mọi hiệu ứng bật: chuyển cảnh, chữ động, cụm nhấn, số chạy, hình, ảnh.
function tatCa(gh) {
  var y = ['==Chu kì== tăng khi dây dài', '((gấp đôi)) nhé', '__dây dài__ {{4}} lần', 'ý bốn', 'ý năm', 'ý sáu'];
  return {
    'tieu-de': du('tieu-de', gh, 0, { chu: ['Con lắc ==đơn=='], phu: ['Vật lí {{10}}'] }, { hinh: HINH }),
    'khai-niem': du('khai-niem', gh, 0, { 'thuat-ngu': ['Chu kì'], 'dinh-nghia': ['Thời gian ==một dao động== toàn phần.'] }, { anh: ANH }),
    'cong-thuc': du('cong-thuc', gh, 5, { 'bieu-thuc': ['T = 2π√(l/g) | ≈ {{2.0}} s'], 'giai-thich': ['==l== là chiều dài', 'g là gia tốc {{9.8}}'] }),
    'y-tung-y': du('y-tung-y', gh, 6, { 'tieu-de': ['Sáu ý'], y: y }, { hinh: HINH }),
    'quy-trinh': du('quy-trinh', gh, 5, { 'tieu-de': ['Quy trình'], buoc: ['Đo ==dây==', 'Thả', 'Đếm', 'Tính', 'Ghi'] }),
    'so-sanh': du('so-sanh', gh, 8, { 'tieu-de': ['So sánh'], trai: ['A'], phai: ['B'], 'y-trai': ['a', 'b', 'c', '==d=='], 'y-phai': ['e', 'f', 'g', 'h'] }),
    'do-thi': du('do-thi', gh, 4, { 'tieu-de': ['Đồ thị'], 'truc-ngang': ['t'], 'truc-doc': ['v'], diem: ['0, 0', '1, 2', '2, 4', '3, 5'] },
      { diem: [[0, 0], [1, 2], [2, 4], [3, 5]] }),
    'thi-nghiem': du('thi-nghiem', gh, 0, { mau: ['li-con-lac-don'] },
      { khaiBao: KHAI_BAO, thamSo: { 'chieu-dai': [[0, 0.4], [Math.max(0.5, gh - 1), 1.6]] }, do: ['chu-ki'] }),
    'minh-hoa': du('minh-hoa', gh, 3, { 'tieu-de': ['Minh hoạ'] },
      { hinhs: [HINH, HINH, HINH].map(function (h, k) { return { viewBox: h.viewBox, phanTu: h.phanTu, nhan: 'Hình ' + k }; }) }),
    anh: du('anh', gh, 1, { 'chu-thich': ['Con lắc ==đơn== trong phòng thí nghiệm'] }, { anh: ANH }),
    cot: du('bieu-do', gh, 4, { 'tieu-de': ['Sản lượng'], kieu: ['cot'], 'du-lieu': ['A | 1', 'B | -2', 'C | 3', 'D | 100000'] },
      { duLieu: [['A', 1], ['B', -2], ['C', 3], ['D', 100000]] }),
    tron: du('bieu-do', gh, 3, { 'tieu-de': ['Tỉ lệ'], kieu: ['tron'], 'du-lieu': ['A | 1', 'B | 2', 'C | 3'] },
      { duLieu: [['A', 1], ['B', 2], ['C', 3]] }),
    'so-do': du('so-do', gh, 6, { 'trung-tam': ['Con lắc'], nhanh: ['==Chu kì==', 'b', 'c', 'd', 'e', 'f'] }),
    'dong-thoi-gian': du('dong-thoi-gian', gh, 6, { 'tieu-de': ['Tiến trình'],
      moc: ['1900 | a', '1910 | b', '1920 | ==c==', '1930 | d', '1940 | e', '1950 | f'] }),
    'cau-hoi': cauHoi(gh)
  };
}
function kiemSuKien(ten, d, ds) {
  var gh = d.thoiLuong;
  var truoc = -1;
  var da = {};
  var tongBut = 0;
  var hetBut = -1;
  ds.forEach(function (e, i) {
    var ma = ten + '@' + gh + '#' + i + ' ' + JSON.stringify(e);
    assert.deepStrictEqual(Object.keys(e).sort(), ['dai', 'loai', 't'], ma);
    assert.ok(CAC_LOAI.indexOf(e.loai) >= 0, ma + ' loai la');
    assert.ok(e.t >= 0 && e.t <= gh - 0.1 + 1e-9, ma + ' ngoai [0, gh - 0,1]');
    assert.ok(e.t >= truoc, ma + ' khong sap theo t');
    truoc = e.t;
    var khoa = e.loai + '@' + e.t;
    assert.ok(!da[khoa], ma + ' trung');
    da[khoa] = true;
    if (e.loai === 'but') {
      assert.ok(e.dai > 0, ma + ' but dai 0');
      assert.ok(e.t + e.dai <= gh - 0.1 + 1e-9, ma + ' but vuot cuoi canh');
      assert.ok(e.t >= hetBut - 1e-9, ma + ' hai doan but chong nhau');
      hetBut = e.t + e.dai;
      tongBut += e.dai;
    } else {
      assert.strictEqual(e.dai, 0, ma);
    }
  });
  assert.ok(tongBut <= 0.4 * gh + 1e-9, ten + '@' + gh + ' tong but ' + tongBut + ' > 40% ' + gh);
  return tongBut;
}

test('suKien: xac dinh, sap theo t, khong trung, trong [0, gh - 0,1], tong but <= 40% moi loai canh', function () {
  [2.5, 2.5667, 6, 20].forEach(function (gh) {
    var bo = tatCa(gh);
    Object.keys(bo).forEach(function (ten) {
      var d = bo[ten];
      var ds = V.suKienCua(d);
      assert.deepStrictEqual(ds, V.suKienCua(d), ten + ' xac dinh');
      assert.ok(ds.length > 0, ten);
      kiemSuKien(ten, d, ds);
    });
  });
});

test('Review Focus 5: canh 2,5 s moi hieu ung bat — khong muc nao, khong su kien nao vuot cuoi canh; but <= 40%', function () {
  var bo = tatCa(2.5);
  Object.keys(bo).forEach(function (ten) {
    var d = bo[ten];
    var gh = d.thoiLuong;
    globalThis.THI_CANH[d.loai].muc(d).forEach(function (m) {
      assert.ok(m.batDau + m.thoiLuong <= gh - 0.2 + 1e-9, ten + ':' + m.id + ' vuot cuoi canh');
    });
    var ds = V.suKienCua(d);
    var tong = kiemSuKien(ten, d, ds);
    assert.ok(tong > 0, ten + ' co tieng but');
    assert.ok(ds.some(function (e) { return e.loai === 'chuyen' && e.t === 0; }), ten + ' co chuyen canh luc 0');
  });
  // Cảnh 2,5 s nhiều chữ: tổng bút bị co về đúng 40%.
  var y = bo['y-tung-y'];
  var tongY = V.suKienCua(y).filter(function (e) { return e.loai === 'but'; }).reduce(function (s, e) { return s + e.dai; }, 0);
  assert.ok(Math.abs(tongY - 0.4 * 2.5) < 0.01, 'co ve 40%: ' + tongY);
});

test('chuyen: chi khi canh co chuyen canh (du.co.chuyen hoac lauBang kieu cu)', function () {
  var d = tatCa(12)['y-tung-y'];
  assert.deepStrictEqual(V.suKienCua(d)[0], { t: 0, loai: 'chuyen', dai: 0 });
  d.co = { banTay: true, mayQuay: true, chuDong: true, chuyen: null, lauBang: false };
  assert.ok(!V.suKienCua(d).some(function (e) { return e.loai === 'chuyen'; }));
  d.co = { lauBang: true };
  assert.ok(V.suKienCua(d).some(function (e) { return e.loai === 'chuyen'; }));
});

test('ting: moi y, buoc, nhanh, moc, cot, lat, lua chon hien ra dung luc muc cua no bat dau', function () {
  var bo = tatCa(20);
  var tim = function (ds, id) { return ds.filter(function (m) { return m.id === id; })[0]; };
  [['y-tung-y', 'cham-', 6], ['quy-trinh', 'hop-', 5], ['so-do', 'nhanh-', 6], ['dong-thoi-gian', 'cham-', 6], ['cot', 'cot-', 4],
    ['tron', 'lat-', 3], ['cau-hoi', 'o-', 4], ['so-sanh', 'y-trai-', 4], ['so-sanh', 'y-phai-', 4]].forEach(function (c) {
    var d = bo[c[0]];
    var muc = globalThis.THI_CANH[d.loai].muc(d);
    var ting = V.suKienCua(d).filter(function (e) { return e.loai === 'ting'; }).map(function (e) { return e.t; });
    for (var k = 0; k < c[2]; k++) {
      var m = tim(muc, c[1] + k);
      assert.ok(ting.some(function (t) { return Math.abs(t - m.batDau) < 0.0011; }), c[0] + ' ' + c[1] + k + ' khong co ting luc ' + m.batDau);
    }
  });
  assert.ok(!V.suKienCua(bo['khai-niem']).some(function (e) { return e.loai === 'ting'; }), 'khai-niem khong co y nao');
});

test('cau hoi: tictac moi giay dem nguoc, dung luc hien dap an', function () {
  [3, 5, 10].forEach(function (cho) {
    var d = cauHoi(20);
    d.cauHoi.cho = cho;
    d.truong.cho = [String(cho)];
    d.cauHoi.batDauGiai = Math.round((d.cauHoi.batDauDem + cho + 0.4) * 1000) / 1000;
    d.thoiLuong = Math.ceil((d.cauHoi.batDauGiai + 3 + 0.6) * 30 - 1e-9) / 30;
    var ds = V.suKienCua(d);
    var tic = ds.filter(function (e) { return e.loai === 'tictac'; }).map(function (e) { return e.t; });
    assert.strictEqual(tic.length, cho);
    tic.forEach(function (t, k) { assert.ok(Math.abs(t - (d.cauHoi.batDauDem + k)) < 0.0011, 'tictac ' + k); });
    var dung = ds.filter(function (e) { return e.loai === 'dung'; });
    assert.strictEqual(dung.length, 1);
    assert.ok(Math.abs(dung[0].t - d.cauHoi.batDauGiai) < 0.0011);
    // Đếm ngược không có tiếng bút (bàn tay đã rời bảng).
    ds.filter(function (e) { return e.loai === 'but'; }).forEach(function (e) {
      assert.ok(e.t + e.dai <= d.cauHoi.batDauDem + 1e-9 || e.t >= d.cauHoi.batDauGiai - 1e-9, 'but trong luc dem ' + JSON.stringify(e));
    });
  });
  assert.ok(!V.suKienCua(tatCa(20)['y-tung-y']).some(function (e) { return e.loai === 'tictac' || e.loai === 'dung'; }));
});

test('nhan: moi cum nhan co mot su kien dung luc no (lan dau cum xuat hien trong loi)', function () {
  var d = tatCa(20)['y-tung-y'];
  var nhan = V.suKienCua(d).filter(function (e) { return e.loai === 'nhan'; });
  assert.strictEqual(nhan.length, 3, JSON.stringify(nhan));
  // "==Chu kì==" ở ý 0: lời có "chu kì" ở từ đầu tiên (t = 1,0) nhưng ý 0 viết từ moc[0] = 1,0 → nổ lúc 1,0 hoặc sau khi viết xong.
  var y0 = globalThis.THI_CANH['y-tung-y'].muc(d).filter(function (m) { return m.id === 'y-0'; })[0];
  assert.ok(nhan[0].t >= y0.batDau, JSON.stringify(nhan[0]));
  var khong = tatCa(20)['khai-niem'];
  khong.truong['dinh-nghia'] = ['Không có cụm nhấn.'];
  assert.ok(!V.suKienCua(khong).some(function (e) { return e.loai === 'nhan'; }));
});

test('but: doan chong nhau duoc gop; canh dai it chu khong bi co', function () {
  var d = tatCa(20)['quy-trinh'];
  var but = V.suKienCua(d).filter(function (e) { return e.loai === 'but'; });
  // Hộp và chữ của một bước viết chồng thời gian: gộp thành một đoạn, không chồng nhau.
  for (var i = 1; i < but.length; i++) { assert.ok(but[i].t > but[i - 1].t + but[i - 1].dai - 1e-9); }
  var muc = globalThis.THI_CANH['quy-trinh'].muc(d).filter(function (m) { return m.kieu !== 'anh' && !m.dong; });
  var dau = Math.min.apply(null, muc.map(function (m) { return m.batDau; }));
  assert.ok(Math.abs(but[0].t - Math.floor(dau * 1000) / 1000) < 0.0011, 'doan but dau bat dau cung muc dau');
  var tong = but.reduce(function (s, e) { return s + e.dai; }, 0);
  assert.ok(tong < 0.4 * 20, 'khong can co: ' + tong);
});

test('tieu de chu nay (chu-dong) khong co tieng but cho chu nay', function () {
  var d = tatCa(12)['tieu-de'];
  d.hinh = null;
  var muc = globalThis.THI_CANH['tieu-de'].muc(d);
  var chu = muc.filter(function (m) { return m.id === 'chu'; })[0];
  assert.ok(chu.nay);
  var but = V.suKienCua(d).filter(function (e) { return e.loai === 'but'; });
  but.forEach(function (e) { assert.ok(e.t >= chu.batDau + chu.thoiLuong - 0.0011 || e.t + e.dai <= chu.batDau + 1e-9, JSON.stringify(e)); });
});
