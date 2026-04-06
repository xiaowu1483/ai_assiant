# 记忆处理器 (实现四个阶段的核心逻辑)
import os
import json
import re
from datetime import datetime
from .config import (
    MEMORY_INDEX_PATH, MEMORY_CONTENTS_DIR, 
    SESSIONS_DIR, STAGING_DIR, MAX_INDEX_LINES
)
from .utils import (
    count_lines, parse_relative_date, 
    ensure_directory, read_file_safe, write_file_safe
)

class MemoryProcessor:
    def __init__(self, llm_client=None):
        """
        :param llm_client: 封装好的 OpenAI 客户端，用于智能整合和摘要
        """
        self.llm = llm_client
        ensure_directory(MEMORY_CONTENTS_DIR)
        ensure_directory(STAGING_DIR)
        ensure_directory(SESSIONS_DIR)

    # ================= 第一阶段：定向 (Orientation) =================
    def load_memory_map(self):
        """
        助手启动时调用。读取 MEMORY.md 构建记忆地图。
        返回索引内容，供 System Prompt 使用。
        """
        if not os.path.exists(MEMORY_INDEX_PATH):
            self._create_default_index()
            return ""
        
        content = read_file_safe(MEMORY_INDEX_PATH)
        # 这里可以加一个检查，如果文件损坏则重建
        return content

    def _create_default_index(self):
        """初始化默认的索引文件"""
        header = "# 记忆索引 (Memory Index)\n> 最后更新：{} | 总行数：0/{}\n\n| 类别 | 文件路径 | 内容摘要 | 最后更新 | 权重 |\n| :--- | :--- | :--- | :--- | :--- |\n".format(
            datetime.now().strftime("%Y-%m-%d %H:%M"), MAX_INDEX_LINES
        )
        write_file_safe(MEMORY_INDEX_PATH, header)

    # ================= 第二阶段：信号收集 (Signal Collection) =================
    def collect_signals(self, session_files=None):
        """
        扫描 sessions 目录，提取高价值信息。
        :param session_files: 可选，指定要扫描的文件列表，默认扫描最近 3 个
        """
        if not session_files:
            # 获取最近 3 个会话文件
            all_files = sorted(os.listdir(SESSIONS_DIR), reverse=True)
            session_files = all_files[:3] if len(all_files) > 3 else all_files

        signals = []
        keywords = ["记住", "记住这个", "偏好", "纠正", "注意", "重要", "决定", "不要","喜欢", "不喜欢",
        "习惯", "常用", "总是", "从不"]
        
        for fname in session_files:
            fpath = os.path.join(SESSIONS_DIR, fname)
            if not fname.endswith('.json'): continue
            
            data = json.loads(read_file_safe(fpath))
            messages = data.get("messages", [])
            
            for msg in messages:
                if msg["role"] == "user":
                    content = msg["content"]
                    # 简单模式匹配：包含关键词且长度适中
                    if any(k in content for k in keywords) and len(content) > 5:
                        signals.append({
                            "source_file": fname,
                            "content": content,
                            "timestamp": data.get("date", datetime.now().strftime("%Y-%m-%d"))
                        })
        
        # 将收集到的信号存入临时区
        signal_text = "\n".join([f"- [{s['timestamp']}] {s['content']}" for s in signals])
        write_file_safe(os.path.join(STAGING_DIR, "new_signals.md"), signal_text)
        return signals

    # ... (保留 __init__, load_memory_map, collect_signals 不变) ...

    # ================= 第三阶段：整合 (Integration) - 增强版 =================
    def integrate_signals(self, signals):
        """
        使用 LLM 辅助整合，处理矛盾和去重
        """
        if not signals:
            return

        from .prompts import SYSTEM_INTEGRATION
        from .validator import MemoryValidator
        
        # 1. 准备上下文
        # 读取相关类别的现有记忆 (此处简化为读取所有，实际可按类别路由)
        existing_memory = ""
        for fname in os.listdir(MEMORY_CONTENTS_DIR):
            if fname.endswith('.md'):
                existing_memory += read_file_safe(os.path.join(MEMORY_CONTENTS_DIR, fname))

        new_signals_text = "\n".join([f"- {s['content']}" for s in signals])

        # 2. 调用 LLM 进行智能整合
        # 注意：这里需要你的 llm_client 支持 chat  completions
        prompt = SYSTEM_INTEGRATION.format(existing_memory=existing_memory[:2000], new_signals=new_signals_text)
        
        try:
            # 假设 llm_client 有一个 generate 方法
            integrated_content = self.llm.generate(prompt, max_tokens=1000)
            
            # 3. 验证与写入
            # 简单解析 LLM 返回的内容，确保包含日期和来源
            lines = integrated_content.split('\n')
            for line in lines:
                if line.strip().startswith('-'):
                    # 验证日期格式 (简单检查)
                    if not re.search(r'\d{4}-\d{2}-\d{2}', line):
                        # 如果 LLM 忘了加日期，补上今天
                        line = f"- [{datetime.now().strftime('%Y-%m-%d')}] {line}"
                    
                    # 验证来源
                    if "(来源：" not in line:
                        line += f" (来源：Signal_Batch_{datetime.now().strftime('%Y%m%d')})"

                    # 写入对应文件 (此处简化为写入默认文件，实际应解析类别)
                    # 为了安全，我们追加到 05_history.md 或根据关键词路由
                    target = os.path.join(MEMORY_CONTENTS_DIR, "05_history.md")
                    with open(target, 'a', encoding='utf-8') as f:
                        f.write(MemoryValidator.clean_content(line) + "\n")
                        
        except Exception as e:
            print(f"[错误] 整合失败：{e}")
            # 降级策略：直接写入原始信号
            self._fallback_integrate(signals)

    def _fallback_integrate(self, signals):
        """当 LLM 不可用时的降级整合策略"""
        for s in signals:
            target = os.path.join(MEMORY_CONTENTS_DIR, "05_history.md")
            entry = f"- [{datetime.now().strftime('%Y-%m-%d')}] {s['content']} (来源：{s['source_file']})\n"
            with open(target, 'a', encoding='utf-8') as f:
                f.write(entry)

    # ================= 第四阶段：修剪与索引 (Pruning & Indexing) - 增强版 =================
    def update_index(self):
        """
        使用 LLM 辅助摘要，确保索引不超过 200 行且信息密度高
        """
        from .prompts import SYSTEM_PRUNING
        from .utils import count_lines

        # 1. 生成原始索引行
        index_rows = []
        contents_files = sorted(os.listdir(MEMORY_CONTENTS_DIR))
        
        for fname in contents_files:
            if not fname.endswith('.md'): continue
            fpath = os.path.join(MEMORY_CONTENTS_DIR, fname)
            # 读取文件头部作为摘要
            with open(fpath, 'r', encoding='utf-8') as f:
                summary = f.read(200).replace('\n', ' ')
            row = f"| {fname} | contents/{fname} | {summary}... | {datetime.now().strftime('%Y-%m-%d')} | High |"
            index_rows.append(row)

        # 2. 构建临时索引内容
        header = "# 记忆索引 (Memory Index)\n> 最后更新：{} | 总行数：{}/{}\n\n| 类别 | 文件路径 | 内容摘要 | 最后更新 | 权重 |\n| :--- | :--- | :--- | :--- | :--- |\n".format(
            datetime.now().strftime("%Y-%m-%d %H:%M"), len(index_rows), MAX_INDEX_LINES
        )
        temp_content = header + "\n".join(index_rows)

        # 3. 检查行数并修剪
        if count_lines(MEMORY_INDEX_PATH) + len(index_rows) > MAX_INDEX_LINES:
            print("[警告] 索引即将超限，调用 LLM 进行摘要修剪...")
            try:
                old_index = read_file_safe(MEMORY_INDEX_PATH)
                prompt = SYSTEM_PRUNING.format(current_index=old_index, new_entries="\n".join(index_rows))
                optimized_index = self.llm.generate(prompt, max_tokens=1500)
                temp_content = optimized_index
            except Exception as e:
                print(f"[警告] LLM 修剪失败，使用默认截断策略：{e}")
                # 降级：保留头部和尾部
                lines = temp_content.splitlines()
                temp_content = "\n".join(lines[:10] + lines[-(MAX_INDEX_LINES-15):])

        # 4. 保存
        write_file_safe(MEMORY_INDEX_PATH, temp_content)


    # ================= 全流程调度 =================
    def run_maintenance(self):
        """
        在助手空闲或关闭前调用，执行完整的记忆维护流程。
        """
        print(">>> 开始记忆维护...")
        signals = self.collect_signals()
        if signals:
            print(f">>> 收集到 {len(signals)} 条信号")
            self.integrate_signals(signals)
            print(">>> 信号整合完成")
        else:
            print(">>> 无新信号")
        
        self.update_index()
        print(">>> 索引更新完成")
        print(">>> 记忆维护结束")
    # ... (保留原有的 __init__, load_memory_map 等方法) ...

    # ================= 会话结束触发器 (Session End Trigger) =================
    def on_session_end(self, messages, session_id=None, blocking=True):
        """
        会话结束时的统一入口。
        1. 保存会话文件 (原子操作)
        2. 触发记忆维护流程 (收集->整合->索引)
        
        :param messages: 当前会话的所有消息列表
        :param session_id: 会话 ID
        :param blocking: 是否阻塞等待完成 (建议 True 以确保数据保存)
        """
        from .saver import SessionSaver
        
        print(">>> 会话结束，开始持久化记忆...")
        
        # 1. 保存会话
        saved_path = SessionSaver.save_session(messages, session_id)
        if not saved_path:
            print("[警告] 会话文件保存失败，跳过记忆更新")
            return False
        
        # 2. 触发维护
        try:
            if blocking:
                # 阻塞模式：确保应用关闭前完成所有写入
                self.run_maintenance()
            else:
                # 非阻塞模式：适合后台线程运行
                import threading
                t = threading.Thread(target=self.run_maintenance)
                t.start()
            
            return True
        except Exception as e:
            print(f"[错误] 记忆维护流程异常：{e}")
            return False

