import datetime

from flask import render_template, json
from jinja2 import Undefined
from sqlalchemy import inspect, text

from report.extensions import db
from report.reports import reports_bp


@reports_bp.route('/table/<string:table_name>', methods=['GET'])
def report(table_name):
    inspector = inspect(db.engine)
    columns = inspector.get_columns(table_name)

    # 获取表数据
    result = db.session.execute(text('SELECT * FROM {}'.format(table_name)))
    rowData = []
    for row in result:
        t = {}
        for index, column in enumerate(columns):
            key = column['name']
            value = row[index]
            if isinstance(value, Undefined):
                value = None
            t[key] = value
        rowData.append(t)

    # 将数据转换为Luckysheet格式
    luckysheet_data = convert_to_luckysheet_format(columns, rowData)

    return render_template('reports/table_data_analysis.html',
                           table_name=table_name,
                           luckysheet_data=json.dumps(luckysheet_data),
                           columns=columns)


def convert_to_luckysheet_format(columns, rowData):
    """
    将数据库查询结果转换为Luckysheet格式
    """
    # 构建工作表配置
    sheet_data = {
        "name": "数据表",
        "color": "",
        "index": "index_01",
        "status": "1",
        "order": "0",
        "hide": 0,
        "row": len(rowData) + 1,  # 数据行数 + 表头行
        "column": len(columns),
        "config": {
            "merge": {},
            "rowlen": {},
            "columnlen": {},
            "rowhidden": {},
            "colhidden": {},
            "borderInfo": {},
        },
        "celldata": [],
        "scrollLeft": 0,
        "scrollTop": 0,
        "luckysheet_select_save": [],
        "luckysheet_conditionformat_save": {},
        "calcChain": [],
        "isPivotTable": False,
        "pivotTable": {},
        "filter_select": {},
        "filter": None,
        "freezen": {},
        "chart": [],
        "load": "1"
    }

    # 设置默认行列尺寸
    for i in range(sheet_data["row"]):
        sheet_data["config"]["rowlen"][str(i)] = 25

    for i in range(sheet_data["column"]):
        sheet_data["config"]["columnlen"][str(i)] = 100

    # 添加表头（第0行）
    for col_idx, column in enumerate(columns):
        cell_value = {
            "v": column['name'],
            "m": column['name'],
            "ct": {"fa": "@", "t": "g"},
            "bg": "rgb(79, 129, 189)",  # 蓝色背景
            "fc": "rgb(255, 255, 255)",  # 白色字体
            "bl": 1,  # 粗体
            "fs": 12  # 字体大小
        }

        sheet_data["celldata"].append({
            "r": 0,
            "c": col_idx,
            "v": cell_value
        })

    # 添加数据行（从第1行开始）
    for row_idx, row in enumerate(rowData):
        for col_idx, column in enumerate(columns):
            column_name = column['name']
            value = row.get(column_name)

            if value is None:
                display_value = ""
                cell_value = {
                    "v": display_value,
                    "m": display_value,
                    "ct": {"fa": "@", "t": "g"}
                }
            else:
                display_value = str(value)

                # 根据数据类型设置格式
                if isinstance(value, (int,)):
                    cell_value = {
                        "v": value,
                        "m": display_value,
                        "ct": {"fa": "#,##0", "t": "n"}
                    }
                elif isinstance(value, (float,)):
                    cell_value = {
                        "v": value,
                        "m": display_value,
                        "ct": {"fa": "#,##0.00", "t": "n"}
                    }
                elif isinstance(value, (datetime.datetime,)):
                    # 日期时间类型
                    display_value = value.strftime("%Y-%m-%d %H:%M:%S")
                    cell_value = {
                        "v": display_value,
                        "m": display_value,
                        "ct": {"fa": "yyyy-mm-dd hh:mm:ss", "t": "d"}
                    }
                elif isinstance(value, (datetime.date,)):
                    # 日期类型
                    display_value = value.strftime("%Y-%m-%d")
                    cell_value = {
                        "v": display_value,
                        "m": display_value,
                        "ct": {"fa": "yyyy-mm-dd", "t": "d"}
                    }
                else:
                    # 文本类型
                    cell_value = {
                        "v": display_value,
                        "m": display_value,
                        "ct": {"fa": "@", "t": "g"}
                    }

            sheet_data["celldata"].append({
                "r": row_idx + 1,  # 从第1行开始
                "c": col_idx,
                "v": cell_value
            })

    return [sheet_data]

