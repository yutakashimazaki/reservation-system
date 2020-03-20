import os
import sys
import configparser
import subprocess
import random
import datetime
import cv2
from datetime import datetime, date, timedelta

from flask import Flask, render_template, request, redirect, url_for, session

from functions.mysql import checkBooking, executeBooking, exportBookedDates, cancelReservation
from functions.mail import sendConfirmReservingMail, sendCancelReservationMail

# config.ini の読み込み
if os.path.exists('./config.ini') :
    config = configparser.ConfigParser()
    try:
        config.read('./config.ini', 'UTF-8')
    except Exception as e :
        print(str(e))
else :
    print('config.ini が見つかりませんでした')
    print('処理を中断します')
    sys.exit(1)


app = Flask(__name__)

app.secret_key = config.get('WebServer', 'sessionKey')

# ルーティング
@app.route('/')
def index():
    return render_template('index.html')

# スペース詳細
@app.route('/details/space-a')
def space_a():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=int(config.get('WebServer', 'sessionTime'))) # セッションタイムアウトの時間指定

    exportBookedDates()
    return render_template('space-a.html')

# 予約
@app.route('/reserve/space-a', methods=['GET', 'POST'])
def reserve_a():
  if request.method == 'POST':

    # フォームからのデータを取得
    startDate = request.form.get('date')
    days = int(request.form.get('days'))

    # dateオブジェクトに変換
    datesToBeBooked = [startDate]
    startDate = datetime.strptime(startDate, '%Y年%m月%d日').date()
    datesToBeChecked = [startDate]

    # レンタル期間が複数日の場合
    if days != 1:
        nextDay = startDate
        for i in range(days - 1):
            nextDay = nextDay + timedelta(days=1)
            datesToBeChecked.append(nextDay) # dateオブジェクト

            nextDayStr = nextDay.strftime('%Y年%m月%d日')
            datesToBeBooked.append(nextDayStr) #Strオブジェクト

    # 予約のチェック
    result = checkBooking(datesToBeChecked)
    if result: # 予約日がダメな場合
        reservedDates = []
        for reservedDate in result:
            reservedDate = reservedDate.strftime('%Y年%m月%d日')
            reservedDates.append(reservedDate)

        message = reservedDates[0]

        if len(reservedDates) > 1:
            for i in range(1, len(reservedDates)):
                message += '、' + reservedDates[i]

        message += 'はご予約できません。'
        return render_template('result.html', message=message)

    # 予約日が空いている場合
    session['datesToBeBooked'] = datesToBeBooked
    # ログインチェック
    if 'usermail' in session: # ログイン済の場合
        return redirect(url_for('confirm_a'))
    else:
        return redirect(url_for('login'))

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
        bookingDates = []
        datesToBeBooked = session['datesToBeBooked']
        usermail = session['usermail']

        for date in datesToBeBooked:
            bookingDate = datetime.strptime(date, '%Y年%m月%d日').date()
            bookingDates.append(bookingDate)

        # 予約チェック
        if checkBooking(bookingDates):
            # 予約できないとき
            return render_template('result.html')

        # 予約の処理（DBに入れる） 戻り値：予約番号
        bookingId = executeBooking(bookingDates, usermail)
        # メールを送信
        message = 'この度はご予約いただきまして誠にありがとうございます。\n'
        message += 'ご予約が完了いたしましたのでご案内申し上げます。\n\n'
        message += '<ご予約内容>\n'
        message += '■予約番号\n' + bookingId
        message += '\n■スペース名\nspacea'
        message += '\n■レンタル日\n' + (session['datesToBeBooked'][0] if len(session['datesToBeBooked']) == 1 else session['datesToBeBooked'][0] + '~' + session['datesToBeBooked'][-1])
        message += '\n\n▼ご予約のキャンセルはこちら\nhttp://0.0.0.0/cancel/space-a\n\n'
        message += '※このメールは自動配信されています。\n'
        message += 'このメールに返信してのお問い合わせなどにはお応えできません。\n'

        sendConfirmReservingMail(session['usermail'], message)
        return render_template('result.html', bookingId=bookingId)

    # セッションタイムアウト等で「datesToBeBooked」の値が空のとき
    return redirect(url_for('space_a'))

# キャンセル画面
@app.route('/cancel/space-a', methods=['GET', 'POST'])
def cancel_a():
    if request.method == 'POST':
        bookingId = request.form.get('bookingId')
        usermail = cancelReservation(bookingId)
        # メールを送信
        message = '予約番号: ' + bookingId + ' のご予約をキャンセルしました。'
        sendCancelReservationMail(usermail, message)
        return render_template('cancel_result.html', bookingId=bookingId, usermail=usermail)
    else:
        return render_template('cancel.html')

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
