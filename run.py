import os
import configparser
from flask import Flask, render_template, Markup

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
# アプリ全体の立ち上げ
# ======================================================
app = Flask(__name__)
app.secret_key = config.get('WebServer', 'sessionKey')

# ======================================================
# 各アプリの登録
# ======================================================
from customer.web import customer
app.register_blueprint(customer, url_prefix='/')

from admin.web import admin
app.register_blueprint(admin, url_prefix='/admin')


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
