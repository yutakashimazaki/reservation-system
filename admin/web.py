import os
import sys
import configparser
import json
from flask import Blueprint, render_template, redirect, url_for, request, session

from admin.dto.reserveInfo import ReserveInfo
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
    if rentalSpace == 'space_b':
        spaceName = 'SPACE B'
    elif rentalSpace == 'space_c':
        spaceName = 'SPACE C'
    elif rentalSpace == 'space_d':
        spaceName = 'SPACE D'

    return spaceName

# ======================================================
# ルーティング処理
# ======================================================
admin = Blueprint('admin', __name__, template_folder='templates', static_folder='./static', static_url_path='/static_a')

# admin.secret_key = config.get('WebServer', 'sessionKey')

# 管理者TOP
@admin.route('/')
def index():
    if 'adminName' not in session:
        return redirect(url_for('admin.login'))

    return render_template('admin/index.html', navigation='Dashboard')

# 各スペースの予約一覧
@admin.route('/reservations/<rentalSpace>')
def reservations(rentalSpace):
    if 'adminName' not in session:
        return redirect(url_for('admin.login'))

    checkSpaceName(rentalSpace)
    spaceName = getSpaceName(rentalSpace)
    # 予約と予約者の情報を取り出して返す
    reserveInfo1 = ReserveInfo('レンタル太郎', 'sample@sample.com', '080-0000-0000', 'レンタル（株）', 'BVIFYlkhvo', '2020/4/22', '10:00', '22:00')
    reserveInfo2 = ReserveInfo('伊達　吾郎', 'abcdefghijklmnopvwxyzasdfghjkl@abc.com', '03-0000-0000', '株式会社レンタル', 'OVHilvyikb', '2020/5/30', '10:00', '22:00')
    reservationList = [reserveInfo1, reserveInfo2]
    return render_template('admin/reservations.html', navigation='Reservation of ' + spaceName, reservationList=reservationList)




# 管理者ログイン
@admin.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        adminName = request.form.get('adminName')
        adminPass = request.form.get('adminPass')

        # ログインチェック
        if adminName == 'sample' and adminPass == '1234':
            session['adminName'] = adminName
            return redirect(url_for('admin.index', navigation='Dashboard'))

        return render_template('admin/login.html', errMsg='ログインできませんでした')

    else:
        session.permanent = True
        return render_template('admin/login.html')

# 管理者ログアウト
@admin.route('/logout')
def logout():
    session.pop('adminName', None)
    return redirect(url_for('admin.login'))
