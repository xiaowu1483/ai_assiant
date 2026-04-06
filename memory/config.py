import os

# 获取当前文件所在目录 (memory/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)  # 项目根目录

# 路径配置
MEMORY_INDEX_PATH = os.path.join(BASE_DIR, "MEMORY.md")
MEMORY_CONTENTS_DIR = os.path.join(BASE_DIR, "contents")
SESSIONS_DIR = os.path.join(ROOT_DIR, "sessions")
STAGING_DIR = os.path.join(BASE_DIR, "staging")

# 系统限制
MAX_INDEX_LINES = 200  # 索引文件最大行数
DATE_FORMAT = "%Y-%m-%d"
