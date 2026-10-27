import streamlit as st
import UI
import AI

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"], key="r1")

if uploaded_file is not None:
    candidate_profile = UI.build_candidate_function(uploaded_file)
    results = UI.match_uploaded_resume_to_jobs(candidate_profile)

    for job in results[:5]:
        st.subheader(job["job_title"])

        st.write(f"Match Score: {job['overall_score']:.2f}%")
        st.write("Matching Skills:", ", ".join(job["matching_skills"]))
        st.write("Missing Skills:", ", ".join(job["missing_skills"]))
else:
    st.info("Please upload a resume")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"], key="r2")

if uploaded_file is not None:
    file_name = uploaded_file.name
    if file_name.endswith(".docx"):
        resume_text = UI.extract_docx_text(uploaded_file)
    else:
        resume_text = UI.extract_pdf_text(uploaded_file)

    result = AI.is_resume(resume_text)
    st.write(f"Resume Confidence: {result["resume_confidence"]:.2f}")
    st.write(f"Sections: {result["section_count"]}")
    st.write(f"Cover Letter Hits: {result["cover_letter_hits"]}")
    st.write(f"Skill Count: {result["skill_count"]}")
    st.write(f"Score: {result["score"]}")

    if result["is_resume"]:
        st.success("This is a resume")
    else:
        st.error("This is not a resume")
else:
    st.info("Please upload a resume")