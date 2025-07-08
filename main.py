# main.py

import asyncio
from crawler.crawler import crawl_url, extract_links
from crawler.queue import enqueue, dequeue, peek_all
from parsers.base import detect_template_type

async def main():
    visited = set()
    max_pages = 1000

    while len(visited) < max_pages:
        url = dequeue()
        if not url:
            break

        if url in visited:
            continue

        html = await crawl_url(url)

        if html:
            try:
                template = detect_template_type(url, html)
                print(f"🧩 Type de page détecté : {template}")
            except Exception as e:
                print(f"⚠️ Erreur de détection pour {url} : {e}")
        else:
            print(f"❌ Pas de contenu HTML pour {url}, on ignore.")
            continue

        visited.add(url)

        for link in extract_links(url, html):
            if link not in visited and link not in peek_all():
                enqueue(link)

# Exécution
if __name__ == "__main__":
    enqueue("https://www.haascnc.com/index.html?locale=en")
    asyncio.run(main())