import re
import AI
import pdfplumber
import dictionary as dct
from docx import Document
from src import resume

def extract_pdf_text(file):
    text = ""

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text

def extract_docx_text(file):
    doc = Document(file)

    paragraphs = []

    for paragraph in doc.paragraphs:
        paragraphs.append(paragraph.text.strip())

    return "\n".join(paragraphs)

def extract_sections(paragraphs):
    sections = {}

    current_section = None

    for line in paragraphs:
        line_lower = line.lower()

        found_section = None

        for section_name, patterns in dct.section_patterns.items():
            if line_lower in patterns:
                found_section = section_name
                break
        if found_section:
            current_section = found_section
            sections[current_section] = []
        elif current_section:
            sections[current_section].append(line.strip())
    return sections

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

def match_uploaded_resume_to_jobs(candidate_profile):
    results = []

    candidate_experience = candidate_profile["experience"]

    for _, job in resume.jobs_df.iterrows():
        result = resume_keyword_match(
            candidate_profile["skills"],
            job["skills"],
            candidate_experience,
            job["experience_required"]
        )

        results.append({
            "job_title": job["title"],
            "overall_score": result["overall_score"],
            "matching_skills": result["matching"],
            "missing_skills": result["missing"]
        })

    results.sort(
        key=lambda x: x["overall_score"],
        reverse=True
    )

    return results

def resume_keyword_match(resume_skills, job_skills, candidate_exp, required_exp):
    if isinstance(job_skills, str):
        job_skills = [
            skill.strip()
            for skill in job_skills.split(",")
        ]

    resume_set = {
        skill.strip().lower()
        for skill in resume_skills
    }
    job_set = {
        skill.strip().lower()
        for skill in job_skills
    }

    matching = resume_set & job_set
    missing = job_set - resume_set

    skill_score = (len(matching) / len(job_set)) * 100 if job_set else 0
    experience_score = resume.calculate_experience_score(candidate_exp, required_exp)

    if len(matching) == 0:
        overall_score = 0
    else:
        overall_score = (skill_score * 0.8) + (experience_score * 0.2)

    return {
        "overall_score": overall_score,
        "matching": list(matching),
        "missing": list(missing)
    }
