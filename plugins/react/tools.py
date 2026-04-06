# plugins/react/tools.py
from datetime import datetime

def search_memory(args):
    """搜索记忆"""
    return f"记忆：{args}"

def calculate(args):
    """计算"""
    try:
        result = eval(args, {"__builtins__": {}}, {})
        return f"结果：{result}"
    except Exception as e:
        return f"错误：{e}"

def get_date(args):
    """获取日期"""
    return f"当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}"

DEFAULT_TOOLS = [
    {'name': 'search_memory', 'description': '搜索记忆', 'func': search_memory},
    {'name': 'calculate', 'description': '数学计算', 'func': calculate},
    {'name': 'get_date', 'description': '获取当前时间', 'func': get_date},
]
