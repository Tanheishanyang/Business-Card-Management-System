const registerCard = document.querySelector(".register-card");
const registerBtn = document.querySelector("#register-btn");
const registerForm = document.querySelector("#register-form");
const backBtn = document.querySelector("#back-btn");

// 点击 Register 按钮
registerBtn.addEventListener("click", (e) => {
  e.preventDefault();
  
  // 扩展卡片并显示表单
  registerCard.classList.add("expanded");
  registerForm.classList.add("visible");

  // 隐藏原始内容
  registerBtn.style.display = "none";
  registerCard.querySelector(".card__description").style.display = "none";
  registerCard.querySelector(".card__bullets").style.display = "none";
});

// 点击 Back 按钮
backBtn.addEventListener("click", () => {
  // 恢复原始卡片大小和内容
  registerCard.classList.remove("expanded");
  registerForm.classList.remove("visible");

  // 显示原始内容
  registerBtn.style.display = "block";
  registerCard.querySelector(".card__description").style.display = "block";
  registerCard.querySelector(".card__bullets").style.display = "block";
});
