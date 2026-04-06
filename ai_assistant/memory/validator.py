# 在写入文件前验证数据的合法性，防止脏数据进入记忆库导致幻觉

import re
from datetime import datetime
from .config import DATE_FORMAT

class MemoryValidator:
    @staticmethod
    def validate_date(date_str):
        """验证日期格式是否为 YYYY-MM-DD"""
        try:
            datetime.strptime(date_str, DATE_FORMAT)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_source(source_file, sessions_dir):
        """验证来源文件是否存在，防止引用失效"""
        import os
        return os.path.exists(os.path.join(sessions_dir, source_file))

    @staticmethod
    def clean_content(content):
        """清理内容中的控制字符，确保存储安全"""
        # 移除不可见字符，保留基本标点
        cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', content)
        return cleaned.strip()

    @staticmethod
    def check_conflict(old_entry, new_entry):
        """
        简单启发式冲突检查
        如果包含否定词或纠正词，视为潜在冲突
        """
        conflict_keywords = ["不", "别", "纠正", "改为", "错误", "放弃"]
        if any(k in new_entry for k in conflict_keywords):
            return True
        return False
