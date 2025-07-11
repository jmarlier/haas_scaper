from bs4 import BeautifulSoup
from sqlalchemy.exc import IntegrityError
from db import get_session
from models import Promotion

def parse_promo_page(url: str, html: str) -> None:
    soup = BeautifulSoup(html, "lxml")
    
    title = soup.find("h1")
    title = title.text.strip() if title else "(Untitled Promo)"

    content_div = soup.select_one("div.promotion-wrapper")
    if not content_div:
        content_div = soup.select_one("main") or soup.select_one(".main-content")

    html_content = str(content_div) if content_div else ""

    session = get_session()
    promo = Promotion(
        title=title,
        html=html_content,
        url=url
    )

    try:
        session.add(promo)
        session.commit()
        print(f"✅ Promo saved: {title}")
    except IntegrityError:
        session.rollback()
        print(f"ℹ️ Promo already in database: {url}")
    finally:
        session.close()