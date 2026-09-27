(function (root) {
  'use strict';
  var V = root.THI_VIDEO;
  root.THI_CANH['minh-hoa'] = {
    muc: function (du) {
      var B = V.tao(du);
      var t = du.truong;
      var kq = B.tieuDe(t['tieu-de'][0], 0.2);
      var n = du.hinhs.length;
      // Ô nội dung chia đều n cột; hình vuông lùi 40 từ đỉnh, cạnh = cao ô − 190 (chừa nhãn 80 và lề); nhãn dưới hình 10.
      var b = V.o('noi-dung');
      var o = b.w / n;
      var kich = b.h - 190;
      du.hinhs.forEach(function (h, k) {
        var giua = b.x + (k + 0.5) * o;
        var hk = B.hinh('hinh-' + k, h, giua - kich / 2, b.y + 40, kich, du.moc.length > k ? du.moc[k] : 1.0 + k);
        kq.push(hk);
        kq.push(B.chu('nhan-' + k, h.nhan, giua - (o - 40) / 2, b.y + 40 + kich + 10, o - 40, 80, 28, hk.batDau + hk.thoiLuong, { can: 'giua' }));
      });
      return kq;
    }
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);
