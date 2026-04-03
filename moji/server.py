"""Moji search API."""

import base64
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .store import StickerStore
from .config import DEFAULT_TOP_K, DEFAULT_THRESHOLD

app = FastAPI(title="Moji", version="0.1.0", description="🍑 Multimodal RAG engine for sticker search")
store = StickerStore()


@app.get("/search")
async def search(
    q: str = Query(..., description="Search query"),
    top_k: int = Query(DEFAULT_TOP_K, ge=1, le=20),
    threshold: float = Query(DEFAULT_THRESHOLD, ge=0.0, le=1.0),
):
    results = await store.search(q, top_k=top_k, threshold=threshold)
    # Return base64-encoded image for each result
    for r in results:
        img_path = Path(r["file"])
        if img_path.exists():
            with open(img_path, "rb") as f:
                r["image_b64"] = base64.b64encode(f.read()).decode()
            r["filename"] = img_path.name
        else:
            r["image_b64"] = None
            r["filename"] = img_path.name
    return {"query": q, "results": results}


class IndexRequest(BaseModel):
    file_path: str


@app.post("/index")
async def index_single(req: IndexRequest):
    from .tagger import tag_image, build_search_text

    try:
        tags = await tag_image(req.file_path)
        search_text = build_search_text(tags)
        doc_id = await store.add(req.file_path, search_text, tags)
        return {"status": "ok", "id": doc_id, "tags": tags}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.get("/health")
async def health():
    return {"status": "ok", "indexed": store.count}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("moji.server:app", host="0.0.0.0", port=8000, reload=True)
