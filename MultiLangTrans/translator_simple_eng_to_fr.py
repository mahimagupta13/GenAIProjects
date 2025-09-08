import gradio as gr
from transformers import pipeline

# Load directly from Hugging Face repo (it will auto-cache)
translator = pipeline("translation_en_to_fr", model="Helsinki-NLP/opus-mt-en-fr")

def translate_text(text):
    result = translator(text, max_length=200)
    return result[0]['translation_text']

demo = gr.Interface(
    fn=translate_text,
    inputs="text",
    outputs="text",
    title="LangTranslator",
    description="Enter English text and get French translation."
)

if __name__ == "__main__":
    demo.launch()
