import aiofiles
from fastapi import FastAPI, UploadFile

from backend import store
from backend.evaluate import run_eval
from backend.generate import generate_answer
from backend.ingest import chunk_pdf
from backend.retrieval import hybrid_search
from backend.verify import verify_citations

app = FastAPI()


@app.post("/upload")
async def upload(file: UploadFile):
    # save pannu
    contents = await file.read()
    save_path = f"data/uploads/{file.filename}"
    async with aiofiles.open(save_path, "wb") as f:
        await f.write(contents)
    # chunk the pdf
    new_chunks = chunk_pdf(save_path)
    store.chunks.extend(new_chunks)
    return {"chunks_added": len(new_chunks)}


@app.post("/chat")
async def chat(body: dict):
    # body is {"query": "..."} -- pull query = body["query"]
    # run hybrid_search(query, store.chunks, k=...) to get top chunk IDs
    # look up the actual chunk dicts for those IDs from store.chunks
    # call generate_answer(query, top_chunks)
    # call verify_citations(answer, store.chunks)
    # return {"answer": ..., "citations": ..., "citation_accuracy": ...}
    # per the API shape in project notes
    query = body["query"]
    top_chunks = hybrid_search(query, store.chunks, k=5)
    top_chunk_dicts = [chunk for chunk in store.chunks if chunk["id"] in top_chunks]
    answer = generate_answer(query, top_chunk_dicts)
    citations = verify_citations(answer, store.chunks)
    return {"answer": answer, "citations": citations, "citation_accuracy": citations["citation_accuracy"]}


@app.post("/eval")
async def eval_endpoint():
    return run_eval(store.chunks, k=5)
