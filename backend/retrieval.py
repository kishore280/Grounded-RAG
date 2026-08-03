import re

import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


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
    # BM25 (Robertson & Zaragoza 2009, building on Robertson & Walker's
    # original 1994 SIGIR "Okapi" paper -- see also this writeup:
    # https://arpitbhayani.me/blogs/bm25/)
    tokenized_chunks = [_tokenize(chunk["text"]) for chunk in chunks]
    bm25 = BM25Okapi(tokenized_chunks)
    tokenized_query = _tokenize(query)
    scores = bm25.get_scores(tokenized_query)
    ranked = sorted(zip(chunks, scores), key=lambda pair: pair[1], reverse=True)
    return [chunk["id"] for chunk, _ in ranked[:k]]


def hybrid_search(query: str, chunks: list[dict], k: int) -> list[str]:
    # get ranked chunk ID lists from dense_search and bm25_search (rank k high
    # enough to cover fusion candidates, not just final k)
    # apply Reciprocal Rank Fusion: for each chunk ID, score = sum over each
    # ranking list of 1 / (rank_constant + rank_in_that_list), rank_constant
    # usually 60
    # sort chunk IDs by fused RRF score descending, return top-k
    pass
