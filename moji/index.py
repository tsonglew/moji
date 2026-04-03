"""Batch index sticker folder."""

import asyncio
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from .config import IMAGE_EXTENSIONS
from .tagger import tag_image, build_search_text
from .store import StickerStore

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def collect_images(input_dir: str) -> list[Path]:
    p = Path(input_dir)
    if p.is_file():
        return [p]
    return sorted(f for f in p.rglob("*") if f.suffix.lower() in IMAGE_EXTENSIONS)


async def index_one(store: StickerStore, image_path: Path, semaphore: asyncio.Semaphore) -> bool:
    async with semaphore:
        try:
            log.info(f"  Tagging: {image_path.name}")
            tags = await tag_image(str(image_path))
            search_text = build_search_text(tags)
            await store.add(str(image_path), search_text, tags)
            log.info(f"  ✅ {image_path.name}: {tags.get('description', '')[:60]}")
            return True
        except Exception as e:
            log.error(f"  ❌ {image_path.name}: {e}")
            return False


async def index_folder(input_dir: str, concurrency: int = 5):
    images = collect_images(input_dir)
    if not images:
        log.error(f"No images found in {input_dir}")
        return

    log.info(f"Found {len(images)} images to index")
    store = StickerStore()
    semaphore = asyncio.Semaphore(concurrency)

    tasks = [index_one(store, img, semaphore) for img in images]
    results = await asyncio.gather(*tasks)

    ok = sum(results)
    log.info(f"\nDone! Indexed {ok}/{len(images)} stickers (total in DB: {store.count})")


def main():
    parser = argparse.ArgumentParser(description="Index sticker folder into Moji")
    parser.add_argument("--input", "-i", required=True, help="Sticker folder or file")
    parser.add_argument("--concurrency", "-c", type=int, default=5, help="Concurrent tagging requests")
    args = parser.parse_args()

    asyncio.run(index_folder(args.input, args.concurrency))


if __name__ == "__main__":
    main()
