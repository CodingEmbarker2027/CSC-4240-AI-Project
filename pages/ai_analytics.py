import streamlit as st
import matplotlib.pyplot as plt
from src import resume
import UI
import AI

# Upload the potential resume for testing
uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"], key="r1")

# If the person uploaded their resume, it then checks to see what the filename ends with
# and extracts the information from the file.
if uploaded_file is not None:
    file_name = uploaded_file.name
    if file_name.endswith(".docx"):
        resume_text = UI.extract_docx_text(uploaded_file)
    else:
        resume_text = UI.extract_pdf_text(uploaded_file)

    result = AI.classify_document(resume_text)

    # If it detects the file as a resume, output the top job along with the
    # recommended jobs.
    if result["document_type"] == "Resume":
        candidate_profile = UI.build_candidate_function(uploaded_file)
        results = AI.get_ranked_jobs(candidate_profile, resume.jobs_df)

        top_job = results[0]

        st.success(f"Top Job: {top_job['title']}")

        st.subheader("Other Jobs Recommended")

        for job in results[1:4]:
            st.write(f"- {job['title']}")

        st.divider()

        # Using Ollama, generate an explanation for why the applicant is a
        # good match, improvements to be made, and if they are to be interviewed
        # for the position.
        prompt = f"""
        Resume Skills:
        {candidate_profile['skills']}
        
        Years of Experience:
        {candidate_profile['experience']}
        
        Recommended Job:
        {top_job['title']}
        
        Skill Score:
        {top_job['skill_score']}
        
        Semantic Score:
        {top_job['semantic_score']}
        
        Experience Score:
        {top_job['experience_score']}
        
        Explain in 3-5 sentences why this job is a good match.
        
        Consider:
            - Existing skills
            - Experience
            - Semantic alignment
            - Potential for growth
            - Ability to learn missing skills

        Do not focus only on missing qualifications.
        """

        prompt2 = f"""
        Candidate_Skills:
        {", ".join(candidate_profile['skills'])}
        
        Missing Skills:
        {", ".join(top_job['missing'])}
        
        Provide:
        1. Why these missing skills are important
        2. A step-by-step learning roadmap
        3. One project idea that teaches most of these skills
        4. Keep the response under 300 words
        """

        prompt3 = f"""
        You are a hiring manager
        
        Role:
        {top_job['title']}
        
        Matching Skills:
        {", ".join(top_job['matching'])}
        
        Missing Skills:
        {", ".join(top_job['missing'])}
        
        Write a short assessment:
        - Would you interview this candidate?
        - What are their strongest qualifications?
        - What concerns would you have?
        - What would improve their chances?
        
        Limit to 150 words
        """

        analysis = UI.generate_analysis(prompt)
        st.subheader("AI Career Analysis")
        st.write(analysis)

        st.divider()

        improvement = UI.generate_analysis(prompt2)
        st.subheader("Improvement Area")
        st.write(improvement)

        st.divider()

        hiring = UI.generate_analysis(prompt3)
        st.subheader("AI Hiring Assistant Manager")
        st.write(hiring)

        st.divider()

        st.session_state["job_results"] = results

    # st.subheader(job["job_title"])
        # st.write(f"Match Score: {job['overall_score']:.2f}%")
        # st.write("Matching Skills:", ", ".join(job["matching_skills"]))
        # st.write("Missing Skills:", ", ".join(job["missing_skills"]))
    else:
        st.error(f"This appears to be a {result['document_type']}")

else:
    st.info("Please upload a resume")
