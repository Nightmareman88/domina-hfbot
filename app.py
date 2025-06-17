
import threading
import gradio as gr
from telegram_bot import run_bot

threading.Thread(target=run_bot, daemon=True).start()

def ping(text):
    return f"Госпожа слышит: {text}"

demo = gr.Interface(
    fn=ping,
    inputs="text",
    outputs="text",
    title="DominaBot • health‑check",
    description="Бот‑госпожа слушает тебя… будь осторожен.",
    theme=gr.themes.Monochrome(),
)

if __name__ == "__main__":
    demo.launch()
