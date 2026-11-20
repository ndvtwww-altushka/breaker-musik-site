import ipaddress
import socket
from urllib.parse import urlparse


def is_public_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            return False
        host = parsed.hostname
        if host == "localhost" or host.endswith(".local") or host.endswith(".internal"):
            return False
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        for info in infos:
            ip = ipaddress.ip_address(info[4][0])
            if not ip.is_global:
                return False
        return True
    except Exception:
        return False


def fetch_url(url: str, timeout=(5, 15), session=None):
    import requests
    s = session or requests.Session()
    return s.get(url, timeout=timeout, stream=True)
