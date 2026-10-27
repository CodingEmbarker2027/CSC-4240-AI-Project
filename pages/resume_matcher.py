import streamlit as st
import AI
import UI
import resume

st.title("AI Resume Matcher")

candidate_id = st.selectbox("Select Candidate", resume.resumes_df["candidate_id"])
job_title_map = dict(zip(resume.jobs_df["job_id"], resume.jobs_df["title"]))
job_id = st.selectbox(
    "Select Job",
    resume.jobs_df["job_id"].tolist(),
    format_func=lambda selected_job_id: f"{selected_job_id} - {job_title_map.get(selected_job_id, 'Unknown')}"
)

if st.button("Analyze Match"):
    result = resume.match_candidate_to_job(candidate_id, job_id)

    st.write(f"Match Score: {result["overall_score"]:.2f}%")

    if len(result["matching"]) == 0:
        st.write("Matching Skills: None")
    else:
        st.write("Matching Skills: ")
        for matching in result['matching']:
            st.write(matching.capitalize())

        if len(result["missing"]) == 0:
            st.write("Missing Skills: None")
        else:
            st.write("Missing Skills: ")
            for missing in result["missing"]:
                st.write(missing.capitalize())