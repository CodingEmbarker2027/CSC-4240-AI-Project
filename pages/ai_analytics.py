import streamlit as st
import matplotlib.pyplot as plt
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

    st.write(f"Detected Type: {result['document_type']}")
    st.write(f"Confidence: {result['confidence']}")

    if result["document_type"] == "Resume":
        candidate_profile = UI.build_candidate_function(uploaded_file)
        results = UI.match_uploaded_resume_to_jobs(candidate_profile)

        top_jobs = results[:5]

        titles = [job["job_title"] for job in top_jobs]
        scores = [job["overall_score"] for job in top_jobs]

        fig, ax = plt.subplots(figsize=(10, 5))

        ax.bar(titles, scores, color="purple")
        ax.invert_yaxis()

        ax.set_xlabel("Match Score (%)")
        ax.set_ylabel("Top Job Recommendations")

        plt.show()
        st.pyplot(plt)

    # st.subheader(job["job_title"])
        # st.write(f"Match Score: {job['overall_score']:.2f}%")
        # st.write("Matching Skills:", ", ".join(job["matching_skills"]))
        # st.write("Missing Skills:", ", ".join(job["missing_skills"]))
    else:
        st.error(f"This appears to be a {result['document_type']}")

else:
    st.info("Please upload a resume")
