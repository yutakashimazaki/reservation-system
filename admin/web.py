from flask import Blueprint, render_template

# ======================================================
# ルーティング処理
# ======================================================
admin = Blueprint('admin', __name__, template_folder='templates', static_folder='./static', static_url_path='/static_a')

# admin.secret_key = config.get('WebServer', 'sessionKey')

@admin.route('/')
def index():
    return render_template('admin/index.html')
