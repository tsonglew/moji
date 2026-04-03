"""Moji 🍑 — Multimodal RAG engine for sticker search."""

from .tagger import tag_image, build_search_text
from .store import StickerStore
from .embedder import embed_texts, embed_query

__all__ = ["tag_image", "build_search_text", "StickerStore", "embed_texts", "embed_query"]
__version__ = "0.1.0"
