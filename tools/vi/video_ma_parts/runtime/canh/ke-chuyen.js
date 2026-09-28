(function (root) {
  'use strict';
  var V = root.THI_VIDEO;
  // Cảnh kể chuyện (spec Q6): nền phủ kín khung (du.nen, lớp nền dưới cùng của lớp bảng, khung-video), nhân vật đứng ở
  // ô `nhan-vat-<vi-tri>` bật vào ở 0,2 s, tiêu đề lớn ở giữa trên (ô `tieu-de`) vào ở 0,4 s; thẻ và dòng tài liệu như
  // mọi cảnh (B.them). Lời chỉ ở phụ đề. Máy quay tắt (lich.py): nền tự phóng chậm.
  //   viet-tay: chữ hoa vàng viền đen (CSS .ke-tieu-de) đọc được trên mọi nền.
  //   cat-dan: nhãn chữ hoa trên dải băng dính màu của cảnh.
  var CO = 44;          // cỡ tiêu đề viet-tay (chữ hoa Itim): 36 ký tự vừa một dòng khổ ngang
  var CO_NHAN = 40;     // cỡ nhãn băng dính cat-dan
  var CO_NHAN_HEP = 32; // nhãn cat-dan khi ô tiêu đề hẹp lại vì thẻ (khổ ngang): hai dòng vẫn vừa ô
  var LOAT = 40;        // khung loạt chiếm dải 40 px trên cùng
  var KHOANG_THE = 20;
  var LE_TAI_LIEU = 6;  // nhân vật dừng trên ô tài liệu 6 px

  function giao(a, b) { return a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h; }

  root.THI_CANH['ke-chuyen'] = {
    muc: function (du) {
      var B = V.tao(du);
      var catDan = (du.chuDe || {}).ten === 'cat-dan';
      var kq = [];
      if (du.nhanVat) {
        var o = V.o('nhan-vat-' + (du.viTri || (du.so % 2 ? 'trai' : 'phai')));
        var tl = V.o('tai-lieu');
        if (B.coTaiLieu && giao(o, tl)) { o.h = tl.y - LE_TAI_LIEU - o.y; }
        kq.push(B.nhanVat(o));
      }
      var td = V.o('tieu-de');
      if (du.loat) { td.y = Math.max(td.y, LOAT); }
      var hep = B.coThe && !V.doc();
      if (hep) { td.w = Math.min(td.w, V.o('the').x - KHOANG_THE - td.x); }
      var chu = du.truong['tieu-de'][0];
      kq.push(catDan
        ? B.chu('tieu-de', chu, td.x, td.y, td.w, td.h, hep ? CO_NHAN_HEP : CO_NHAN, 0.4, { mau: 'bang', bang: true, can: 'giua' })
        : B.chu('tieu-de', chu, td.x, td.y, td.w, td.h, CO, 0.4, { mau: 'ke-tieu-de', can: 'giua', nay: !!(du.co && du.co.chuDong) }));
      return B.them(kq);
    }
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);
