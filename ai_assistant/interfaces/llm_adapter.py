# interfaces/llm_adapter.py
from abc import ABC, abstractmethod

class ILLMAdapter(ABC):
    """LLM 适配器接口 - 任何 LLM 服务都实现这个接口"""
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 1000, system_prompt: str = None) -> str:
        pass
    
    @abstractmethod
    def chat(self, messages: list, max_tokens: int = 1000) -> str:
        pass
