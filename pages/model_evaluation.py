import matplotlib.pyplot as plt
import streamlit as st
import numpy as np
from sklearn.metrics import confusion_matrix
from src import resume

if "job_results" not in st.session_state:
    st.warning("Please upload a resume first")
    st.stop()

results = st.session_state["job_results"]

st.header("Resume Results")
st.divider()

top_job = results[0]
top_jobs = results[:4]

titles = [job["title"] for job in top_jobs]
scores = [job["score"] for job in top_jobs]

fig, ax = plt.subplots(figsize=(10, 5))

ax.bar(titles, scores, color="purple")
ax.invert_yaxis()

ax.set_xlabel("Match Score (%)")
ax.set_ylabel("Top Job Recommendations")

plt.show()
st.pyplot(plt)

st.header("Radar Plot Customizer")
st.divider()

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

if top_job["score"] >= 85:
    color = "green"
elif top_job["score"] >= 70:
    color = "orange"
else:
    color = "red"

figure, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
ax.plot(angles, values, color=color, linewidth=2)
ax.fill(angles, values, color=color, alpha=0.25)
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories)

plt.title("Best Job Match Breakdown")
st.pyplot(figure)

weakest = min(
    [
        ("Skills", top_job["skill_score"]),
        ("Semantic", top_job["semantic_score"]),
        ("Experience", top_job["experience_score"])
    ],
    key=lambda x: x[1]
)

st.info(f"Primary improvement area: {weakest[0]}")



