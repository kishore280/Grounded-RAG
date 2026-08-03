import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi


def dense_search(query: str, chunks: list[dict], k: int) -> list[str]:
    # Sentence-BERT (Reimers & Gurevych 2019, https://arxiv.org/abs/1908.10084)
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = model.encode(query)
    chunk_texts = [chunk["text"] for chunk in chunks]
    chunk_embeddings = model.encode(chunk_texts)
    similarities = np.dot(chunk_embeddings, query_embedding) / (
        np.linalg.norm(chunk_embeddings, axis=1) * np.linalg.norm(query_embedding)
    )
    ranked = sorted(zip(chunks, similarities), key=lambda pair: pair[1], reverse=True)
    return [chunk["id"] for chunk, _ in ranked[:k]]
    


def bm25_search(query: str, chunks: list[dict], k: int) -> list[str]:
    # tokenize each chunk's text (simple .split() or basic word tokenization)
    # build BM25Okapi index over tokenized chunks
    # tokenize the query the same way, get BM25 scores per chunk
    # sort chunks by score descending, return top-k chunk IDs
    pass


def hybrid_search(query: str, chunks: list[dict], k: int) -> list[str]:
    # get ranked chunk ID lists from dense_search and bm25_search (rank k high
    # enough to cover fusion candidates, not just final k)
    # apply Reciprocal Rank Fusion: for each chunk ID, score = sum over each
    # ranking list of 1 / (rank_constant + rank_in_that_list), rank_constant
    # usually 60
    # sort chunk IDs by fused RRF score descending, return top-k
    pass
