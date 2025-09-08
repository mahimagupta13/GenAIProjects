import gradio as gr
from transformers import pipeline
import json

# Load languages from JSON file
with open("languages.json", "r", encoding="utf-8") as f:
    LANGUAGE_CODES = json.load(f)

# Cache translators to avoid reloading
translator_cache = {}

def get_translator(src_lang, tgt_lang):
    """Load or return cached MarianMT translator. Returns None if model not available."""
    model_name = f"Helsinki-NLP/opus-mt-{src_lang}-{tgt_lang}"
    if model_name in translator_cache:
        return translator_cache[model_name]
    try:
        translator_cache[model_name] = pipeline("translation", model=model_name)
        return translator_cache[model_name]
    except Exception:
        return None

def translate_text(text, src_lang, tgt_lang):
    if not text.strip():
        return "⚠️ Please enter some text to translate."
    if src_lang == tgt_lang:
        return text
    translator = get_translator(src_lang, tgt_lang)
    if translator is None:
        return f"❌ Translation model for {src_lang} → {tgt_lang} is not available."
    try:
        result = translator(text, max_length=200)
        return result[0]['translation_text']
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Gradio Interface
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    # Header
    gr.HTML(
        """
        <div style="text-align:center; padding: 25px; background: linear-gradient(90deg, #36D1DC, #5B86E5);
                    border-radius: 15px; color: white;">
            <h1 style="font-size:2.5em;">🌐 Universal Language Translator</h1>
            <p style="font-size:1.2em;">Translate text between <b>100+ languages</b> with open-source Helsinki-NLP models.<br>
            Communicate globally, explore new cultures, and break language barriers! ✨</p>
        </div>
        """
    )

    # Language selectors
    with gr.Row():
        src_dropdown = gr.Dropdown(
            choices=list(LANGUAGE_CODES.keys()), 
            value="English", 
            label="🌐 Source Language"
        )
        tgt_dropdown = gr.Dropdown(
            choices=list(LANGUAGE_CODES.keys()), 
            value="French", 
            label="🎯 Target Language"
        )

    # Text input/output
    input_text = gr.Textbox(
        label="✍️ Enter text to translate",
        placeholder="Type your sentence here...",
        lines=5
    )
    output_text = gr.Textbox(
        label="✅ Translated text",
        interactive=False,
        lines=5
    )

    # Buttons
    with gr.Row():
        translate_btn = gr.Button("🚀 Translate", variant="primary")
        clear_btn = gr.Button("🧹 Clear")

    # Button actions
    translate_btn.click(
        fn=lambda text, src, tgt: translate_text(text, LANGUAGE_CODES[src], LANGUAGE_CODES[tgt]),
        inputs=[input_text, src_dropdown, tgt_dropdown],
        outputs=output_text
    )

    clear_btn.click(
        fn=lambda: ("", ""),
        inputs=[],
        outputs=[input_text, output_text]
    )

if __name__ == "__main__":
    demo.launch()
