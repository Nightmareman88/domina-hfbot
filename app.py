import os
import requests
from flask import Flask, request
import gradio as gr

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.1")

# Telegram API endpoint
URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

def query_model(prompt):
    response = requests.post(
        f"https://api-inference.huggingface.co/models/{HF_MODEL}",
        headers={"Authorization": f"Bearer {HF_API_TOKEN}"},
        json={"inputs": prompt},
    )
    return response.json()[0]["generated_text"] if isinstance(response.json(), list) else "..."

def generate_image(prompt):
    response = requests.post(
        "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2",
        headers={"Authorization": f"Bearer {HF_API_TOKEN}"},
        json={"inputs": prompt},
    )
    return response.content

def handle_message(data):
    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if any(word in text.lower() for word in ["покажи", "нарисуй", "изображение", "картина", "картинка"]):
        image = generate_image(text)
        files = {"photo": ("image.png", image)}
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
            data={"chat_id": chat_id},
            files=files,
        )
    else:
        response_text = query_model("Ты — строгая госпожа. Ответь на это как госпожа: " + text)
        requests.post(URL, json={"chat_id": chat_id, "text": response_text})

app = Flask(__name__)

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    handle_message(data)
    return {"ok": True}

def launch_bot():
    return "Госпожа готова к приёму..."

demo = gr.Interface(fn=launch_bot, inputs=[], outputs="text")

if __name__ == "__main__":
    app.run()
