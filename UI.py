import re

import pdfplumber
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
    headers = {
        "EDUCATION",
        "SKILLS",
        "EXPERIENCE",
        "PROJECTS"
    }

    sections = {}

    current_section = None

    for line in paragraphs:
        line_upper = line.upper()

        if line_upper in headers:
            current_section = line_upper
            sections[current_section] = []
        elif current_section:
            sections[current_section].append(line)

    return sections

def build_candidate_function(file_path):
    file_name = file_path.name

    if file_name.lower().endswith(".docx"):
        paragraphs = extract_docx_text(file_path)
    else:
        paragraphs = extract_pdf_text(file_path)

    sections = extract_sections(paragraphs.splitlines())
    experience_text = "\n".join(sections.get("EXPERIENCE", []))
    experience_match = re.search(r"\b(\d+)\+?\s+years?\b", experience_text, re.IGNORECASE)
    skills = [
        skill.strip()
        for line in sections.get("SKILLS", [])
        for skill in line.split(",")
        if skill.strip()
    ]

    return {
        "skills": skills,
        "education": sections.get("EDUCATION", []),
        "experience": int(experience_match.group(1)) if experience_match else 0,
        "projects": sections.get("PROJECTS", [])
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
