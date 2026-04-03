"""VLM-based sticker tagging."""

import json
import base64
import httpx
from pathlib import Path

from .config import TAGGING_PROMPT, VLM_PROVIDER, GEMINI_API_KEY, GEMINI_MODEL


def _encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def _mime_from_ext(ext: str) -> str:
    return {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".gif": "image/gif",
        ".webp": "image/webp", ".bmp": "image/bmp",
    }.get(ext, "image/jpeg")


async def tag_image_gemini(image_path: str) -> dict:
    """Tag an image using Gemini API."""
    import google.generativeai as genai

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)

    image_bytes = Path(image_path).read_bytes()
    ext = Path(image_path).suffix.lower()

    response = await model.generate_content_async(
        [
            {"inline_data": {"mime_type": _mime_from_ext(ext), "data": image_bytes}},
            TAGGING_PROMPT,
        ],
        generation_config={"temperature": 0.1, "response_mime_type": "application/json"},
    )

    return json.loads(response.text)


async def tag_image(image_path: str) -> dict:
    """Tag an image, returns {description, emotion, scene, tags}."""
    if VLM_PROVIDER == "gemini":
        return await tag_image_gemini(image_path)
    raise ValueError(f"Unsupported VLM provider: {VLM_PROVIDER}")


def build_search_text(tags: dict) -> str:
    """Build a search-friendly text from tagging results."""
    parts = [
        tags.get("description", ""),
        tags.get("emotion", ""),
        tags.get("scene", ""),
        " ".join(tags.get("tags", [])),
    ]
    return " ".join(p for p in parts if p)
