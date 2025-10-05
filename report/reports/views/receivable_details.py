import json

import numpy as np
import pandas as pd
from flask import render_template
from sqlalchemy import text

from report.extensions import db
from report.reports import reports_bp


@reports_bp.route('/ReceivableDetails', methods=['GET', 'POST'])
def reports_index():
    return render_template("reports/receivable_details.html")


@reports_bp.route('/FetchData/ReceivableDetails', methods=['POST'])
def receivable_details():
    result = db.session.execute(text('select * from {}'.format('ads_shop_fee')))
    df = pd.DataFrame(result.fetchall(), columns=result.keys())

    id_vars = ['shopname', 'x_floor_name', 'tenantname', 'settle_no']
    value_vars = list(column_mapping.keys())
    # 将宽表转换为长表
    df_long = pd.melt(df, id_vars=id_vars, value_vars=value_vars, var_name='费用科目', value_name='金额')
    # 根据映射关系，将原始列名拆分为费用类型和收付类型
    df_long[['费用类型', '收付类型']] = df_long['费用科目'].map(column_mapping).apply(pd.Series)
    # 然后，我们可以构建一个透视表，将店铺信息作为行，月份和费用类型、收付类型作为列
    pivot_df = pd.pivot_table(df_long,
                              index=['shopname', 'tenantname','x_floor_name'],
                              columns=['settle_no', '费用类型', '收付类型'],
                              values='金额',
                              aggfunc='sum').sort_values('x_floor_name', ascending=False)

    luckysheet_data = build_luckysheet_from_pivot(pivot_df)
    luckysheet_json_str = json.dumps(luckysheet_data, ensure_ascii=False, indent=2)
    return luckysheet_json_str


column_mapping = {
    # 租赁合同费用
    'f_001_0': ('租金', '应收'), 'f_001_1': ('租金', '已收'),
    'f_002_0': ('租金', '应收'), 'f_002_1': ('租金', '已收'),
    'f_003_0': ('租金', '应收'), 'f_003_1': ('租金', '已收'),

    'f_101_0': ('管理费', '应收'), 'f_101_1': ('管理费', '已收'),

    'f_1_302_0': ('电费', '应收'), 'f_1_302_1': ('电费', '已收'),
    'f_1_303_0': ('水费', '应收'), 'f_1_303_1': ('水费', '已收'),
    'f_1_804_0': ('燃气费', '应收'), 'f_1_804_1': ('燃气费', '已收'),
    'f_1_304_0': ('现场服务费', '应收'), 'f_1_304_1': ('现场服务费', '已收'),

    # 多经合同费用
    'f_501_0': ('多经场地使用费', '应收'), 'f_501_1': ('多经场地使用费', '已收'),
    'f_502_0': ('多经管理费', '应收'), 'f_502_1': ('多经管理费', '已收'),
    'f_503_0': ('多经电费', '应收'), 'f_503_1': ('多经电费', '已收'),
    'f_2_302_0': ('多经电费', '应收'), 'f_2_302_1': ('多经电费', '已收'),
    'f_2_303_0': ('多经水费', '应收'), 'f_2_303_1': ('多经水费', '已收'),
    'f_2_804_0': ('多经燃气费', '应收'), 'f_2_804_1': ('多经燃气费', '已收'),
    'f_504_0': ('多经现场服务费', '应收'), 'f_504_1': ('多经现场服务费', '已收'),
    'f_2_304_0': ('多经现场服务费', '应收'), 'f_2_304_1': ('多经现场服务费', '已收'),

    # 仓库合同费用
    'f_403_0': ('仓库使用费', '应收'), 'f_403_1': ('仓库使用费', '已收'),
    'f_3_302_0': ('仓库电费', '应收'), 'f_3_302_1': ('仓库电费', '已收'),
    'f_3_303_0': ('仓库水费', '应收'), 'f_3_303_1': ('仓库水费', '已收'),
    'f_3_804_0': ('仓库燃气费', '应收'), 'f_3_804_1': ('仓库燃气费', '已收'),
    'f_3_304_0': ('仓库现场服务费', '应收'), 'f_3_304_1': ('仓库现场服务费', '已收'),

    # 其他费用
    'f_306_0': ('垃圾清运费', '应收'), 'f_306_1': ('垃圾清运费', '已收'),
    'f_401_0': ('泔水费', '应收'), 'f_401_1': ('泔水费', '已收'),
    'f_802_0': ('消杀费', '应收'), 'f_802_1': ('消杀费', '已收'),
    'f_808_0': ('餐厨垃圾清运费', '应收'), 'f_808_1': ('餐厨垃圾清运费', '已收'),
    'f_809_0': ('虫害防治费', '应收'), 'f_809_1': ('虫害防治费', '已收'),
    'f_810_0': ('隔油池清掏费', '应收'), 'f_810_1': ('隔油池清掏费', '已收'),
    'f_811_0': ('排油烟系统清洗费', '应收'), 'f_811_1': ('排油烟系统清洗费', '已收'),
    'f_404_0': ('停车费', '应收'), 'f_404_1': ('停车费', '已收')
}


def build_luckysheet_from_pivot(pivot_df, sheet_name="透视表"):
    # 获取索引和列的层级数
    row_levels = pivot_df.index.nlevels
    col_levels = pivot_df.columns.nlevels

    # 初始化工作表数据 - 完整结构基于Luckysheet官方文档
    sheet_data = {
        "name": sheet_name,
        "color": "",
        "index": "index_01",
        "status": "1",
        "order": "0",
        "hide": 0,
        "row": len(pivot_df) + col_levels + 1,  # 总行数：数据行数 + 列标题行数 + 行索引标题行
        "column": len(pivot_df.columns) + row_levels,  # 总列数：数据列数 + 行索引列数
        "config": {
            "merge": {},  # 合并单元格
            "rowlen": {},  # 表格行高
            "columnlen": {},  # 表格列宽
            "rowhidden": {},  # 隐藏行
            "colhidden": {},  # 隐藏列
            "borderInfo": {},  # 边框
        },
        "celldata": [],  # 初始化使用的单元格数据
        "data": [],  # 更新和存储使用的单元格数据
        "scrollLeft": 0,
        "scrollTop": 0,
        "luckysheet_select_save": [],
        "luckysheet_conditionformat_save": {},
        "calcChain": [],
        "isPivotTable": False,
        "pivotTable": {},
        "filter_select": {},
        "filter": None,
        "luckysheet_alternateformat_save": [],
        "luckysheet_alternateformat_save_modelCustom": [],
        "freezen": {},
        "chart": [],
        "visibledatarow": [],
        "visibledatacolumn": [],
        "ch_width": 0,
        "rh_height": 0,
        "load": "1"
    }

    current_row = 0
    all_merge_cells = []

    # 1. 构建多级列标题
    for level in range(col_levels):
        col_header_row = current_row
        # 获取当前层级的列值
        level_values = []
        for col in pivot_df.columns:
            if isinstance(col, tuple):
                level_values.append(col[level] if level < len(col) else "")
            else:
                level_values.append(col if level == 0 else "")

        # 计算列标题的合并单元格
        merge_start = 0
        current_value = level_values[0]

        for i in range(1, len(level_values) + 1):
            if i == len(level_values) or level_values[i] != current_value:
                # 如果连续相同值的单元格数量大于1，则需要合并
                if merge_start < i - 1:
                    merge_cell = {
                        "r": col_header_row,
                        "c": merge_start + row_levels,  # 偏移行索引的列数
                        "rs": 1,  # 合并行数
                        "cs": i - merge_start  # 合并列数
                    }
                    all_merge_cells.append(merge_cell)

                if i < len(level_values):
                    current_value = level_values[i]
                    merge_start = i

        # 添加列标题单元格数据
        for col_idx, value in enumerate(level_values):
            if pd.isna(value):
                display_value = ""
            else:
                display_value = str(value)

            cell_value = {
                "v": display_value,
                "m": display_value,
                "ct": {"fa": "@", "t": "g"}  # 文本格式
            }

            # 为表头添加基本样式
            if level == col_levels - 1:  # 最内层列标题
                cell_value["bg"] = "rgb(245, 245, 245)"
                cell_value["bl"] = 1  # 粗体

            sheet_data["celldata"].append({
                "r": col_header_row,
                "c": col_idx + row_levels,
                "v": cell_value
            })

        current_row += 1

    # 2. 构建行索引标题行
    for row_idx, row_name in enumerate(pivot_df.index.names):
        if row_name is None:
            display_value = ""
        else:
            display_value = str(row_name)

        cell_value = {
            "v": display_value,
            "m": display_value,
            "ct": {"fa": "@", "t": "g"},
            "bg": "rgb(245, 245, 245)",
            "bl": 1  # 粗体
        }

        sheet_data["celldata"].append({
            "r": current_row,
            "c": row_idx,
            "v": cell_value
        })

        # 3. 处理行索引的合并单元格
        for level in range(row_levels):
            merge_start = 0
            current_value = pivot_df.index[0][level] if row_levels > 0 else pivot_df.index[0]

            for row_idx in range(1, len(pivot_df.index) + 1):
                if row_idx == len(pivot_df.index):
                    # 最后一行
                    current_row_value = None
                else:
                    if row_levels > 0:
                        current_row_value = pivot_df.index[row_idx][level]
                    else:
                        current_row_value = pivot_df.index[row_idx]

                if row_idx == len(pivot_df.index) or current_row_value != current_value:
                    if merge_start < row_idx - 1:
                        merge_cell = {
                            "r": merge_start + current_row + 1,
                            "c": level,
                            "rs": row_idx - merge_start,
                            "cs": 1
                        }
                        all_merge_cells.append(merge_cell)

                    if row_idx < len(pivot_df.index):
                        if row_levels > 0:
                            current_value = pivot_df.index[row_idx][level]
                        else:
                            current_value = pivot_df.index[row_idx]
                        merge_start = row_idx

    # 4. 填充行索引和数据值
    data_start_row = current_row + 1

    for row_idx, row_index in enumerate(pivot_df.index):
        data_row = data_start_row + row_idx

        # 添加行索引值
        if row_levels > 0:
            # 多级索引
            for level_idx, index_value in enumerate(row_index):
                if pd.isna(index_value):
                    display_value = ""
                else:
                    display_value = str(index_value)

                cell_value = {
                    "v": display_value,
                    "m": display_value,
                    "ct": {"fa": "@", "t": "g"}
                }

                sheet_data["celldata"].append({
                    "r": data_row,
                    "c": level_idx,
                    "v": cell_value
                })
        else:
            # 单级索引
            if pd.isna(row_index):
                display_value = ""
            else:
                display_value = str(row_index)

            cell_value = {
                "v": display_value,
                "m": display_value,
                "ct": {"fa": "@", "t": "g"}
            }

            sheet_data["celldata"].append({
                "r": data_row,
                "c": 0,
                "v": cell_value
            })

        # 添加数据单元格
        for col_idx, value in enumerate(pivot_df.iloc[row_idx]):
            if pd.isna(value):
                display_value = ""
                cell_value = {
                    "v": display_value,
                    "m": display_value,
                    "ct": {"fa": "@", "t": "g"}
                }
            else:
                display_value = str(value)

                # 根据数据类型设置格式
                if isinstance(value, (int, np.integer)):
                    cell_value = {
                        "v": value,
                        "m": display_value,
                        "ct": {"fa": "#,##0", "t": "n"}  # 整数格式
                    }
                elif isinstance(value, (float, np.floating)):
                    cell_value = {
                        "v": value,
                        "m": display_value,
                        "ct": {"fa": "#,##0.00", "t": "n"}  # 小数格式
                    }
                else:
                    cell_value = {
                        "v": display_value,
                        "m": display_value,
                        "ct": {"fa": "@", "t": "g"}  # 文本格式
                    }

            sheet_data["celldata"].append({
                "r": data_row,
                "c": col_idx + row_levels,
                "v": cell_value
            })

    # 5. 设置合并单元格配置（使用正确的键名格式）
    if all_merge_cells:
        merge_config = {}
        for i, merge_cell in enumerate(all_merge_cells):
            # 使用正确的键名格式: "行号_列号"
            key = f"{merge_cell['r']}_{merge_cell['c']}"
            merge_config[key] = {
                "r": merge_cell["r"],
                "c": merge_cell["c"],
                "rs": merge_cell["rs"],
                "cs": merge_cell["cs"]
            }

        sheet_data["config"]["merge"] = merge_config

    # 6. 设置默认行列尺寸
    for i in range(sheet_data["row"]):
        sheet_data["config"]["rowlen"][str(i)] = 25  # 默认行高

    for i in range(sheet_data["column"]):
        sheet_data["config"]["columnlen"][str(i)] = 100  # 默认列宽

    return [sheet_data]