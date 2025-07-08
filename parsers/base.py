# parsers/base.py

from bs4 import BeautifulSoup

def detect_template_type(url: str, html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # MACHINE
    if "/machines/" in url and soup.select_one("div.machine-specifications, div.spec-table"):
        return "machine"

    # PROMOTION
    if "/hot-deals" in url or "/promo" in url or "Today's Hot Deals" in soup.text:
        return "promo"

    # SERVICE / PARTS / SUPPORT
    if "/haas-service-parts/" in url or "/service" in url:
        return "service"

    # BLOG / COMMUNITY
    if "/Community" in url or "blog" in url.lower():
        return "blog"

    # TOOLING
    if "/haas-tooling/" in url:
        return "tooling"

    # PRICELIST
    if "shop/category/pricelist" in url:
        return "pricelist"

    # PAGE DE CONTACT / À PROPOS
    if "contact" in url or "about" in url:
        return "info"

    return "unknown"