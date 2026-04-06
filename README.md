🤖 手机 AI 助手
基于 Python 的个人 AI 助手，支持记忆管理、ReAct 推理、上下文自动摘要，可部署到手机或云服务器。

✨ 核心特性
特性	说明
🧠 长期记忆	自动保存用户偏好、重要决策，重启后不丢失

🔍 ReAct 推理	思考→行动→观察，支持工具调用，减少幻觉

📝 上下文管理	对话过长自动摘要，保留最近内容

🔌 插件架构	新增功能无需修改核心代码

📁 项目结构
mobile_ai_assistant/

├── main.py                    # 命令行入口

├── main_gradio.py                # Web 入口

├── config.yaml                # 配置文件

├── requirements.txt           # 依赖

│

├── core/                      # 核心对话模块

│   ├── engine.py              # LLM 适配器

│   └── chat.py                # 会话管理

│

├── memory/                    # 记忆模块

│   ├── processor.py           # 记忆处理（4 阶段）

│   ├── saver.py               # 会话保存

│   └── contents/              # 记忆内容

│

├── plugins/                   # 插件模块

│   ├── react/                 # ReAct 推理

│   ├── context_manager.py     # 上下文管理

│   └── plugin_base.py         # 插件基类

│

├── interfaces/                # 接口定义

├── utils/                     # 工具函数

└── logs/                      # 日志目录

🚀 快速开始
1. 安装依赖
pip install -r requirements.txt
2. 配置 API Key
编辑 config.yaml：

openai:
  api_key: "你的 API Key"
  model: "qwen-plus"
  base_url: "url"
3. 运行
# 命令行模式
python main.py

# 网页 模式
python main_gradio.py


⚙️ 配置调优
config.yaml

openai:

  model: "model-name"        # 模型选择
  
  temperature: 0.5         # 创造性 (0-1)
  
  max_tokens: 1000         # 最大输出

memory:

  max_index_lines: 200     # 索引最大行数
  
  auto_maintenance: true   # 自动维护
  
plugins/react/engine.py

MAX_ITERATIONS = 3         # 推理轮数 (1-5)

plugins/context_manager.py

MAX_MESSAGES = 10          # 上下文长度

SUMMARY_TRIGGER = 8        # 摘要触发

🔌 添加插件

1. 创建插件
# plugins/my_plugin.py

  from plugins.plugin_base import PluginBase

  class MyPlugin(PluginBase):

    def register_events(self):
    
        self.event_bus.subscribe('message.received', self._on_message)
    
    def name(self) -> str:
    
        return "MyPlugin"
    
    def _on_message(self, data):
    
        print(f"收到消息：{data}")
2. 注册插件
# main.py

from plugins.my_plugin import MyPlugin

MyPlugin(event_bus)

无需修改核心代码
