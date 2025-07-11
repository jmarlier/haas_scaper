

import asyncio
import httpx
import logging
import json
import time

from utils.network import fetch_with_retries
from utils.queue_manager import URLQueue, is_ignored_url
from db.models import init_db, save_service_data
from parsers.parser_router import detect_page_type, parse_page_by_type

DOCS_URLS = [
    "https://www.haascnc.com/service/troubleshooting-and-how-to.html",
    "https://www.haascnc.com/service/alarm-search.html",
    "https://www.haascnc.com/service/service-documents.html"
]

RATE_LIMIT = 5
semaphore = asyncio.Semaphore(RATE_LIMIT)

EXPORT_JSON = True
DRY_RUN = False

logger = logging.getLogger("crawler")
logger.setLevel(logging.DEBUG)
if not logger.hasHandlers():
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

async def fetch_limited(url, *args, **kwargs):
    async with semaphore:
        return await fetch_with_retries(url, *args, **kwargs)

def save_data_if_valid(page_type, data, url):
    if page_type == "service" and "pdf_url" in data:
        save_service_data(data)
        logger.info(f"📘 Technical document saved: {url}")
    else:
        logger.warning(f"⚠️ Docs data not recognized for {url}")

async def crawl_docs(dry_run=DRY_RUN):
    print("🔧 Initializing the database and queue...")
    init_db()
    queue = URLQueue()

    print("📋 Exploring Haas technical pages...")
    links = list(set(DOCS_URLS))
    results = {"service": []}
    n_success, n_failed = 0, 0
    start_time = time.time()

    for full_url in links:
        if is_ignored_url(full_url):
            logger.info(f"[IGNORED] {full_url}")
        elif queue.is_known(full_url):
            logger.info(f"[DUPLICATE] {full_url}")
        else:
            queue.add_url(full_url)
            logger.info(f"[ADDED] {full_url}")

    while True:
        urls = queue.get_next_batch(limit=RATE_LIMIT)
        if not urls:
            break

        tasks = [fetch_limited(url) for url in urls]
        responses = await asyncio.gather(*tasks)

        for url, response in zip(urls, responses):
            if response and response.status_code == 200:
                page_type = detect_page_type(url, response.text)
                logger.info(f"Detected type for {url}: {page_type}")
                if page_type == "service":
                    data = parse_page_by_type(page_type, url, response.text)
                    if data and "title" in data:
                        results["service"].append(data)
                        n_success += 1
                        if not dry_run:
                            save_data_if_valid(page_type, data, url)
                            queue.mark_done(url)
                        else:
                            logger.info(f"[DRY RUN] {url} would have been processed as a technical document.")
                    else:
                        logger.warning(f"⚠️ No service data saved for {url}")
                        n_failed += 1
                        if not dry_run:
                            queue.mark_failed(url, reason="no data")
                else:
                    logger.warning(f"Incorrect type for {url}: {page_type}")
                    n_failed += 1
                    if not dry_run:
                        queue.mark_failed(url, reason="not service")
            else:
                logger.error(f"❌ Fetch failed for {url}")
                n_failed += 1
                if not dry_run:
                    queue.mark_failed(url, reason="fetch failed")

        stats = queue.count_by_status()
        logger.info(f"Queue state: {stats}")

    elapsed = time.time() - start_time
    logger.info(f"Crawl finished in {elapsed:.1f}s. Success: {n_success}, Failures: {n_failed}")

    if EXPORT_JSON:
        with open("crawl_docs_results.json", "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info("JSON export finished: crawl_docs_results.json")

if __name__ == "__main__":
    asyncio.run(crawl_docs(dry_run=DRY_RUN))