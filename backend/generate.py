import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

llm_prompt = (
    "Answer the question using ONLY the context below. "
    "Tag every claim/sentence with the chunk ID it came from, "
    "e.g. 'Photosynthesis converts light into energy [C4].' "
    "If the context doesn't cover the question, say you don't know "
    "instead of guessing.\n\n"
    "Context:\n{context}\n\n"
    "Question: {query}\n\n"
    "Answer:"
)

client = Groq(api_key=os.environ["GROQ_API_KEY"])
model = "llama-3.1-8b-instant"


def generate_answer(query: str, chunks: list[dict]) -> str:
    # Two separate claims here, don't conflate them:
    #   - The retrieve-then-generate PATTERN (feed retrieved chunks into an
    #     LLM to answer, closed-book) is Lewis et al. 2020, "Retrieval-
    #     Augmented Generation for Knowledge-Intensive NLP Tasks" --
    #     https://arxiv.org/abs/2005.11401 -- the paper the whole RAG
    #     architecture is named after.
    #   - The specific inline [C_id] citation-tagging PROMPT DESIGN is namma choice
    context = "\n".join([f"[{chunk['id']}] {chunk['text']}" for chunk in chunks])
    prompt = llm_prompt.format(context=context, query=query)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    content = response.choices[0].message.content
    if content is None:
        raise RuntimeError("Groq returned nothing")
    return content
