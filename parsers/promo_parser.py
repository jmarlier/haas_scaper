from bs4 import BeautifulSoup

def parse_promo_page(url: str, html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    title = soup.find("h1")
    title_text = title.get_text(strip=True) if title else ""

    # Exemple de dates et codes promo s'ils existent
    promo_info = soup.find(class_="promo-banner") or soup.find(class_="promotion-details")
    promo_text = promo_info.get_text(strip=True) if promo_info else ""

    return {
        "url": url,
        "title": title_text,
        "promo_text": promo_text,
    }