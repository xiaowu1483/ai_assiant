# main.py
import sys
import os
import time

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', buffering=1)

print("=== 程序启动 ===", flush=True)

from utils.logger import setup_logger
logger = setup_logger()
# 模块导入
from interfaces.event_bus import EventBus
from core.engine import LLMAdapter
from core.chat import ChatSession
from memory.hooks import MemoryBackend
from plugins.react.engine import ReActEngine
from plugins.react.tools import DEFAULT_TOOLS

from plugins.context_manager import ContextManager

event_bus = None
current_session = None
react_engine = None

def handle_exit(signum, frame):
    logger.info(">>> 退出信号，保存记忆...")
    if current_session:
        current_session.end()
        time.sleep(1)
    sys.exit(0)

def main():
    global event_bus, current_session, react_engine, context_manager
    
    print("=== AI 助手启动 ===", flush=True)
    logger.info("=== AI 助手启动 ===")
    
    # 1. 创建事件总线
    event_bus = EventBus()
    
    # 2. 初始化 LLM
    print(">>> 初始化 LLM...", flush=True)
    llm_adapter = LLMAdapter()
    
    # 3. 初始化记忆
    print(">>> 初始化记忆...", flush=True)
    memory_backend = MemoryBackend(llm_adapter=llm_adapter, event_bus=event_bus)
    
    # 4. 初始化 ReAct 引擎
    print(">>> 初始化 ReAct...", flush=True)
    react_engine = ReActEngine(llm_adapter=llm_adapter, tools=DEFAULT_TOOLS)
    # 可添加新模块
    # 5. 初始化上下文管理器 ✅ 新增
    print(">>> 初始化上下文管理...", flush=True)
    context_manager = ContextManager(llm_adapter=llm_adapter, memory_backend=memory_backend)





    
    # 5. 创建会话
    current_session = ChatSession(
        llm_adapter=llm_adapter,
        memory_backend=memory_backend,
        event_bus=event_bus
    )
    current_session.start()
    
    # 6. 构建 ReAct System Prompt
    memory_map = memory_backend.load_memory_map()
    react_system_prompt = f"""
你是一个专业、准确、简洁的智能助手，使用 ReAct 模式回答问题。

回答原则：
1. 先思考再回答（ReAct 模式）
2. 不确定的内容明确说明
3. 不编造不存在的信息
4. 优先使用记忆中的信息
5. 回答简洁，避免冗余

格式：
Thought: [思考]
Action: [工具名] [参数]
Observation: [工具返回]
Final Answer: [最终答案]

{memory_map}
"""
    
    print("\n--- 助手已就绪 (输入 'exit' 退出) ---", flush=True)
    
    try:
        while True:
            try:
                user_input = input("\n你：").strip()
                if not user_input:
                    continue
                if user_input.lower() in ['exit', 'quit', '退出']:
                    break
                
                # 使用 ReAct 引擎处理，传入上下文 ✅ 修改
                print("\n[思考中...]", flush=True)
                response = react_engine.run(
                    user_input, 
                    system_prompt=react_system_prompt,
                    context=context_manager.get_context()  # ✅ 从上下文管理器获取
                )
                print(f"\n助手：{response}", flush=True)
                
                # 保存到上下文管理器 ✅ 修改
                context_manager.add_message("user", user_input)
                context_manager.add_message("assistant", response)
                
                # 同时保存到 session（用于记忆模块）
                current_session.history.append({"role": "user", "content": user_input})
                current_session.history.append({"role": "assistant", "content": response})

                # 添加命令支持
                if user_input == '/context':
                    stats = context_manager.get_stats()
                    print(f"\n[上下文状态]")
                    print(f"当前消息数：{stats['total_messages']}/{stats['max_messages']}")
                    print(f"摘要触发点：{stats['summary_trigger']}")
                    print(f"最近消息：")
                    for msg in context_manager.get_context()[-4:]:
                        preview = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
                        print(f"  {msg['role']}: {preview}")
                    continue

                
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\n>>> Ctrl+C", flush=True)
                break
                
    except Exception as e:
        logger.error(f"主循环异常：{e}")
        print(f"❌ 错误：{e}", flush=True)
    finally:
        print(">>> 结束会话...", flush=True)
        current_session.end()
        time.sleep(1)
        print("=== 程序结束 ===", flush=True)

if __name__ == "__main__":
    main()
