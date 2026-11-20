import re
import json
from typing import List
from .base import Track

class HTMLScanner:
    def __init__(self, session):
        self.session = session

    def extract(self, url: str) -> List[Track]:
        try:
            resp = self.session.get(url, timeout=(5, 30))
            if resp.status_code != 200:
                return []
            text = resp.text
            tracks = []
            # JSON-LD
            for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', text, re.S):
                try:
                    data = json.loads(m.group(1))
                    if isinstance(data, dict) and data.get("@type") == "AudioObject":
                        tracks.append(Track(url=data.get("contentUrl") or data.get("url"), title=data.get("name"), source_url=url))
                except Exception:
                    pass
            # <audio> tags
            for m in re.finditer(r'<audio[^>]*src="([^"]+)"', text):
                tracks.append(Track(url=m.group(1), source_url=url))
            # <a> links to audio files
            for m in re.finditer(r'<a[^>]*href="([^"]+\.(?:mp3|m4a|aac|ogg|opus|wav|flac|webm))"', text, re.I):
                tracks.append(Track(url=m.group(1), source_url=url))
            return tracks
        except Exception:
            return []
