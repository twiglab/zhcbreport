from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, redirect

main_bp = Blueprint('main_bp', __name__, url_prefix='/')

@main_bp.route('/', methods=['GET'])
def index():
    bizdate = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    sysdate = (datetime.now()).strftime('%Y%m%d')
    return render_template("index.html", bizdate=bizdate, sysdate=sysdate)

