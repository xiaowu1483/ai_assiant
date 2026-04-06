# main_gradio.py
import gradio as gr
from interfaces.event_bus import EventBus
from core.engine import LLMAdapter
from core.chat import ChatSession
from memory.hooks import MemoryBackend

# 全局变量
session = None
is_initialized = False

def init_system():
    global session, is_initialized
    try:
        event_bus = EventBus()
        llm_adapter = LLMAdapter()
        memory_backend = MemoryBackend(llm_adapter=llm_adapter, event_bus=event_bus)
        session = ChatSession(
            llm_adapter=llm_adapter,
            memory_backend=memory_backend,
            event_bus=event_bus
        )
        session.start()
        is_initialized = True
        return "✅ 助手已就绪"
    except Exception as e:
        return f"❌ 初始化失败：{e}"

def chat(message, history):
    if not is_initialized:
        return "⏳ 助手正在初始化，请稍等..."
    if not message:
        return "请输入消息"
    try:
        response = session.send_message(message)
        return response
    except Exception as e:
        return f"❌ 错误：{e}"

def clear_session(history):
    global session
    if session:
        session.end()
        session.start()
    return "✅ 会话已清空", []

# 创建界面
with gr.Blocks(title="AI 助手", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 AI 助手")
    
    chatbot = gr.Chatbot(label="对话", height=400)
    msg = gr.Textbox(placeholder="输入消息...", label="消息", container=False)
    
    with gr.Row():
        send_btn = gr.Button("发送", variant="primary")
        clear_btn = gr.Button("清空会话", variant="secondary")
    
    status = gr.Textbox(label="状态", value="正在初始化...", interactive=False)
    
    # 初始化
    def init():
        return init_system()
    demo.load(init, outputs=[status])
    
    # 绑定事件
    send_btn.click(chat, inputs=[msg, chatbot], outputs=[msg])
    msg.submit(chat, inputs=[msg, chatbot], outputs=[msg])
    clear_btn.click(clear_session, inputs=[chatbot], outputs=[status, chatbot])

if __name__ == "__main__":
    print(">>> 启动 Gradio 界面...")
    print(">>> 本地访问：http://127.0.0.1:7860")
    print(">>> 手机访问：http://你的 IP:7860")
    demo.launch(server_name="0.0.0.0", server_port=7860)
