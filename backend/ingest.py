import fitz


def chunk_pdf(path: str) -> list[dict]:
    # open doc with fitz
    # loop pages, get blocks with page.get_text("blocks")
    # skip block_type != 0 (images), skip text < 30 chars
    # append {"id": f"C{chunk_id}", "text": ..., "source": path, "page": ..., "is_heading": ...}
    # call _merge_heading_with_body before returning
    pass


def _merge_heading_with_body(chunks: list[dict]) -> list[dict]:
    # loop chunks, if current is_heading and next is not, merge their text
    # re-index IDs after merging
    pass
