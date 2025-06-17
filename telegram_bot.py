
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

DOMINA_NAME = "Госпожа"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Ты осмелился заговорить с {DOMINA_NAME}? Напиши что-нибудь, жалкий.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    response = f"Ты сказал: “{user_msg}”? Помни своё место, раб."
    await update.message.reply_text(response)

def run_bot():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        print("Ошибка: переменная окружения TELEGRAM_TOKEN не найдена.")
        return

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Telegram DominaBot запущен...")
    app.run_polling()
