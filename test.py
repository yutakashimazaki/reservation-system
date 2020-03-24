import os
import sys
import configparser
import random
import string
import hashlib
from datetime import datetime, date
import MySQLdb
from functions.authentication import strechPassword, generateValidateCode

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

# データベースへの接続とカーソルの生成
conn = MySQLdb.connect(
    host = config.get('MySQL', 'hostname'),
    user = config.get('MySQL', 'user'),
    passwd = config.get('MySQL', 'password'),
    db = config.get('MySQL', 'schema'))

print('connection is successful')

cursor = conn.cursor()
mail = 'athlete_s.y@docomo.ne.jp'

try:
    cursor.execute('select name, company, available from user where mail=%s', (mail,))
    fetch = cursor.fetchone()
    if fetch:
        name = fetch[0]
        print(strechPassword('nfd0DEovgIDmNIT0', 'wU1g5RhcWD'))
        print(strechPassword('asdfghjklpoiuytrewq', 'wU1g5RhcWD'))
    else:
        print('not found')
except Exception as e :
    print(str(e))
finally:
    cursor.close()
    conn.close()
