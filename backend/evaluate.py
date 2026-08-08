import json

from backend.generate import generate_answer
from backend.retrieval import dense_search, hybrid_search
from backend.verify import verify_citations


def run_eval(chunks: list[dict], k: int = 5) -> dict:
    with open("eval/eval_set.json", encoding="utf-8") as f:
        eval_set = json.load(f)

    chunk_dict = {chunk["id"]: chunk for chunk in chunks}
    dense_precisions = []
    hybrid_precisions = []
    citation_accuracies = []
    per_question_results = []

    for item in eval_set:
        question = item["question"]
        relevant_ids = set(item["relevant_chunk_ids"])

        dense_ids = dense_search(question, chunks, k)
        hybrid_ids = hybrid_search(question, chunks, k)

        dense_precision = len(relevant_ids & set(dense_ids)) / k
        hybrid_precision = len(relevant_ids & set(hybrid_ids)) / k
        dense_precisions.append(dense_precision)
        hybrid_precisions.append(hybrid_precision)

        top_chunks = [chunk_dict[cid] for cid in hybrid_ids if cid in chunk_dict]
        answer = generate_answer(question, top_chunks)
        verification = verify_citations(answer, chunks)
        citation_accuracies.append(verification["citation_accuracy"])

        per_question_results.append({
            "question": question,
            "relevant_chunk_ids": list(relevant_ids),
            "dense_retrieved": dense_ids,
            "hybrid_retrieved": hybrid_ids,
            "dense_precision_at_k": dense_precision,
            "hybrid_precision_at_k": hybrid_precision,
            "answer": answer,
            "citation_accuracy": verification["citation_accuracy"],
        })

    return {
        "precision_at_k_dense": sum(dense_precisions) / len(dense_precisions),
        "precision_at_k_hybrid": sum(hybrid_precisions) / len(hybrid_precisions),
        "citation_accuracy": sum(citation_accuracies) / len(citation_accuracies),
        "per_question_results": per_question_results,
    }
