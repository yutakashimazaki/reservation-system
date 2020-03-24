//=====================================
// パスワード強度チェック
//=====================================
const passMsg = document.getElementById("pass-msg");
let passwordLevel = 0;

function setPassMessage(password) {
  passwordLevel = getPasswordLevel(password);
  let message = "パスワードの強度: ";
  if (passwordLevel == 1) {message += "弱い";}
  if (passwordLevel == 2) {message += "やや弱い";}
  if (passwordLevel == 3) {message += "普通";}
  if (passwordLevel == 4) {message += "やや強い";}
  if (passwordLevel == 5) {message += "強い";}
  passMsg.textContent = message;
}
//=====================================
// パスワード一致チェック
//=====================================
const confMsg = document.getElementById("comf-msg");
let passMatch = false;
function setConfMessage(confirmPassword) {
 let password = document.getElementById("passwd").value;
 if (password == confirmPassword) {
   confMsg.textContent = "";
   passMatch = true;
 } else {
   confMsg.textContent =  "パスワードが一致しません";
   passMatch = false;
 }
}

//=====================================
// パスワード一致チェック
//=====================================
const vaidateMsg = document.getElementById("validate-msg");
document.getElementById("register-btn").addEventListener('click', (e) => {
    let message = "";
    if(passwordLevel < 3) {
        e.preventDefault();
        message = "パスワードの強度を「普通」以上にしてください";
    } else if(!passMatch) {
        e.preventDefault();
        message = "パスワードを一致させてください";
    }
    vaidateMsg.textContent = message;
});
