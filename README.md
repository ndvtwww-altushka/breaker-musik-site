# Breaker Musik Site

A local music extractor that finds audio tracks from any public URL. Built with FastAPI, yt-dlp, and a layered parsing approach.

## Features

- **Layer 1** — yt-dlp for known platforms (SoundCloud, YouTube, VK, Bandcamp, etc.)
- **Layer 2** — HTML scanner for direct audio links, `<audio>` tags, JSON-LD, og:audio
- **Layer 3** — Shallow crawler to find track pages on the same host
- **Layer 4** (optional) — Playwright for JS-rendered pages
- **Web UI** — Dark, minimal interface for pasting URLs and playing/downloading tracks
- **Docker-ready** — One command to run

## Quick Start

```bash
# With Docker
docker compose up --build

# Or locally
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000

## API

```
POST /api/parse      - Extract tracks from a URL (form: url)
GET  /api/stream     - Proxy stream audio (query: url)
GET  /api/download   - Download audio with filename (query: url, title)
GET  /health         - Health check
```

## Enable Playwright (Layer 4)

```bash
# Install browsers
playwright install chromium

# Run with env
ENABLE_PLAYWRIGHT=1 uvicorn app:app
```

## How it Works

```
URL → ParserRegistry
     ├─ YtDlpParser (known domains)     → Track[]
     ├─ HTMLScanner (static HTML)       → Track[]
     ├─ Crawler (same-host links)       → Track[]
     └─ PlaywrightParser (if enabled)   → Track[]
```

First parser returning tracks wins.

## Tech Stack

- **FastAPI** + **Uvicorn**
- **yt-dlp** for media extraction
- **requests** + **BeautifulSoup** (HTMLScanner)
- **Playwright** (optional)
- **Pico.css** for UI
