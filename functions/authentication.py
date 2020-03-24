import os
import sys
import configparser
import random
import string
import hashlib
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


# ログイン処理
def loginUser(mail, password):
    # データベースへの接続とカーソルの生成
    conn = MySQLdb.connect(
        host = config.get('MySQL', 'hostname'),
        user = config.get('MySQL', 'user'),
        passwd = config.get('MySQL', 'password'),
        db = config.get('MySQL', 'schema'))

    print('connection is successful')

    cursor = conn.cursor()
    result = 0

    try:
        cursor.execute('select salt, password, available from user where mail=%s', (mail,))
        fetch = cursor.fetchone()
        if fetch:
            userSalt = fetch[0]
            userPass = fetch[1]
            userVerification = fetch[2]
            if userVerification == 1:
                if userPass == strechPassword(password, userSalt):
                    result = 1
                    print('login is successful')
                else:
                    result = -1
                    print('password is incorrect')
            else:
                result = -2
                print('this user is not availavle')
    except Exception as e :
        print(str(e))
    finally:
        cursor.close()
        conn.close()

    return result


def tempRegisterUser(mail, password, phone, firstName, lastName, company, tempPass):
    # データベースへの接続とカーソルの生成
    conn = MySQLdb.connect(
        host = config.get('MySQL', 'hostname'),
        user = config.get('MySQL', 'user'),
        passwd = config.get('MySQL', 'password'),
        db = config.get('MySQL', 'schema'))

    print('connection is successful')
    cursor = conn.cursor()
    result = 0

    salt = generateSalt()
    hashedPass = strechPassword(password, salt)
    hashedTempPass = strechTempPassword(tempPass, salt)
    try:
        cursor.execute('select available from user where mail=%s', (mail,))
        fetch = cursor.fetchone()
        if fetch:
            if fetch[0] == 0:   # verificationが完了していないユーザーは上書き
                cursor.execute('delete from user where mail=%s', (mail,))
                cursor.execute('insert into user(mail, salt, password, phone, firstName, lastName, company, tempPass) values(%s, %s, %s, %s, %s, %s, %s, %s)', (mail, salt, hashedPass, phone, firstName, lastName, company, hashedTempPass))
                result = 1
                print('temporary register is successful')
        else:
            cursor.execute('insert into user(mail, salt, password, phone, firstName, lastName, company, tempPass) values(%s, %s, %s, %s, %s, %s, %s, %s)', (mail, salt, hashedPass, phone, firstName, lastName, company, hashedTempPass))
            result = 1
            print('temporary register is successful')

    except Exception as e :
        print(str(e))
    finally:
        conn.commit()
        cursor.close()
        conn.close()

    return result


def registerUser(mail, code):
    # データベースへの接続とカーソルの生成
    conn = MySQLdb.connect(
        host = config.get('MySQL', 'hostname'),
        user = config.get('MySQL', 'user'),
        passwd = config.get('MySQL', 'password'),
        db = config.get('MySQL', 'schema'))

    print('connection is successful')
    cursor = conn.cursor()
    result = 0

    try:
        cursor.execute('select salt, tempPass from user where mail=%s', (mail,))
        fetch = cursor.fetchone()
        if fetch:
            userSalt = fetch[0]
            userTempPass = fetch[1]
            if userTempPass == strechTempPassword(code, userSalt):
                result = 1
                cursor.execute('update user set available = 1 where mail=%s', (mail,))
                print('verification is successful')
            else:
                result = -1
                print('verification code  is incorrect')

    except Exception as e :
        print(str(e))
    finally:
        conn.commit()
        cursor.close()
        conn.close()

    return result

# ソルトを生成
def generateSalt():
    tokenLength = 10
    salt = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(tokenLength)])
    return salt

# パスワードをストレッチ
def strechPassword(password, salt):
    hashedPass = ''
    for i in range(1000):
        text=(hashedPass + salt + password + salt).encode('utf-8')
        hashedPass = hashlib.sha256(text).hexdigest()
    return hashedPass

def strechTempPassword(password, salt):
    hashedPass = ''
    for i in range(1000):
        text=(hashedPass + password + salt).encode('utf-8')
        hashedPass = hashlib.sha256(text).hexdigest()
    return hashedPass

# ワンタイムパスワードを生成
def generateValidateCode():
    tokenLength = 16
    code = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(tokenLength)])
    return code
