import socket
import ipaddress
import requests

def is_public_url(url: str) -> bool:
    try:
        if not url.startswith(("http://", "https://")):
            return False
        host = url.split("/")[2].split(":")[0]
        ip = socket.gethostbyname(host)
        addr = ipaddress.ip_address(ip)
        return not addr.is_private and not addr.is_loopback and not addr.is_reserved
    except Exception:
        return False

def fetch_url(url: str, session: requests.Session, timeout=(5, 30)):
    return session.get(url, timeout=timeout)
