import requests
from bs4 import BeautifulSoup


def fix_relative_url(base_url: str, href: str) -> str:
    """Relative URL'leri absolute URL'ye dönüştürür."""
    if href.startswith("./"):
        href = href[1:]
    elif href.startswith("."):
        href = href[1:]
    if not href.startswith("/"):
        href = "/" + href
    return f"{base_url}{href}"


def fetch(url: str, method: str = "GET", headers: dict = None, params: dict = None, json_body: dict = None) -> requests.Response:
    """HTTP isteği yapar, timeout ve hata yönetimi dahil."""
    default_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    if headers:
        default_headers.update(headers)

    if method == "POST":
        return requests.post(url, json=json_body, headers=default_headers, timeout=15)
    return requests.get(url, params=params, headers=default_headers, timeout=15)


def parse_html(text: str) -> BeautifulSoup:
    """HTML metnini BeautifulSoup nesnesine dönüştürür."""
    return BeautifulSoup(text, "html.parser")


def clean_html(text: str) -> str:
    """HTML tag'lerini temizler, düz metin döner."""
    if "<" in text:
        return BeautifulSoup(text, "html.parser").get_text(strip=True)
    return text
