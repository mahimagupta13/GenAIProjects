import gradio as gr
from transformers import pipeline

# Load summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(user_text):
    if not user_text.strip():
        return "⚠️ Please enter some text to summarize."
    try:
        summary = summarizer(user_text, max_length=130, min_length=30, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Gradio Interface
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.HTML(
        """
        <div style="text-align:center; padding: 25px; background: linear-gradient(90deg, #FF7E5F, #FEB47B);
                    border-radius: 15px; color: white;">
            <h1 style="font-size:2.5em;">📝 Text Summarization Chatbot</h1>
            <p style="font-size:1.2em;">Paste any text and get a concise summary instantly.<br>
            Powered by Hugging Face Transformers. ⚡</p>
        </div>
        """
    )

    with gr.Row():
        input_text = gr.Textbox(
            label="✍️ Enter your text here",
            placeholder="Paste your text to summarize...",
            lines=6
        )
    
    output_text = gr.Textbox(
        label="📰 Summary",
        interactive=False,
        lines=4
    )

    summarize_btn = gr.Button("🔹 Summarize", variant="primary")

    summarize_btn.click(
        fn=summarize_text,
        inputs=input_text,
        outputs=output_text
    )

if __name__ == "__main__":
    demo.launch()
