import ollama
import AI
import pdfplumber
import dictionary as dct
from docx import Document


def list_installed_qwen_models():
    """Return installed Qwen3 model names reported by the local Ollama server."""
    response = ollama.list()
    models = response.get("models", []) if isinstance(response, dict) else getattr(response, "models", [])
    names = []

    for model in models:
        if isinstance(model, dict):
            name = model.get("model") or model.get("name")
        else:
            name = getattr(model, "model", None) or getattr(model, "name", None)

        if name and name.lower().startswith("qwen3"):
            names.append(name)

    return sorted(set(names))

# Extracts text from a PDF file
def extract_pdf_text(file):
    text = ""

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text

# Extracts text from a DOCX or Word file
def extract_docx_text(file):
    doc = Document(file)

    text_parts = []

    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text_parts.append(paragraph.text.strip())

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    text_parts.append(cell.text.strip())

    final_text = "\n".join(text_parts)
    return final_text

# After uploading a resume, retrieve the information that is on the file.
def build_candidate_function(file_path):
    file_name = file_path.name

    if file_name.endswith(".docx"):
        resume_text = extract_docx_text(file_path)
    else:
        resume_text = extract_pdf_text(file_path)

    return {
        "skills": AI.extract_skills_nlp(resume_text),
        "education": AI.extract_education_nlp(resume_text),
        "experience": AI.experience_years_nlp(resume_text),
        "candidate_text": resume_text
    }

# Used for the Ollama model to generate prompts about improvements, skills needed, and
# whether the applicant is worth an interview.
def generate_analysis(prompt, model_name, context_length):
    if not model_name:
        raise ValueError("Choose an installed Qwen3 model before generating a review.")

    response = ollama.chat(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={"num_ctx": context_length},
    )

    return response["message"]["content"]
