"""ChromaDB-based sticker store."""

import uuid
import chromadb
from pathlib import Path

from .config import CHROMA_PERSIST_DIR
from .embedder import embed_texts, embed_query

COLLECTION_NAME = "stickers"


class StickerStore:
    def __init__(self, persist_dir: str | None = None):
        persist_dir = persist_dir or CHROMA_PERSIST_DIR
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=persist_dir)
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
        )

    @property
    def count(self) -> int:
        return self._collection.count()

    async def add(self, file_path: str, search_text: str, tags: dict) -> str:
        """Index a sticker. Returns the document ID."""
        doc_id = str(uuid.uuid5(uuid.NAMESPACE_URL, file_path))
        embedding = (await embed_texts([search_text]))[0]

        self._collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[search_text],
            metadatas=[{
                "file": file_path,
                "description": tags.get("description", ""),
                "emotion": tags.get("emotion", ""),
                "scene": tags.get("scene", ""),
                "tags": ",".join(tags.get("tags", [])),
            }],
        )
        return doc_id

    async def search(self, query: str, top_k: int = 3, threshold: float = 0.3) -> list[dict]:
        """Search stickers by text query."""
        query_embedding = await embed_query(query)

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        items = []
        if not results["ids"][0]:
            return items

        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            score = 1 - dist  # cosine distance → similarity
            if score >= threshold:
                items.append({
                    "file": meta["file"],
                    "description": meta["description"],
                    "tags": meta["tags"].split(",") if meta.get("tags") else [],
                    "emotion": meta.get("emotion", ""),
                    "scene": meta.get("scene", ""),
                    "score": round(score, 4),
                })
        return items

    def get_by_id(self, doc_id: str) -> dict | None:
        result = self._collection.get(ids=[doc_id], include=["metadatas"])
        if result["metadatas"]:
            return result["metadatas"][0]
        return None
