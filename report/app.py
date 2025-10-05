from datetime import datetime, timedelta

from flask import Flask

from report.extensions import db
from report.main import main_bp
from report.reports import reports_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object('report.config')
    app.debug = True
    db.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(reports_bp, url_prefix='/reports')

    @app.context_processor
    def inject_global_variables():
        # 返回的字典中的变量将在所有模板中可用
        return dict(
            bizdate=(datetime.now() - timedelta(days=1)).strftime('%Y%m%d'),
            sysdate=(datetime.now()).strftime('%Y%m%d')
        )
    return app
