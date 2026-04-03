# Moji 🍑

Multimodal RAG engine for sticker search. Drop your memes, get a semantic search API. Bot-agnostic.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌───────────┐
│  Sticker     │────▶│  Indexer     │────▶│  ChromaDB  │
│  Collection  │     │  (VLM tag)   │     │  + Meta    │
└─────────────┘     └──────────────┘     └─────┬─────┘
                                               │
┌─────────────┐     ┌──────────────┐            │
│  Client /   │────▶│  Search API  │◀───────────┘
│  Bot        │     │  (FastAPI)   │
└─────────────┘     └──────────────┘
```

## Quick Start

### 1. Install

```bash
pip install -r requirements.txt
```

### 2. Index stickers

```bash
# Point to your sticker folder
python -m moji.index --input ./stickers/ --provider gemini
```

### 3. Start search API

```bash
python -m moji.server
# API available at http://localhost:8000
```

### 4. Search

```bash
curl "http://localhost:8000/search?q=开心&top_k=3"
```

## API

### `GET /search`

| Param  | Type   | Default | Description          |
|--------|--------|---------|----------------------|
| q      | string | —       | Search query (text)  |
| top_k  | int    | 3       | Number of results    |
| threshold | float | 0.3  | Min similarity score |

**Response:**

```json
{
  "results": [
    {
      "file": "stickers/happy_cat.gif",
      "description": "一只猫咪开心地转圈，表达极度快乐",
      "tags": ["开心", "快乐", "猫咪", "转圈"],
      "score": 0.92
    }
  ]
}
```

### `POST /index`

Upload and index a single sticker on the fly.

### `GET /health`

Health check.

## Configuration

```bash
# Environment variables
export GEMINI_API_KEY=your_key          # For VLM tagging
export EMBEDDING_PROVIDER=gemini        # or "local" for BGE-M3
export CHROMA_PERSIST_DIR=./data        # Vector DB storage
```

## License

MIT
