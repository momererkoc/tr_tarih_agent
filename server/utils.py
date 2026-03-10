import requests
from bs4 import BeautifulSoup
from server.config import Config


class HttpClient:
    """Merkezi HTTP istek yöneticisi (Session destekli)"""
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(Config.DEFAULT_HEADERS)

    def fetch(self, url, method="GET", params=None, json_body=None, data=None, headers=None, timeout=15):
        try:
            if method == "POST":
                return self.session.post(url, json=json_body, data=data, params=params, headers=headers, timeout=timeout)
            return self.session.get(url, params=params, headers=headers, timeout=timeout)
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"HTTP İsteği Başarısız: {e}")


def parse_html(text):
    return BeautifulSoup(text, "html.parser")


def clean_html(text):
    if not text:
        return ""
    if "<" in text:
        return BeautifulSoup(text, "html.parser").get_text(strip=True)
    return text.strip()


def fix_relative_url(base_url, href):
    if not href:
        return ""
    if href.startswith("http"):
        return href
    if href.startswith("./"):
        href = href[1:]
    elif href.startswith("."):
        href = href[1:]
    if not href.startswith("/"):
        href = "/" + href
    return f"{base_url}{href}"
