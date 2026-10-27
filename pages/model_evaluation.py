import matplotlib.pyplot as plt
import resume
import AI
from collections import Counter
import streamlit as st
import seaborn as sns
import pandas as pd
from sklearn.metrics import confusion_matrix

resume_skills = []

for skills in resume.resumes_df["skills"]:
    resume_skills.extend(
        skill.strip()
        for skill in skills.split(",")
    )

job_skills = []

for skills in resume.jobs_df["skills"]:
    job_skills.extend(
        skill.strip()
        for skill in skills.split(",")
    )

resume_counts = Counter(resume_skills)
job_counts = Counter(job_skills)

top_skills = resume_counts.most_common(10)

skills = [x[0] for x in top_skills]
counts = [x[1] for x in top_skills]

plt.figure(figsize=(10, 5))
plt.bar(skills, counts)
plt.title("Most Common Skills")
plt.xticks(rotation=45)
plt.show()

st.pyplot(plt)

all_skills = set(list(resume_counts.keys()) + list(job_counts.keys()))
skills = sorted(all_skills)

resume_values = [resume_counts.get(skill, 0) for skill in skills]
job_values = [job_counts.get(skill, 0) for skill in skills]

x = range(len(skills))
width = 0.4

plt.figure(figsize=(12, 6))

plt.bar(
    [i - width / 2 for i in x],
    resume_values,
    width=width,
    label="Candidate Supply"
)

plt.bar(
    [i + width / 2 for i in x],
    job_values,
    width=width,
    label="Job Demand"
)

plt.title("Candidate Skills vs Job Demand")
plt.xlabel("Skills")
plt.ylabel("Frequency")

plt.xticks(x, skills, rotation=45)
plt.legend()
plt.tight_layout()
plt.show()

st.pyplot(plt)

scores = []

for _, candidate in resume.resumes_df.iterrows():
    for _, job in resume.jobs_df.iterrows():
        result = resume.keyword_match(
            candidate["skills"],
            job["skills"],
            candidate["experience_years"],
            job["experience_required"]
        )

        scores.append(result["overall_score"])

plt.figure(figsize=(12, 6))
plt.hist(scores, bins=10, edgecolor="black")

plt.title("Match Score Distribution")
plt.xlabel("Match Score (%)")
plt.ylabel("Number of Matches")

plt.grid(axis="y", alpha=0.3)
plt.show()

st.pyplot(plt)

heatmap_data = []

for _, candidate in resume.resumes_df.iterrows():
    candidate_scores = []

    for _, job in resume.jobs_df.iterrows():
        result = resume.keyword_match(
            candidate["skills"],
            job["skills"],
            candidate["experience_years"],
            job["experience_required"]
        )

        candidate_scores.append(result["overall_score"])

    heatmap_data.append(candidate_scores)

heatmap_df = pd.DataFrame(
    heatmap_data,
    index=resume.resumes_df["name"],
    columns=resume.jobs_df["title"]
)

top_candidates = (
    heatmap_df.max(axis=1)
    .sort_values(ascending=False)
    .head(15)
    .index
)

top_heatmap = heatmap_df.loc[top_candidates]

plt.figure(figsize=(12, 6))

sns.heatmap(
    top_heatmap,
    annot=True,
    cmap="viridis",
    fmt=".1f"
)

plt.title("Candidate vs Job Match Scores")
plt.xlabel("Jobs")
plt.ylabel("Candidates")

plt.tight_layout()
plt.show()

st.pyplot(plt)

actuals = []
predictions = []

for _, candidate in AI.gpt_df.iterrows():
    profile = AI.build_candidate_profile_nlp(candidate["Resume"])
    prediction = AI.predict_job_category(profile, resume.jobs_df)

    actuals.append(candidate["Category"])
    predictions.append(prediction["predicted_job"])

categories = sorted(set(actuals) | set(predictions))

cm = confusion_matrix(actuals, predictions, labels=categories)
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=categories, yticklabels=categories)

plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Resume Category Prediction")
plt.show()

results = AI.calculate_top_n_accuracy(AI.gpt_df, resume.jobs_df)
labels = list(results.keys())
values = list(results.values())

plt.figure(figsize=(8, 5))
plt.bar(labels, values)
plt.xlabel("Recommendation Rank")
plt.ylabel("Accuracy")
plt.title("Top-N Recommendation Accuracy")
plt.ylim(0, 100)
plt.show()

st.pyplot(plt)

candidate = AI.gpt_df.iloc[0]

profile = AI.build_candidate_profile_nlp(candidate["Resume"])

ranked_jobs = AI.get_ranked_jobs(profile, resume.jobs_df)

top_jobs = ranked_jobs[:5]
job_titles = [job["title"] for job in top_jobs]
scores = [job["score"] for job in top_jobs]

plt.figure(figsize=(10, 6))
plt.barh(job_titles, scores)

plt.xlabel("Match Score")
plt.ylabel("Job Score")
plt.title("Top 5 Recommended Jobs")

plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()

st.pyplot(plt)