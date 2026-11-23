
from functools import lru_cache

from sentence_transformers import SentenceTransformer, util


# Load the model once and reuse it.
@lru_cache(maxsize=1)
def get_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


def split_into_chunks(text, max_words=220, overlap=40):
    """
    Split long documents into smaller overlapping sections.

    This helps prevent long resumes and job descriptions from
    being truncated when processed by the transformer.
    """
    if not isinstance(text, str):
        raise TypeError("Input text must be a string.")

    words = text.split()

    if not words:
        return []

    if len(words) <= max_words:
        return [text]

    chunks = []
    step = max_words - overlap

    for start in range(0, len(words), step):
        chunk = words[start:start + max_words]

        if chunk:
            chunks.append(" ".join(chunk))

        if start + max_words >= len(words):
            break

    return chunks


def semantic_similarity(resume_text, job_description):
    """
    Compare a resume against a job description using Sentence
    Transformer embeddings and cosine similarity.

    Returns a similarity score from 0 to 100.

    This score measures semantic similarity. It is not a
    probability that the applicant will qualify for the job.
    """
    if not isinstance(resume_text, str) or not resume_text.strip():
        raise ValueError("Resume text is empty.")

    if not isinstance(job_description, str) or not job_description.strip():
        raise ValueError("Job description is empty.")

    resume_chunks = split_into_chunks(resume_text)
    job_chunks = split_into_chunks(job_description)

    model = get_model()

    resume_embeddings = model.encode(
        resume_chunks,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    job_embeddings = model.encode(
        job_chunks,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    # Each job-description chunk is compared against every
    # resume chunk. We retain its strongest resume match.
    similarities = util.cos_sim(
        resume_embeddings,
        job_embeddings
    )

    best_matches = similarities.max(dim=0).values

    # Average the best match for each job-description chunk.
    score = best_matches.mean().item()

    # Convert cosine similarity into a 0-100 display scale.
    score = max(0.0, min(1.0, score)) * 100

    return round(score, 2)


if __name__ == "__main__":
    resume = """
    Computer engineering student with experience in Python,
    C++, embedded systems, Linux, and software development.
    """

    job = """
    We are looking for a software engineer with programming
    experience in Python and C++, knowledge of Linux systems,
    and experience developing software applications.
    """

    score = semantic_similarity(resume, job)

    print(f"Semantic Similarity: {score}%")
