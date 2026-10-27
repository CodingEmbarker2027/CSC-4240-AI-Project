import pandas as pd

jobs_df = pd.read_csv("job_list.csv")
resumes_df = pd.read_csv("resume_list.csv")

def clean_skills(skill_string):
    if isinstance(skill_string, list):
        return {
            skill.strip().lower()
            for skill in skill_string
        }

    return {
        skill.strip()
        for skill in skill_string.split(",")
    }

def calculate_experience_score(candidate_exp, required_exp):
    if candidate_exp >= required_exp:
        return 100

    return (candidate_exp / required_exp) * 100

def keyword_match(resume_skills, job_skills, candidate_exp, required_exp):
    resume_set = clean_skills(resume_skills)
    job_set = clean_skills(job_skills)

    matching = resume_set & job_set
    missing = job_set - resume_set

    skill_score = (len(matching) / len(job_set)) * 100
    experience_score = calculate_experience_score(candidate_exp, required_exp)

    if len(matching) == 0:
        overall_score = 0
    else:
        overall_score = (skill_score * 0.8) + (experience_score * 0.2)

    return {
        "overall_score": overall_score,
        "matching": list(matching),
        "missing": list(missing)
    }

def get_candidate(candidate_id):
    candidate = resumes_df[resumes_df["candidate_id"] == candidate_id]
    return candidate.iloc[0]

def match_candidate_to_job(candidate_id, job_id):
    candidate = resumes_df[resumes_df["candidate_id"] == candidate_id].iloc[0]
    job = jobs_df[jobs_df["job_id"] == job_id].iloc[0]

    return keyword_match(
        candidate["skills"],
        job["skills"],
        candidate["experience_years"],
        job["experience_required"]
    )

def generate_suggestions(missing_skills):
    suggestions = []

    for skill in missing_skills:
        suggestions.append(f"Consider learning {skill}")

    return suggestions

def find_best_jobs(candidate_id):
    results = []

    for _, job in jobs_df.iterrows():
        match_result = match_candidate_to_job(candidate_id, job["job_id"])

        results.append({
            "job_title": job["title"],
            "overall_score": match_result["overall_score"],
            "matching_skills": match_result["matching"],
            "missing_skills": match_result["missing"]
        })

    results.sort(key=lambda x: x["overall_score"], reverse=True)
    return results

def main():
    recommendations = find_best_jobs(1)

    for job in recommendations[:5]:
         print(f"\n{job['job_title']}")

         print(
             f"Score: "
             f"{job['overall_score']:.2f}%"
         )

         print(
            "Matching Skills:",
            ", ".join(job["matching_skills"])
         )

         print(
             "Missing Skills:",
             ", ".join(job["missing_skills"])
         )

if __name__ == "__main__":
    main()



