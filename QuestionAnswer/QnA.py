import gradio as gr
from transformers import pipeline
import PyPDF2
import pandas as pd

# Load Question Answering model
qa_model = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

def read_file(file_obj):
    """Read text from a file object (txt, pdf, or Excel)."""
    if file_obj.name.endswith(".txt"):
        return file_obj.read().decode("utf-8")
    elif file_obj.name.endswith(".pdf"):
        pdf_text = ""
        reader = PyPDF2.PdfReader(file_obj)
        for page in reader.pages:
            pdf_text += page.extract_text()
        return pdf_text
    elif file_obj.name.endswith((".xls", ".xlsx")):
        df = pd.read_excel(file_obj)
        return df.apply(lambda x: ' '.join(x.astype(str)), axis=1).str.cat(sep=' ')
    else:
        return None

def answer_question(user_text, file_obj, question):
    """Answer question from either text input or uploaded file."""
    context = ""
    if file_obj is not None:
        context = read_file(file_obj)
        if context is None:
            return "❌ Unsupported file type! Use .txt, .pdf, or Excel (.xls/.xlsx)."
    elif user_text.strip():
        context = user_text
    else:
        return "⚠️ Please provide either text input or upload a file."

    try:
        result = qa_model(question=question, context=context)
        return result['answer']
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Gradio Interface
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.HTML("""
    <div style="text-align:center; padding: 20px; background: linear-gradient(90deg, #36D1DC, #5B86E5);
                border-radius: 12px; color: white;">
        <h1 style="font-size:2.2em;">❓ Question Answering Bot</h1>
        <p>Ask questions on your text, PDF, or Excel files and get instant answers using a Hugging Face model. ✨</p>
    </div>
    """)

    with gr.Row():
        text_input = gr.Textbox(
            label="Enter text here (optional)",
            placeholder="Type or paste text...",
            lines=6
        )
        file_input = gr.File(
            label="Or upload a file (.txt, .pdf, .xls, .xlsx)",
            file_types=[".txt", ".pdf", ".xls", ".xlsx"]
        )

    question_input = gr.Textbox(
        label="Enter your question",
        placeholder="Type your question here..."
    )

    output_text = gr.Textbox(
        label="Answer",
        interactive=False,
        lines=4
    )

    submit_btn = gr.Button("🟢 Get Answer", variant="primary")

    submit_btn.click(
        fn=answer_question,
        inputs=[text_input, file_input, question_input],
        outputs=output_text
    )

if __name__ == "__main__":
    demo.launch()
