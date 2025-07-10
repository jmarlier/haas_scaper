import asyncio
from utils.network import fetch_with_retries

URL = "https://www.haascnc.com/machines/vertical-mills.html"

async def main():
    response = await fetch_with_retries(URL)
    if response:
        html = response.text
        with open("vf-2.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("✅ Page HTML enregistrée dans vf-2.html")

if __name__ == "__main__":
    asyncio.run(main())