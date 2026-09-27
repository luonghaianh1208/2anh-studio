(function (root) {
  'use strict';
  var V = root.THI_VIDEO;
  root.THI_CANH['so-sanh'] = {
    muc: function (du) {
      var B = V.tao(du);
      var t = du.truong;
      var nt = t['y-trai'].length;
      var kq = B.tieuDe(t['tieu-de'][0], 0.2);
      // Hai ô cột; vạch chia ở giữa khe hai cột, cao bằng cột trái. Tên cột ở đỉnh ô (cao 70), ý lùi 20 và bắt đầu
      // dưới 95, mỗi ý cao 84. Khổ dọc hai ô xếp chồng: vạch chia nằm ngang giữa khe, tên cột cao 50, ý bắt đầu dưới
      // 60 và chia đều phần ô còn lại cho 4 ý, chữ ý nhỏ hơn một cỡ (26).
      var a = V.o('hai-cot-trai'), b = V.o('hai-cot-phai');
      var chong = b.y >= a.y + a.h;
      var cao = chong ? 50 : 70, dau = chong ? 60 : 95, buoc = chong ? (a.h - 60) / 4 : 84, co = chong ? 26 : 28;
      if (chong) {
        var yGiua = (a.y + a.h + b.y) / 2;
        kq.push(B.net('giua', V.duongQua([[a.x, yGiua], [a.x + a.w, yGiua]], 9), 0.3, 0.6, {}));
      } else {
        var xGiua = (a.x + a.w + b.x) / 2;
        kq.push(B.net('giua', V.duongQua([[xGiua, a.y], [xGiua, a.y + a.h]], 9), 0.3, 0.6, {}));
      }
      kq.push(B.chu('trai', t.trai[0], a.x, a.y, a.w, cao, 34, 0.3, { mau: 'nhan' }));
      kq.push(B.chu('phai', t.phai[0], b.x, b.y, b.w, cao, 34, Math.max(0.3, du.moc[nt] - 0.9), { mau: 'nhan' }));
      t['y-trai'].forEach(function (y, k) { kq.push(B.chu('y-trai-' + k, y, a.x + 20, a.y + dau + k * buoc, a.w - 20, buoc, co, du.moc[k], { am: 'ting' })); });
      t['y-phai'].forEach(function (y, k) { kq.push(B.chu('y-phai-' + k, y, b.x + 20, b.y + dau + k * buoc, b.w - 20, buoc, co, du.moc[nt + k], { am: 'ting' })); });
      return kq;
    }
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);
