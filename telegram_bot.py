
import os
import asyncio
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

DOMINA_PROMPT = (
    "Ты — искусственный интеллект, который играет роль доминирующей, язвительной Госпожи. "
    "Ты не проявляешь сочувствия, отвечаешь с иронией, принижаешь собеседника, "
    "используешь командный и снисходительный тон. "
    "Не извиняйся. Не будь вежливой. Ты — главная. Ответь на следующее:\n\n"
)

HF_MODEL   = os.getenv("HF_MODEL", "HuggingFaceH4/zephyr-7b-beta")
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
HF_HEADERS = {"Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}"}

def llm_reply(user_text: str) -> str:
    prompt = DOMINA_PROMPT + f"{user_text}\n\nОтвет Госпожи:"
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 160,
            "temperature": 1.0,
            "top_p": 0.95,
            "do_sample": True,
            "repetition_penalty": 1.05,
            "return_full_text": False,
        },
    }
    try:
        r = requests.post(HF_API_URL, headers=HF_HEADERS, json=payload, timeout=60)
        if r.ok and isinstance(r.json(), list):
            return r.json()[0]["generated_text"].strip()
    except Exception as e:
        print("[LLM error]", e)
    return f"Ты сказал: “{user_text}”? Помни своё место, раб."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ты осмелился заговорить со своей Госпожой? Говори, но учти последствия."
    )

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text or ""
    reply = await asyncio.to_thread(llm_reply, user_msg)
    await update.message.reply_text(reply)

def run_bot():
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN не найден.")
        return

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))

    print("🤖 Telegram DominaBot запущен …")
    app.run_polling(stop_signals=None)
