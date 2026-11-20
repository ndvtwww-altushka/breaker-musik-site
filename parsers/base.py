from dataclasses import dataclass
from typing import Optional

@dataclass
class Track:
    url: str
    title: Optional[str] = None
    source_url: Optional[str] = None
    duration: Optional[int] = None
    bitrate: Optional[int] = None
    extension: Optional[str] = None