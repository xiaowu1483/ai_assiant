# core/chat.py
import logging
from interfaces.llm_adapter import ILLMAdapter
from interfaces.memory_backend import IMemoryBackend
from interfaces.event_bus import EventBus

logger = logging.getLogger(__name__)

class ChatSession:
    def __init__(self, llm_adapter: ILLMAdapter, memory_backend: IMemoryBackend, event_bus: EventBus):
        """
        依赖注入：通过接口传入，不关心具体实现
        """
        self.engine = llm_adapter
        self.memory = memory_backend
        self.event_bus = event_bus
        self.history = []
        self.system_prompt = ""
        self.is_active = False

    def start(self):
        logger.info(">>> 会话启动")
        try:
            memory_map = self.memory.load_memory_map()
            self.system_prompt = f"""
            你是一个运行在手机上的 AI 助手。
            以下是你的记忆地图，请参考这些信息回答用户问题，不要编造不存在的信息：
            {memory_map}
            
            如果用户询问的内容不在记忆中，请诚实回答不知道，不要幻觉。
            """
            self.is_active = True
            self.history = []
            logger.info(">>> 记忆地图加载成功")
        except Exception as e:
            logger.error(f"启动失败：{e}")
            self.system_prompt = "你是一个有帮助的助手。"

    def send_message(self, user_input):
        if not self.is_active:
            return "会话未启动或已结束。"
        
        self.history.append({"role": "user", "content": user_input})
        messages = [{"role": "system", "content": self.system_prompt}] + self.history
        
        try:
            logger.info(f"用户：{user_input}")
            response = self.engine.chat(messages)
            #logger.info(f"助手：{response}")
            self.history.append({"role": "assistant", "content": response})
            return response
        except Exception as e:
            logger.error(f"对话失败：{e}")
            return "抱歉，网络连接出现问题，请稍后重试。"

    def end(self):
        if not self.is_active:
            return
        
        logger.info(">>> 会话结束，发布事件...")
        # 通过事件总线通知其他模块，不直接调用
        self.event_bus.publish('session.end', {
            'messages': self.history,
            'session_id': None
        })
        self.is_active = False
