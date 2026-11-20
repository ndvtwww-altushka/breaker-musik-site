import re
from urllib.parse import urljoin, urlparse
from typing import List
from .base import Track

class Crawler:
    def __init__(self, session, max_depth=1, max_pages=5):
        self.session = session
        self.max_depth = max_depth
        self.max_pages = max_pages

    def extract(self, url: str) -> List[Track]:
        from parsers.html_scanner import HTMLScanner
        scanner = HTMLScanner(session=self.session)
        visited = set()
        to_visit = [(url, 0)]
        tracks = []
        while to_visit and len(visited) < self.max_pages:
            current_url, depth = to_visit.pop(0)
            if current_url in visited:
                continue
            visited.add(current_url)
            tracks.extend(scanner.extract(current_url))
            if depth < self.max_depth:
                try:
                    resp = self.session.get(current_url, timeout=(5, 30))
                    for m in re.finditer(r'href="([^"]+)"', resp.text):
                        link = urljoin(current_url, m.group(1))
                        if urlparse(link).netloc == urlparse(url).netloc and link not in visited:
                            to_visit.append((link, depth + 1))
                except Exception:
                    pass
        return tracks
