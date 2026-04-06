# interfaces/event_bus.py
from typing import Callable, Dict, List

class EventBus:
    """
    事件总线 - 模块之间通过这个通信，互不直接依赖
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, callback: Callable):
        """订阅事件"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
    
    def publish(self, event_type: str, data: dict = None):
        """发布事件"""
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"[事件处理错误] {event_type}: {e}")
    
    def clear(self):
        """清空所有订阅"""
        self._subscribers.clear()
