import re

import pymupdf4llm


def chunk_pdf(path: str) -> list[dict]:
    pages = pymupdf4llm.to_markdown(path, page_chunks=True)  # type: ignore[assignment]
    chunks = []
    chunk_id = 0
    for page in pages:
        page_num = page["metadata"]["page_number"] - 1  # type: ignore[index]
        blocks = re.split(r"\n\s*\n", page["text"])  # type: ignore[index]
        for block in blocks:
            stripped_text = block.strip()
            if len(stripped_text.split()) < 4:
                continue
            is_heading = stripped_text.startswith("#")
            chunks.append({
                "id": f"C{chunk_id}",
                "text": stripped_text,
                "source": path,
                "page": page_num,
                "is_heading": is_heading,
            })
            chunk_id += 1
    return _merge_heading_with_body(chunks)


def _merge_heading_with_body(chunks: list[dict]) -> list[dict]:
    merged_chunks = []
    i = 0
    while i < len(chunks):
        current = chunks[i]
        if current["is_heading"] and i + 1 < len(chunks) and not chunks[i + 1]["is_heading"]:
            current["text"] += " " + chunks[i + 1]["text"]
            merged_chunks.append(current)
            i += 2
        else:
            merged_chunks.append(current)
            i += 1
    for idx, chunk in enumerate(merged_chunks):
        chunk["id"] = f"C{idx}"
    return merged_chunks
