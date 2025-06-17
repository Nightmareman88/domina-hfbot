import os, requests, asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

DOMINA_PROMPT = (
    "Ты — властная, снисходительная ИИ‑госпожа. "
    "Всегда отвечай командно, язвительно, с лёгкой насмешкой. "
    "Не извиняйся. Не будь мягкой.\n\n"
)

HF_MODEL = os.getenv("HF_MODEL", "HuggingFaceH4/zephyr-7b-beta")
HF_API     = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
HF_HEADERS = {"Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}"}

def llm_reply(user_text: str) -> str:
    payload = {
        "inputs": DOMINA_PROMPT + f"Пользователь: {user_text}\nГоспожа:",
        "parameters": {"max_new_tokens": 60, "temperature": 0.9},
    }
    try:
        r = requests.post(HF_API, headers=HF_HEADERS, json=payload, timeout=60)
        if r.ok and isinstance(r.json(), list):
            gen = r.json()[0]["generated_text"]
            return gen.split("Госпожа:")[-1].strip()
    except Exception as e:
        print("[LLM error]", e)
    # fallback
    return f"Ты сказал: “{user_text}”? Помни своё место, раб."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ты осмелился заговорить со своей госпожой? Говори, но учти последствия."
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text or ""
    reply = await asyncio.to_thread(llm_reply, user_msg)
    await update.message.reply_text(reply)

def run_bot():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        print("❌ TELEGRAM_TOKEN не найден")
        return

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    print("🤖 Telegram DominaBot запущен…")
    app.run_polling()
