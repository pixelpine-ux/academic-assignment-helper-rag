import os
from typing import List
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError
from models import DocumentChunk

LLM_MODEL = "gpt-3.5-turbo"
MAX_CONTEXT_CHUNKS = 5


def generate_answer(question: str, chunks: List[DocumentChunk]) -> dict:
    """
    Build a prompt from retrieved chunks and ask the LLM to answer the question.
    Returns the answer text and the source document IDs used.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key.startswith("sk-your"):
        raise ValueError("OPENAI_API_KEY is not configured. Set a valid key in your .env file.")

    context_blocks = []
    for i, chunk in enumerate(chunks[:MAX_CONTEXT_CHUNKS], start=1):
        context_blocks.append(
            f"[Source {i} — Document ID {chunk.document_id}, Chunk {chunk.chunk_index}]\n{chunk.chunk_text}"
        )
    context = "\n\n---\n\n".join(context_blocks)

    prompt = (
        "You are an academic assistant. Answer the question below using ONLY the provided sources. "
        "Cite the source number (e.g. [Source 1]) when you use information from it. "
        "If the answer cannot be found in the sources, say so explicitly.\n\n"
        f"Sources:\n{context}\n\n"
        f"Question: {question}"
    )

    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,  # low temperature = more factual, less creative
        )
    except AuthenticationError:
        raise ValueError("Invalid OpenAI API key. Check your OPENAI_API_KEY in .env.")
    except RateLimitError:
        raise RuntimeError("OpenAI rate limit reached. Try again shortly.")
    except APIConnectionError:
        raise RuntimeError("Could not connect to OpenAI API. Check your internet connection.")

    return {
        "answer": response.choices[0].message.content,
        "source_document_ids": list({chunk.document_id for chunk in chunks}),
        "chunks_used": len(chunks),
    }
