from bs4 import BeautifulSoup
from typing import List

def extract_machine_links(html: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        print("🔗", href)  # DEBUG

        if (
            href.startswith("/content/haascnc/en/machines/")
            and href.endswith(".html")
            and " " not in href
        ):
            full_url = "https://www.haascnc.com" + href.split("?")[0].rstrip("/")
            links.add(full_url)

    return sorted(links)
def parse_machine_page(url: str, html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    # Main title
    title = soup.find("h1")
    title = title.get_text(strip=True) if title else ""

    # Subtitle or description
    subtitle_tag = soup.find("h2")
    subtitle = subtitle_tag.get_text(strip=True) if subtitle_tag else ""

    # Specifications
    specs = {}
    spec_section = soup.select_one(".specifications, .spec-table, table")
    if spec_section:
        rows = spec_section.find_all("tr")
        for row in rows:
            cols = row.find_all(["td", "th"])
            if len(cols) == 2:
                key = cols[0].get_text(strip=True)
                value = cols[1].get_text(strip=True)
                specs[key] = value

    # Main image
    image_url = ""
    img_tag = soup.select_one(".product-hero img") or soup.find("img")
    if img_tag and img_tag.get("src"):
        image_url = img_tag["src"]
        if image_url.startswith("/"):
            image_url = "https://www.haascnc.com" + image_url

    # PDF brochure
    pdf_url = ""
    for a in soup.find_all("a", href=True):
        if ".pdf" in a["href"]:
            pdf_url = a["href"]
            if pdf_url.startswith("/"):
                pdf_url = "https://www.haascnc.com" + pdf_url
            break

    # Optional promo text
    promo_text = ""
    promo = soup.select_one(".promo-banner")
    if promo:
        promo_text = promo.get_text(strip=True)

    return {
        "url": url,
        "title": title,
        "subtitle": subtitle,
        "specs": specs,
        "image_url": image_url,
        "pdf_url": pdf_url,
        "promo_text": promo_text,
    }


# Extract model links from a series page (e.g., vf-series.html)
def extract_model_links_from_series(html: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if (
            href.startswith("/machines/")
            and href.endswith(".html")
            and " " not in href
        ):
            full_url = "https://www.haascnc.com" + href.split("?")[0].rstrip("/")
            links.add(full_url)

    return sorted(links)