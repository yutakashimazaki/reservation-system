import os
import sys
import configparser
import random
import string
from datetime import datetime, date
import MySQLdb

from dto.spaceInfo import SpaceInfo
from dto.spaceDetails import SpaceDetails

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


# 全てのスペースの情報を返す
def getAllSpaceInfo():
    allSpaceInfo = {}
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
        cursor.execute('select id, spaceName, address, tell, startTime, endTime from rental_space')
        fetch = cursor.fetchall()
        if fetch:
            for info in fetch:
                id = info[0]
                spaceInfo = SpaceInfo(info[1], info[2], info[3], info[4], info[5])
                allSpaceInfo[id] = spaceInfo

            print("getting all space's infomation is successful")

    except Exception as e :
        print(str(e))
    finally:
        cursor.close()
        conn.close()

    return allSpaceInfo

# スペースの詳細を返す
def getSpaceDetails(rentalSpace):
    spaceDetails = None
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
        cursor.execute('select * from rental_space where id=%s', (rentalSpace,))
        fetch = cursor.fetchone()
        if fetch:
            description = fetch[2]
            capacity = fetch[3]
            roomSize = fetch[4]
            address = fetch[5]
            tell = fetch[6]
            startTime = fetch[7]
            endTime = fetch[8]
            nearStation = fetch[9]
            spaceDetails = SpaceDetails(description, capacity , roomSize, address, tell, startTime, endTime, nearStation)
            print("getting space's details is successful")

    except Exception as e :
        print(str(e))
    finally:
        cursor.close()
        conn.close()

    return spaceDetails

# スペースの説明文を返す
def getSpaceDescription(rentalSpace):
    spaceDescription = None
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
        cursor.execute('select description from rental_space where id=%s', (rentalSpace,))
        fetch = cursor.fetchone()
        if fetch:
            spaceDescription = fetch[0]
            print("getting space's description is successful")

    except Exception as e :
        print(str(e))
    finally:
        cursor.close()
        conn.close()

    return spaceDescription

# スペースの備品情報を取得
def getSpaceEquipments(rentalSpace):
    return '未定'

# スペースの料金プランを取得
def getSpaceBudgetPlan(rentalSpace):
    return '未定'

# スペースのレビューを取得
def getSpaceReview(rentalSpace):
    return '未定'
