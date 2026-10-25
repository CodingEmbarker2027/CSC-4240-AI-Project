# Career-Match AI

Career-Match AI is an NLP-powered application designed to evaluate resume-to-job fit, identify skill gaps, and suggest actionable resume improvements. Moving beyond simple keyword matching, this project utilizes pre-trained Sentence Transformers to compute dense vector representations of resumes and job descriptions, providing a semantic match score that aligns with human HR evaluations.

## Project Structure

This repository is organized to support data exploration, AI agent collaboration, and the final web application.

### 📁 `.github/`
Contains configuration and instructions for the project's AI agents.
* **`developer.agent.md`**: Prompt guidelines and behavioral instructions for the Coder/Developer AI agent.
* **`planner.agent.md`**: Prompt guidelines and architectural instructions for the Planner/Architect AI agent.

### 📁 `data/`
Holds all datasets, testing materials, and raw inputs.
* **`raw_resumes/`**: Directory containing unstructured applicant resumes in `.docx` format.
* **`5_vacancies.csv`**: Full-text, real-world job descriptions serving as our target evaluation pool.
* **`annotation_instructions.docx`**: Evaluation criteria established by a senior HR specialist for ground-truth ranking.
* **`annotations-for-the-first-30-vacancies.txt`**: Ground-truth preference rankings from two independent annotators evaluating candidate CVs against the 5 vacancies.
* **`gpt_dataset.csv`**: A corpus of 400 long-form, unstructured natural language resumes categorized by tech disciplines.
* **`job_list.csv`**: 15 structured target roles with minimum experience requirements and core skills.
* **`resume_list.csv`**: 50 structured candidate profiles containing target roles, education, experience, and skills.

### 📁 `src/`
Contains reusable backend logic and data processing scripts.
* **`docx_parser.py`**: Utility script to parse and extract raw text from the `.docx` files in the `raw_resumes` folder.
* **`resume.py`**: The baseline heuristic matching script, calculating match scores using skill overlap and experience requirements.

### 📄 Root Files
* **`app.py`**: The main Streamlit web application that serves as the final hybrid matching engine UI.
* **`career_match.ipynb`**: The primary Jupyter Notebook for data exploration, running the Sentence Transformer models, and calculating evaluation metrics (Spearman correlation).
* **`project_checklist.md`**: The step-by-step execution plan and task tracker for the team.
* **`project_proposal.md`**: The finalized academic project proposal detailing motivation, methodology, and evaluation strategies.
* **`requirements.txt`**: List of Python dependencies required to run the project.
* **`.gitignore`**: Specifies intentionally untracked files (like virtual environments and caches) that Git should ignore.

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/career-match-ai.git](https://github.com/YOUR_USERNAME/career-match-ai.git)
   cd career-match-ai