import streamlit as st
import matplotlib.pyplot as plt
from src import resume
import UI
import AI

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"], key="r1")

if uploaded_file is not None:
    file_name = uploaded_file.name
    if file_name.endswith(".docx"):
        resume_text = UI.extract_docx_text(uploaded_file)
    else:
        resume_text = UI.extract_pdf_text(uploaded_file)

    result = AI.classify_document(resume_text)

    if result["document_type"] == "Resume":
        candidate_profile = UI.build_candidate_function(uploaded_file)
        results = AI.get_ranked_jobs(candidate_profile, resume.jobs_df)

        top_job = results[0]

        st.success(f"Top Job: {top_job['title']}")

        st.subheader("Other Jobs Recommended")

        for job in results[1:4]:
            st.write(f"- {job['title']}")

        st.session_state["job_results"] = results

    # st.subheader(job["job_title"])
        # st.write(f"Match Score: {job['overall_score']:.2f}%")
        # st.write("Matching Skills:", ", ".join(job["matching_skills"]))
        # st.write("Missing Skills:", ", ".join(job["missing_skills"]))
    else:
        st.error(f"This appears to be a {result['document_type']}")

else:
    st.info("Please upload a resume")
