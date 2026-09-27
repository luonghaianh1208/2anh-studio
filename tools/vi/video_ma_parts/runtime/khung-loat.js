(function (root) {
  'use strict';

  // Khung loạt (khoá đầu `loat`): tên loạt ở góc trái trên, "0k/N" ở góc phải trên. Lớp #khung-loat nằm ngoài lớp
  // bảng (như #nhac-nguon) nên đứng yên khi máy quay chạy và khi chuyển cảnh; hiện từ khung đầu của cảnh.
  // Kiểu chữ và màu theo chủ đề ở viet-tay.css / cat-dan.css.

  // Số cảnh và tổng, cùng số chữ số (ít nhất hai): 3/8 -> "03/08", 3/12 -> "03/12".
  function chuoiSo(so, tong) {
    var n = Math.max(2, String(tong).length);
    function dem(x) { var s = String(x); while (s.length < n) { s = '0' + s; } return s; }
    return dem(so) + '/' + dem(tong);
  }

  // Trang: thêm lớp vào khung (sau lớp bảng); du.loat = {ten, so, tong} từ lich.gan_loat.
  function dung(khung, du) {
    var el = document.createElement('div');
    el.id = 'khung-loat';
    var ten = document.createElement('span');
    ten.className = 'ten';
    ten.textContent = du.loat.ten;
    var so = document.createElement('span');
    so.className = 'so';
    so.textContent = chuoiSo(du.loat.so, du.loat.tong);
    el.appendChild(ten);
    el.appendChild(so);
    khung.appendChild(el);
    return el;
  }

  root.THI_KHUNG_LOAT = { chuoiSo: chuoiSo, dung: dung };
})(typeof globalThis !== 'undefined' ? globalThis : this);
