import fitz  # PyMuPDF
from app.ai_engine import generate

import fitz  # PyMuPDF
from app.ai_engine import generate

async def extract_and_classify_requirements(file):
    pdf_bytes = await file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = "\n".join([page.get_text() for page in doc])

    output = []
    for line in text.split(". "):
        if not line.strip():
            continue
        prompt = f"Classify the following requirement into SDLC phase: '{line.strip()}'"
        try:
            result = generate(prompt)
            output.append({
                "sentence": line.strip(),
                "phase": result.strip()
            })
        except Exception as e:
            output.append({
                "sentence": line.strip(),
                "phase": "Error",
                "error": str(e)
            })
    return output
