import os
import sys
import configparser
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate

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


# メッセージ作成
def createMessage(toAddress, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = config.get('Email', 'fromAddress')
    msg['To'] = toAddress
    msg['Date'] = formatdate()
    return msg

# 予約確認メール送信
def sendConfirmReservingMail(toAddress, body):
    subject = 'ご予約の確認'
    msg = createMessage(toAddress, subject, body)
    smtpobj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpobj.ehlo()
    smtpobj.starttls()
    smtpobj.ehlo()
    smtpobj.login(config.get('Email', 'fromAddress'), config.get('Email', 'password'))
    smtpobj.sendmail(config.get('Email', 'fromAddress'), toAddress, msg.as_string())
    smtpobj.close()

# 予約確認メール送信
def sendCancelReservationMail(toAddress, body):
    subject = 'ご予約キャンセルの確認'
    msg = createMessage(toAddress, subject, body)
    smtpobj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpobj.ehlo()
    smtpobj.starttls()
    smtpobj.ehlo()
    smtpobj.login(config.get('Email', 'fromAddress'), config.get('Email', 'password'))
    smtpobj.sendmail(config.get('Email', 'fromAddress'), toAddress, msg.as_string())
    smtpobj.close()
