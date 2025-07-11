import sqlite3
from sqlalchemy.orm import declarative_base
Base = declarative_base()

DB_PATH = "haasSiteData.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    # Table machines
    cur.execute("""
    CREATE TABLE IF NOT EXISTS machines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE,
        title TEXT,
        subtitle TEXT,
        image_url TEXT,
        pdf_url TEXT,
        promo_text TEXT
    );
    """)

    # Table specs liées aux machines (clé étrangère)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS machine_specs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        machine_id INTEGER,
        label TEXT,
        value TEXT,
        FOREIGN KEY(machine_id) REFERENCES machines(id) ON DELETE CASCADE
    );
    """)

    # Table promotions
    cur.execute("""
    CREATE TABLE IF NOT EXISTS promos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE,
        title TEXT,
        promo_text TEXT
    );
    """)

    # Table documents techniques / support
    cur.execute("""
    CREATE TABLE IF NOT EXISTS service_docs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE,
        title TEXT,
        description TEXT,
        pdf_url TEXT
    );
    """)

    conn.commit()
    conn.close()


# Fonction pour sauvegarder les données d'une machine et ses spécifications
def save_machine_data(data: dict):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Insertion dans machines
    cur.execute("""
        INSERT OR IGNORE INTO machines (url, title, subtitle, image_url, pdf_url, promo_text)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data.get("url"),
        data.get("title"),
        data.get("subtitle"),
        data.get("image_url"),
        data.get("pdf_url"),
        data.get("promo_text"),
    ))

    # Récupérer l'ID de la machine (nouvelle ou existante)
    cur.execute("SELECT id FROM machines WHERE url = ?", (data.get("url"),))
    machine_id = cur.fetchone()[0]

    # Insertion des specs
    specs = data.get("specs", {})
    for label, value in specs.items():
        cur.execute("""
            INSERT INTO machine_specs (machine_id, label, value)
            VALUES (?, ?, ?)
        """, (machine_id, label, value))

    conn.commit()
    conn.close()

def save_promo_data(data: dict):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT OR IGNORE INTO promos (url, title, promo_text)
        VALUES (?, ?, ?)
    """, (
        data.get("url"),
        data.get("title"),
        data.get("promo_text"),
    ))

    conn.commit()
    conn.close()

def save_service_data(data: dict):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT OR IGNORE INTO service_docs (url, title, description, pdf_url)
        VALUES (?, ?, ?, ?)
    """, (
        data.get("url"),
        data.get("title"),
        data.get("description"),
        data.get("pdf_url"),
    ))

    conn.commit()
    conn.close()
    create_full_text_indexes()


# Création des index full-text pour la recherche
def create_full_text_indexes():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("CREATE VIRTUAL TABLE IF NOT EXISTS machines_fts USING fts5(title, subtitle, promo_text, content='machines', content_rowid='id')")
    cur.execute("CREATE VIRTUAL TABLE IF NOT EXISTS promos_fts USING fts5(title, promo_text, content='promos', content_rowid='id')")
    cur.execute("CREATE VIRTUAL TABLE IF NOT EXISTS service_docs_fts USING fts5(title, description, content='service_docs', content_rowid='id')")
    conn.commit()
    conn.close()