import os

import pandas as pd

def read_csv_data(csv_file):
    """
    读取CSV文件并返回数据
    """
    try:
        csv_path = os.path.join(os.getenv('REPORT_DATA_BASE_DIR'), csv_file)
        df = pd.read_csv(csv_path)
        df.fillna(0, inplace=True)
        data = df.to_dict('records')
        columns = df.columns.tolist()
        return {
            'success': True,
            'data': data,
            'columns': columns,
            'total_records': len(data)
        }

    except FileNotFoundError:
        return {
            'success': False,
            'error': '报表数据未生成，请联系管理！'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'读取文件时出错: {str(e)}'
        }
