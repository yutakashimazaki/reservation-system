//=====================================
// メニュー
//=====================================
const accountMenu = document.getElementById('menu-account');
const customerMenu = document.getElementById('menu-customer');
const reserveMenu = document.getElementById('menu-reserve');
const accountSubMenu = document.getElementById('sub-menu-account');
const customerSubMenu = document.getElementById('sub-menu-customer');
const reserveSubMenu = document.getElementById('sub-menu-reserve');

accountMenu.addEventListener('click', () => {
  accountSubMenu.classList.toggle('no-active');
});
customerMenu.addEventListener('click', () => {
  customerSubMenu.classList.toggle('no-active');
});
reserveMenu.addEventListener('click', () => {
  reserveSubMenu.classList.toggle('no-active');
});

//=====================================
// 管理者アカウント
//=====================================
const adminAccount = document.getElementById('admin-account');
const adminMenu = document.getElementById('admin-menu');

adminAccount.addEventListener('click', () => {
  adminMenu.classList.toggle('no-active');
});
