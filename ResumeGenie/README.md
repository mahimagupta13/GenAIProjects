# ResumeGenie

A small Streamlit app that checks a resume for common sections, action verbs,
measurable results, and (optionally) keyword overlap with a job description.
The scores are heuristic guidance, not a prediction of hiring outcomes or ATS
performance. The app does not send resume content to an external AI service.

## Run locally

Python 3.12 or newer is required.

```powershell
uv sync
uv run streamlit run main.py
```

Alternatively, install the project with pip and run Streamlit:

```powershell
python -m pip install -e .
python -m streamlit run main.py
```

Upload a searchable PDF, DOCX, or TXT resume (up to 10 MB). Paste a job
description to see matching and potentially missing terms. Scanned PDFs need to
be OCR-processed before the app can analyze their text.