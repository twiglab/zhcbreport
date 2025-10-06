import os
from datetime import date
from flask import render_template, request, jsonify, send_file

from report.reports import reports_bp
from report.reports.utils import read_csv_data



@reports_bp.route('/receivable_details_csv', methods=['GET'])
def receivable_details_csv():
    report_date = request.args.get('report_date')
    b,msg = validate_report_date(report_date)
    if not b:
        return render_template('reports/receivable_details_csv.html',
                               error=msg)


    result = read_csv_data(f'receivable_details/shop_fee_per_day_{report_date}.csv'.format(datestr=report_date))
    if result['success']:
        return render_template('reports/receivable_details_csv.html',
                               report_date=report_date,
                               data=result['data'],
                               columns=result['columns'],
                               total_records=result['total_records'])
    else:
        return render_template('reports/receivable_details_csv.html',
                               report_date=report_date,
                               error=result['error'])


@reports_bp.route('/receivable_details_csv/download')
def receivable_details_csv_download():
    """
        处理应收账款明细CSV报表请求
        URL格式: /reports/receivable_details_csv?report_date=20251005
        """
    try:
        # 获取查询参数
        report_date = request.args.get('report_date')
        b, msg = validate_report_date(report_date)
        if not b:
            return jsonify({
                'success': False,
                'error': msg
            }), 400

        csv_path = os.path.join(os.getenv('REPORT_DATA_BASE_DIR'), f'receivable_details/shop_fee_per_day_{report_date}.csv'.format(datestr=report_date))

        # 检查文件是否存在
        if not os.path.exists(csv_path):
            return jsonify({
                'success': False,
                'error': '文件不存在'
            }), 404

        # 生成下载文件名
        filename = f"南瑞路项目租金管理费应收账表明细表_{report_date}.csv"

        return send_file(
            csv_path,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv',
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500


def validate_report_date(report_date):
    if report_date is None:
        return False, "请求报告日期不能为空"

    if len(report_date) != 8 or not report_date.isdigit():
        return False, '日期格式错误，请使用YYYYMMDD格式'

    return True, None
