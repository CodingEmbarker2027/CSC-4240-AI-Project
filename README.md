# Career-Match AI

Career-Match AI is an NLP-powered application designed to evaluate resume-to-job fit, identify skill gaps, and suggest actionable resume improvements. Moving beyond simple keyword matching, this project utilizes pre-trained Sentence Transformers to compute dense vector representations of resumes and job descriptions, providing a semantic match score that aligns with human HR evaluations.

## Project Structure

This repository is organized to support data exploration, AI agent collaboration, and the final web application.

### 📁 `.github/`
Contains configuration and instructions for the project's AI agents.
* **`agents/developer.agent.md`**: Prompt guidelines and behavioral instructions for the Coder/Developer AI agent.
* **`agents/planner.agent.md`**: Prompt guidelines and architectural instructions for the Planner/Architect AI agent.

### 📁 `data/`
Holds all datasets, testing materials, and raw inputs.
* **`data/raw_resumes/`**: Contains unstructured applicant resumes in `.docx` format.
* **`5_vacancies.csv`**: Full-text, real-world job descriptions serving as our target evaluation pool.
* **`annotation_instructions.docx`**: Evaluation criteria established by a senior HR specialist for ground-truth ranking.
* **`annotations-for-the-first-30-vacancies.txt`**: Ground-truth preference rankings from two independent annotators evaluating candidate CVs against the 5 vacancies.
* **`gpt_dataset.csv`**: A corpus of 400 long-form, unstructured natural language resumes categorized by tech disciplines.
* **`job_list.csv`**: 15 structured target roles with minimum experience requirements and core skills.
* **`resume_list.csv`**: 50 structured candidate profiles containing target roles, education, experience, and skills.

### 📁 `src/`
Contains reusable backend logic and data processing scripts.
* **`docx_parser.py`**: Utility script to parse and extract raw text from `.docx` files in `data/raw_resumes/`.
* **`resume.py`**: The baseline heuristic matching script, calculating match scores using skill overlap and experience requirements.
* **`job_scraper.py`**: Fetches and cleans live job descriptions from Greenhouse's public Job Board API.

### 📄 Root Files
* **`app.py`**: The Streamlit entry point; it loads the pages in `pages/`.
* **`career_match.ipynb`**: The primary Jupyter Notebook for data exploration, running the Sentence Transformer models, and calculating evaluation metrics (Spearman correlation).
* **`project_checklist.md`**: The step-by-step execution plan and task tracker for the team.
* **`project_proposal.md`**: The finalized academic project proposal detailing motivation, methodology, and evaluation strategies.
* **`requirements.txt`**: List of Python dependencies required to run the project.
* **`.gitignore`**: Specifies intentionally untracked files (like virtual environments and caches) that Git should ignore.
* **`model_connect_test.py`**: Diagnostic script to verify Ollama connectivity, RAM-based model selection, vector embeddings, and structured JSON output.


## Setup

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

## Local LLM Setup (Ollama)

The AI resume matching workflow combines Sentence Transformers semantic embeddings with skill and experience scores. It then uses the Qwen3 model through Ollama to explain the match and suggest improvements. Complete this setup to use those AI analysis features. The models run locally without external API keys.

### 1. Install Ollama

#### Windows
1. Download the installer from [ollama.com](https://ollama.com) and run `OllamaSetup.exe`.
2. Once installed, Ollama runs in the background at `http://localhost:11434`.
3. Verify in PowerShell:
   ```powershell
   ollama --version
   ```

#### macOS
1. Download from [ollama.com](https://ollama.com) (or install via Homebrew: `brew install ollama`).
2. Drag **Ollama** into your **Applications** folder and launch it once to register the CLI symlink.
3. Verify in Terminal *(Apple Silicon M-series chips automatically use Metal GPU acceleration)*:
   ```bash
   ollama --version
   ```

#### Linux
1. Run the official install script and start the background service:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   sudo systemctl enable --now ollama
   ```
2. Verify in Terminal:
   ```bash
   ollama --version
   ```

### 2. Pull Required Models

Run these commands in your terminal to download the embedding model and whichever Qwen3 model(s) you want to use:

1. **Pull the Embedding Model:**
   ```bash
   ollama pull all-minilm
   ```

2. **Pull the Qwen3 Model(s):**
   Pull one or more models. The sizes below are suggestions; the app lets you choose among the Qwen3 models installed in Ollama:

   | System RAM | Model Tier | Ollama Pull Command |
   | :--- | :--- | :--- |
   | **≤ 8 GB RAM** | **Qwen3 1.7B** | `ollama pull qwen3:1.7b` |
   | **16 GB RAM** | **Qwen3 4B** | `ollama pull qwen3:4b` |
   | **32 GB RAM** | **Qwen3 8B** | `ollama pull qwen3:8b` |

On the AI/NLP Analytics page, select an installed Qwen3 model before generating reviews. The app does not automatically select a model. It labels 1.7B as the lightest option, 4B as a middle ground, and 8B as larger and potentially slower. Suggested starting contexts are 4,096 tokens for 1.7B and 4,096 or 8,192 for 4B and 8B. These are starting points, not guarantees; larger contexts use more memory and may slow responses. You can choose a different context size. The diagnostic script `model_connect_test.py` still reports a RAM-based suggested model independently.

### 3. Hardware Acceleration Notes
* **NVIDIA & Apple Silicon:** Ollama automatically detects CUDA (NVIDIA) and Metal (Mac) with no extra setup.
* **Intel Arc / Core Ultra iGPUs (Windows):** Ollama may default to CPU unless Vulkan is enabled. Before running tests or the web app, enable Vulkan in PowerShell:
  ```powershell
  $env:OLLAMA_VULKAN="1"
  $env:OLLAMA_IGPU_ENABLE="1"
  ```

### 4. Verify Connection (`model_connect_test.py`)

With your `.venv` set up (from **First-time setup** above), make sure Ollama is fully stopped, including its tray app, before running this test. The script starts Ollama with its configured hardware environment, checks server health, RAM detection, embeddings, and JSON output, then shuts down the server it started:

**Windows PowerShell:**
```powershell
.\.venv\Scripts\python.exe model_connect_test.py
```

**macOS/Linux:**
```bash
.venv/bin/python model_connect_test.py
```

After the test finishes, start Ollama again before using the Qwen-powered AI
analysis page in the website.

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

## Running the Local Website

After completing **First-time setup** above, open a terminal in the project
folder and run the matching command for your operating system:

**Windows PowerShell:**
```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

**macOS/Linux:**
```bash
.venv/bin/python -m streamlit run app.py
```

Streamlit can start while Ollama is off. Start Ollama before using the
AI/NLP Analytics page, which calls Qwen3 to generate match explanations and
improvement suggestions. It generates a separate review for each ranked job,
including the job title, posting details, match scores, skill gaps, and next
steps. Keep Ollama running while using that page.

Open [http://localhost:8501](http://localhost:8501) in your browser (or use
the `Local URL` printed by Streamlit). Keep the terminal running while using
the website. Press `Ctrl+C` there to stop it.

The first time you open an AI/NLP page, Sentence Transformers downloads the
`all-MiniLM-L6-v2` model. An internet connection is needed for this download,
and that first page load may take longer.

## Live Job Board Fetching (Greenhouse)

The live job fetcher (`job_scraper.py` in the repository root) pulls real-time postings from Greenhouse's public Job Board API using a company's **board slug**:

```text
https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs?content=true
```

### Quick guide: find Greenhouse jobs by keyword

1. **Search the official Greenhouse candidate portal:** Visit [MyGreenhouse Jobs](https://my.greenhouse.com/) to discover and follow roles from participating Greenhouse employers. You can create an account to save your profile and get job alerts.
2. **Search public job boards with keywords:** In Google, try queries such as:
   ```text
   site:job-boards.greenhouse.io "data analyst" Python remote
   site:job-boards.greenhouse.io "software engineer" Kubernetes "New York"
   ```
   Replace the title, skill, and location terms with what you want. For older Greenhouse board links, also try `site:boards.greenhouse.io`.
3. **Verify the opening:** Open the result on the employer's own career page and confirm the role is still open. Copy the company's board slug from its Greenhouse URL, then enter that slug in the app's **Live Greenhouse jobs** settings.

The app's optional keyword filter matches **job titles**. Use MyGreenhouse or a search query like the examples above to find postings by skills or other words in the description.

### 1. How to Find Any Company's Slug
1. **Check the Job URL:** Open a company's Greenhouse-hosted job board and copy the path segment after the domain. For example, `https://boards.greenhouse.io/acme` has the slug `acme`; the public URL may also use `https://job-boards.greenhouse.io/acme`.
2. **Search via Google:** Search `site:job-boards.greenhouse.io "<Company Name>"` to locate their hosted board URL.
3. **Verify in Browser:** Paste `https://boards-api.greenhouse.io/v1/boards/<slug>/jobs` into your browser—if valid, it will return a live JSON feed of open roles.

**Ready-to-Use Example Slugs:** `discord`, `stripe`, `airbnb`, `cloudflare`, `databricks`, `anthropic`, `figma`

### 2. Use Live Jobs in the App
On the **AI/NLP Analytics** page, choose **Live Greenhouse jobs**, enter the company's board slug, optionally filter job titles, and set the maximum number of postings. The fetched postings are ranked against the uploaded resume alongside the saved sample-jobs option. Each result uses the full posting description when Greenhouse provides one, and the top recommendation includes a link to the posting.

The app estimates required experience only when the posting explicitly states a minimum. Skills are detected from the posting using the project's skill list, so live-job skill gaps may omit skills that are not in that list. If no minimum is detected, experience is treated as unspecified for scoring.

The standalone `job_scraper.py` example can still be run directly. Its `fetch_demo_jobs()` parameters control the same board slug, title filter, and result limit.

```python
# In job_scraper.py
jobs = fetch_demo_jobs(
    company_slug="stripe",   # Replace with any valid Greenhouse board slug
    keyword="engineer",      # Filter job titles by keyword (use "" for all roles)
    limit=5                  # Maximum number of matching jobs to return
)
```
