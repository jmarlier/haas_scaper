from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

def extract_links(base_url: str, html: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)

        if parsed.netloc.endswith("haascnc.com") and "/videos/" not in parsed.path and "/community/" not in parsed.path:
            if parsed.path.endswith(".html") or "locale=en" in parsed.query or parsed.path == "/":
                if not any(x in parsed.path for x in ["/fr/", "/es/", "/pt/", "/de/", "/it/", "/zh/", "/ja/"]):
                    links.add(full_url)

    return list(links)