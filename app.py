
import gradio as gr

def domina_response(message):
    if not message:
        return "Говори, раб. Я слушаю."
    return f"Ты осмелился сказать: “{message}”? Помни своё место."

with gr.Blocks(theme=gr.themes.Monochrome()) as demo:
    gr.Markdown("## 😈 Госпожа‑бот")
    inp = gr.Textbox(label="Скажи что‑нибудь")
    out = gr.Textbox(label="Ответ госпожи")
    btn = gr.Button("Подчиниться")
    btn.click(domina_response, inputs=inp, outputs=out)

if __name__ == "__main__":
    demo.launch()
