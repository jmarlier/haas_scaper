import asyncio
import httpx
import random
import logging
from typing import Optional
from utils.user_agents import get_random_user_agent
from utils.proxies import get_next_proxy

# Charge les proxys depuis un fichier texte (un par ligne)
def load_proxies(filepath: str = "proxies.txt") -> list[str]:
    try:
        with open(filepath, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

PROXIES = load_proxies()

# Setup du logger
logger = logging.getLogger("crawler")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Handler console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Handler fichier
file_handler = logging.FileHandler("crawler.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Fonction principale de récupération avec gestion du proxy, UA et retry
async def fetch_with_retries(
    url: str,
    max_retries: int = 5,
    timeout: int = 30
) -> Optional[httpx.Response]:
    for attempt in range(1, max_retries + 1):
        proxy = get_next_proxy()
        headers = {"User-Agent": get_random_user_agent()}

        try:
            url = url.replace("https://www.haascnc.comhttps://", "https://")  # corrige les URLs doublées
            async with httpx.AsyncClient(proxies=proxy, headers=headers, timeout=timeout, follow_redirects=True) as client:
                response = await client.get(url)

                if response.status_code == 200:
                    logger.debug(f"[{response.status_code}] OK: {url} via {proxy}")
                    return response

                elif response.status_code in [429, 500, 502, 503]:
                    logger.warning(f"[{response.status_code}] Retry {attempt}/{max_retries} for {url}")
                else:
                    logger.error(f"[{response.status_code}] Failed: {url}")
                    return None

        except httpx.RequestError as e:
            logger.error(f"[ERROR] {url} via {proxy} => {e}")

        await asyncio.sleep(2 ** attempt)  # backoff exponentiel

    logger.error(f"[GAVE UP] Max retries exceeded for {url}")
    return None