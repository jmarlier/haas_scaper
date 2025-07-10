import asyncio
import httpx
import logging
import time
import json

from utils.network import fetch_with_retries
from utils.queue_manager import URLQueue, is_ignored_url
from db.models import init_db, save_machine_data, save_promo_data, save_service_data
from parsers.machine_parser import extract_machine_links, extract_model_links_from_series
from parsers.parser_router import detect_page_type, parse_page_by_type

CATALOGUE_URLS = [
    "https://www.haascnc.com/machines/vertical-mills.html",
    "https://www.haascnc.com/machines/rotaries-indexers.html",
]

RATE_LIMIT = 5  # max 5 requêtes simultanées
MAX_DEPTH = 5   # profondeur maximale de crawl
semaphore = asyncio.Semaphore(RATE_LIMIT)

EXPORT_JSON = True  # Active l'export JSON des résultats à la fin
DRY_RUN = False     # Si True, ne sauvegarde rien en base, ne marque pas done/failed

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
        print(f"🎯 Promo enregistrée : {url}")
    elif page_type == "service" and "pdf_url" in data and "description" in data:
        save_service_data(data)
        print(f"📘 Support enregistré : {url}")
    elif page_type == "machine":
        save_machine_data(data)
        print(f"✅ Données machine sauvegardées pour {url}")
    else:
        print(f"⚠️ Données non reconnues pour {url}")

async def crawl_machines_from_catalogue(depth=0, dry_run=DRY_RUN):
    if depth > MAX_DEPTH:
        logger.warning(f"Profondeur max atteinte ({MAX_DEPTH}), arrêt du crawl.")
        return
    print("🔧 Initialisation de la base et de la queue...")
    init_db()
    queue = URLQueue()

    print("📋 Exploration des catalogues machines Haas...")
    links = []
    results = {"machine": [], "promo": [], "service": []}
    n_success, n_failed = 0, 0
    start_time = time.time()

    for catalogue_url in CATALOGUE_URLS:
        print(f"🌐 Lecture catalogue : {catalogue_url}")
        try:
            r = httpx.get(catalogue_url, headers={"User-Agent": "Mozilla/5.0"}, follow_redirects=True)
            html = r.text
            sub_links = extract_machine_links(html)
            logger.info(f"🔗 {len(sub_links)} liens extraits de {catalogue_url}")
            links.extend(sub_links)
        except Exception as e:
            print(f"❌ Erreur catalogue {catalogue_url} → {e}")

    links = list(set(links))  # dédupliqué
    for full_url in links:
        if is_ignored_url(full_url):
            logger.info(f"[IGNORED] {full_url}")
        elif queue.is_known(full_url):
            logger.info(f"[DUPLICATE] {full_url}")
        else:
            queue.add_url(full_url)
            logger.info(f"[ADDED] {full_url}")

    logger.info(f"📥 {len(links)} URL candidates, {len([u for u in links if not is_ignored_url(u) and not queue.is_known(u)])} ajoutées à la queue.")

    while True:
        urls = queue.get_next_batch(limit=RATE_LIMIT)
        if not urls:
            break

        tasks = [fetch_limited(url) for url in urls]
        responses = await asyncio.gather(*tasks)

        for url, response in zip(urls, responses):
            print(f"🌐 Fetched: {url}")
            if response and response.status_code == 200:
                page_type = detect_page_type(url, response.text)
                logger.info(f"Type détecté pour {url} : {page_type}")
                if page_type in ("machine", "promo", "service"):
                    data = parse_page_by_type(page_type, url, response.text)
                    if data and "title" in data:
                        results[page_type].append(data)
                        n_success += 1
                        if not dry_run:
                            save_data_by_type(page_type, data, url)
                            queue.mark_done(url)
                        else:
                            logger.info(f"[DRY RUN] Données non sauvegardées pour {url}")
                            logger.info(f"[DRY RUN] {url} aurait été marqué comme done.")
                    else:
                        print(f"⚠️ Aucune donnée enregistrée pour {url}")
                        n_failed += 1
                        if not dry_run:
                            queue.mark_failed(url, reason="no data")
                        else:
                            logger.info(f"[DRY RUN] {url} aurait été marqué comme failed (no data).")
                elif page_type == "unknown":
                    logger.warning(f"Type de page inconnu pour {url}")
                    n_failed += 1
                    if not dry_run:
                        queue.mark_failed(url, reason="unknown type")
                    else:
                        logger.info(f"[DRY RUN] {url} aurait été marqué comme failed (unknown type).")
            else:
                queue.mark_failed(url, reason="fetch failed")
                print(f"❌ Échec pour {url}")
                n_failed += 1
                if dry_run:
                    logger.info(f"[DRY RUN] {url} aurait été marqué comme failed (fetch failed).")

        # Log d'état de la queue
        stats = queue.count_by_status()
        logger.info(f"État de la queue : {stats}")

    # Log final
    elapsed = time.time() - start_time
    logger.info(f"Résumé final de la queue : {queue.count_by_status()}")
    logger.info(f"Crawl terminé en {elapsed:.1f} secondes. Succès: {n_success}, Échecs: {n_failed}, Pages/sec: {n_success/elapsed if elapsed else 0:.2f}")

    if EXPORT_JSON:
        with open("crawl_results.json", "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Export JSON terminé : crawl_results.json")

async def retry_failed_urls(max_retries=2, batch_size=5):
    """
    Retente automatiquement les URLs en échec (status 'failed'), jusqu'à max_retries fois.
    """
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
                logger.info(f"✅ Retry OK: {url}")
                queue.mark_done(url)
            else:
                logger.warning(f"❌ Retry failed: {url}")
        stats = queue.count_by_status()
        logger.info(f"État de la queue après retry: {stats}")

if __name__ == "__main__":
    asyncio.run(crawl_machines_from_catalogue(dry_run=DRY_RUN))
    asyncio.run(retry_failed_urls())
