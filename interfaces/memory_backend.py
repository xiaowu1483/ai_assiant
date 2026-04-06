# interfaces/memory_backend.py
from abc import ABC, abstractmethod

class IMemoryBackend(ABC):
    """记忆后端接口 - 任何记忆系统都实现这个接口"""
    
    @abstractmethod
    def load_memory_map(self) -> str:
        """加载记忆地图"""
        pass
    
    @abstractmethod
    def on_session_end(self, messages: list, session_id: str = None) -> bool:
        """会话结束时调用"""
        pass
    
    @abstractmethod
    def on_event(self, event_type: str, data: dict) -> None:
        """响应事件"""
        pass
