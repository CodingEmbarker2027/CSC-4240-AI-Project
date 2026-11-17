from pathlib import Path
from docx import Document

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

def main():
    resume_dir = Path("data/raw_resumes")

    for file_path in resume_dir.glob("*.docx"):
        text = extract_docx_text(file_path)

        print(f"\n--- {file_path.name} ---\n")
        print(text[:500])

if __name__ == "__main__":
    main()