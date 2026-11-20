from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Track:
    title: str
    url: str
    source_url: str
    duration: Optional[int] = None
    bitrate: Optional[int] = None
    extension: str = "mp3"

class BaseParser:
    def can_handle(self, url: str) -> bool:
        raise NotImplementedError

    def extract(self, url: str) -> List[Track]:
        raise NotImplementedError
