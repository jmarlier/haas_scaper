from bs4 import BeautifulSoup
from urllib.parse import urljoin
from sqlalchemy.exc import IntegrityError
from db import get_session
from models import PDF, Document


def parse_pdf_links(base_url: str, html: str) -> None:
    soup = BeautifulSoup(html, "lxml")
    session = get_session()
    count = 0

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().endswith(".pdf"):
            full_url = urljoin(base_url, href)
            title = a.text.strip() or "PDF Document"

            pdf = PDF(
                url=full_url,
                title=title,
                local_path="",  # à compléter après téléchargement
                page_type="auto"
            )

            try:
                session.add(pdf)
                session.commit()
                print(f"📄 PDF saved: {title} => {full_url}")
                count += 1
            except IntegrityError:
                session.rollback()

    session.close()
    if count == 0:
        print("ℹ️ No new PDF found on this page.")


def parse_blog_page(url: str, html: str) -> None:
    soup = BeautifulSoup(html, "lxml")

    title = soup.find("h1")
    title = title.text.strip() if title else "(Untitled Blog)"

    content_block = soup.select_one("article") or soup.select_one("div.blog-content")
    content = content_block.get_text(separator="\n", strip=True) if content_block else ""

    session = get_session()
    blog_post = Document(
        url=url,
        title=title,
        content=content,
        type="blog"
    )

    try:
        session.add(blog_post)
        session.commit()
        print(f"📝 Blog saved: {title}")
    except IntegrityError:
        session.rollback()
        print(f"ℹ️ Blog already in database: {url}")
    finally:
        session.close()