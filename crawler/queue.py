from bs4 import BeautifulSoup
from sqlalchemy.exc import IntegrityError
from db import get_session
from models import Machine

def parse_machine_page(url: str, html: str) -> None:
    soup = BeautifulSoup(html, "lxml")
    name = soup.find("h1").text.strip() if soup.find("h1") else "Unnamed Machine"
    model = soup.select_one("span.machine-model")
    model = model.text.strip() if model else None

    desc_block = soup.select_one("div.machine-description, div.machine-intro")
    description = desc_block.get_text(separator="\n", strip=True) if desc_block else None

    category = None
    breadcrumb = soup.select("ul.breadcrumb li")
    if breadcrumb and len(breadcrumb) > 1:
        category = breadcrumb[1].text.strip()

    session = get_session()
    machine = Machine(
        name=name,
        model=model,
        description=description,
        category=category,
        url=url,
    )

    try:
        session.add(machine)
        session.commit()
        print(f"✅ Machine enregistrée : {name}")
    except IntegrityError:
        session.rollback()
        print(f"ℹ️ Machine déjà en base : {url}")
    finally:
        session.close()