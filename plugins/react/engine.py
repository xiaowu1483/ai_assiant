# plugins/react/engine.py
import re
import logging

logger = logging.getLogger(__name__)

class ReActEngine:
    MAX_ITERATIONS = 3
    
    def __init__(self, llm_adapter, tools=None):
        self.llm = llm_adapter
        self.tools = tools or []
        self.tool_map = {t['name']: t['func'] for t in self.tools}
    
    def register_tool(self, name, description, func):
        self.tools.append({'name': name, 'description': description, 'func': func})
        self.tool_map[name] = func
    
    def get_tools_prompt(self):
        if not self.tools:
            return ""
        prompt = "\n\n可用工具：\n"
        for tool in self.tools:
            prompt += f"- {tool['name']}: {tool['description']}\n"
        prompt += "\n使用格式：Action: 工具名 [参数]\n"
        return prompt
    
    def parse_action(self, text):
        pattern = r'Action:\s*(\w+)\s*(?:\[(.*?)\])?'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return {'tool': match.group(1), 'args': match.group(2) or ''}
        return None
    
    def execute_tool(self, tool_name, args):
        if tool_name not in self.tool_map:
            return f"错误：未知工具 '{tool_name}'"
        try:
            return str(self.tool_map[tool_name](args))
        except Exception as e:
            return f"工具错误：{e}"
    
    def run(self, user_input, system_prompt="", context=None):  # ✅ 添加 context 参数
        """
        执行 ReAct 推理
        :param context: 对话历史列表 [{"role": "...", "content": "..."}]
        """
        messages = [
            {"role": "system", "content": system_prompt + self.get_tools_prompt()}
        ]
        
        # ✅ 添加对话历史
        if context:
            messages.extend(context[-10:])  # 只保留最近 10 条
        
        messages.append({"role": "user", "content": user_input})
        
        for i in range(self.MAX_ITERATIONS):
            response = self.llm.chat(messages, max_tokens=800)
            
            action = self.parse_action(response)
            
            if action:
                observation = self.execute_tool(action['tool'], action['args'])
                
                messages.append({"role": "assistant", "content": response})
                messages.append({
                    "role": "user",
                    "content": f"Observation: {observation}\n请给出最终答案。"
                })
                
                if "Final Answer" in response or "最终答案" in response:
                    return self._extract_answer(response)
            else:
                return response
        
        return response
    
    def _extract_answer(self, text):
        patterns = [r'Final Answer:\s*(.*)', r'最终答案:\s*(.*)']
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return text.strip()
