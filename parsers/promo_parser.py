from bs4 import BeautifulSoup, Tag
from typing import List, Dict, Optional
import re
import logging

def clean_text(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    text = text.replace("_", " ").replace("\n", " ").strip()
    text = re.sub(r"\s+", " ", text)
    return text if text else None

def is_generic(text: Optional[str]) -> bool:
    if not text:
        return True
    text = text.lower().strip()
    if len(text) < 8:
        return True
    if text in {"introducing the", "current tooling promotions", "order with a machine", "pay by invoice"}:
        return True
    return False

def extract_promo_blocks(soup: BeautifulSoup) -> List[Dict]:
    promos = []
    seen = set()
    logger = logging.getLogger("promo_parser")
    for gridpad in soup.find_all("div", class_=lambda c: isinstance(c, str) and "gridpad" in c):
        if not isinstance(gridpad, Tag):
            continue
        title_tag = gridpad.find("h2") if isinstance(gridpad, Tag) else None
        title = clean_text(title_tag.get_text(strip=True) if isinstance(title_tag, Tag) else None)
        desc_tag = gridpad.find("h3") if isinstance(gridpad, Tag) else None
        if not desc_tag:
            desc_tag = gridpad.find("p") if isinstance(gridpad, Tag) else None
        description = clean_text(desc_tag.get_text(strip=True) if isinstance(desc_tag, Tag) else None)
        cond_tag = gridpad.find("i") if isinstance(gridpad, Tag) else None
        conditions = clean_text(cond_tag.get_text(strip=True) if isinstance(cond_tag, Tag) else None)
        link_tag = None
        if isinstance(gridpad, Tag):
            for a in gridpad.find_all("a"):
                if re.search(r"learn|en savoir", a.get_text(strip=True), re.I):
                    link_tag = a
                    break
            if not link_tag:
                link_tag = gridpad.find("a")
        link = link_tag.get("href") if isinstance(link_tag, Tag) else None
        logger.info(f"[PROMO CANDIDATE] title: {title!r} | description: {description!r}")
        print(f"[PROMO CANDIDATE] title: {title!r} | description: {description!r}")
        # Only filter on title
        if not title or is_generic(title):
            logger.info(f"[PROMO DROPPED] Reason: generic or empty title: {title!r}")
            print(f"[PROMO DROPPED] Reason: generic or empty title: {title!r}")
            continue
        key = (title, description)
        if key in seen:
            logger.info(f"[PROMO DROPPED] Reason: duplicate: {key!r}")
            print(f"[PROMO DROPPED] Reason: duplicate: {key!r}")
            continue
        seen.add(key)
        promos.append({
            "title": title,
            "description": description,
            "conditions": conditions,
            "link": link,
        })
    return promos

def parse_promo_page(url: str, html: str) -> dict:
    logger = logging.getLogger("promo_parser")
    logger.info(f"[PROMO PARSER] Called for URL: {url}")
    print(f"[PROMO PARSER] Called for URL: {url}")
    logger.info(f"[PROMO PARSER] HTML length: {len(html)}")
    print(f"[PROMO PARSER] HTML length: {len(html)}")
    print(f"[PROMO PARSER] HTML excerpt: {html[:500]!r}")
    soup = BeautifulSoup(html, "html.parser")
    gridpad_count = len(soup.find_all("div", class_=lambda c: isinstance(c, str) and "gridpad" in c))
    logger.info(f"[PROMO PARSER] gridpad blocks found: {gridpad_count}")
    print(f"[PROMO PARSER] gridpad blocks found: {gridpad_count}")
    promos = extract_promo_blocks(soup)
    if not promos:
        h1_tag = soup.find("h1")
        title = clean_text(h1_tag.get_text(strip=True) if h1_tag else None)
        promo_info = soup.find(class_="promo-banner") or soup.find(class_="promotion-details")
        promo_text = clean_text(promo_info.get_text(strip=True) if promo_info else None)
        if title and not is_generic(title):
            promos = [{
                "title": title,
                "description": promo_text,
                "conditions": None,
                "link": None,
            }]
    result = {"url": url}
    if promos:
        result.update(promos[0])
    result["promos"] = promos  # Always a list
    logger.info(f"[PROMO PARSER] promos extracted: {len(promos)}")
    print(f"[PROMO PARSER] promos extracted: {len(promos)}")
    return result