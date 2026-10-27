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

## Run the local website

Open a terminal in the project folder (the folder containing `app.py` and
`requirements.txt`). The commands below create a virtual environment using
your default Python installation; they do not hard-code a Python version or
an installation path.

### First-time setup

**Windows PowerShell:**

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**macOS/Linux:**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

On Windows, `py --list` shows the installed Python versions. To select a
specific installed version, replace `py` in the first command with a launcher
version such as `py -3.12`. On macOS/Linux, use the appropriate installed
`python3.x` command instead of `python3` if needed.

If you already created `.venv`, skip the first command. You only need to
install dependencies again if `requirements.txt` changes.

### Start the website

Whenever you want to run the website, open a terminal in the project folder.
Use the matching command for your operating system:

**Windows PowerShell:**
```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

**macOS/Linux:**
```bash
.venv/bin/python -m streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser (or use
the `Local URL` printed by Streamlit). Keep the terminal running while using
the website. Press `Ctrl+C` there to stop it.

The first time you open an AI/NLP page, Sentence Transformers downloads the
`all-MiniLM-L6-v2` model. An internet connection is needed for this download,
and that first page load may take longer.