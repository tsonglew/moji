"""ZhipuAI embedding provider."""

import httpx
from .config import ZHIPUAI_API_KEY, EMBEDDING_MODEL, EMBEDDING_DIMENSIONS

_EMBED_URL = "https://open.bigmodel.cn/api/paas/v4/embeddings"


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings via ZhipuAI embedding-3."""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            _EMBED_URL,
            headers={
                "Authorization": f"Bearer {ZHIPUAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": EMBEDDING_MODEL,
                "input": texts,
                "dimensions": EMBEDDING_DIMENSIONS,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        # Sort by index to maintain order
        embeddings = sorted(data["data"], key=lambda x: x["index"])
        return [e["embedding"] for e in embeddings]


async def embed_query(text: str) -> list[float]:
    results = await embed_texts([text])
    return results[0]
