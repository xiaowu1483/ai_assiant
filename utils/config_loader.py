#  安全加载根目录的 config.yaml 文件。
import os
import yaml

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')

def get_config():
    if not os.path.exists(CONFIG_PATH):
        # 如果配置文件不存在，返回空字典或抛出错误
        # 为了健壮性，这里返回空字典，但会在 engine 中报错提醒
        return {}
    
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"[错误] 配置文件加载失败：{e}")
        return {}
