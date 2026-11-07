import re
from pathlib import Path
import pandas as pd
import dictionary as dct
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
from src import resume

@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")
model = load_model()

gpt_df = pd.read_csv(Path(__file__).resolve().parent / "data" / "gpt_dataset.csv")

resume_embeddings = model.encode(gpt_df["Resume"].tolist(), convert_to_tensor=True)
interview_embeddings = model.encode(dct.INTERVIEW_EXAMPLES, convert_to_tensor=True)
cover_letter_embeddings = model.encode(dct.COVER_LETTER_EXAMPLES, convert_to_tensor=True)
research_embeddings = model.encode(dct.RESEARCH_EXAMPLES, convert_to_tensor=True)

def generate_embedding(text):
    return model.encode(text, convert_to_tensor=True)

def extract_skills_nlp(text):
    text = text.lower()

    found_skills = set()

    for skill in dct.skill_set:
        pattern = rf"\b{re.escape(skill.lower())}\b"

        if re.search(pattern, text):
            found_skills.add(skill)
    return sorted(found_skills)

def experience_years_nlp(text):
    text = text.lower()

    patterns = [
        r'(\d+)\+?\s+years?\s+of\s+experience',
        r'over\s+(\d+)\s+years',
        r'(\d+)\s+years'
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            return int(match.group(1))
    return 0

def extract_education_nlp(text):
    text = text.lower()

    found = set()

    for keyword in dct.degrees:
        pattern = rf"\b{re.escape(keyword)}\b"

        if re.search(pattern, text):
            found.add(keyword)
    return sorted(found)

def extract_degree_level(text):
    text = text.lower()

    if "phd" in text or "doctorate" in text:
        return "phD"
    elif "master" in text:
        return "Master"
    elif "bachelor" in text or "b.s." in text or "bs" in text:
        return "Bachelor"
    elif "associate" in text:
        return "Associate"
    return "Unknown"

def build_candidate_profile_nlp(resume_text):
    return {
        "skills": extract_skills_nlp(resume_text),
        "experience": experience_years_nlp(resume_text),
        "education": extract_education_nlp(resume_text)
    }

def build_candidate_text(candidate):
    return f"""
    Name: {candidate['name']}
    Skills: {candidate['skills']}
    Experience: {candidate['experience_years']} years
    """

def build_nlp_candidate(profile):
    return f"""
    Candidate Skills: {' '.join(profile['skills'])}
    Experience: {profile['experience']} years
    Education: {' '.join(profile['education'])}
    """

def build_job_text(job):
    return f"""
    Job Title: {job['title']}
    Skills: {job['skills']}
    Experience: {job['experience_required']} years
    """

def ai_match_score(candidate, job):
    candidate_text = build_candidate_text(candidate)
    job_text = build_job_text(job)

    candidate_embedding = model.encode([candidate_text])
    job_embedding = model.encode([job_text])

    similarity = cosine_similarity(candidate_embedding, job_embedding)

    return similarity[0][0] * 100

def calculate_final_score(semantic_score, experience_score, skill_score):
    return (
        semantic_score * 0.6 +
        skill_score * 0.3 +
        experience_score * 0.1
    )

def calculate_skill_score(candidate_profile, job):
    candidate_set = {
        skill.lower()
        for skill in candidate_profile["skills"]
    }

    job_set = {
        skill.lower().strip()
        for skill in job["skills"].split(",")
    }

    matching = candidate_set & job_set
    missing = job_set - candidate_set

    skill_score = (len(matching) / len(job_set)) * 100

    return {
        "overall_score": skill_score,
        "matching": list(matching),
        "missing": list(missing)
    }

def get_ranked_jobs(profile, jobs_df):
    ranked_jobs = []

    candidate_embedding = generate_embedding(build_nlp_candidate(profile))

    for _, job in jobs_df.iterrows():
        result = ai_nlp_match_score(profile, job, candidate_embedding)

        ranked_jobs.append({
            "title": job["title"],
            "score": result["final_score"],
            "semantic_score": result["semantic_score"],
            "experience_score": result["experience_score"],
            "skill_score": result["skill_score"]
        })

    ranked_jobs.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return ranked_jobs

def ai_nlp_match_score(candidate_profile, job, candidate_embedding):
    job_embedding = generate_embedding(build_job_text(job))

    semantic_score = calculate_semantic_score(candidate_embedding, job_embedding)

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
        "final_score": final_score
    }

def calculate_semantic_score(candidate_embedding, job_embedding):
    similarity = util.cos_sim(candidate_embedding, job_embedding)

    return similarity.item() * 100

def predict_job_category(profile, jobs_df):
    best_job = None
    best_score = -1

    for _, job in jobs_df.iterrows():
        result = ai_nlp_match_score(profile, job)

        if result["final_score"] > best_score:
            best_score = result["final_score"]
            best_job = job["title"]

    return {
        "predicted_job": best_job,
        "score": best_score
    }

def classify_document(text):
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

    if cover_letter_hits >= 2:
        scores["Cover Letter"] += 0.30
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
        "research_hits": research_hits,
    }

def main():
    print(build_candidate_profile_nlp(gpt_df["Resume"].iloc[0]))

if __name__ == "__main__":
    main()

