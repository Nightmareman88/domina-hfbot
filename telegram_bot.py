import os
import asyncio
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, Application,
    CommandHandler, MessageHandler,
    ContextTypes, filters
)

# ── токены и настройки ──────────────────────────────────────────────
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DOMINA_PROMPT = (
    "Ты — властная, снисходительная ИИ‑госпожа. "
    "Всегда отвечай командно, язвительно, с лёгкой насмешкой. "
    "Не извиняйся. Не будь мягкой.\n\n"
)

HF_MODEL   = os.getenv("HF_MODEL", "HuggingFaceH4/zephyr-7b-beta")
HF_API     = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
HF_HEADERS = {"Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}"}

# ── генерация ответа госпожи ────────────────────────────────────────
def llm_reply(user_text: str) -> str:
    prompt = (
        "Ты — строгая, язвительная ИИ-госпожа. "
        "Отвечай жёстко, снисходительно, как будто перед тобой ничтожество.\n\n"
        + user_text
    )

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 150,
            "temperature": 0.95,
            "top_p": 0.95,
            "do_sample": True,
            "repetition_penalty": 1.1,
            "return_full_text": False
        }
    }

    try:
        r = requests.post(HF_API, headers=HF_HEADERS, json=payload, timeout=60)
        if r.ok and isinstance(r.json(), list):
            return r.json()[0]["generated_text"].strip()
    except Exception as e:
        print("[LLM error]", e)

    return f"Ты сказал: “{user_text}”? Помни своё место, раб."


# ── обработчики Telegram ────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ты осмелился заговорить со своей госпожой? Говори, но учти последствия."
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text or ""
    reply = await asyncio.to_thread(llm_reply, user_msg)
    await update.message.reply_text(reply)

# ── запуск бота ─────────────────────────────────────────────────────
def run_bot():
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN не найден.")
        return

    # Явно создаём event loop для нового потока
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("🤖 Telegram DominaBot запущен …")
    app.run_polling(stop_signals=None)

