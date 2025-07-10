import asyncio
import logging
from crawler.crawler import crawl_url
from crawler.queue import enqueue, dequeue, peek_all
from crawler.link_extractor import extract_links
from parsers.base import detect_template_type
from parsers.machine import parse_machine_page
from parsers.promo import parse_promo_page
from parsers.service_doc import parse_service_doc
from parsers.pdf_blog_parsers import parse_pdf_links, parse_blog_page

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/crawler.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    enqueue("https://www.haascnc.com/index.html?locale=en")
    visited = set()

    while True:
        url = dequeue()
        if not url or url in visited:
            break

        html = await crawl_url(url)
        if not html:
            continue

        try:
            page_type = detect_template_type(url, html)
            logger.info(f"Type détecté pour {url} : {page_type}")

            parse_pdf_links(url, html)

            if page_type == "machine":
                parse_machine_page(url, html)
            elif page_type == "promo":
                parse_promo_page(url, html)
            elif page_type == "service-doc":
                parse_service_doc(url, html)
            elif page_type == "blog":
                parse_blog_page(url, html)

        except Exception as e:
            logger.warning(f"Erreur de détection ou parsing pour {url} : {e}")

        visited.add(url)
        for link in extract_links(url, html):
            if link not in visited and link not in peek_all():
                enqueue(link)

if __name__ == "__main__":
    asyncio.run(main())