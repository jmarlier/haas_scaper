import asyncio

from db.models import init_db, save_machine_data
from parsers.machine_parser import parse_machine_page

URL = "https://www.haascnc.com/machines/vertical-mills/mini-mills/mini-mill.html"

async def main():
    print("🔧 Initialisation de la base de données...")
    init_db()

    print("📄 Lecture du fichier vf-2.html")
    with open("vf-2.html", "r", encoding="utf-8") as f:
        html = f.read()

    print("✅ Fichier chargé, parsing en cours...")
    data = parse_machine_page(URL, html)
    save_machine_data(data)
    print("💾 Données enregistrées avec succès dans haasSiteData.db")

if __name__ == "__main__":
    asyncio.run(main())