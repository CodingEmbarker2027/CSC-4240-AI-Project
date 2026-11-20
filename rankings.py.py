"""Rank the five benchmark vacancies for each candidate resume."""

from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

from src.docx_parser import extract_docx_text


def embed_documents(model, texts):
    """Combine embeddings from chunks that fit within the model's token limit."""
    tokenizer = model.tokenizer
    chunk_size = model.max_seq_length - tokenizer.num_special_tokens_to_add(pair=False)
    chunks = []
    chunk_sizes = []
    document_ranges = []

    for text in texts:
        offsets = tokenizer(
            text, add_special_tokens=False, truncation=False,
            return_offsets_mapping=True, verbose=False,
        )["offset_mapping"]
        if not offsets:
            raise ValueError("A resume or vacancy has no text to embed.")

        start_chunk = len(chunks)
        for start in range(0, len(offsets), chunk_size):
            end = min(start + chunk_size, len(offsets))
            chunks.append(text[offsets[start][0]:offsets[end - 1][1]])
            chunk_sizes.append(end - start)
        document_ranges.append((start_chunk, len(chunks)))

    vectors = model.encode(chunks, normalize_embeddings=True)
    documents = np.stack([
        np.average(vectors[start:end], axis=0, weights=chunk_sizes[start:end])
        for start, end in document_ranges
    ])
    return documents / np.linalg.norm(documents, axis=1, keepdims=True)


def main():
    data_dir = Path(__file__).resolve().parent / "data"
    vacancies = pd.read_csv(data_dir / "5_vacancies.csv")
    resume_paths = sorted(
        (data_dir / "raw_resumes").glob("*.docx"),
        key=lambda path: int(path.stem),
    )
    candidate_ids = [int(path.stem) for path in resume_paths]
    resume_texts = [extract_docx_text(path) for path in resume_paths]
    vacancy_texts = [
        f"{job.job_title}\n{job.job_description}"
        for job in vacancies.itertuples(index=False)
    ]

    model = SentenceTransformer("all-MiniLM-L6-v2")
    candidate_vectors = embed_documents(model, resume_texts)
    vacancy_vectors = embed_documents(model, vacancy_texts)
    # The embeddings have unit length, so their dot products give cosine similarity.
    similarities = candidate_vectors @ vacancy_vectors.T

    rankings = []
    for candidate_id, scores in zip(candidate_ids, similarities, strict=True):
        # Stable sorting keeps vacancies in CSV order when their scores tie.
        job_indices = np.argsort(-scores, kind="stable")
        for rank, job_index in enumerate(job_indices, start=1):
            vacancy = vacancies.iloc[job_index]
            rankings.append({
                "candidate_id": candidate_id,
                "vacancy_number": job_index + 1,
                "vacancy_id": vacancy["id"],
                "job_title": vacancy["job_title"],
                "semantic_score": scores[job_index],
                "ai_rank": rank,
            })

    results = pd.DataFrame(rankings)
    output_path = data_dir / "ai_rankings.csv"
    results.to_csv(output_path, index=False, float_format="%.8f")
    print(f"Saved {len(results)} rankings for {len(candidate_ids)} candidates to {output_path}.")
    print(results.head(len(vacancies)).to_string(index=False))


if __name__ == "__main__":
    main()
