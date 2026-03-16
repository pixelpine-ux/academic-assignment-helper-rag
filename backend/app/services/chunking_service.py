from typing import List
import tiktoken

CHUNK_SIZE = 500      # tokens per chunk
CHUNK_OVERLAP = 100   # tokens shared between consecutive chunks
ENCODING_MODEL = "cl100k_base"  # the tokenizer OpenAI uses for text-embedding-3-small


def chunk_text(text: str) -> List[str]:
    """
    Split text into overlapping chunks of ~500 tokens each.
    Returns a list of strings ready to be embedded individually.
    """
    if not text or not text.strip():
        raise ValueError("Cannot chunk empty text.")

    encoder = tiktoken.get_encoding(ENCODING_MODEL)
    tokens = encoder.encode(text)

    if len(tokens) <= CHUNK_SIZE:
        return [text]

    chunks = []
    start = 0

    while start < len(tokens):
        end = start + CHUNK_SIZE
        chunk_tokens = tokens[start:end]
        chunks.append(encoder.decode(chunk_tokens))
        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks
