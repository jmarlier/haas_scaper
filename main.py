import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/crawler.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
import httpx
import random
import asyncio
from utils.proxies import get_random_proxy
from utils.user_agents import get_random_user_agent

logger = logging.getLogger(__name__)

MAX_RETRIES = 5
BACKOFF_FACTOR = 1.5
TIMEOUT = 20

semaphore = asyncio.Semaphore(5)  # Limite à 5 req/s

async def crawl_url(url: str) -> str | None:
    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept": "text/html,application/xhtml+xml",
    }

    for attempt in range(1, MAX_RETRIES + 1):
        proxy = get_random_proxy()
        try:
            async with semaphore:
                async with httpx.AsyncClient(proxies=proxy, timeout=TIMEOUT, follow_redirects=True) as client:
                    logger.debug(f"Requesting {url} [Try {attempt}] via {proxy}")
                    response = await client.get(url, headers=headers)
                    if response.status_code == 200:
                        return response.text
                    elif response.status_code in (429, 500, 502, 503, 504):
                        raise httpx.HTTPStatusError(f"Retryable status code: {response.status_code}", request=response.request, response=response)

        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            wait_time = BACKOFF_FACTOR ** attempt
            logger.warning(f"Attempt {attempt} failed for {url}: {e}. Retrying in {wait_time:.1f}s...")
            await asyncio.sleep(wait_time)

    logger.error(f"Failed to fetch {url} after {MAX_RETRIES} attempts.")
    return None