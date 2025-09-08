import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.formatters import TextFormatter
import gradio as gr
from transformers import pipeline

# Use a stable summarization model without forcing torch dtype
text_summary = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")


def extract_video_id(url):
    # Regex to extract the video ID from various YouTube URL formats
    regex = r"(?:youtube\.com\/(?:[^\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None


def chunk_text_by_sentences(text, max_chars=1500):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = []
    current_len = 0
    for sentence in sentences:
        if not sentence:
            continue
        candidate_len = current_len + len(sentence) + (1 if current else 0)
        if candidate_len <= max_chars:
            current.append(sentence)
            current_len = candidate_len
        else:
            if current:
                chunks.append(" ".join(current))
            if len(sentence) > max_chars:
                for i in range(0, len(sentence), max_chars):
                    chunks.append(sentence[i:i + max_chars])
                current = []
                current_len = 0
            else:
                current = [sentence]
                current_len = len(sentence)
    if current:
        chunks.append(" ".join(current))
    return chunks


def summarize_long_text(text):
    chunks = chunk_text_by_sentences(text, max_chars=1500)
    partial = []
    for chunk in chunks:
        if not chunk.strip():
            continue
        result = text_summary(chunk, max_length=180, min_length=60, do_sample=False)
        partial.append(result[0]['summary_text'])
    if not partial:
        return ""
    combined = " ".join(partial)
    if len(combined) > 1500:
        final = text_summary(combined, max_length=200, min_length=80, do_sample=False)
        return final[0]['summary_text']
    return combined


def get_youtube_transcript(video_url):
    video_id = extract_video_id(video_url)
    if not video_id:
        return "❌ Video ID could not be extracted. Please check the URL."

    try:
        # Prefer English transcripts; include auto-generated if needed
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        except NoTranscriptFound:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en-US', 'en-GB'])

        formatter = TextFormatter()
        text_transcript = formatter.format_transcript(transcript).strip()
        if not text_transcript:
            return "❌ Transcript is empty."

        summary_text = summarize_long_text(text_transcript)
        return summary_text if summary_text else "❌ Could not produce a summary."
    except TranscriptsDisabled:
        return "❌ Transcripts are disabled for this video."
    except NoTranscriptFound:
        return "❌ No English transcript found for this video."
    except Exception as e:
        return f"❌ An error occurred: {e}"


gr.close_all()

demo = gr.Interface(
    fn=get_youtube_transcript,
    inputs=[gr.Textbox(label="YouTube URL", lines=1, placeholder="Paste YouTube video link...")],
    outputs=[gr.Textbox(label="Summarized text", lines=8)],
    title="YouTube Script Summarizer",
    description="Enter a YouTube URL to fetch its transcript and get a concise summary."
)

demo.launch()