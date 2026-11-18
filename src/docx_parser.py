from pathlib import Path
from docx import Document

def extract_docx_text(file):
    doc = Document(file)

    text_parts = []

    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text_parts.append(paragraph.text.strip())

    # If the resume is formatted similarly to a table, extract the text in this manner.
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    text_parts.append(cell.text.strip())

    final_text = "\n".join(text_parts)
    return final_text

def main():
    # Leaves the current pwd and heads to the data directory, where
    # the raw_resumes directory is located.
    base_dir = Path(__file__).resolve().parent.parent
    # A simple test of one of the resumes
    file_path = (base_dir / "data" / "raw_resumes" / "20.docx")
    text = extract_docx_text(file_path)

    print(f"\n--- {file_path.name} ---\n")
    print(text[:500])

if __name__ == "__main__":
    main()