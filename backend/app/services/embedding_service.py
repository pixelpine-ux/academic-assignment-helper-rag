import os
from typing import List
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536


def get_embedding(text: str) -> List[float]:
    """
    Convert a string of text into a 1536-dimensional vector using OpenAI embeddings.
    Raises a clear exception on any failure — never returns silently.
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or api_key.startswith("sk-your"):
        raise ValueError(
            "OPENAI_API_KEY is not configured. Set a valid key in your .env file."
        )

    client = OpenAI(api_key=api_key)

    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text.strip()
        )
        return response.data[0].embedding

    except AuthenticationError:
        raise ValueError("Invalid OpenAI API key. Check your OPENAI_API_KEY in .env.")
    except RateLimitError:
        raise RuntimeError("OpenAI rate limit reached. Try again shortly.")
    except APIConnectionError:
        raise RuntimeError("Could not connect to OpenAI API. Check your internet connection.")
