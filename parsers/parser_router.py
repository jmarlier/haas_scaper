from parsers import machine_parser, promo_parser, doc_parser
# blog_parser est optionnel, à ajouter si besoin
import re
from bs4 import BeautifulSoup
import logging

def parse_page_by_type(page_type: str, url: str, html: str) -> dict:
    if page_type == "machine":
        return machine_parser.parse_machine_page(url, html)
    elif page_type == "promo":
        return promo_parser.parse_promo_page(url, html)
    elif page_type == "service":
        return doc_parser.parse_service_doc_page(url, html)
    # elif page_type == "blog":
    #     return blog_parser.parse_blog_page(url, html)
    else:
        return {}


# --- Auto detection and routing ---
def detect_page_type(url: str, html: str) -> str:
    """Détecte le type de page en fonction de l'URL et du contenu HTML."""
    logger = logging.getLogger("parser_router")
    url_lower = url.lower()
    html_lower = html.lower()
    soup = BeautifulSoup(html, "html.parser")
    gridpad_count = len(soup.find_all("div", class_=lambda c: isinstance(c, str) and "gridpad" in c))
    promo_h2 = False
    for h2 in soup.find_all("h2"):
        text = h2.get_text(strip=True).lower()
        if re.search(r"promo|offre|deal|remise|gratuit|discount|save|bonus|bundle|winner", text):
            promo_h2 = True
            break
    detected = "unknown"
    if "/machines/" in url_lower:
        if "Specs" in html or "Travel" in html or "Spindle" in html:
            detected = "machine"
    elif "/promos/" in url_lower or "promo-banner" in html_lower:
        detected = "promo"
    elif gridpad_count >= 2:
        detected = "promo"
    elif promo_h2:
        detected = "promo"
    elif "/service/" in url_lower or "alarm code" in html_lower or "manual" in html_lower:
        detected = "service"
    logger.info(f"[DETECT TYPE] URL: {url} | Detected: {detected} | gridpad: {gridpad_count} | promo_h2: {promo_h2}")
    return detected

def route_parse(url: str, html: str) -> dict:
    """Route automatiquement vers le bon parseur en fonction du type détecté."""
    page_type = detect_page_type(url, html)
    return parse_page_by_type(page_type, url, html)