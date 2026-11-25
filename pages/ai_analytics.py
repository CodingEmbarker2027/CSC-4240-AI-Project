import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import requests
from src import resume
import UI
import AI
import job_scraper


@st.cache_data(ttl=900, show_spinner=False)
def fetch_greenhouse_jobs(company_slug, keyword, limit):
    return job_scraper.fetch_demo_jobs(company_slug, keyword, limit)


@st.cache_data(ttl=3600, show_spinner=False)
def generate_job_review(prompt, model_name, context_length):
    return UI.generate_analysis(prompt, model_name, context_length)


st.title("AI Resume Matcher")

with st.expander("AI review model settings", expanded=True):
    try:
        installed_qwen_models = UI.list_installed_qwen_models()
        ollama_error = None
    except Exception as error:
        installed_qwen_models = []
        ollama_error = str(error)

    if installed_qwen_models:
        model_options = ["Choose a model"] + installed_qwen_models

        def model_label(model_name):
            if model_name == "Choose a model":
                return model_name
            normalized_name = model_name.lower()
            if "1.7b" in normalized_name:
                return f"{model_name} — lightest, usually fastest"
            if "4b" in normalized_name:
                return f"{model_name} — middle ground"
            if "8b" in normalized_name:
                return f"{model_name} — larger, may be slower"
            return model_name

        selected_model = st.selectbox(
            "Installed Qwen3 model",
            model_options,
            index=0,
            format_func=model_label,
        )
        if selected_model == "Choose a model":
            selected_model = None
            suggested_context = "Choose a model to see a context suggestion."
        elif "1.7b" in selected_model.lower():
            suggested_context = "Suggested starting context: 4,096 tokens."
        elif "4b" in selected_model.lower():
            suggested_context = "Suggested starting context: 4,096 or 8,192 tokens."
        elif "8b" in selected_model.lower():
            suggested_context = "Suggested starting context: 4,096 or 8,192 tokens."
        else:
            suggested_context = "Suggested starting context: 4,096 tokens."

        context_length = st.number_input(
            "Context size (tokens)",
            min_value=2048,
            max_value=32768,
            value=4096,
            step=1024,
            help="Larger context lets Qwen consider more text but uses more memory. Choose a size your model and computer can handle.",
        )
        st.caption(suggested_context)
        st.caption("These are starting points, not guarantees. Larger contexts use more memory and may slow responses.")
        st.caption("The app will use only the model you select. Sentence Transformer scores are still included in each review.")
    else:
        selected_model = None
        context_length = 4096
        if ollama_error:
            st.warning(f"Could not read installed models from Ollama. Make sure Ollama is running. Details: {ollama_error}")
        else:
            st.info("No installed Qwen3 model was found. Pull one in Ollama, then rerun this page.")
            st.code("ollama pull qwen3:4b", language="powershell")

job_source = st.radio(
    "Job source",
    ["Saved sample jobs", "Live Greenhouse jobs"],
    horizontal=True,
)

if st.session_state.get("active_job_source") != job_source:
    st.session_state.pop("job_results", None)
    st.session_state.pop("job_results_source", None)
    st.session_state["active_job_source"] = job_source

jobs_df = resume.jobs_df if job_source == "Saved sample jobs" else pd.DataFrame()
if job_source == "Live Greenhouse jobs":
    with st.expander("Greenhouse job board settings", expanded=True):
        company_slug = st.text_input("Company board slug", "discord")
        keyword = st.text_input("Filter job titles (optional)", "engineer")
        limit = st.number_input("Maximum jobs", min_value=1, max_value=50, value=10)

    try:
        live_jobs = fetch_greenhouse_jobs(company_slug, keyword.strip(), int(limit))
    except (ValueError, requests.RequestException) as error:
        st.error(f"Could not load that Greenhouse board: {error}")
        live_jobs = []
    except Exception as error:
        st.error(f"Could not load Greenhouse jobs: {error}")
        live_jobs = []

    if live_jobs:
        jobs_df = pd.DataFrame([
            {
                "job_id": job["url"] or job["title"],
                "title": job["title"],
                "experience_required": job_scraper.required_experience_years(job["description"]),
                "skills": ",".join(AI.extract_skills_nlp(job["description"])),
                "job_description": job["description"],
                "location": job["location"],
                "url": job["url"],
            }
            for job in live_jobs
        ])
        st.caption(f"Loaded {len(jobs_df)} live jobs from Greenhouse. Experience requirements are estimated only when explicitly stated.")
    else:
        st.info("No matching live postings were found, so there are no jobs to rank. Check the board slug and title filter.")

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

    if not resume_text.strip():
        st.error("No readable text was found in that file.")
        st.stop()

    result = AI.classify_document(resume_text)

    # If it detects the file as a resume, output the top job along with the
    # recommended jobs.
    if result["document_type"] == "Resume":
        candidate_profile = UI.build_candidate_function(uploaded_file)
        if jobs_df.empty:
            st.warning("There are no jobs available to rank. Choose saved jobs or load live postings.")
            st.stop()
        results = AI.get_ranked_jobs(candidate_profile, jobs_df)
        # Save as soon as ranking succeeds so the visualizations page is usable
        # even if the optional Ollama feedback step is unavailable.
        st.session_state["job_results"] = results
        st.session_state["job_results_source"] = job_source

        top_job = results[0]

        if top_job.get("location"):
            st.caption(f"Location: {top_job['location']}")
        if top_job.get("url"):
            st.link_button("View job posting", top_job["url"])

        st.success(f"Top Job: {top_job['title']}")

        st.subheader("Other Jobs Recommended")

        for job in results[1:4]:
            st.write(f"- {job['title']}")

        st.divider()

        # Generate a separate, job-specific review for every ranked posting.
        st.subheader("Job-by-job AI reviews")
        st.caption("Each review names its job posting and uses that posting's description, score, and skill gaps.")
        if not selected_model:
            st.info("Choose an installed Qwen3 model above to generate the reviews. Match scores and rankings are available without Qwen.")
        else:
            st.caption(f"Selected model: `{selected_model}` · Context: {int(context_length):,} tokens")
            review_progress = st.progress(0, text="Preparing job reviews...")

            for index, job_result in enumerate(results, start=1):
                matching_rows = jobs_df[jobs_df["job_id"] == job_result["job_id"]]
                job_details = matching_rows.iloc[0] if not matching_rows.empty else None
                if job_details is not None:
                    description = AI.build_job_text(job_details)
                    location = job_result.get("location") or "Not listed"
                    posting_url = job_result.get("url", "")
                else:
                    description = "Job description was unavailable."
                    location = job_result.get("location") or "Not listed"
                    posting_url = job_result.get("url", "")

                prompt = f"""
You are reviewing one specific resume-to-job match. Review only the job identified below.

JOB TO REVIEW: {job_result['title']}
LOCATION: {location}
POSTING URL: {posting_url or 'Not provided'}
JOB DESCRIPTION (excerpt):
{description[:2500]}

CANDIDATE RESUME EVIDENCE (excerpt):
{candidate_profile.get('candidate_text', '')[:2500]}

EXTRACTED CANDIDATE PROFILE:
- Skills: {', '.join(candidate_profile['skills']) or 'None detected'}
- Experience: {candidate_profile['experience']} years detected
- Education: {', '.join(candidate_profile['education']) or 'None detected'}

MATCH RESULTS FOR THIS JOB ONLY:
- Overall score: {job_result['score']:.1f}%
- Semantic score: {job_result['semantic_score']:.1f}%
- Skill score: {job_result['skill_score']:.1f}%
- Experience score: {job_result['experience_score']:.1f}%
- Matching skills: {', '.join(job_result['matching']) or 'None detected'}
- Missing skills: {', '.join(job_result['missing']) or 'None detected'}

Write a concise review (about 120-180 words) with these labeled parts:
1. FIT FOR THIS ROLE: explain the match using specific resume evidence and the named job's requirements.
2. SKILL GAPS: explain the most relevant missing skills and whether the posting describes them as required or preferred, when clear.
3. NEXT STEPS: give two practical ways the candidate could strengthen their application or build a gap skill.

Do not invent experience, qualifications, or job requirements. If information is unclear, say so. Do not make a hiring decision or claim the score is a probability of getting hired.
"""

                with st.expander(f"{index}. {job_result['title']} — {job_result['score']:.1f}% match", expanded=index == 1):
                    if location != "Not listed":
                        st.caption(f"Location: {location}")
                    if posting_url:
                        st.link_button(
                            "View this job posting",
                            posting_url,
                            key=f"job_posting_{index}_{job_result['job_id']}",
                        )
                    try:
                        review = generate_job_review(prompt, selected_model, int(context_length))
                        st.write(review)
                    except Exception as error:
                        st.error(f"Could not generate this job's review: {error}")
                review_progress.progress(index / len(results), text=f"Reviewed {index} of {len(results)} jobs")

            review_progress.empty()

    else:
        st.error(f"This appears to be a {result['document_type']}")

else:
    st.info("Please upload a resume")
