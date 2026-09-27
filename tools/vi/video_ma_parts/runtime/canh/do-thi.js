(function (root) {
  'use strict';
  var V = root.THI_VIDEO;

  function soVN(v) { return String(Math.round(v * 1000) / 1000).replace('.', ','); }
  function tyLe(v, thap, cao, a, b) { return cao === thap ? (a + b) / 2 : a + (v - thap) * (b - a) / (cao - thap); }

  root.THI_CANH['do-thi'] = {
    muc: function (du) {
      var B = V.tao(du);
      var t = du.truong;
      var xs = du.diem.map(function (p) { return p[0]; });
      var ys = du.diem.map(function (p) { return p[1]; });
      var xMin = Math.min.apply(null, xs), xMax = Math.max.apply(null, xs);
      var yMin = Math.min.apply(null, ys), yMax = Math.max.apply(null, ys);
      // Gốc trục lùi 80 từ mép trái và mép đáy ô nội dung; trục ngang tới cách mép phải 80, trục đứng tới dưới đỉnh
      // 40. Điểm vẽ trong [X0, X1] × [Y1, Y0], lùi 50 (ngang) và 40 (đứng) khỏi hai trục. Tên trục ngang rộng 68 %
      // trục, canh phải về cuối trục; tên trục đứng rộng 70 % trục.
      var o = V.o('noi-dung');
      var gx = o.x + 80, gy = o.y + o.h - 80;
      var cuoiX = o.x + o.w - 80, dinhY = o.y + 40;
      var dai = cuoiX - gx;
      var X0 = gx + 50, X1 = cuoiX - 50, Y0 = gy - 40, Y1 = dinhY + 40;
      var kq = B.tieuDe(t['tieu-de'][0], 0.2);
      kq.push(B.net('truc-x', V.duongQua([[gx, gy], [cuoiX, gy]], 1), 0.3, 0.6, {}));
      kq.push(B.net('truc-y', V.duongQua([[gx, gy], [gx, dinhY]], 2), 0.4, 0.6, {}));
      // Khổ dọc trục ngắn: tên trục ngang trải từ mép trái ô tới cuối trục, tên trục đứng tới cách mép phải ô 20.
      var doc = V.doc();
      var rNgang = doc ? cuoiX - o.x : 0.68 * dai, rDoc = doc ? o.x + o.w - 20 - (gx + 20) : 0.7 * dai;
      kq.push(B.chu('truc-ngang', t['truc-ngang'][0], cuoiX - rNgang, gy + 42, rNgang, 40, 20, 1.0, { can: 'phai', mau: 'nhan' }));
      kq.push(B.chu('truc-doc', t['truc-doc'][0], gx + 20, o.y - 4, rDoc, 40, 24, 1.0, { mau: 'nhan' }));
      kq.push(B.chu('x-min', soVN(xMin), X0 - 60, gy + 6, 120, 30, 20, 1.0, { can: 'giua' }));
      kq.push(B.chu('x-max', soVN(xMax), X1 - 60, gy + 6, 120, 30, 20, 1.0, { can: 'giua' }));
      kq.push(B.chu('y-min', soVN(yMin), gx - 120, Y0 - 15, 110, 30, 20, 1.0, { can: 'phai' }));
      kq.push(B.chu('y-max', soVN(yMax), gx - 120, Y1 - 15, 110, 30, 20, 1.0, { can: 'phai' }));
      var truoc = null;
      du.diem.forEach(function (p, k) {
        var px = tyLe(p[0], xMin, xMax, X0, X1);
        var py = tyLe(p[1], yMin, yMax, Y0, Y1);
        if (truoc) { kq.push(B.net('doan-' + k, V.duongQua([truoc, [px, py]], 40 + k), du.moc[k], 0.4, { mau: 'nhan' })); }
        kq.push(B.net('diem-' + k, V.vongTron(px, py, 9), du.moc[k], 0.3, { mau: 'do' }));
        truoc = [px, py];
      });
      return kq;
    }
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);
