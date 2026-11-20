from typing import List, Protocol
from .base import Track

class Parser(Protocol):
    def extract(self, url: str) -> List[Track]: ...

class ParserRegistry:
    def __init__(self, parsers: List[Parser]):
        self.parsers = parsers

    def extract(self, url: str) -> List[Track]:
        tracks = []
        for p in self.parsers:
            try:
                tracks.extend(p.extract(url))
            except Exception:
                pass
        return tracks
