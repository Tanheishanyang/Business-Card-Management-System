// =========== [禁止页面触摸滚动的另一种写法 - 配合 touch-action 使用] ==========
// 若某些机型仍需在 JS 层面禁止默认滚动，可开启下行注释
// document.addEventListener("touchmove", function(e) {
//   e.preventDefault();
// }, { passive: false });

// =========== [卡片跟随鼠标 / 触摸点光效] ========== 
const cards = document.querySelectorAll('.card');
cards.forEach(card => {
  // ---------- 鼠标移动 ----------
  card.onmousemove = function(e) {
    const x = e.pageX - card.offsetLeft;
    const y = e.pageY - card.offsetTop;
    card.style.setProperty('--x', x + 'px');
    card.style.setProperty('--y', y + 'px');
  };

  // ---------- 触摸移动 ----------
  card.ontouchmove = function(e) {
    // 如果需要保留浏览器某些默认行为，可注释掉本行
    e.preventDefault();
    const touch = e.touches[0];
    const rect = card.getBoundingClientRect();
    const x = touch.clientX - rect.left;
    const y = touch.clientY - rect.top;
    card.style.setProperty('--x', x + 'px');
    card.style.setProperty('--y', y + 'px');
  };
});
