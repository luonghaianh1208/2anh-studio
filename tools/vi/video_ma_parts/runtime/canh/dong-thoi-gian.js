(function (root) {
  'use strict';
  var V = root.THI_VIDEO;
  // Trục ngang ở giữa ô `dong-thoi-gian` (y = AY), từ AX0 tới AX1 (mũi tên), lùi 36 hai bên. Đến 4 mốc: nhãn trên
  // trục, mô tả dưới trục, mỗi mốc một ô rộng bằng khoảng giữa hai mốc. Từ 5 mốc: mốc chẵn cả nhãn và mô tả ở trên
  // (mô tả từ đỉnh ô), mốc lẻ ở dưới (xen kẽ cao thấp), nên mỗi ô rộng gần gấp đôi mà không chạm ô cùng phía.
  // Ô chữ không vượt hai mép ô.

  function tach(v) {
    var i = v.indexOf('|');
    return [v.slice(0, i).trim(), v.slice(i + 1).trim()];
  }

  root.THI_CANH['dong-thoi-gian'] = {
    muc: function (du) {
      var B = V.tao(du);
      var t = du.truong;
      var b = V.o('dong-thoi-gian');
      var AX0 = b.x + 36, AX1 = b.x + b.w - 36, AY = b.y + b.h / 2;
      var kq = B.tieuDe(t['tieu-de'][0], 0.2);
      kq.push(B.net('truc', V.muiTen(AX0, AY, AX1, AY, 9), 0.3, 0.6, { quay: false }));
      var n = t.moc.length;
      var o = (AX1 - 40 - AX0) / n;
      // Khổ dọc luôn so le (ô hẹp); nhãn cao hai dòng (70) và mô tả dài tới đỉnh ô (trên) hoặc đáy ô (dưới).
      var doc = V.doc();
      var xen = doc || n > 4;
      var w = xen ? 2 * o - 24 : o - 20;
      var hNhan = doc ? 70 : 38;
      t.moc.forEach(function (v, k) {
        var hai = tach(v);
        var x = AX0 + (k + 0.5) * o;
        var trai = Math.max(b.x, x - w / 2), phai = Math.min(b.x + b.w, x + w / 2);
        var duoi = xen && k % 2 === 1;
        kq.push(B.net('cham-' + k, V.vongTron(Math.round(x * 10) / 10, AY, 10), du.moc[k], 0.3, { mau: 'do', am: 'ting' }));
        var yNhan = duoi ? AY + 26 : AY - 26 - hNhan;
        // Nhãn phía trên trục (khổ dọc) dồn xuống sát trục.
        var tuyNhan = { can: 'giua', mau: 'nhan' };
        if (doc && !duoi) { tuyNhan.day = true; }
        var nhan = B.chu('nhan-' + k, hai[0], trai, yNhan, phai - trai, hNhan, 26, du.moc[k] + 0.25, tuyNhan);
        kq.push(nhan);
        var yDuoi = duoi ? AY + 30 + hNhan : AY + 26;
        var moTa = xen && !duoi
          ? [b.y, doc ? yNhan - 6 - b.y : 132, { can: 'giua', day: true }]
          : [yDuoi, doc ? b.y + b.h - yDuoi : (xen ? 132 : 150), { can: 'giua' }];
        kq.push(B.chu('mo-ta-' + k, hai[1], trai, moTa[0], phai - trai, moTa[1], xen ? 20 : 22,
          nhan.batDau + nhan.thoiLuong, moTa[2]));
      });
      return kq;
    }
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);
