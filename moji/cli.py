"""CLI entry points."""

import argparse
import asyncio
import uvicorn


def main():
    parser = argparse.ArgumentParser(prog="moji", description="🍑 Moji — Sticker search engine")
    sub = parser.add_subparsers(dest="command")

    # Index
    idx = sub.add_parser("index", help="Index sticker folder")
    idx.add_argument("--input", "-i", required=True, help="Sticker folder or file")
    idx.add_argument("--concurrency", "-c", type=int, default=5)
    idx.add_argument("--provider", "-p", default="gemini", help="VLM provider")

    # Serve
    srv = sub.add_parser("serve", help="Start search API server")
    srv.add_argument("--host", default="0.0.0.0")
    srv.add_argument("--port", type=int, default=8000)

    args = parser.parse_args()

    if args.command == "index":
        if args.provider:
            import moji.config as cfg
            cfg.VLM_PROVIDER = args.provider
        from moji.index import index_folder
        asyncio.run(index_folder(args.input, args.concurrency))

    elif args.command == "serve":
        uvicorn.run("moji.server:app", host=args.host, port=args.port, reload=True)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
