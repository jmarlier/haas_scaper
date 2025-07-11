import asyncio

from db.models import init_db, save_machine_data
from parsers.machine_parser import parse_machine_page

URL = "https://www.haascnc.com/machines/vertical-mills/mini-mills/mini-mill.html"

async def main():
    print("🔧 Initializing the database...")
    init_db()

    print("📄 Reading file vf-2.html")
    with open("vf-2.html", "r", encoding="utf-8") as f:
        html = f.read()

    print("✅ File loaded, parsing in progress...")
    data = parse_machine_page(URL, html)
    save_machine_data(data)
    print("💾 Data successfully saved in haasSiteData.db")

if __name__ == "__main__":
    asyncio.run(main())