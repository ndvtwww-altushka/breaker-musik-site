from typing import List, Optional
from .base import BaseParser, Track

class ParserRegistry:
    def __init__(self, parsers: List[BaseParser]):
        self.parsers = parsers

    def extract(self, url: str) -> List[Track]:
        for parser in self.parsers:
            if parser.can_handle(url):
                try:
                    result = parser.extract(url)
                    if result:
                        return result
                except Exception:
                    continue
        return []
