import re
from pathlib import Path

import pandas as pd
import dictionary as dct
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity
from src import resume

model = SentenceTransformer("all-MiniLM-L6-v2")
gpt_df = pd.read_csv(Path(__file__).resolve().parent / "data" / "gpt_dataset.csv")
resume_embeddings = model.encode(gpt_df["Resume"].tolist(), convert_to_tensor=True)

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

def ai_nlp_match_score(candidate_profile, job):
    candidate_text = build_nlp_candidate(candidate_profile)
    job_text = build_job_text(job)

    semantic_score = calculate_semantic_score(candidate_text, job_text)

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

def calculate_semantic_score(candidate_text, job_text):
    candidate_embedding = generate_embedding(candidate_text)
    job_embedding = generate_embedding(job_text)

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

def get_ranked_jobs(profile, jobs_df):
    ranked_jobs = []

    for _, job in jobs_df.iterrows():
        result = ai_nlp_match_score(profile, job)

        ranked_jobs.append({
            "title": job["title"],
            "score": result["final_score"]
        })

    ranked_jobs.sort(key=lambda x: x["score"], reverse=True)

    return ranked_jobs

def calculate_top_n_accuracy(gpt, jobs_df):
    top1 = 0
    top3 = 0
    top5 = 0

    total = len(gpt)

    for _, candidate in gpt.iterrows():
        profile = build_candidate_profile_nlp(candidate["Resume"])

        ranked_jobs = get_ranked_jobs(profile, jobs_df)
        actual = candidate["Category"]

        top_1_jobs = [x["title"] for x in ranked_jobs[:1]]
        top_3_jobs = [x["title"] for x in ranked_jobs[:3]]
        top_5_jobs = [x["title"] for x in ranked_jobs[:5]]

        if actual in top_1_jobs:
            top1 += 1
        if actual in top_3_jobs:
            top3 += 1
        if actual in top_5_jobs:
            top5 += 1

    return {
        "Top-1": (top1 / total) * 100,
        "Top-3": (top3 / total) * 100,
        "Top-5": (top5 / total) * 100
    }

def is_resume(text):
    section_count = sum(1 for section in dct.resume_sections if section in text.lower())
    cover_letter_hits = sum(1 for phrase in dct.cover_letter_phrases if phrase in text.lower())

    uploaded_embedding = model.encode(text, convert_to_tensor=True)
    similarities = util.cos_sim(uploaded_embedding, resume_embeddings)

    max_similarity = similarities.max().item()
    profile = build_candidate_profile_nlp(text)

    skill_count = len(profile["skills"])

    score = 0

    if max_similarity >= 0.45:
        score += 1
    if skill_count >= 2:
        score += 1
    if section_count >= 2:
        score += 1
    if cover_letter_hits >= 2:
        score -= 2

    return {
        "is_resume": score >= 2,
        "resume_confidence": max_similarity,
        "section_count": section_count,
        "cover_letter_hits": cover_letter_hits,
        "skill_count": skill_count,
        "score": score
    }

def main():
    print(build_candidate_profile_nlp(gpt_df["Resume"].iloc[0]))

if __name__ == "__main__":
    main()

