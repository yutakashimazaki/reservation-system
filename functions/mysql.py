import os
import sys
import configparser
import random
import string
from datetime import datetime, date
import MySQLdb

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


# 今月(本日)以降３ヶ月の予約状況をファイルに書き込む処理
def exportBookedDates():
    # データベースへの接続とカーソルの生成
    conn = MySQLdb.connect(
        host = config.get('MySQL', 'hostname'),
        user = config.get('MySQL', 'user'),
        passwd = config.get('MySQL', 'password'),
        db = config.get('MySQL', 'schema'))

    print('connection is successful')

    cursor = conn.cursor()
    result = []

    try:
        cursor.execute('select date from sapace_a')
        fetch = cursor.fetchall()
        if fetch:
            with open('./static/csv/bookedDates.csv', 'w') as f:
                for date in fetch:
                    if date[0] >= datetime.now().date(): # 本日以降の日に限る
                        line = date[0].strftime('%Y,%m,%d') + '\n'
                        f.write(line)
        print('exporting reserved dates to csv is successful')
    except Exception as e :
        print(str(e))
    finally:
        conn.commit()
        cursor.close()
        conn.close()



# 予約を確認する処理
def checkBooking(datesToBeChecked):
    # データベースへの接続とカーソルの生成
    conn = MySQLdb.connect(
        host = config.get('MySQL', 'hostname'),
        user = config.get('MySQL', 'user'),
        passwd = config.get('MySQL', 'password'),
        db = config.get('MySQL', 'schema'))

    print('connection is successful')
    cursor = conn.cursor()
    result = []

    try:
        for date in datesToBeChecked:
            cursor.execute('select date from sapace_a where date=%s', (date,))
            fetch = cursor.fetchone()
            if fetch:
                if date == fetch[0]:
                    result.append(date)

        print('All reserved dates are checked')
    except Exception as e :
        print(str(e))
    finally:
        cursor.close()
        conn.close()

    return result


# 予約を書き込む処理
def executeBooking(bookingDates, usermail):
    # データベースへの接続とカーソルの生成
    conn = MySQLdb.connect(
        host = config.get('MySQL', 'hostname'),
        user = config.get('MySQL', 'user'),
        passwd = config.get('MySQL', 'password'),
        db = config.get('MySQL', 'schema'))

    print('connection is successful')
    cursor = conn.cursor()

    bookingId = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(10)])

    try:
        for date in bookingDates:
            cursor.execute('insert into sapace_a(date, days, usermail, bookingId) values(%s, %s, %s, %s)', (date, len(bookingDates), usermail, bookingId))

        print('inserting reserving date is successful')
    except Exception as e :
        print(str(e))
    finally:
        conn.commit()
        cursor.close()
        conn.close()

    return bookingId


# 予約を取り消す処理
def cancelReservation(bookingId):
    # データベースへの接続とカーソルの生成
    conn = MySQLdb.connect(
        host = config.get('MySQL', 'hostname'),
        user = config.get('MySQL', 'user'),
        passwd = config.get('MySQL', 'password'),
        db = config.get('MySQL', 'schema'))

    print('connection is successful')
    cursor = conn.cursor()
    usermail = None

    try:
        cursor.execute('select usermail from sapace_a where bookingId=%s', (bookingId,))
        fetch = cursor.fetchone()
        if fetch:
            usermail = str(fetch[0])
            cursor.execute('delete from sapace_a where bookingId=%s', (bookingId,))
            print('canceling reserved date is successful')
        else: # 予約番号がないとき
            print('this booking number is nothing')

    except Exception as e :
        print(str(e))
    finally:
        conn.commit()
        cursor.close()
        conn.close()

    return usermail
