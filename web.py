import os
import sys
import configparser
import json
import subprocess
import random
import datetime
from datetime import datetime, date, timedelta

from flask import Flask, render_template, request, redirect, url_for, session, abort, Markup

from dto.spaceInfo import SpaceInfo
from dto.spaceDetails import SpaceDetails
from functions.rentalspace import getAllSpaceInfo, getSpaceDetails, getSpaceDescription, getSpaceEquipments, getSpaceBudgetPlan, getSpaceReview
from functions.reservation import checkBooking, executeBooking, exportBookedDates, cancelReservation
from functions.mail import sendMail
from functions.authentication import loginUser, registerUser, tempRegisterUser, generateValidateCode

# ======================================================
# config.ini の読み込み
# ======================================================
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

# ======================================================
# 関数（仮）
# ======================================================
def checkSpaceName(rentalSpace):
    spaceList = json.loads(config.get("RentalSpace","spaceList"))
    if rentalSpace not in spaceList:
        abort(404)

def getSpaceName(rentalSpace):
    spaceName = 'SPACE A'
    if session['rentalSpace'] == 'space_b':
        spaceName = 'SPACE B'
    elif session['rentalSpace'] == 'space_c':
        spaceName = 'SPACE C'
    elif session['rentalSpace'] == 'space_d':
        spaceName = 'SPACE D'

    return spaceName

def generateFailedMsg(result):
    reservedDates = []
    for reservedDate in result:
        reservedDate = reservedDate.strftime('%Y年%m月%d日')
        reservedDates.append(reservedDate)

    message = reservedDates[0]

    if len(reservedDates) > 1:
        for i in range(1, len(reservedDates)):
            message += '、' + reservedDates[i]

    message += 'はご予約できません。'

    return message

# ======================================================
# ルーティング処理
# ======================================================
app = Flask(__name__)

app.secret_key = config.get('WebServer', 'sessionKey')

# HOME
@app.route('/')
def index():
    allSpaceInfo = getAllSpaceInfo()
    if not allSpaceInfo:
        abort(500)
    return render_template('index.html', allSpaceInfo=allSpaceInfo)

# スペース詳細
@app.route('/<rentalSpace>/details')
def details(rentalSpace):
    checkSpaceName(rentalSpace)
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=int(config.get('WebServer', 'sessionTime'))) # セッションタイムアウトの時間指定

    exportBookedDates(rentalSpace)
    # スペースの情報を取得
    spaceDetails = getSpaceDetails(rentalSpace)
    if not spaceDetails:
        abort(500)
    session['rentalSpace'] = rentalSpace
    spaceName = getSpaceName(rentalSpace)
    return render_template('space.html', spaceName=spaceName, description=spaceDetails.description, rentalSpace=rentalSpace, includingPage='details.html', spaceDetails=spaceDetails)

# 備品情報
@app.route('/<rentalSpace>/equipments')
def equipments(rentalSpace):
    checkSpaceName(rentalSpace)
    description = getSpaceDescription(rentalSpace)
    if not description:
        abort(500)
    # スペースの備品情報を取得
    spaceEquipments = getSpaceEquipments(rentalSpace)
    if not spaceEquipments:
        abort(500)
    session['rentalSpace'] = rentalSpace
    spaceName = getSpaceName(rentalSpace)
    return render_template('space.html', spaceName=spaceName, description=description, rentalSpace=rentalSpace, includingPage='equipments.html', spaceEquipments=spaceEquipments)

# 料金プラン
@app.route('/<rentalSpace>/budget-plan')
def budgetPlan(rentalSpace):
    checkSpaceName(rentalSpace)
    description = getSpaceDescription(rentalSpace)
    if not description:
        abort(500)
    # スペースの料金プランを取得
    spaceBudgetPlan = getSpaceBudgetPlan(rentalSpace)
    if not spaceBudgetPlan:
        abort(500)
    session['rentalSpace'] = rentalSpace
    spaceName = getSpaceName(rentalSpace)
    return render_template('space.html', spaceName=spaceName, description=description, rentalSpace=rentalSpace, includingPage='budgetPlan.html', spaceBudgetPlan=spaceBudgetPlan)

# レビュー
@app.route('/<rentalSpace>/review')
def review(rentalSpace):
    checkSpaceName(rentalSpace)
    description = getSpaceDescription(rentalSpace)
    if not description:
        abort(500)
    # スペースのレビューを取得
    spaceReview = getSpaceReview(rentalSpace)
    if not spaceReview:
        abort(500)
    session['rentalSpace'] = rentalSpace
    spaceName = getSpaceName(rentalSpace)
    return render_template('space.html', spaceName=spaceName, description=description, rentalSpace=rentalSpace, includingPage='review.html', spaceReview=spaceReview)

# 予約内容のチェック
@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    if 'rentalSpace' not in session:
        return redirect(url_for('index'))
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

        # 予約日がダメな場合
        result = checkBooking(session['rentalSpace'], datesToBeChecked)
        if result:
            message = generateFailedMsg(result)
            spaceName = getSpaceName(session['rentalSpace'])
            return render_template('result.html', message=message, spaceName=spaceName)

        # 予約日が空いている場合
        session['datesToBeBooked'] = datesToBeBooked
        if 'usermail' in session: # ログイン済の場合
            return redirect(url_for('confirm'))
        else:
            return redirect(url_for('login'))

    else:
        # エラーなどでリダイレクトしたい場合
        return redirect(url_for('details', rentalSpace=session['rentalSpace']))

# 予約内容確認画面
@app.route('/confirm')
def confirm():
    if 'rentalSpace' not in session:
        return redirect(url_for('index'))
    if 'usermail' not in session:
        return redirect(url_for('login'))

    if 'datesToBeBooked' in session:
        # スペース名の取得
        spaceName = getSpaceName(session['rentalSpace'])

        # 料金の計算
        charge = 25000
        chargeAll = charge * len(session['datesToBeBooked'])

        # 料金のフォーマット指定
        charge = '{:,}'.format(charge)
        chargeAll = '{:,}'.format(chargeAll)
        session['chargeAll'] = chargeAll
        return render_template('confirm.html', spaceName=spaceName, charge=charge)

    # セッションタイムアウト等で「datesToBeBooked」の値が空のとき
    return redirect(url_for('details', rentalSpace=session['rentalSpace']))

# 予約処理
@app.route('/result')
def result():
    if 'rentalSpace' not in session:
        return redirect(url_for('index'))
    if 'usermail' not in session:
        return redirect(url_for('login'))

    if 'datesToBeBooked' in session:
        bookingDates = []
        rentalSpace = session['rentalSpace']
        datesToBeBooked = session['datesToBeBooked']
        usermail = session['usermail']
        spaceName = getSpaceName(rentalSpace)

        for date in datesToBeBooked:
            bookingDate = datetime.strptime(date, '%Y年%m月%d日').date()
            bookingDates.append(bookingDate)

        # 予約日がダメな場合
        result = checkBooking(rentalSpace, bookingDates)
        if result:
            message = generateFailedMsg(result)
            return render_template('result.html', message=message, spaceName=spaceName)

        # 予約の処理
        bookingId = executeBooking(rentalSpace, bookingDates, usermail)
        # メールを送信
        subject = 'ご予約の確認'
        message = 'この度はご予約いただきまして誠にありがとうございます。\n'
        message += 'ご予約が完了いたしましたのでご案内申し上げます。\n\n'
        message += '<ご予約内容>\n'
        message += '■予約番号\n' + bookingId
        message += '\n■スペース名\n' + spaceName
        message += '\n■レンタル日\n' + (session['datesToBeBooked'][0] if len(session['datesToBeBooked']) == 1 else session['datesToBeBooked'][0] + '~' + session['datesToBeBooked'][-1])
        message += '\n\n▼ご予約のキャンセルはこちら\nhttp://0.0.0.0/cancel/' + rentalSpace + '\n\n'
        message += '※このメールは自動配信されています。\n'
        message += 'このメールに返信してのお問い合わせなどにはお応えできません。\n'

        sendMail(session['usermail'], subject, message)
        return render_template('result.html', bookingId=bookingId, spaceName=spaceName)

    # セッションタイムアウト等で「datesToBeBooked」の値が空のとき
    return redirect(url_for('details', rentalSpace=rentalSpace))

# キャンセル画面
@app.route('/cancel/<rentalSpace>', methods=['GET', 'POST'])
def cancel(rentalSpace):
    checkSpaceName(rentalSpace)
    if 'usermail' not in session:
        session['spaceToBeCanceled'] = rentalSpace
        return redirect(url_for('login'))

    if request.method == 'POST':
        bookingId = request.form.get('bookingId')
        usermail = session['usermail']
        result = cancelReservation(rentalSpace, usermail, bookingId)
        if result == 0:
            return render_template('cancel_result.html', bookingId=bookingId, rentalSpace=rentalSpace)
        # メールを送信
        subject = 'ご予約キャンセルの確認'
        message = '予約番号: ' + bookingId + ' のご予約をキャンセルしました。'
        sendMail(usermail, subject, message)
        session.pop('spaceToBeCanceled', None)
        return render_template('cancel_result.html', bookingId=bookingId, usermail=usermail, rentalSpace=rentalSpace)
    else:
        return render_template('cancel.html', rentalSpace=rentalSpace)

# ログイン
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        mail = request.form.get('usermail')
        password = request.form.get('userpass')
        result = loginUser(mail, password)

        # ログイン失敗
        if result == 0:
            return render_template('login.html', errMsg='このメールアドレスは登録されていません')
        elif result == -1:
            return render_template('login.html', errMsg='パスワードが間違っています')
        elif result == -2:
            return render_template('login.html', errMsg='アカウントのメール認証がされていません')

        session['usermail'] = mail

        if 'accountRequest' in session:
            return redirect(url_for('account'))
        elif 'spaceToBeCanceled' in session:
            return redirect(url_for('cancel', rentalSpace=session['spaceToBeCanceled']))
        elif 'datesToBeBooked' in session:
            return redirect(url_for('confirm'))
        elif 'rentalSpace' in session:
            return redirect(url_for('details', rentalSpace=session['rentalSpace']))

        return redirect(url_for('index'))

    else:
      return render_template('login.html')

# ログアウト
@app.route('/logout')
def logout():
    session.pop('usermail', None)
    return redirect(url_for('index'))

# 会員登録
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        mail = request.form.get('usermail')
        password = request.form.get('userpass')
        firstName = request.form.get('firstName').encode('utf-8')
        lastName = request.form.get('lastName').encode('utf-8')
        phone = request.form.get('phone')
        company = request.form.get('company').encode('utf-8')
        tempPass = generateValidateCode()

        # エラーの場合
        if tempRegisterUser(mail, password, phone, firstName, lastName, company, tempPass) == 0:
            return render_template('register.html', errMsg='このメールアドレスは既に登録されています')

        # メールを送信
        subject = '会員登録'
        message = 'まだ登録は完了していません。\n\n'
        message += '認証コードは ' + tempPass + ' です。\n\n'
        message += '下記URLから認証ページに移動できます。\nhttp://0.0.0.0/verify'
        sendMail(mail, subject, message)
        return redirect(url_for('verify'))

    else:
      return render_template('register.html')

# 会員登録
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        mail = request.form.get('usermail')
        code = request.form.get('code')
        result = registerUser(mail, code)

        # エラーの場合
        if result == 0:
            return render_template('verify.html', errMsg='メールアドレスが間違っています')
        elif result == -1:
            return render_template('verify.html', errMsg='認証コードが違います')

        # メールを送信
        subject = '会員登録完了'
        message = '登録が完了しました。\n'
        sendMail(mail, subject, message)
        return redirect(url_for('login'))
    else:
      return render_template('verify.html')

# マイページ
@app.route('/account')
def account():
    if not ('usermail' in session):
        session['accountRequest'] = True
        return redirect(url_for('login'))

    session.pop('accountRequest', None)
    return render_template('account.html')

# ======================================================
# エラー表示
# ======================================================
# 404ページ
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page-not-found.html'), 404

# 500ページ
@app.errorhandler(500)
def internal_server_error(error):
    return render_template('internal_server_error.html'), 500

# ======================================================
# フィルター
# ======================================================
# 改行コード
@app.template_filter('linebreaker')
def linebreaker(line):
    return Markup(line.replace('\n', '<br>'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
