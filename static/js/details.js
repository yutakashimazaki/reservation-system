//=====================================
// スライダー
//=====================================

$(document).ready(function(){
    $('.img-slider').bxSlider({
        auto: true,
        pause: 5000,
    });
});

//=====================================
// カレンダー
//=====================================
const calendar = document.getElementById('js-calendar');
const prevBtn = document.getElementById('prev');
const nextBtn = document.getElementById('next');

const weeks = ['日', '月', '火', '水', '木', '金', '土'];
const date = new Date();
let year = date.getFullYear();
let month = date.getMonth() + 1;
const thisYear = date.getFullYear();
const thisMonth = date.getMonth() + 1;
const thisDate = date.getDate();

// １ヶ月分のカレンダーを作成して表示する関数
function createCalendar(year, month) {
    const startDate = new Date(year, month - 1, 1); // 月の最初の日を取得
    const endDate = new Date(year, month, 0); // 月の最後の日を取得
    const endDayCount = endDate.getDate(); // 月の末日
    const lastMonthEndDate = new Date(year, month - 1, 0); // 前月の最後の日の情報
    const lastMonthendDayCount = lastMonthEndDate.getDate(); // 前月の末日
    const startDay = startDate.getDay(); // 月の最初の日の曜日を取得
    let dayCount = 1; // 日にちのカウント
    let calendarHtml = ''; // HTMLを組み立てる変数
    const bookedDates = getBookedDates(year, month); //予約されている日

    calendarHtml += '<h1>' + year  + '年' + month + '月</h1>';
    calendarHtml += '<table>';

    // 曜日の行を作成
    for (let i = 0; i < weeks.length; i++) {
        calendarHtml += '<td><div>' + weeks[i] + '</div></td>';
    }

    for (let w = 0; w < 5; w++) {
        calendarHtml += '<tr>';

        for (let d = 0; d < 7; d++) {
          if (w == 0 && d < startDay) {
              // 1行目で1日の曜日の前
              calendarHtml += '<td><div></div></td>';
          } else if (dayCount > endDayCount) {
              // 末尾の日数を超えた
              calendarHtml += '<td><div></div></td>';
          } else if (month == thisMonth && thisDate > dayCount) {
              //本日以前の日にち
              calendarHtml += '<td class="day past"><div>' + dayCount + '</div></td>';
              dayCount++;
          } else if (bookedDates.includes(dayCount)) {
              calendarHtml += `<td class="day disable"><div>` + dayCount + '</div></td>';
              dayCount++;
          } else {
              calendarHtml += `<td class="day usable"><div class="cal-day" data-date="${year}年${month}月${dayCount}日">` + dayCount + '</div></td>';
              dayCount++;
          }
        }
        calendarHtml += '</tr>';
    }
    calendarHtml += '</table>';

    calendar.innerHTML = calendarHtml;
}

// 「<」「>」が押されたときに前後の月のカレンダーを表示する関数
function moveCalendar(e) {
    calendar.innerHTML = '';

    if (e.target.id === 'prev') {
        month--;

        if (month < 1) {
            year--;
            month = 12;
        }
        if (month == thisMonth) {
          prevBtn.classList.add('no-active');
        }
        if (month == thisMonth + 1) {
          nextBtn.classList.remove('no-active');
        }
    }

    if (e.target.id === 'next') {
        month++;

        if (month > 12) {
            year++;
            month = 1;
        }
        if (month == thisMonth + 1) {
          prevBtn.classList.remove('no-active');
        }
        if (month == thisMonth + 2) {
          nextBtn.classList.add('no-active');
        }
    }

    createCalendar(year, month);
}

// CSVファイルから予約済の日を取得する関数
function getBookedDates(year, month){
    const bookedDates = [];
    const bookedDays = [];
    let pageUrl = location.href.split('/');
    let spaceName = pageUrl[pageUrl.length - 2];
    let req = new XMLHttpRequest(); // HTTPでファイルを読み込むためのXMLHttpRrequestオブジェクトを生成
    req.open("get", 'http://0.0.0.0/static/csv/bookedDates_' + spaceName + '.csv', false); // アクセスするファイルを指定(同期処理)
    req.send(null); // HTTPリクエストの発行

    // トランザクション完了後，ステータスコードが200の場合
    if(req.status === 200) {
       let tmp = req.responseText.split('\n'); // 改行を区切り文字として行を要素とした配列を生成

       // 各行ごとにカンマで区切った文字列を要素とした3次元配列を生成
       for(let i = 0; i < tmp.length ; i++){
           // year, month, day
           bookedDates[i] = tmp[i].split(',');
       }
       for (let i = 0; i < bookedDates.length - 1; i++) {
           if (Number(bookedDates[i][0]) === year && Number(bookedDates[i][1]) === month ) {
               bookedDays.push(Number(bookedDates[i][2]));
           }
       }
    }
    return bookedDays;
}

createCalendar(year, month); //最初にカレンダーを表示

prevBtn.addEventListener('click', moveCalendar);
nextBtn.addEventListener('click', moveCalendar);

//日付をクリックするとフォームに自動入力
document.addEventListener('click', (e) => {
    if(e.target.classList.contains("cal-day")) {
        selectedDate.value = e.target.dataset.date;
        calFrame.classList.remove('cal-frame');
    }
});

//=====================================
// 予約フォーム
//=====================================
const selectedDate = document.getElementById('js-date');
const calFrame = document.getElementById('js-cal-frame');

const today = thisYear +　'年' + thisMonth + '月' + thisDate + '日';
selectedDate.value = today;

selectedDate.addEventListener('click', () => {
  calFrame.classList.add('cal-frame');
});



// ページ内遷移
// $(function(){
//    // #で始まるアンカーをクリックした場合に処理
//    $('a[href^=#]').click(function() {
//       // スクロールの速度
//       var speed = 1000; // ミリ秒
//       // アンカーの値取得
//       var href= $(this).attr("href");
//       // 移動先を取得
//       var target = $(href == "#" || href == "" ? 'html' : href);
//       // 移動先を数値で取得
//       var position = target.offset().buttom;
//       // スムーススクロール
//       $('body,html').animate({scrollTop:position}, speed, 'swing');
//       return false;
//    });
// });
