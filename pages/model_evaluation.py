import matplotlib.pyplot as plt
import streamlit as st
import numpy as np

# Unless a resume has been uploaded, they cannot
# access the plots.
if "job_results" not in st.session_state:
    st.info("Upload a resume on the AI/NLP Analytics page first. Once its jobs are ranked, their charts will appear here.")
    st.stop()

results = st.session_state["job_results"]
result_source = st.session_state.get("job_results_source", "Unknown job source")

st.header("Match Result Visualizations")
st.caption(f"Results source: {result_source}")

top_job = results[0]
top_jobs = results[:4]

# Get the job scores for the top job and recommended jobs.
titles = [job["title"] for job in top_jobs]
scores = [job["score"] for job in top_jobs]

fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(titles, scores, color="purple")
ax.invert_yaxis()
ax.set_xlabel("Match Score (%)")
ax.set_xlim(0, 100)
ax.set_ylabel("Recommended Jobs")
ax.set_title("Top Job Matches")
fig.tight_layout()
st.pyplot(fig, clear_figure=True)

st.divider()

# A radar plot is used to visualize the strengths between the semantic score, skill score,
# and experience score.
st.header("Radar Plot Customizer")

selected_title = st.selectbox("Analyze Job", [job["title"] for job in results[:4]])
selected_job = next(job for job in results if job["title"] == selected_title)

col1, col2, col3 = st.columns(3)

col1.metric("Skill Score", f"{selected_job['skill_score']:.2f}")
col2.metric("Semantic Score", f"{selected_job['semantic_score']:.2f}")
col3.metric("Experience Score", f"{selected_job['experience_score']:.2f}")

categories = [
    "Skills",
    "Semantics",
    "Experience"
]

values = [
    selected_job["skill_score"],
    selected_job["semantic_score"],
    selected_job["experience_score"]
]

values += values[:1]

angles = np.linspace(
    0,
    2 * np.pi,
    len(categories),
    endpoint=False
).tolist()

angles += angles[:1]

if selected_job["score"] >= 85:
    color = "green"
elif selected_job["score"] >= 70:
    color = "orange"
else:
    color = "red"

figure, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
ax.plot(angles, values, color=color, linewidth=2)
ax.fill(angles, values, color=color, alpha=0.25)
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories)

ax.set_title(f"{selected_job['title']} Match Breakdown")
st.pyplot(figure, clear_figure=True)

scores = {
    "Skills": selected_job["skill_score"],
    "Semantic": selected_job["semantic_score"],
    "Experience": selected_job["experience_score"]
}

strongest = max(scores, key=scores.get)
weakest = min(scores, key=scores.get)

st.success(f"Strongest Area: {strongest}")

# Determine which one needs the most area of improvement
if weakest == "Semantic":
    st.warning("""
    The candidate has many required qualifications, but
    the overall resume narrative does not strongly align
    with this career path.
    """)
elif weakest == "Skills":
    st.warning("""
    The candidate appears to be a good fit for this role, but
    there are notable gaps in the required technical skill set.
    """)
elif weakest == "Experience":
    st.warning("""
    The candidate possesses many of the necessary skills
    for this role, but may need additional professional
    experience to meet typical industry expectations.
    """)

st.divider()

# How well does the resume align with the job the applicant is applying for?
st.header("Semantic Similarity Heatmap")
semantic_scores = [job["semantic_score"] for job in results[:10]]
job_titles = [job["title"] for job in results[:10]]

scores = np.array([semantic_scores])

fig, ax = plt.subplots(figsize=(10, 3), constrained_layout=True)

heatmap = ax.imshow(scores, cmap="YlGn", aspect="auto")
ax.set_xticks(np.arange(len(job_titles)))
ax.set_xticklabels(job_titles, rotation=30, ha="right")
ax.set_yticks([0])
ax.set_yticklabels(["Resume"])

for i, score in enumerate(semantic_scores):
    ax.text(i, 0, f"{score:.0f}", ha="center", va="center", color="black")

colorbar = fig.colorbar(heatmap, ax=ax)
colorbar.set_label("Semantic Similarity")
st.pyplot(fig, clear_figure=True)
st.divider()
