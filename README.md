# Grounded RAG

NotebookLM-style RAG app: upload a PDF, ask questions, get answers where every
claim is tagged with the exact source chunk it came from and lexically
verified against it. Hybrid (dense + sparse) retrieval, hand-written, no
LangChain/LlamaIndex — every stage is explainable at the code level.

## Architecture

```
PDF upload
  -> ingest.py      chunk_pdf(): pymupdf4llm markdown extraction,
                     paragraph/heading-aware chunking
  -> retrieval.py    dense_search() + bm25_search() fused via
                     hybrid_search() (Reciprocal Rank Fusion)
  -> generate.py     LLM answers from retrieved chunks only, tags
                     each claim with its source chunk ID: "... [C4]"
  -> verify.py       lexical grounding check: does the cited chunk
                     actually share meaningful words with the claim?
  -> evaluate.py     runs eval/eval_set.json, reports precision@k
                     (dense vs hybrid) and citation accuracy
```

FastAPI backend (`backend/main.py`): `POST /upload`, `POST /chat`, `POST /eval`.
React + Vite + TanStack Query frontend (`frontend/`).

## Stack

- `pymupdf4llm` — PDF -> Markdown extraction (preserves table structure)
- `sentence-transformers` (all-MiniLM-L6-v2) — dense embeddings
- `rank_bm25` — sparse/keyword retrieval
- Groq (`llama-3.1-8b-instant`) — generation, hosted free tier
- `numpy` — cosine similarity
- No vector DB (in-memory store, fine at this corpus size), no paid APIs

## Paper references

- Retrieve-then-generate architecture: Lewis et al. 2020,
  https://arxiv.org/abs/2005.11401
- Dense retrieval: Reimers & Gurevych 2019 (Sentence-BERT),
  https://arxiv.org/abs/1908.10084
- Sparse retrieval: Robertson & Zaragoza 2009 (BM25),
  https://www.nowpublishers.com/article/Details/INR-019
- Fusion: Cormack, Clarke & Buettcher 2009 (Reciprocal Rank Fusion),
  https://dl.acm.org/doi/10.1145/1571941.1572114
- Citation tagging + lexical grounding check: no single paper, own design
  choice, informed by the general faithfulness/attribution literature

## Design decisions

- **Inline citation tagging** in one generation pass, not a separate
  "find supporting quote" pass — cheaper, one LLM call instead of two.
- **Lexical grounding check** (shared meaningful words, >3 chars, >=2
  shared) instead of LLM-as-judge — cheap, fast, directionally useful
  first-pass check. Known limitation: paraphrased-but-correct answers can
  under-score (fewer literal shared words), and short claims (dates,
  numbers) initially failed structurally until the word-length threshold
  was tuned down from >4 to >3 chars.
- **PyMuPDF4LLM over raw PyMuPDF block extraction** — found live in
  testing that raw block extraction splits table label/value columns into
  disconnected chunks (a train ticket's "Total Fare" question answered "I
  don't know" because the label and the number were in separate chunks).
  Switched extraction to PyMuPDF4LLM, which preserves table rows as
  correctly-paired Markdown table syntax.
- **Word-count, not char-count, chunk filter** — found live in testing
  that filtering short blocks by character count (`< 30 chars`) drops
  real content on sparse documents (a certificate's completion date,
  `"Awarded on\nJuly 21, 2022"`, is 24 characters but 5 real words).
  Switched to a word-count filter (`< 4 words`), which matches how
  production RAG chunking guides actually do this.
- **No vector DB** — brute-force cosine similarity over a few hundred
  chunks is fast enough; a vector DB solves a scale problem this project
  doesn't have yet.

## Known limitations

- **Context dilution on merged tables.** Fixing the table label/value
  split (above) merges an entire table's rows into one chunk when there
  are no blank lines between them. A 5-row marks-allocation table became
  one chunk — correct for "what's the total," but diluted retrieval
  precision for narrow sub-questions embedded in one row of that table
  (e.g. "marks for IIT/IISc candidates" scored 0.0 precision@5 in eval,
  despite the answer being present in the retrieved chunk's text). A
  documented RAG failure mode, not a bug: keeping tables intact (for
  correctness) trades off against keeping chunks small (for retrieval
  precision). Next step: row-level table chunking that still keeps each
  row's label+value paired.
- **Bilingual/Devanagari text extraction** occasionally garbles ligatures
  in the source PDF's font — a PyMuPDF/font-mapping limitation, not a
  chunking bug. English text in the same documents extracts cleanly.
- **Lexical verification false negatives on paraphrase.** A correct
  answer that rewords the source ("fee amount" vs the source's plain
  "Fee") can score below the shared-word threshold despite being right.
- No LLM-as-judge verification, no persistence across restarts, no
  auth/multi-user, not publicly hosted — all explicitly out of scope for
  this build.

## Eval results (GATE PDF, 20 hand-written Q/A pairs, k=5)

```
precision_at_k_dense:  0.17
precision_at_k_hybrid: 0.17
citation_accuracy:     0.69
```

Dense and hybrid tied on this eval set — for most of these queries the
correct chunk is strong enough that both methods surface it independently,
so RRF fusion isn't adding much *for this particular set*. On an earlier,
smaller eval set hybrid did rescue two dense misses on keyword-heavy
queries (vocabulary mismatch), and lost slightly on one broad conceptual
query — hybrid's advantage is query-dependent, not universal, and that
nuance is worth stating plainly rather than claiming a clean win.

Run it live: `POST /eval` (needs a PDF already uploaded via `/upload`).

## Running it

```
python -m venv venv
venv/Scripts/pip install -r requirements.txt   # fastapi, uvicorn, python-multipart,
                                                # pymupdf4llm, sentence-transformers,
                                                # rank_bm25, numpy, groq, python-dotenv, aiofiles
```

`.env`: `GROQ_API_KEY=...` (free key at console.groq.com)

```
uvicorn backend.main:app --reload      # backend on :8000
cd frontend && npm install && npm run dev   # frontend on :5173
```
