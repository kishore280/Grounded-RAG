import fitz


def chunk_pdf(path: str) -> list[dict]:
    # open doc with fitz
    doc = fitz.open(path)
    chunks = []
    chunk_id = 0
    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("blocks")
        for block in blocks:
            text = block[4]
            block_type = block[6]
            if block_type != 0:
                continue
            # word count, not char count -- char count drops short-but-real
            # lines like dates on sparse docs (e.g. certificates)
            if len(text.split()) < 4:
                continue
            stripped_text = text.strip()
            is_heading = len(stripped_text) < 80 and not stripped_text.endswith((":", "?", "!","."))
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
