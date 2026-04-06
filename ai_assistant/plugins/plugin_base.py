# plugins/plugin_base.py
from abc import ABC, abstractmethod
from interfaces.event_bus import EventBus

class PluginBase(ABC):
    """所有插件的基类"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.register_events()
    
    @abstractmethod
    def register_events(self):
        """插件在此注册需要监听的事件"""
        pass
    
    @abstractmethod
    def name(self) -> str:
        """插件名称"""
        pass
    
    def cleanup(self):
        """插件清理"""
        pass
