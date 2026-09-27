(function (root) {
  'use strict';

  // Khổ khung hình theo điểm CSS: một nguồn cho máy quay, bàn tay, chuyển cảnh và vùng kiểm tràn.
  // Trang gọi THI_KHO.dat(du.kho) (từ kho.py) trước khi dựng cảnh; chưa đặt (test Node, dữ liệu cũ) là khổ ngang.
  var NGANG = { ten: 'ngang', rong: 1280, cao: 720, day: 620, tamX: 640, tamY: 310 };
  var hien = NGANG;
  // Bảng ô bố cục {khổ: {tên ô: {x, y, w, h}}}: một nguồn là runtime/o-bo-cuc.json (kho.py đọc cùng file).
  // Trang nhúng nó vào window.THI_O_BO_CUC trước file này; trong Node thì đọc thẳng file.
  var BANG = root.THI_O_BO_CUC || (typeof module === 'object' && module.exports ? require('./o-bo-cuc.json') : {});

  function dat(kho) {
    hien = kho || NGANG;
    if (root.THI_VIDEO) { root.THI_VIDEO.kho = hien; }
    return hien;
  }
  function lay() { return hien; }
  // Ô bố cục `ten` của khổ hiện tại (bản sao). Mỗi khổ có bảng riêng, không mượn bảng khổ khác; khổ lạ hay tên lạ là lỗi.
  function o(ten) {
    var bang = BANG[hien.ten];
    if (!bang) { throw new Error('Khổ ' + hien.ten + ' không có bảng ô bố cục.'); }
    var b = bang[ten];
    if (!b) { throw new Error('Ô bố cục `' + ten + '` không có ở khổ ' + hien.ten + '.'); }
    return { x: b.x, y: b.y, w: b.w, h: b.h };
  }

  root.THI_KHO = { NGANG: NGANG, dat: dat, lay: lay, o: o };
})(typeof globalThis !== 'undefined' ? globalThis : this);
