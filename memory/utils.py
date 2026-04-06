# 提供文件操作、日期解析和行数统计等工具函数。
# memory/utils.py
import os
import re
from datetime import datetime, timedelta
from .config import DATE_FORMAT

def count_lines(filepath):
    """统计文件行数，用于修剪阶段"""
    if not os.path.exists(filepath):
        return 0
    with open(filepath, 'r', encoding='utf-8') as f:
        return sum(1 for _ in f)

def parse_relative_date(text, reference_date=None):
    """
    整合阶段：将模糊时间转换为具体日期
    例如：'昨天' -> '2023-10-27'
    """
    if reference_date is None:
        reference_date = datetime.now()
    
    today = reference_date.date()
    
    if "昨天" in text or "昨日" in text:
        return (today - timedelta(days=1)).strftime(DATE_FORMAT)
    elif "今天" in text or "今日" in text:
        return today.strftime(DATE_FORMAT)
    elif "明天" in text or "明日" in text:
        return (today + timedelta(days=1)).strftime(DATE_FORMAT)
    elif "上周" in text:
        return (today - timedelta(weeks=7)).strftime(DATE_FORMAT)  # 已修正
    
    # 尝试匹配标准日期格式 YYYY-MM-DD
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    match = re.search(date_pattern, text)
    if match:
        return match.group()
        
    return today.strftime(DATE_FORMAT)

def ensure_directory(path):
    """确保目录存在"""
    if not os.path.exists(path):
        os.makedirs(path)

def read_file_safe(filepath):
    """安全读取文件"""
    if not os.path.exists(filepath):
        return ""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file_safe(filepath, content):
    """安全写入文件"""
    ensure_directory(os.path.dirname(filepath))
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
