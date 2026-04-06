# plugins/react_plugin.py
from plugins.plugin_base import PluginBase
from plugins.react.engine import ReActEngine
from plugins.react.tools import DEFAULT_TOOLS

class ReactPlugin(PluginBase):
    """ReAct 推理插件"""
    
    # 配置
    ENABLED = True
    MAX_ITERATIONS = 5
    
    def __init__(self, event_bus):
        self.engine = None
        super().__init__(event_bus)
    
    def register_events(self):
        # 监听系统初始化完成
        self.event_bus.subscribe('system.ready', self._init_engine)
        # 监听消息发送前
        self.event_bus.subscribe('message.before_send', self._process_request)
    
    def name(self) -> str:
        return "ReAct_Framework"
    
    def _init_engine(self, data: dict):
        """初始化 ReAct 引擎"""
        if not self.ENABLED:
            return
        
        llm_adapter = data.get('llm_adapter')
        if llm_adapter:
            self.engine = ReActEngine(
                llm_adapter=llm_adapter,
                tools=DEFAULT_TOOLS
            )
            # 可注册更多工具
            # self.engine.register_tool('...', '...', func)
    
    def _process_request(self, data: dict):
        """处理请求，使用 ReAct 推理"""
        if not self.ENABLED or not self.engine:
            return
        
        messages = data.get('messages', [])
        user_input = None
        
        # 提取用户最后一条消息
        for msg in reversed(messages):
            if msg['role'] == 'user':
                user_input = msg['content']
                break
        
        if user_input:
            # 执行 ReAct 推理
            result = self.engine.run(user_input)
            
            # 将结果注入到系统（需要与 chat.py 配合）
            print(f"\n[ReAct] 思考轮数：{result['iterations']}")
            print(f"[ReAct] 思考过程：{result['thought'][:200]}...")
            
            # 可以在这里修改 messages 或存储结果
            data['react_result'] = result
