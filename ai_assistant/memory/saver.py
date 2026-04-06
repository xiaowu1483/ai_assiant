# 负责将会话数据原子性地保存到 sessions/ 目录。使用“先写临时文件再重命名”的策略，防止文件损坏。
import os
import json
import tempfile
import shutil
from datetime import datetime
from .config import SESSIONS_DIR

class SessionSaver:
    @staticmethod
    def save_session(messages, session_id=None):
        """
        原子性保存会话记录
        :param messages: 对话消息列表 [{"role": "...", "content": "..."}]
        :param session_id: 可选会话 ID，默认使用时间戳
        :return: 保存的文件路径
        """
        if not os.path.exists(SESSIONS_DIR):
            os.makedirs(SESSIONS_DIR)

        if session_id is None:
            session_id = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        
        filename = f"{session_id}.json"
        final_path = os.path.join(SESSIONS_DIR, filename)
        
        # 数据结构
        data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "session_id": session_id,
            "messages": messages
        }

        # 原子写入：先写临时文件，再重命名
        try:
            fd, temp_path = tempfile.mkstemp(suffix='.json', dir=SESSIONS_DIR)
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 移动临时文件到正式路径 (原子操作)
            shutil.move(temp_path, final_path)
            return final_path
        except Exception as e:
            # 清理临时文件
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
            print(f"[错误] 会话保存失败：{e}")
            return None
