import re


def _meaningful_words(text: str) -> set[str]:
    return {w for w in re.findall(r"\w+", text.lower()) if len(w) > 3}


def verify_citations(answer: str, chunks: list[dict]) -> dict:
    claims = re.split(r"\.\s*", answer)
    claims = [claim.strip() for claim in claims if claim.strip()]
    chunk_ids = [re.findall(r"\[(C\d+)\]", claim) for claim in claims]
    chunk_id_sets = [set(ids) for ids in chunk_ids]
    chunk_id_dict = {chunk['id']: chunk['text'] for chunk in chunks}
    passed_claims = 0
    total_claims = len(claims)
    per_claim_results = []
    for claim, chunk_id_set in zip(claims, chunk_id_sets):
        shared_words = 0
        for chunk_id in chunk_id_set:
            if chunk_id in chunk_id_dict:
                shared_words += len(_meaningful_words(claim) & _meaningful_words(chunk_id_dict[chunk_id]))
        passed_claims += shared_words >= 2
        per_claim_results.append({"claim": claim, "chunk_ids": list(chunk_id_set), "shared_words": shared_words, "result": shared_words >= 2})
    citation_accuracy = passed_claims / total_claims
    return {"citation_accuracy": citation_accuracy, "per_claim_results": per_claim_results}
