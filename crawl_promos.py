

import asyncio
import httpx
import logging
import json
import time

from utils.network import fetch_with_retries
from utils.queue_manager import URLQueue, is_ignored_url
from db.models import init_db, save_promo_data
from parsers.parser_router import detect_page_type, parse_page_by_type

PROMO_URLS = [
    "https://www.haascnc.com/special-offers.html"
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

def save_data_by_type(page_type, data, url):
    if page_type == "promo" and "promo_text" in data:
        save_promo_data(data)
        logger.info(f"🎯 Promo enregistrée : {url}")
    else:
        logger.warning(f"⚠️ Données {page_type} non reconnues pour {url}")

async def crawl_promos(dry_run=DRY_RUN):
    print("🔧 Initialisation de la base et de la queue...")
    init_db()
    queue = URLQueue()

    print("📋 Exploration des pages promotions Haas...")
    links = list(set(PROMO_URLS))
    results = {"promo": []}
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
                logger.info(f"Type détecté pour {url} : {page_type}")
                if page_type == "promo":
                    data = parse_page_by_type(page_type, url, response.text)
                    if data and "title" in data:
                        results["promo"].append(data)
                        n_success += 1
                        if not dry_run:
                            save_data_by_type(page_type, data, url)
                            queue.mark_done(url)
                        else:
                            logger.info(f"[DRY RUN] Données non sauvegardées pour {url}")
                            logger.info(f"[DRY RUN] {url} aurait été marqué comme done.")
                    else:
                        logger.warning(f"⚠️ Aucune donnée promo enregistrée pour {url}")
                        n_failed += 1
                        if not dry_run:
                            queue.mark_failed(url, reason="no data")
                        else:
                            logger.info(f"[DRY RUN] {url} aurait été marqué comme failed (no data).")
                else:
                    logger.warning(f"Type incorrect pour {url} : {page_type}")
                    n_failed += 1
                    if not dry_run:
                        queue.mark_failed(url, reason="not promo")
                    else:
                        logger.info(f"[DRY RUN] {url} aurait été marqué comme failed (not promo).")
            else:
                logger.error(f"❌ Échec de fetch pour {url}")
                n_failed += 1
                if not dry_run:
                    queue.mark_failed(url, reason="fetch failed")
                else:
                    logger.info(f"[DRY RUN] {url} aurait été marqué comme failed (fetch failed).")

        stats = queue.count_by_status()
        logger.info(f"État de la queue : {stats}")

    elapsed = time.time() - start_time
    logger.info(f"Crawl terminé en {elapsed:.1f}s. Succès: {n_success}, Échecs: {n_failed}")

    if EXPORT_JSON:
        with open("crawl_promos_results.json", "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info("Export JSON terminé : crawl_promos_results.json")

async def retry_failed_promos(max_retries=2, batch_size=5, dry_run=DRY_RUN):
    queue = URLQueue()
    for attempt in range(1, max_retries + 1):
        failed_urls = queue.get_failed_urls(limit=batch_size)
        if not failed_urls:
            logger.info("Aucune URL en échec à retenter.")
            break
        logger.info(f"Retry {attempt}/{max_retries} pour {len(failed_urls)} URLs failed...")
        tasks = [fetch_limited(url) for url in failed_urls]
        responses = await asyncio.gather(*tasks)
        for url, response in zip(failed_urls, responses):
            if response and response.status_code == 200:
                page_type = detect_page_type(url, response.text)
                data = parse_page_by_type(page_type, url, response.text)
                if data and "title" in data:
                    if not dry_run:
                        save_data_by_type(page_type, data, url)
                        queue.mark_done(url)
                    else:
                        logger.info(f"[DRY RUN] Données non sauvegardées pour {url}")
                        logger.info(f"[DRY RUN] {url} aurait été marqué comme done.")
                else:
                    if not dry_run:
                        queue.mark_failed(url, reason="no data")
                    else:
                        logger.info(f"[DRY RUN] {url} aurait été marqué comme failed (no data).")
            else:
                if not dry_run:
                    queue.mark_failed(url, reason="fetch failed")
                else:
                    logger.info(f"[DRY RUN] {url} aurait été marqué comme failed (fetch failed).")
        stats = queue.count_by_status()
        logger.info(f"État de la queue après retry: {stats}")

if __name__ == "__main__":
    asyncio.run(crawl_promos(dry_run=DRY_RUN))
    asyncio.run(retry_failed_promos(dry_run=DRY_RUN))