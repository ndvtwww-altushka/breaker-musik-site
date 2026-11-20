"""Breaker Musik Site — local music scraper.

Layers:
  1. yt-dlp      (known media sites)
  2. HTML scanner (curl_cffi / requests + regex + JSON-LD)
  3. Crawler     (shallow crawl of same-host pages)
  4. Playwright  (optional, ENABLE_PLAYWRIGHT=1)
"""
import os
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
import requests

from parsers.registry import ParserRegistry
from parsers.ytdlp_parser import YtDlpParser
from parsers.html_scanner import HTMLScanner
from parsers.crawler import Crawler
from parsers.playwright_parser import PlaywrightParser
from parsers.network import fetch_url, is_public_url

app = FastAPI(title="Breaker Musik Site")

STATIC_DIR = Path(__file__).resolve().parent / "static"
INDEX = STATIC_DIR / "index.html"

session = requests.Session()
session.headers["User-Agent"] = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

registry = ParserRegistry([
    YtDlpParser(),
    HTMLScanner(session=session),
    Crawler(session=session),
    PlaywrightParser(),
])


@app.get("/", response_class=HTMLResponse)
async def index():
    if not INDEX.exists():
        raise HTTPException(500, "static/index.html not found")
    return HTMLResponse(INDEX.read_text(encoding="utf-8"))


@app.get("/static/{name}")
async def static_file(name: str):
    path = (STATIC_DIR / name).resolve()
    if not path.is_file() or not path.is_relative_to(STATIC_DIR):
        raise HTTPException(404, "Not found")
    return FileResponse(path)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/parse")
async def parse(url: str = Form(...)):
    if not is_public_url(url):
        raise HTTPException(400, "Only public http(s) URLs are supported")
    tracks = registry.extract(url)
    seen, out = set(), []
    for t in tracks:
        if t.url in seen:
            continue
        seen.add(t.url)
        out.append({
            "title": t.title or "audio",
            "url": t.url,
            "source_url": t.source_url,
            "duration": t.duration,
            "bitrate": t.bitrate,
            "extension": t.extension,
        })
    return {"tracks": out}


@app.get("/api/stream")
async def stream(url: str):
    if not is_public_url(url):
        raise HTTPException(400, "Only public http(s) URLs are supported")
    page = _guess_referer(url)
    upstream = session.get(url, stream=True, timeout=(5, 30), headers={
        "Referer": page,
        "Accept": "*/*",
    })
    if upstream.status_code >= 400:
        raise HTTPException(upstream.status_code, "Upstream error")

    def chunked():
        try:
            for chunk in upstream.iter_content(chunk_size=65536):
                yield chunk
        finally:
            upstream.close()

    headers = {"Accept-Ranges": "bytes"}
    content_type = upstream.headers.get("Content-Type", "audio/mpeg")
    if "charset" in content_type:
        content_type = content_type.split(";")[0].strip()
    if "content-length" in upstream.headers:
        headers["Content-Length"] = upstream.headers["content-length"]
    return StreamingResponse(chunked(), status_code=200, media_type=content_type, headers=headers)


@app.get("/api/download")
async def download(url: str, title: str = ""):
    if not is_public_url(url):
        raise HTTPException(400, "Only public http(s) URLs are supported")
    upstream = session.get(url, stream=True, timeout=(5, 30), headers={"Referer": _guess_referer(url)})
    if upstream.status_code >= 400:
        raise HTTPException(upstream.status_code, "Upstream error")

    def chunked():
        try:
            for chunk in upstream.iter_content(chunk_size=65536):
                yield chunk
        finally:
            upstream.close()

    safe = "".join(c for c in (title or "audio").strip() if c.isprintable()).replace("/", "-")[:120]
    ext = url.rsplit(".", 1)[-1].lower().split("?")[0]
    if ext not in ("mp3", "m4a", "aac", "ogg", "opus", "wav", "flac", "webm"):
        ext = "mp3"
    filename = f"{safe}.{ext}" if safe else f"audio.{ext}"
    return StreamingResponse(
        chunked(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": 'attachment; filename="{filename}"'},
    )


def _guess_referer(url: str) -> str:
    host = url.split("/")[2] if len(url.split("/")) > 2 else ""
    return f"https://{host}/"