### Phase 1: Setup & Data Prep
- [ ] **Install Packages:** Run `pip install -r requirements.txt` (needs `pandas`, `sentence-transformers`, `scipy`, `streamlit`, `python-docx`).
- [ ] **Parse Resumes (Coder Agent Task):** Write `src/docx_parser.py` to extract text from the 10 Word documents in `data/raw_resumes/` and add them to your candidate pool.

### Phase 2: The Keyword Baseline
- [ ] **Run Existing Logic:** Adapt `src/resume.py` to score all candidates against the 5 real jobs in `5_vacancies.csv`.
- [ ] **Save Baseline Ranks:** Generate a 1-to-5 ranking of the jobs for each candidate based on this old keyword math.

### Phase 3: The AI Upgrade
- [ ] **Embed Text:** In `career_match.ipynb`, use `SentenceTransformer('all-MiniLM-L6-v2')` to embed the job descriptions and candidate resumes.
- [ ] **Score & Rank:** Calculate cosine similarity between them and generate a new 1-to-5 "AI Rank" for each candidate.

### Phase 4: Evaluation (To grade the AI)
- [ ] **Get Ground Truth:** Average Annotator 1 and Annotator 2's lists from the text file to create a "Consensus Rank".
- [ ] **Run the Math:** Use `scipy.stats.spearmanr` to compare the Baseline Ranks vs. the Consensus, and the AI Ranks vs. the Consensus. (The AI should win).

### Phase 5: The Web App (Final Deliverable)
- [ ] **Build UI (Coder Agent Task):** Create `app.py` using Streamlit with a file uploader (`st.file_uploader`).
- [ ] **Show Match %:** Run uploaded resumes through the Sentence Transformer and display the match percentage.
- [ ] **Show Gap Analysis:** Compare explicit skills to show "Missing Skills" and print actionable improvement advice.