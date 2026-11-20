"""Layer 1: yt-dlp support for known media sites (SoundCloud, YouTube, VK, Bandcamp...)."""
from typing import List

import yt_dlp
from .base import BaseParser, Track

KNOWN_DOMAINS = (
    "soundcloud.com", "youtu.be", "youtube.com", "vk.com", "vkvideo.ru",
    "bandcamp.com", "audius.co", "mixcloud.com", "douyin.com", "tiktok.com",
)


class YtDlpParser(BaseParser):
    def can_handle(self, url: str) -> bool:
        host = __import__("urllib.parse").urlparse(url).hostname or ""
        return host.endswith(KNOWN_DOMAINS) if host else False

    def extract(self, url: str) -> List[Track]:
        ydl_opts = {
            "quiet": True,
            "extract_flat": False,
            "nocheckcertificate": True,
            "skip_download": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        if not info:
            return []
        entries = info.get("entries") or [info]
        tracks: List[Track] = []
        for entry in entries:
            if not entry:
                continue
            title = entry.get("title") or "Audio track"
            formats = entry.get("formats") or []
            audio_url = ""
            best_audio = None
            for fmt in formats:
                acodec = fmt.get("acodec")
                abr = fmt.get("abr") or 0
                if acodec and acodec != "none" and abr > 0:
                    if best_audio is None or abr > best_audio.get("abr", 0):
                        best_audio = fmt
            if best_audio and best_audio.get("url"):
                audio_url = best_audio["url"]
            if not audio_url:
                audio_url = entry.get("url") or ""
            if not audio_url:
                continue
            tracks.append(Track(title=title, url=audio_url, source_url=entry.get("webpage_url") or url,
                                extension=best_audio.get("ext", "m4a")))
        return tracks
