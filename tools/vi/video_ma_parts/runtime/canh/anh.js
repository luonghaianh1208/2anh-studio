(function (root) {
  'use strict';
  var V = root.THI_VIDEO;
  root.THI_CANH.anh = {
    muc: function (du) {
      var B = V.tao(du);
      var t = du.truong;
      var chuThich = t['chu-thich'][0];
      var n = V.demKyTu(chuThich);
      // Ảnh trong ô `anh-lon`; chú thích trong ô `chu-thich` ngay dưới (khổ ngang: cách 15, cùng bề rộng).
      var o = V.o('anh-lon'), c = V.o('chu-thich');
      return [
        B.anh('anh', du.anh, o.x, o.y, o.w, o.h, 0.2),
        B.chu('chu-thich', chuThich, c.x, c.y, c.w, c.h, n <= 60 ? 30 : (n <= 75 ? 26 : 24), du.moc.length ? du.moc[0] : 1.0, { can: 'giua' })
      ];
    }
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);
