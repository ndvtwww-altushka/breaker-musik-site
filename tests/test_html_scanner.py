import pytest
from parsers.html_scanner import HTMLScanner

class FakeSession:
    def get(self, url, timeout=None):
        class Resp:
            status_code = 200
            text = '<audio src="test.mp3"></audio>\n<a href="audio.wav">download</a>\n<script type="application/ld+json">{"@type": "AudioObject", "contentUrl": "track.ogg", "name": "Test Track"}</script>'
        return Resp()


def test_extracts_audio():
    scanner = HTMLScanner(session=FakeSession())
    tracks = scanner.extract("http://example.com")
    urls = [t.url for t in tracks]
    assert "test.mp3" in urls
    assert "audio.wav" in urls
    assert "track.ogg" in urls
