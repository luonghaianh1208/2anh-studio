(function (root) {
  'use strict';
  var V = root.THI_VIDEO;
  // Bản vẽ mô hình nằm trong khung ô `thi-nghiem`, lùi 4 mỗi bên; bảng số ở ô `bang-so`.
  function banVe() {
    var o = V.o('thi-nghiem');
    return { x: o.x + 4, y: o.y + 4, rong: o.w - 8, cao: o.h - 8 };
  }

  function thamSoTai(du, t) {
    var K = root.THI_NGHIEM_KHUNG;
    var p = K.thamSoMacDinh(du.khaiBao);
    Object.keys(du.thamSo).forEach(function (ma) {
      var ds = du.thamSo[ma];
      var cuoi = ds[ds.length - 1];
      if (t < ds[0][0]) { return; }
      if (t >= cuoi[0]) { p[ma] = cuoi[1]; return; }
      for (var i = 1; i < ds.length; i++) {
        if (t < ds[i][0]) {
          var a = ds[i - 1], b = ds[i];
          p[ma] = a[1] + (b[1] - a[1]) * (t - a[0]) / (b[0] - a[0]);
          return;
        }
      }
    });
    return p;
  }

  function giaTri(du, t) {
    var p = thamSoTai(du, t);
    return { tham: p, dai: root.THI_NGHIEM_MO_HINH.tinh(p) };
  }

  function mocGanNhat(du, t) {
    var m = du.danDau;
    Object.keys(du.thamSo).forEach(function (ma) {
      du.thamSo[ma].forEach(function (x) { if (x[0] <= t && x[0] > m) { m = x[0]; } });
    });
    return m;
  }

  // Mô hình chạy một lần (ném xiên, tốc độ phản ứng) chạy lại từ mốc tham-so gần nhất.
  function thoiGianMoHinh(du, t) {
    var goc = du.khaiBao.hoatHinh === 'mot-lan' ? mocGanNhat(du, t) : du.danDau;
    return Math.max(0, t - goc);
  }

  function soThapPhan(buoc) {
    var s = String(buoc);
    var i = s.indexOf('.');
    return i < 0 ? 0 : Math.min(3, s.length - i - 1);
  }
  function tim(ds, ma) { return ds.filter(function (x) { return x.ma === ma; })[0]; }

  root.THI_CANH['thi-nghiem'] = {
    thamSoTai: thamSoTai,
    giaTri: giaTri,
    mocGanNhat: mocGanNhat,
    thoiGianMoHinh: thoiGianMoHinh,
    muc: function (du) {
      var B = V.tao(du);
      var kb = du.khaiBao;
      var o = V.o('thi-nghiem'), s = V.o('bang-so');
      var kq = B.tieuDe(kb.ten, 0.2);
      kq.push(B.net('khung', V.hopQua(o.x, o.y, o.w, o.h, 5), 0.1, 0.7, {}));
      // Bảng số: nhãn cao 40, ba dòng thông số cao 56, cách 10 rồi nhãn số đo và ba dòng cao 58.
      kq.push(B.chu('nhan-tham-so', 'Thông số', s.x, s.y, s.w, 40, 26, 0.4, { mau: 'nhan' }));
      Object.keys(du.thamSo).slice(0, 3).forEach(function (ma, k) {
        kq.push(B.chu('ts-' + k, '', s.x, s.y + 42 + k * 56, s.w, 56, 20, 0.4, { dong: true }));
      });
      var yDo = s.y + 42 + 3 * 56 + 10;
      kq.push(B.chu('nhan-do', 'Số đo', s.x, yDo, s.w, 40, 26, 0.4, { mau: 'nhan' }));
      du.do.slice(0, 3).forEach(function (ma, k) {
        kq.push(B.chu('do-' + k, '', s.x, yDo + 42 + k * 58, s.w, 58, 20, 0.4, { dong: true, mau: 'do' }));
      });
      return kq;
    },
    dung: function (goc) {
      // Chữ mô hình vẽ trên canvas (ví dụ "Số dao động") cũng dùng Itim như cả khung hình; chỉ đổi trong trang video.
      root.THI_NGHIEM_KHUNG.PHONG = "'Itim', sans-serif";
      var b = banVe();
      var c = document.createElement('canvas');
      c.id = 'ban-ve';
      c.width = b.rong;
      c.height = b.cao;
      c.style.position = 'absolute';
      c.style.left = b.x + 'px';
      c.style.top = b.y + 'px';
      c.style.background = '#ffffff';
      goc.appendChild(c);
    },
    capNhat: function (goc, du, t) {
      var K = root.THI_NGHIEM_KHUNG;
      var M = root.THI_NGHIEM_MO_HINH;
      var g = giaTri(du, t);
      var b = banVe();
      var ctx = goc.querySelector('#ban-ve').getContext('2d');
      ctx.clearRect(0, 0, b.rong, b.cao);
      var tm = thoiGianMoHinh(du, t);
      if (typeof M.thoiLuong === 'function') { tm = Math.min(tm, M.thoiLuong(g.tham, g.dai)); }
      M.ve(ctx, g.tham, tm, { rong: b.rong, cao: b.cao }, g.dai);
      Object.keys(du.thamSo).slice(0, 3).forEach(function (ma, k) {
        var ts = tim(du.khaiBao.thamSo, ma);
        goc.querySelector('[data-id="ts-' + k + '"]').innerHTML =
          K.danhDau(ts.ten) + ' = ' + K.dinhDang(g.tham[ma], soThapPhan(ts.buoc)) + ' ' + K.danhDau(ts.donVi || '');
      });
      du.do.slice(0, 3).forEach(function (ma, k) {
        var dl = tim(du.khaiBao.daiLuongDo, ma);
        goc.querySelector('[data-id="do-' + k + '"]').innerHTML =
          K.danhDau(dl.ten) + ' = ' + K.dinhDang(g.dai[ma], dl.chuSo) + ' ' + K.danhDau(dl.donVi || '');
      });
    }
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);
