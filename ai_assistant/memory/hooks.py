# memory/hooks.py
from interfaces.memory_backend import IMemoryBackend
from interfaces.event_bus import EventBus
from .processor import MemoryProcessor

class MemoryBackend(IMemoryBackend):
    """记忆模块 - 实现 IMemoryBackend 接口"""
    
    def __init__(self, llm_adapter, event_bus: EventBus):
        self.processor = MemoryProcessor(llm_client=llm_adapter)
        self.event_bus = event_bus
        self._register_events()
    
    def _register_events(self):
        """注册事件监听"""
        self.event_bus.subscribe('session.end', self._on_session_end)
        self.event_bus.subscribe('memory.update', self._on_memory_update)
    
    def load_memory_map(self) -> str:
        return self.processor.load_memory_map()
    
    def on_session_end(self, messages: list, session_id: str = None) -> bool:
        return self.processor.on_session_end(messages, session_id, blocking=True)
    
    def on_event(self, event_type: str, data: dict) -> None:
        pass  # 通过 _register_events 处理
    
    def _on_session_end(self, data: dict):
        """响应会话结束事件"""
        messages = data.get('messages', [])
        session_id = data.get('session_id')
        self.on_session_end(messages, session_id)
    
    def _on_memory_update(self, data: dict):
        """响应记忆更新事件"""
        pass
