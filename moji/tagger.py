"""ZhipuAI GLM-5V-based sticker tagging."""

import json
import base64
import httpx
from pathlib import Path

from .config import ZHIPUAI_API_KEY, VLM_MODEL, TAGGING_PROMPT

_CHAT_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"


def _encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def _mime_from_ext(ext: str) -> str:
    return {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".gif": "image/gif",
        ".webp": "image/webp", ".bmp": "image/bmp",
    }.get(ext, "image/jpeg")


async def tag_image(image_path: str) -> dict:
    """Tag an image using GLM-5V. Returns {description, emotion, scene, tags}."""
    ext = Path(image_path).suffix.lower()
    b64 = _encode_image(image_path)
    mime = _mime_from_ext(ext)

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            _CHAT_URL,
            headers={
                "Authorization": f"Bearer {ZHIPUAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": VLM_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:{mime};base64,{b64}"},
                            },
                            {"type": "text", "text": TAGGING_PROMPT},
                        ],
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 512,
            },
        )
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"]
        # Strip markdown code fences if present
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            text = text.rsplit("```", 1)[0] if "```" in text else text
        return json.loads(text.strip())


def build_search_text(tags: dict) -> str:
    """Build a search-friendly text from tagging results."""
    parts = [
        tags.get("description", ""),
        tags.get("emotion", ""),
        tags.get("scene", ""),
        " ".join(tags.get("tags", [])),
    ]
    return " ".join(p for p in parts if p)
