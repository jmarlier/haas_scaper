from bs4 import BeautifulSoup
from sqlalchemy.exc import IntegrityError
from db import get_session
from models import Document

def parse_service_doc(url: str, html: str) -> None:
    soup = BeautifulSoup(html, "lxml")

    title = soup.find("h1")
    title = title.text.strip() if title else "(Document sans titre)"

    main_content = soup.select_one("div.main-content") or soup.select_one("article") or soup.select_one("main")
    content = main_content.get_text(separator="\n", strip=True) if main_content else ""

    doc_type = "alarm" if "alarm" in url.lower() or "alarm" in title.lower() else "service"

    session = get_session()
    doc = Document(
        url=url,
        title=title,
        content=content,
        type=doc_type,
    )

    try:
        session.add(doc)
        session.commit()
        print(f"✅ Document enregistré : {title}")
    except IntegrityError:
        session.rollback()
        print(f"ℹ️ Document déjà en base : {url}")
    finally:
        session.close()