import os
import subprocess
import random
import datetime
import cv2
from datetime import datetime, date, timedelta

from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,dtjrdtulf,agr?RT'

# ルーティング
@app.route('/')
def index():
    return render_template('index.html')

# スペース詳細
@app.route('/details/space-a')
def space_a():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1)
    return render_template('space-a.html')

# 予約
@app.route('/reserve/space-a', methods=['GET', 'POST'])
def reserve_a():
  if request.method == 'POST':

    # フォームからのデータを取得
    startDate = request.form.get('date')
    days = request.form.get('days')

    # dateオブジェクトに変換
    datesToBeBooked = [startDate]
    startDate = datetime.strptime(startDate, '%Y年%m月%d日')
    startDate = startDate.date()
    # datesToBeBooked = [startDate]

    # レンタル期間が複数日の場合
    if days != 1:
        nextDay = startDate
        for i in range(int(days) - 1):
            nextDay = nextDay + timedelta(days=1)
            nextDayStr = nextDay.strftime('%Y年%m月%d日')
            datesToBeBooked.append(nextDayStr)

    # ここで予約のチェック引数:datesToBeBooked 戻り値:bool
    if 0 == 0:
        session['datesToBeBooked'] = datesToBeBooked
        # ログインチェック
        if 'usermail' in session: # ログイン済の場合
            return redirect(url_for('confirm_a'))
        else:
            return redirect(url_for('login'))

    # 予約日がダメな場合
    return render_template('result.html')

  else:
    # エラーなどでリダイレクトしたい場合
    return redirect(url_for('space_a'))

# 予約確認
@app.route('/confirm/space-a')
def confirm_a():
    if 'datesToBeBooked' in session:
        # 料金の計算
        charge = 25000
        chargeAll = charge * len(session['datesToBeBooked'])

        # 料金のフォーマット指定
        charge = '{:,}'.format(charge)
        chargeAll = '{:,}'.format(chargeAll)
        session['chargeAll'] = chargeAll
        return render_template('confirm.html', charge=charge)

    # セッションタイムアウト等で「datesToBeBooked」の値が空のとき
    return redirect(url_for('space_a'))

# 結果画面
@app.route('/result/space-a')
def result_a():
    if 'datesToBeBooked' in session:
        # 予約チェック
        if 0 == 0:
            # 予約の処理（DBに入れる） 戻り値：予約番号
            # メールを送信
            bookingId = 'BKLJBSLCj8934'
            return render_template('result.html', bookingId=bookingId)

        # 予約できないとき
        return render_template('result.html')
    # セッションタイムアウト等で「datesToBeBooked」の値が空のとき
    return redirect(url_for('space_a'))


# ログイン
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # ログイン処理
        session['usermail'] = request.form.get('usermail')

        if 'datesToBeBooked' in session:
            return redirect(url_for('confirm_a'))

        # 予約日がセッションになければスペース詳細ページへ遷移
        return redirect(url_for('space_a'))

    else:
      return render_template('login.html')

# 会員登録
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return render_template('register.html', validation=1)

    else:
      return render_template('register.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
