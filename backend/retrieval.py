import re

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer


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
    # RRF (Cormack, Clarke & Buettcher, SIGIR 2009 --
    # https://dl.acm.org/doi/10.1145/1571941.1572114 -- 
    dense_ranked = dense_search(query, chunks, k=20)
    bm25_ranked = bm25_search(query, chunks, k=20)
    ranked_ids = set(dense_ranked + bm25_ranked)
    fused_scores = {}
    for chunk_id in ranked_ids:
        score = 0
        for ranked_list in [dense_ranked, bm25_ranked]:
            if chunk_id in ranked_list:
                rank = ranked_list.index(chunk_id) + 1
                score += 1 / (60 + rank)
        fused_scores[chunk_id] = score
    ranked = sorted(fused_scores.items(), key=lambda pair: pair[1], reverse=True)
    return [chunk_id for chunk_id, _ in ranked[:k]]
