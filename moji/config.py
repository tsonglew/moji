import os
from pathlib import Path

# === ZhipuAI Config ===
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY", "")

# VLM for tagging
VLM_MODEL = os.getenv("VLM_MODEL", "glm-5v-turbo")

# Embedding
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "embedding-3")
EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", "2048"))

# ChromaDB
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(Path(__file__).parent / "data"))

# Search defaults
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "3"))
DEFAULT_THRESHOLD = float(os.getenv("DEFAULT_THRESHOLD", "0.3"))

# Supported image extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}

# Tagging prompt
TAGGING_PROMPT = """请为这张表情包/贴纸图片生成结构化描述。严格按以下 JSON 格式输出，不要任何其他文字：

{
  "description": "用一两句话描述这张图片的内容和画面",
  "emotion": "主要表达的情绪（如：开心、无语、愤怒、惊讶、感动、搞笑等）",
  "scene": "适合在什么聊天场景下使用",
  "tags": ["关键词1", "关键词2", "关键词3", "关键词4"]
}"""
