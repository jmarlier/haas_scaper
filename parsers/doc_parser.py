

from bs4 import BeautifulSoup
from typing import Dict

def parse_service_doc_page(url: str, html: str) -> Dict:
    """
    Parse a Haas service document page (guide, alarm, PDF...). Extracts the title, description, and PDF link if present.
    """
    soup = BeautifulSoup(html, "html.parser")

    title = soup.find("h1")
    description = soup.find("div", class_="description")
    pdf_link = soup.find("a", href=lambda href: href and href.endswith(".pdf"))

    return {
        "type": "service",
        "url": url,
        "title": title.get_text(strip=True) if title else "",
        "description": description.get_text(strip=True) if description else "",
        "pdf_url": pdf_link["href"] if pdf_link else None,
    }