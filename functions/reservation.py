import os
import sys
import configparser
import json
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
def exportBookedDates(rentalSpace):
    preventSqlInjection(rentalSpace)
    # データベースへの接続とカーソルの生成
    conn = MySQLdb.connect(
        host = config.get('MySQL', 'hostname'),
        user = config.get('MySQL', 'user'),
        passwd = config.get('MySQL', 'password'),
        db = config.get('MySQL', 'schema'),
        charset = config.get('MySQL', 'charset'))

    print('connection is successful')

    cursor = conn.cursor()

    try:
        cursor.execute('select date from %s' % rentalSpace)
        fetch = cursor.fetchall()
        if fetch:
            with open('./static/csv/bookedDates_' + rentalSpace + '.csv', 'w') as f:
                for date in fetch:
                    if date[0] >= datetime.now().date(): # 本日以降の日に限る
                        line = date[0].strftime('%Y,%m,%d') + '\n'
                        f.write(line)
        print('exporting reserved dates to csv is successful')
    except Exception as e :
        print(str(e))
    finally:
        cursor.close()
        conn.close()



# 予約を確認する処理
def checkBooking(rentalSpace, datesToBeChecked):
    preventSqlInjection(rentalSpace)
    # データベースへの接続とカーソルの生成
    conn = MySQLdb.connect(
        host = config.get('MySQL', 'hostname'),
        user = config.get('MySQL', 'user'),
        passwd = config.get('MySQL', 'password'),
        db = config.get('MySQL', 'schema'),
        charset = config.get('MySQL', 'charset'))

    print('connection is successful')
    cursor = conn.cursor()
    result = []

    try:
        for date in datesToBeChecked:
            cursor.execute('select date from ' + rentalSpace + ' where date=%s', (date,))
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
    print(result)
    return result


# 予約を書き込む処理
def executeBooking(rentalSpace, bookingDates, usermail):
    preventSqlInjection(rentalSpace)
    # データベースへの接続とカーソルの生成
    conn = MySQLdb.connect(
        host = config.get('MySQL', 'hostname'),
        user = config.get('MySQL', 'user'),
        passwd = config.get('MySQL', 'password'),
        db = config.get('MySQL', 'schema'),
        charset = config.get('MySQL', 'charset'))

    print('connection is successful')
    cursor = conn.cursor()

    bookingId = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(10)])

    try:
        for date in bookingDates:
            cursor.execute('insert into ' + rentalSpace + '(date, days, usermail, bookingId) values(%s, %s, %s, %s)', (date, len(bookingDates), usermail, bookingId))

        print('inserting reserving date is successful')
    except Exception as e :
        print(str(e))
    finally:
        conn.commit()
        cursor.close()
        conn.close()

    return bookingId


# 予約を取り消す処理
def cancelReservation(rentalSpace, usermail, bookingId):
    preventSqlInjection(rentalSpace)
    # データベースへの接続とカーソルの生成
    conn = MySQLdb.connect(
        host = config.get('MySQL', 'hostname'),
        user = config.get('MySQL', 'user'),
        passwd = config.get('MySQL', 'password'),
        db = config.get('MySQL', 'schema'),
        charset = config.get('MySQL', 'charset'))

    print('connection is successful')
    cursor = conn.cursor()
    result = 0

    try:
        cursor.execute('select usermail, date from ' + rentalSpace + ' where bookingId=%s', (bookingId,))
        fetch = cursor.fetchone()
        if fetch:
            if usermail == str(fetch[0]):
                date = fetch[1]
                if date >= datetime.now().date(): # 本日以降の日に限る
                    cursor.execute('delete from ' + rentalSpace + ' where bookingId=%s', (bookingId,))
                    result = 1
                    print('canceling reserved date is successful')
            else:
                print('usermail is incorrect')
        else:
            print('this booking number is nothing')

    except Exception as e :
        print(str(e))
    finally:
        conn.commit()
        cursor.close()
        conn.close()

    return result

# SQLインジェクションチェック
def preventSqlInjection(rentalSpace):
    spaceList = json.loads(config.get("RentalSpace","spaceList"))
    if rentalSpace not in spaceList:
        raise Exception('SQLインジェクションの可能性あり')
