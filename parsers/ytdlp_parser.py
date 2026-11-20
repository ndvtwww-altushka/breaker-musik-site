import subprocess
import json
from typing import List
from .base import Track

class YtDlpParser:
    def extract(self, url: str) -> List[Track]:
        try:
            result = subprocess.run(
                ["yt-dlp", "--dump-json", "--no-download", url],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                return []
            data = json.loads(result.stdout)
            tracks = []
            if "entries" in data:
                for entry in data["entries"]:
                    tracks.append(Track(
                        url=entry.get("url") or entry.get("webpage_url"),
                        title=entry.get("title"),
                        duration=entry.get("duration"),
                        extension=entry.get("ext"),
                        source_url=url,
                    ))
            else:
                tracks.append(Track(
                    url=data.get("url") or data.get("webpage_url"),
                    title=data.get("title"),
                    duration=data.get("duration"),
                    extension=data.get("ext"),
                    source_url=url,
                ))
            return tracks
        except Exception:
            return []
