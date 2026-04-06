# plugins/context_manager.py
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class ContextManager:
    """
    上下文管理器
    - 保留最近 N 条完整对话
    - 超过阈值后，将旧对话摘要存入记忆
    """
    
    # 配置参数
    MAX_MESSAGES = 10          # 保留最近 10 条消息（5 轮对话）
    SUMMARY_TRIGGER = 8        # 达到 8 条时触发摘要
    SUMMARY_BATCH = 4          # 每次摘要 4 条消息
    
    def __init__(self, llm_adapter, memory_backend=None):
        self.llm = llm_adapter
        self.memory = memory_backend
        self.message_buffer = []  # 消息缓冲区
    
    def add_message(self, role: str, content: str):
        """添加消息到缓冲区"""
        self.message_buffer.append({
            "role": role,
            "content": content
        })
        
        # 检查是否需要摘要
        if len(self.message_buffer) >= self.SUMMARY_TRIGGER:
            self._summarize_old_messages()
    
    def get_context(self) -> List[Dict]:
        """获取当前上下文（供 ReAct 引擎使用）"""
        return self.message_buffer[-self.MAX_MESSAGES:]
    
    def _summarize_old_messages(self):
        """摘要旧消息"""
        if len(self.message_buffer) < self.SUMMARY_TRIGGER:
            return
        
        # 提取要摘要的消息（最早的几条）
        messages_to_summarize = self.message_buffer[:self.SUMMARY_BATCH]
        
        # 生成摘要
        summary = self._generate_summary(messages_to_summarize)
        
        # 存入记忆模块
        if self.memory:
            self._save_to_memory(summary)
        
        # 删除已摘要的消息，保留一条摘要记录
        self.message_buffer = self.message_buffer[self.SUMMARY_BATCH:]
        self.message_buffer.insert(0, {
            "role": "system",
            "content": f"[对话摘要] {summary}"
        })
        
        logger.info(f"[上下文] 已摘要 {self.SUMMARY_BATCH} 条消息，当前保留 {len(self.message_buffer)} 条")
    
    def _generate_summary(self, messages: List[Dict]) -> str:
        """调用 LLM 生成摘要"""
        try:
            # 构建摘要 Prompt
            conversation_text = "\n".join([
                f"{m['role']}: {m['content']}" for m in messages
            ])
            
            prompt = f"""
请简要总结以下对话的核心内容，提取关键信息和决策：

{conversation_text}

摘要要求：
1. 简洁明了，50 字以内
2. 提取用户偏好、重要决策、关键事实
3. 忽略寒暄和无关内容

摘要：
"""
            response = self.llm.generate(prompt, max_tokens=200)
            return response.strip()
        except Exception as e:
            logger.error(f"摘要生成失败：{e}")
            return "对话已摘要（生成失败）"
    
    def _save_to_memory(self, summary: str):
        """将摘要存入记忆模块"""
        try:
            # 写入记忆文件（追加到 history）
            from memory.config import MEMORY_CONTENTS_DIR
            import os
            from datetime import datetime
            
            history_file = os.path.join(MEMORY_CONTENTS_DIR, "05_history.md")
            
            entry = f"- [{datetime.now().strftime('%Y-%m-%d')}] [对话摘要] {summary}\n"
            
            with open(history_file, 'a', encoding='utf-8') as f:
                f.write(entry)
            
            logger.info(f"[记忆] 摘要已存入：{summary[:50]}...")
        except Exception as e:
            logger.error(f"记忆保存失败：{e}")
    
    def clear(self):
        """清空上下文"""
        self.message_buffer = []
        logger.info("[上下文] 已清空")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "total_messages": len(self.message_buffer),
            "max_messages": self.MAX_MESSAGES,
            "summary_trigger": self.SUMMARY_TRIGGER
        }
