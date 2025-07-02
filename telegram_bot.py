
import os, json, asyncio, requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.1")
HF_IMAGE_MODEL = os.getenv("HF_IMAGE_MODEL", "stabilityai/sdxl")

HF_HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}
LLM_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
IMG_URL = f"https://api-inference.huggingface.co/models/{HF_IMAGE_MODEL}"

MEMORY_FILE = "memory.json"
IMAGE_KEYWORDS = ["нарисуй", "изобрази", "госпожу", "картинка", "latex", "накажи"]

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(mem):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(mem, f, ensure_ascii=False, indent=2)

memory_data = load_memory()

def generate_text(user_id, username, user_input):
    history = memory_data.get(str(user_id), {}).get("memory", [])
    prompt = (
        "Ты — доминирующая, язвительная ИИ‑госпожа. Не будь вежливой. Никогда не извиняйся.\n\n"
        f"История:\n{''.join([f'- {h}\n' for h in history[-5:]])}\n"
        f"Пользователь: {user_input}\nГоспожа:"
    )
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 180,
            "temperature": 0.95,
            "top_p": 0.9,
            "do_sample": True,
            "return_full_text": False
        }
    }
    try:
        r = requests.post(LLM_URL, headers=HF_HEADERS, json=payload, timeout=60)
        if r.ok and isinstance(r.json(), list):
            reply = r.json()[0]["generated_text"].strip()
            if str(user_id) not in memory_data:
                memory_data[str(user_id)] = {"name": username, "memory": []}
            memory_data[str(user_id)]["memory"].append(reply)
            save_memory(memory_data)
            return reply
    except Exception as e:
        print("[LLM error]", e)
    return "Ты не стоишь даже слов."

def generate_image(prompt: str) -> bytes | None:
    payload = {"inputs": prompt}
    try:
        r = requests.post(IMG_URL, headers=HF_HEADERS, json=payload, timeout=90)
        if r.ok:
            return r.content
    except Exception as e:
        print("[IMG error]", e)
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ты снова приполз? Говори, раб.")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text or ""
    user_id = update.effective_user.id
    username = update.effective_user.username or "аноним"

    if any(k in msg.lower() for k in IMAGE_KEYWORDS):
        img = await asyncio.to_thread(generate_image, f"NSFW mistress, {msg}")
        if img:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=img)

    reply = await asyncio.to_thread(generate_text, user_id, username, msg)
    await update.message.reply_text(reply)

def run_bot():
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN не найден")
        return
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    print("🤖 DominaBot v2 запущен…")
    app.run_polling(stop_signals=None)
