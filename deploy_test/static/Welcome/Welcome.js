console.clear();

const cardsContainer = document.querySelector(".cards");
const cardsContainerInner = document.querySelector(".cards__inner");
const cards = Array.from(document.querySelectorAll(".card"));
const overlay = document.querySelector(".overlay");
const glowButtons = Array.from(document.querySelectorAll(".glow-btn"));

const applyOverlayMask = (e) => {
  const overlayEl = e.currentTarget;
  const x = e.pageX - cardsContainer.offsetLeft;
  const y = e.pageY - cardsContainer.offsetTop;

  overlayEl.style = `--opacity: 1; --x: ${x}px; --y:${y}px;`;
};

const initOverlayCard = (cardEl) => {
  const overlayCard = document.createElement("div");
  overlayCard.classList.add("card");
  overlay.append(overlayCard);
  observer.observe(cardEl);
  createOverlayCta(overlayCard, cardEl.lastElementChild);
};

const createOverlayCta = (overlayCard, ctaEl) => {
  const overlayCta = document.createElement("div");
  overlayCta.classList.add("cta");
  overlayCta.textContent = ctaEl.textContent;
  overlayCta.setAttribute("aria-hidden", true);
  overlayCard.append(overlayCta);
};

const observer = new ResizeObserver((entries) => {
  entries.forEach((entry) => {
    const cardIndex = cards.indexOf(entry.target);
    let width = entry.borderBoxSize[0].inlineSize;
    let height = entry.borderBoxSize[0].blockSize;

    if (cardIndex >= 0) {
      overlay.children[cardIndex].style.width = `${width}px`;
      overlay.children[cardIndex].style.height = `${height}px`;
    }
  });
});

// 为按钮单独定义光效逻辑
const applyButtonOverlayMask = (e) => {
  const button = e.currentTarget;
  const rect = button.getBoundingClientRect(); // 获取按钮的边界信息
  const x = e.clientX - rect.left; // 鼠标相对按钮左上角的 X 坐标
  const y = e.clientY - rect.top;  // 鼠标相对按钮左上角的 Y 坐标

  overlay.style = `
    --opacity: 1;
    --x: ${x}px;
    --y: ${y}px;
    width: ${rect.width}px; /* 根据按钮宽度调整光效宽度 */
    height: ${rect.height}px; /* 根据按钮高度调整光效高度 */
    position: absolute; /* 设置光效为绝对定位 */
    left: ${rect.left + window.scrollX}px; /* 光效跟随按钮移动 */
    top: ${rect.top + window.scrollY}px;
  `;
};

// 添加事件监听到按钮
glowButtons.forEach((button) => {
  button.addEventListener("pointermove", applyButtonOverlayMask);
  button.addEventListener("pointerleave", () => {
    overlay.style = "--opacity: 0"; // 鼠标离开时隐藏光效
  });
});

cards.forEach(initOverlayCard);
document.body.addEventListener("pointermove", applyOverlayMask);
