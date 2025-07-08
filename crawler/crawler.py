# crawler/crawler.py

import httpx
from utils.user_agents import get_random_user_agent

async def crawl_url(url: str) -> None:
    headers = {
        "User-Agent": get_random_user_agent()
    }

    timeout = httpx.Timeout(10.0, read=20.0)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            print(f"✅ {url} - {response.status_code}")
            print(response.text[:500])  # aperçu HTML (optionnel)

            print("\n🔗 Liens internes détectés :")
            links = extract_links(url, response.text)
            for link in links:
                print(link)
            return response.text  # ✅ retourne le HTML
        except httpx.HTTPStatusError as e:
            print(f"❌ Erreur HTTP {e.response.status_code} pour {url}")
        except Exception as e:
            print(f"❌ Erreur générale pour {url} : {e}")
            return None  # si une erreur a eu lieu
        
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_links(base_url: str, html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        if href.startswith("#") or "javascript:" in href:
            continue

        # Convertir lien relatif → absolu
        full_url = urljoin(base_url, href)

        # Garder uniquement les pages internes en anglais
        if full_url.startswith("https://www.haascnc.com/") and "/fr/" not in full_url:
            links.append(full_url)

    return list(set(links))  # supprimer les doublons