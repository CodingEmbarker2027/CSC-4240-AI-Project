import re
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from threading import Lock
import pandas as pd
import dictionary as dct
import streamlit as st
from src import resume

_model_preload_executor = ThreadPoolExecutor(max_workers=1)
_model_preload_future: Future[None] | None = None
_model_preload_lock = Lock()


# Reduces the amount of resources used in Streamlit when loading the page
@st.cache_resource
def load_model():
    from src import semantic_matcher

    return semantic_matcher.get_model()


@st.cache_resource
def load_document_reference_embeddings():
    gpt_df = pd.read_csv(Path(__file__).resolve().parent / "data" / "gpt_dataset.csv")
    model = load_model()
    return (
        model.encode(gpt_df["Resume"].tolist(), convert_to_tensor=True),
        model.encode(dct.INTERVIEW_EXAMPLES, convert_to_tensor=True),
        model.encode(dct.COVER_LETTER_EXAMPLES, convert_to_tensor=True),
        model.encode(dct.RESEARCH_EXAMPLES, convert_to_tensor=True),
    )


def preload_models():
    load_model()
    load_document_reference_embeddings()


def start_model_preload():
    global _model_preload_future

    with _model_preload_lock:
        if _model_preload_future is None:
            _model_preload_future = _model_preload_executor.submit(preload_models)


def get_model_preload_status():
    if _model_preload_future is None or not _model_preload_future.done():
        return "loading", None

    error = _model_preload_future.exception()
    if error is not None:
        return "failed", error

    return "ready", None


# Using a dictionary of skills, find the skills in the resume
def extract_skills_nlp(text):
    text = text.lower()

    found_skills = set()

    for skill in dct.skill_set:
        pattern = rf"\b{re.escape(skill.lower())}\b"

        if re.search(pattern, text):
            found_skills.add(skill)
    return sorted(found_skills)

# Extract the experience based on certain patterns using regex
def experience_years_nlp(text):
    text = text.lower()

    patterns = [
        r'(\d+)\+?\s+years?\s+of\s+experience',
        r'over\s+(\d+)\s+years',
        r'(\d+)\+?\s+years?\s+experience',
        r'(\d+)\+?\s+years?\s+experience',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return int(match.group(1))

    section_match = re.search(r'experience[:\s\n]+(\d+)', text, re.IGNORECASE)
    if section_match:
        return int(section_match.group(1))

    date_ranges = re.findall(r'(\d{4})\s*[-–]\s*(present|\d{4})', text, re.IGNORECASE)

    total_years = 0
    current_year = datetime.now().year

    for start, end in date_ranges:
        start = int(start)

        if end.lower() == "present":
            end = current_year
        else:
            end = int(end)

        total_years += max(0, end - start)

    return total_years

# Extract the education based on a certain pattern using regex
def extract_education_nlp(text):
    text = text.lower()

    found = set()

    for keyword in dct.degrees:
        pattern = rf"\b{re.escape(keyword)}\b"

        if re.search(pattern, text):
            found.add(keyword)
    return sorted(found)

# Create a profile of the candidate using the 3 previous funcion
def build_candidate_profile_nlp(resume_text):
    return {
        "skills": extract_skills_nlp(resume_text),
        "experience": experience_years_nlp(resume_text),
        "education": extract_education_nlp(resume_text)
    }

def build_nlp_candidate(profile):
    return f"""
    Candidate Skills: {' '.join(profile['skills'])}
    Experience: {profile['experience']} years
    Education: {' '.join(profile['education'])}
    """

def build_job_text(job):
    # Prefer full job description when one exists.
    if "job_description" in job.index:
        description = job["job_description"]

        if pd.notna(description) and str(description).strip():
            return str(description)

    # Support other common description-column names.
    for column in ["job_description","description", "job_desc"]:
        if column in job.index:
            description = job[column]

            if pd.notna(description) and str(description).strip():
                return str(description)
    return f"""
    Job Title: {job['title']}
    Skills: {job['skills']}
    Experience: {job['experience_required']} years
    """

# A final calculation of the actual job score based on certain criteria
def calculate_final_score(semantic_score, experience_score, skill_score):
    return (
        semantic_score * 0.6 +
        skill_score * 0.3 +
        experience_score * 0.1
    )

# Gets a score based on the skills the person has and is missing.
def calculate_skill_score(candidate_profile, job):
    candidate_set = {
        skill.lower().strip()
        for skill in candidate_profile["skills"]
    }

    job_set = {
        skill.lower().strip()
        for skill in job["skills"].split(",")
        if skill.strip()
    }

    matching = candidate_set & job_set
    missing = job_set - candidate_set

    if job_set:
        skill_score = (len(matching) / len(job_set)) * 100
    else: 
        skill_score = 0

    return {
        "overall_score": skill_score,
        "matching": list(matching),
        "missing": list(missing)
    }

# Ranks the top jobs for the applicant based on their job score.
def get_ranked_jobs(profile, jobs_df):
    ranked_jobs = []

    # Retrieve the complete resume text.
    candidate_text = profile.get("candidate_text", "")

    # Use the structured candidate profile only as a fallback.
    if not isinstance(candidate_text, str) or not candidate_text.strip():
        candidate_text = build_nlp_candidate(profile)

    for _, job in jobs_df.iterrows():
        result = ai_nlp_match_score(profile, job, candidate_text)

        ranked_jobs.append({
            "job_id": job.get("job_id", job["title"]),
            "title": job["title"],
            "score": result["final_score"],
            "semantic_score": result["semantic_score"],
            "experience_score": result["experience_score"],
            "skill_score": result["skill_score"],
            "missing": result["missing"],
            "matching": result["matching"],
            "location": job.get("location", ""),
            "url": job.get("url", ""),
        })

    ranked_jobs.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return ranked_jobs

# Generates the match score using AI tools that will be used for the rankings.
def ai_nlp_match_score(candidate_profile, job, candidate_text):
    from src import semantic_matcher

    job_text = build_job_text(job)

    semantic_score = semantic_matcher.semantic_similarity(candidate_text, job_text)

    experience_score = resume.calculate_experience_score(
        candidate_profile["experience"],
        job["experience_required"]
    )

    skill_result = calculate_skill_score(candidate_profile, job)
    skill_score = skill_result["overall_score"]

    final_score = calculate_final_score(semantic_score, experience_score, skill_score)

    return {
        "semantic_score": semantic_score,
        "experience_score": experience_score,
        "skill_score": skill_score,
        "final_score": final_score,
        "missing": skill_result["missing"],
        "matching": skill_result["matching"]
    }

# Based on certain criteria, classify whether the file is a resume or if it is
# another file similarly used for jobs that is not a resume.
def classify_document(text):
    from sentence_transformers import util

    model = load_model()
    (
        resume_embeddings,
        interview_embeddings,
        cover_letter_embeddings,
        research_embeddings,
    ) = load_document_reference_embeddings()
    uploaded_embedding = model.encode(text, convert_to_tensor=True)
    scores = {}

    resume_similarities = util.cos_sim(uploaded_embedding, resume_embeddings)
    scores["Cover Letter"] = util.cos_sim(uploaded_embedding, cover_letter_embeddings).max().item()
    scores["Interview Notes"] = util.cos_sim(uploaded_embedding, interview_embeddings).max().item()
    scores["Research Notes"] = util.cos_sim(uploaded_embedding, research_embeddings).max().item()

    scores["Resume"] = (resume_similarities.max().item() * 0.7 + resume_similarities.mean().item() * 0.3)

    section_count = sum(1 for section in dct.resume_sections if section in text.lower())
    cover_letter_hits = sum(1 for phrase in dct.cover_letter_phrases if phrase in text.lower())
    interview_hits = sum(1 for phrase in dct.interview_phrases if phrase in text.lower())
    research_hits = sum(text.lower().count(term) for term in dct.research_phrases)

    email_found = bool(re.search(r'\S+@\S+', text))
    phone_found = bool(re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text))

    if section_count >= 4:
        scores["Resume"] += 0.40
    elif section_count >= 2:
        scores["Resume"] += 0.20

    if email_found:
        scores["Resume"] += 0.10
    if phone_found:
        scores["Resume"] += 0.10

    if "dear" in text.lower():
        scores["Resume"] -= 0.15

    if "warm regards" in text.lower():
        scores["Resume"] -= 0.20

    if cover_letter_hits >= 2:
        scores["Cover Letter"] += 0.30
    if "dear" in text.lower():
        scores["Cover Letter"] += 0.20
    if "warm regards" in text.lower():
        scores["Cover Letter"] += 0.30
    if "thank you" in text.lower():
        scores["Cover Letter"] += 0.20
    if "to whom it may concern" in text.lower():
        scores["Cover Letter"] += 0.40
    if "sincerely" in text.lower():
        scores["Cover Letter"] += 0.25
    if "i am writing" in text.lower():
        scores["Cover Letter"] += 0.20

    if interview_hits >= 2:
        scores["Interview Notes"] += 0.40
    if research_hits >= 2:
        scores["Research Notes"] += 0.60

    document_type = max(scores, key=scores.get)

    confidence = scores[document_type]

    if confidence < 0.30:
        document_type = "Unknown"

    return {
        "document_type": document_type,
        "confidence": confidence,
        "scores": scores,
        "section_count": section_count,
        "cover_letter_hits": cover_letter_hits,
        "interview_hits": interview_hits,
        "research_hits": research_hits
    }

def main():
    gpt_df = pd.read_csv(Path(__file__).resolve().parent / "data" / "gpt_dataset.csv")
    print(build_candidate_profile_nlp(gpt_df["Resume"].iloc[0]))

if __name__ == "__main__":
    main()
