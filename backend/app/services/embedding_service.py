import os
from typing import List
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError
import hashlib

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536


def get_embedding(text: str) -> List[float]:
    """
    Convert a string of text into a 1536-dimensional vector using OpenAI embeddings.
    Falls back to deterministic mock embeddings if OpenAI key is not configured.
    """
    api_key = os.getenv("OPENAI_API_KEY")

    # Mock mode for testing without OpenAI
    if not api_key or api_key.startswith("sk-your"):
        print("⚠️  Using mock embeddings (OpenAI key not configured)")
        return _generate_mock_embedding(text)

    client = OpenAI(api_key=api_key)

    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text.strip()
        )
        return response.data[0].embedding

    except AuthenticationError:
        print("⚠️  Invalid OpenAI key, falling back to mock embeddings")
        return _generate_mock_embedding(text)
    except RateLimitError:
        raise RuntimeError("OpenAI rate limit reached. Try again shortly.")
    except APIConnectionError:
        raise RuntimeError("Could not connect to OpenAI API. Check your internet connection.")


def _generate_mock_embedding(text: str) -> List[float]:
    """
    Generate deterministic mock embedding for testing.
    Uses hash of text to create consistent 1536-dim vector.
    """
    # Create deterministic seed from text
    text_hash = hashlib.sha256(text.encode()).digest()
    
    # Generate 1536 floats between -1 and 1
    embedding = []
    for i in range(EMBEDDING_DIMENSIONS):
        # Use hash bytes to generate pseudo-random but deterministic values
        byte_val = text_hash[i % len(text_hash)]
        normalized = (byte_val / 255.0) * 2 - 1  # Scale to [-1, 1]
        embedding.append(normalized)
    
    return embedding
