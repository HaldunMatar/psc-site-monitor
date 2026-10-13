import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (psc-site-monitor)"}


class FetchError(Exception):
    """تعذّر جلب الصفحة (شبكة / حجب / مهلة) — ليس بالضرورة تغييرًا في الموقع."""


def fetch_html(url: str, timeout: float = 20, verify: bool = True) -> str:
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, verify=verify)
        r.raise_for_status()
    except requests.RequestException as e:
        raise FetchError(str(e)) from e
    r.encoding = r.apparent_encoding if r.encoding in (None, "ISO-8859-1") else r.encoding
    return r.text


def html_to_text(html: str) -> str:
    """يستخرج النص المرئي فقط (بدون script/style) ويوحّد المسافات."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return " ".join(soup.get_text(" ").split())
