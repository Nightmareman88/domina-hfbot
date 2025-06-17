import threading
from telegram_bot import run_bot
import gradio as gr

# ── запускаем Telegram‑бот в фоновом потоке ─────────────────────────
def launch_bot():
    run_bot()          # ⬅︎ важно: без сигнал‑хендлеров

threading.Thread(target=launch_bot, daemon=True).start()

# ── минимальный Gradio UI (health‑check) ────────────────────────────
def ping(txt):     # отвечает госпожой, чтобы было видно в UI
    return f"Ты осмелился сказать: “{txt}”? Помни своё место."

demo = gr.Interface(fn=ping, inputs="text", outputs="text",
                    title="DominaBot — живой",
                    theme=gr.themes.Monochrome())

if __name__ == "__main__":
    demo.launch()          # Gradio поднимет порт 7860
