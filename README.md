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
* **`job_scraper.py`**: Fetches and cleans live job descriptions from Greenhouse's public Job Board API.

### 📄 Root Files
* **`app.py`**: The main Streamlit web application that serves as the final hybrid matching engine UI.
* **`career_match.ipynb`**: The primary Jupyter Notebook for data exploration, running the Sentence Transformer models, and calculating evaluation metrics (Spearman correlation).
* **`project_checklist.md`**: The step-by-step execution plan and task tracker for the team.
* **`project_proposal.md`**: The finalized academic project proposal detailing motivation, methodology, and evaluation strategies.
* **`requirements.txt`**: List of Python dependencies required to run the project.
* **`.gitignore`**: Specifies intentionally untracked files (like virtual environments and caches) that Git should ignore.
* **`model_connect_test.py`**: Diagnostic script to verify Ollama connectivity, RAM-based model selection, vector embeddings, and structured JSON output.


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

## Live Job Board Fetching (Greenhouse)

The live job fetcher (`src/job_scraper.py`) pulls real-time postings from Greenhouse's public Job Board API using a company's **board slug**:

```text
https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs?content=true
```

### 1. How to Find Any Company's Slug
1. **Check the Job URL:** Open a company's Greenhouse job posting and copy the path segment immediately following `greenhouse.io/`:
   * `https://greenhouse.io` → slug is **`stripe`**
   * `https://greenhouse.io` → slug is **`discord`**
2. **Search via Google:** Search `site:job-boards.greenhouse.io "<Company Name>"` to locate their hosted board URL.
3. **Verify in Browser:** Paste `https://boards-api.greenhouse.io/v1/boards/<slug>/jobs` into your browser—if valid, it will return a live JSON feed of open roles.

**Ready-to-Use Example Slugs:** `discord`, `stripe`, `airbnb`, `cloudflare`, `databricks`, `anthropic`, `figma`

### 2. How to Customize the Target Company in Code
To change the default company, role filter, or number of fetched jobs, update the `fetch_demo_jobs()` parameters in **`src/job_scraper.py`** (or pass them from **`pages/resume_matcher.py`**):

```python
# In src/job_scraper.py
jobs = fetch_demo_jobs(
    company_slug="stripe",   # Replace with any valid Greenhouse board slug
    keyword="engineer",      # Filter job titles by keyword (use "" for all roles)
    limit=5                  # Maximum number of matching jobs to return
)
```

## Local LLM Setup (Ollama)

Career-Match AI uses [Ollama](https://ollama.com) to run local embedding and reasoning models on your machine without external API keys.

### 1. Install Ollama

#### Windows
1. Download the installer from [://ollama.com](https://://ollama.com) and run `OllamaSetup.exe`.
2. Once installed, Ollama runs in the background at `http://localhost:11434`.
3. Verify in PowerShell:
   ```powershell
   ollama --version
   ```

#### macOS
1. Download from [://ollama.com](https://://ollama.com) (or install via Homebrew: `brew install ollama`).
2. Drag **Ollama** into your **Applications** folder and launch it once to register the CLI symlink.
3. Verify in Terminal *(Apple Silicon M-series chips automatically use Metal GPU acceleration)*:
   ```bash
   ollama --version
   ```

#### Linux
1. Run the official install script and start the background service:
   ```bash
   curl -fsSL https://ollama.com | sh
   sudo systemctl enable --now ollama
   ```
2. Verify in Terminal:
   ```bash
   ollama --version
   ```

### 2. Pull Required Models

Run these commands in your terminal to download the embedding model and the Qwen3 reasoning model matching your system RAM:

1. **Pull the Embedding Model:**
   ```bash
   ollama pull all-minilm
   ```

2. **Pull the Qwen3 Model(s):**
   Pull the tier that matches your hardware (or pull all three if sharing across different machines):

   | System RAM | Model Tier | Ollama Pull Command |
   | :--- | :--- | :--- |
   | **≤ 8 GB RAM** | **Qwen3 1.7B** | `ollama pull qwen3:1.7b` |
   | **16 GB RAM** | **Qwen3 4B** | `ollama pull qwen3:4b` |
   | **32 GB RAM** | **Qwen3 8B** | `ollama pull qwen3:8b` |

### 3. Hardware Acceleration Notes
* **NVIDIA & Apple Silicon:** Ollama automatically detects CUDA (NVIDIA) and Metal (Mac) with no extra setup.
* **Intel Arc / Core Ultra iGPUs (Windows):** Ollama may default to CPU unless Vulkan is enabled. Before running tests or the web app, enable Vulkan in PowerShell:
  ```powershell
  $env:OLLAMA_VULKAN="1"
  $env:OLLAMA_IGPU_ENABLE="1"
  ```

### 4. Verify Connection (`model_connect_test.py`)

With your `.venv` set up (from **First-time setup** above), run the diagnostic test to verify server health, RAM detection, embeddings, and JSON output:

**Windows PowerShell:**
```powershell
.\.venv\Scripts\python.exe model_connect_test.py
```

**macOS/Linux:**
```bash
.venv/bin/python model_connect_test.py
```

### 5. Developer Quick Reference: Local Inference

#### Vector Embeddings & Cosine Similarity
```python
import numpy as np
import ollama

emb1 = ollama.embeddings(model="all-minilm", prompt="Python developer with FastAPI experience.")["embedding"]
emb2 = ollama.embeddings(model="all-minilm", prompt="Backend software engineer working with Python.")["embedding"]

v1, v2 = np.array(emb1), np.array(emb2)
similarity = float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
print(f"Similarity Score: {similarity:.4f}")
```

#### Structured JSON Generation (Qwen3)
```python
import json
import ollama

prompt = """Evaluate candidate fit for a Python backend role.
Candidate has 3 years of Python and SQL experience.
Output MUST be valid JSON matching this schema:
{
  "fit_score": 85,
  "verdict": "Interview | Reject",
  "reason": "short explanation"
}"""

response = ollama.generate(
    model="qwen3:4b",  # or qwen3:1.7b / qwen3:8b
    prompt=prompt,
    format="json",
    options={"temperature": 0.1, "num_ctx": 2048}
)

data = json.loads(response["response"])
print(json.dumps(data, indent=2))
```
