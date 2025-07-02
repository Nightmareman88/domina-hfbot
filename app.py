
import threading
import gradio as gr
from telegram_bot import run_bot

threading.Thread(target=run_bot, daemon=True).start()

def ping(msg): return f"Госпожа слышит: {msg}"

gr.Interface(fn=ping, inputs="text", outputs="text",
             title="DominaBot v2",
             description="NSFW Telegram Госпожа с памятью и генерацией изображений",
             theme=gr.themes.Monochrome()).launch()
