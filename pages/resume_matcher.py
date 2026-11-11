import streamlit as st
import matplotlib.pyplot as plt
from src import resume

st.title("AI Resume Matcher")

candidate_name_map = dict(zip(resume.resumes_df["candidate_id"], resume.resumes_df["name"]))
candidate_id = st.selectbox(
    "Select Candidate",
    resume.resumes_df["candidate_id"],
    format_func=lambda selected_candidate_id: candidate_name_map[selected_candidate_id],
)
job_title_map = dict(zip(resume.jobs_df["job_id"], resume.jobs_df["title"]))
job_id = st.selectbox(
    "Select Job",
    resume.jobs_df["job_id"].tolist(),
    format_func=lambda selected_job_id: f"{selected_job_id} - {job_title_map.get(selected_job_id, 'Unknown')}"
)

if st.button("Analyze Match"):
    result = resume.match_candidate_to_job(candidate_id, job_id)
    score = result["overall_score"]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Job Score",
            f"{score:.2f}"
        )

    with col2:
        st.metric(
            "Matching Skills #",
            len(result['matching'])
        )

    with col3:
        st.metric(
            "Missing Skills #",
            len(result['missing'])
        )

    st.progress(int(score))

    if score >= 85:
        st.success("🟢 Excellent Match")
    elif score >= 70:
        st.info("🔵 Strong Match")
    elif score >= 55:
        st.warning("🟡 Moderate Match")
    else:
        st.error("🔴 Weak Match")

    matching = len(result["matching"])
    missing = len(result["missing"])

    fig, ax = plt.subplots()

    ax.pie(
        [matching, missing],
        labels=["Matching", "Missing"],
        autopct="%1.0f%%",
        colors=["green", "red"],
        wedgeprops={"width": 0.4}
    )

    ax.set_title("Skill Coverage")
    st.pyplot(fig)

    left, right = st.columns(2)

    with left:
        st.subheader("✅ Matching Skills")
        if not result["matching"]:
            st.write("None")
        else:
            for skill in result["matching"]:
                f"- {skill.capitalize()}"

    with right:
        st.subheader("❌ Missing Skills")
        if not result["missing"]:
            st.write("None")
        else:
            for skill in result["missing"]:
                f"- {skill.capitalize()}"