# core/engine.py
import openai
import time
import logging
from interfaces.llm_adapter import ILLMAdapter
from utils.config_loader import get_config

logger = logging.getLogger(__name__)

class LLMAdapter(ILLMAdapter):
    """OpenAI/DashScope 适配器 - 实现 ILLMAdapter 接口"""
    
    def __init__(self):
        config = get_config()
        self.api_key = config.get('openai', {}).get('api_key')
        self.model = config.get('openai', {}).get('model', 'qwen-plus')
        self.base_url = config.get('openai', {}).get('base_url', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
        
        if not self.api_key:
            raise ValueError("[错误] 未找到 API Key，请检查 config.yaml")
        
        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
        logger.info(f">>> 引擎初始化完成，模型：{self.model}")

    def generate(self, prompt: str, max_tokens: int = 1000, system_prompt: str = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return self._chat_completion(messages, max_tokens)

    def chat(self, messages: list, max_tokens: int = 1000) -> str:
        return self._chat_completion(messages, max_tokens)

    def _chat_completion(self, messages: list, max_tokens: int) -> str:
        retries = 3
        for i in range(retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model, messages=messages, max_tokens=max_tokens, temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.warning(f"API 请求失败 (尝试 {i+1}/{retries}): {e}")
                if i == retries - 1:
                    raise e
                time.sleep(2 ** i)
        return ""
