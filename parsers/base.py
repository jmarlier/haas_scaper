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
# parsers/base.py

from bs4 import BeautifulSoup

def detect_template_type(url: str, html: str) -> str:
    if "/machines/" in url:
        return "machine"
    if "/content/haascnc/en/video/promo/" in url or "/promo/" in url or "/hot-deals" in url:
        return "promo"
    if "/service/" in url and "alarm" in url.lower():
        return "service-doc"
    if "/haas-service-parts/" in url or "/service" in url:
        return "service"
    if "/about/news/" in url or "/community/" in url or "blog" in url.lower():
        return "blog"
    if "/haas-tooling/" in url:
        return "tooling"
    if "shop/category/pricelist" in url:
        return "pricelist"
    if "contact" in url or "about" in url:
        return "info"

    soup = BeautifulSoup(html, "lxml")

    if soup.find("table", class_="machine-specs") or soup.select_one("div.machine-specifications, div.spec-table"):
        return "machine"
    if soup.find("div", class_="promotion-wrapper") or "Today's Hot Deals" in soup.text:
        return "promo"
    if soup.find("h1") and "alarm" in soup.h1.text.lower():
        return "service-doc"
    if soup.find("article"):
        return "blog"

    return "unknown"