"""Embedding provider."""

from .config import EMBEDDING_PROVIDER, GEMINI_API_KEY, EMBEDDING_MODEL


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts."""
    if EMBEDDING_PROVIDER == "gemini":
        return await _embed_gemini(texts)
    raise ValueError(f"Unsupported embedding provider: {EMBEDDING_PROVIDER}")


async def embed_query(text: str) -> list[float]:
    """Embed a single query string."""
    results = await embed_texts([text])
    return results[0]


async def _embed_gemini(texts: list[str]) -> list[list[float]]:
    import google.generativeai as genai

    genai.configure(api_key=GEMINI_API_KEY)
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=texts,
        task_type="retrieval_query" if len(texts) == 1 else "RETRIEVAL_DOCUMENT",
    )
    if len(texts) == 1:
        return [result["embedding"]]
    return [e["embedding"] for e in result["embedding"]]
