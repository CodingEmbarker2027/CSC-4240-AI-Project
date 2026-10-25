# AI Project Proposal (Revised)

**Project Name:** Career-Match AI  
**Team Members:** Jenil Goyani, Connor Reagan, Aaron Thongmanivong, Izaiah Townsend, Dylan Watson  

---

### 1. Motivation
* **Navigating Modern Hiring:** Job seekers frequently face automated Applicant Tracking Systems (ATS) that filter resumes before a recruiter ever reads them.
* **Skill Transparency:** Applicants often struggle to quantify how well their background aligns with specific roles or identify actionable skill gaps.
* **Recruiter Alignment:** By bridging the gap between resume phrasing and job description semantics, we aim to provide candidates with data-driven feedback to optimize their profiles.

---

### 2. Updated Project Description & Technical Approach
Career-Match AI is an NLP-powered application that evaluates resume-to-job fit, identifies skill gaps, and suggests actionable resume improvements.

* **Semantic Embeddings:** Rather than relying on rigid keyword search, we utilize pre-trained **Sentence Transformers** (e.g., `all-MiniLM-L6-v2` or domain-adapted embeddings) to compute dense vector representations of resume sections and job descriptions.
* **Cosine Similarity Scoring:** Generate a nuanced semantic match score based on vector distance, capturing contextual relevance even when differing terminology is used.
* **Gap Analysis & Feedback:** Extract key skill entities to display matching vs. missing competencies and leverage an LLM/NLP prompt to suggest targeted resume enhancements.
* **Interactive UI:** Provide an intuitive web/desktop interface for users to upload resumes (PDF/DOCX/text), paste a target job description, and view analysis results in real time.

---

### 3. Evaluation & Benchmarking Strategy (Incorporating Feedback)
To meet academic evaluation standards and measure genuine predictive performance:
* **Labeled Benchmark Datasets:** Instead of scraping ad-hoc samples, we are utilizing open-source, human-annotated resume–job matching datasets (e.g., Hugging Face / Kaggle annotated pairs) as ground-truth test data.
* **Baseline vs. Advanced Model Comparison:**
  * **Baseline:** Traditional TF-IDF / BM25 / Keyword Overlap.
  * **Proposed Model:** Bi-Encoder / Cross-Encoder Sentence Transformers.
* **Metrics:** Evaluate models using quantitative metrics such as Mean Squared Error (MSE), Pearson/Spearman correlation (for continuous scores), or Precision@K / Recall / F1-Score (for classification/ranking fit).

---

### 4. Revised Execution Plan & Milestones

- [ ] **Dataset Selection & Preprocessing:**
   * Curate and clean the identified open-source labeled resume-job pair dataset.
   * Establish parsing pipelines for resume and job description text (tokenization, section segmentation).

- [ ] **Embedding Pipeline & Baseline Implementation:**
   * Implement a TF-IDF / keyword-matching baseline model.
   * Integrate Sentence Transformer embeddings to compute cosine similarity scores between candidate profiles and job requirements.

- [ ] **Evaluation & Optimization:**
   * Benchmark the Sentence Transformer model against the baseline on the labeled test split.
   * Tune thresholds or test Cross-Encoder re-ranking if inference speed permits.

- [ ] **Skill Gap Extraction & LLM Feedback**
   * Implement entity/skill recognition to display matched vs. missing requirements.
   * Generate contextual resume revision recommendations.

- [] **Interface & Integration:**
   * Build a lightweight, accessible UI (using Streamlit).
   * Conduct end-to-end user testing to ensure a complete, deployable deliverable within the semester timeline.