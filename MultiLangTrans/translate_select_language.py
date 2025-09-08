import gradio as gr
from transformers import pipeline

# Define available language pairs (extendable)
LANGUAGE_CODES = {
    "English": "en",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    "Hindi": "hi",
}

# Cache translators so models don’t reload every time
translator_cache = {}

def get_translator(src_lang, tgt_lang):
    model_name = f"Helsinki-NLP/opus-mt-{src_lang}-{tgt_lang}"
    if model_name not in translator_cache:
        translator_cache[model_name] = pipeline("translation", model=model_name)
    return translator_cache[model_name]

def translate_text(text, src_lang, tgt_lang):
    if src_lang == tgt_lang:
        return text  # No need to translate
    try:
        translator = get_translator(src_lang, tgt_lang)
        result = translator(text, max_length=200)
        return result[0]['translation_text']
    except Exception as e:
        return f"❌ Error: {str(e)}"

with gr.Blocks() as demo:
    gr.Markdown("## 🌍 Multi-Language Translator")

    with gr.Row():
        src_dropdown = gr.Dropdown(choices=list(LANGUAGE_CODES.keys()), value="English", label="Source Language")
        tgt_dropdown = gr.Dropdown(choices=list(LANGUAGE_CODES.keys()), value="French", label="Target Language")

    input_text = gr.Textbox(label="Enter text")
    output_text = gr.Textbox(label="Translated text")

    translate_btn = gr.Button("Translate")

    translate_btn.click(
        fn=lambda text, src, tgt: translate_text(text, LANGUAGE_CODES[src], LANGUAGE_CODES[tgt]),
        inputs=[input_text, src_dropdown, tgt_dropdown],
        outputs=output_text,
    )

if __name__ == "__main__":
    demo.launch()
