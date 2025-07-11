import os
import sqlite3
import tempfile
from db.models import init_db, save_machine_data, save_promo_data, save_service_data, DB_PATH

def setup_temp_db():
    # Use a temporary file for DB_PATH
    tmp = tempfile.NamedTemporaryFile(delete=False)
    db_path = tmp.name
    tmp.close()
    return db_path

def test_save_machine_data_and_uniqueness():
    db_path = setup_temp_db()
    orig_db_path = DB_PATH
    try:
        # Patch DB_PATH
        import db.models
        db.models.DB_PATH = db_path
        init_db()
        data = {
            "url": "https://www.haascnc.com/machines/vf-2.html",
            "title": "VF-2",
            "subtitle": "Vertical Mill",
            "image_url": "img.png",
            "pdf_url": "vf2.pdf",
            "promo_text": "Special!",
            "specs": {"Travel": "30x16x20", "Spindle": "8100 rpm"}
        }
        save_machine_data(data)
        # Try to insert duplicate
        save_machine_data(data)
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM machines WHERE url=?", (data["url"],))
        count = cur.fetchone()[0]
        assert count == 1
        cur.execute("SELECT title FROM machines WHERE url=?", (data["url"],))
        assert cur.fetchone()[0] == "VF-2"
        # Check specs
        cur.execute("SELECT label, value FROM machine_specs WHERE machine_id = (SELECT id FROM machines WHERE url=?)", (data["url"],))
        specs = dict(cur.fetchall())
        assert specs["Travel"] == "30x16x20"
        assert specs["Spindle"] == "8100 rpm"
        conn.close()
    finally:
        db.models.DB_PATH = orig_db_path
        os.unlink(db_path)

def test_save_promo_data_and_retrieve():
    db_path = setup_temp_db()
    orig_db_path = DB_PATH
    try:
        import db.models
        db.models.DB_PATH = db_path
        init_db()
        data = {"url": "https://www.haascnc.com/promo.html", "title": "Promo1", "promo_text": "Big Sale!"}
        save_promo_data(data)
        save_promo_data(data)  # duplicate
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM promos WHERE url=?", (data["url"],))
        count = cur.fetchone()[0]
        assert count == 1
        cur.execute("SELECT title FROM promos WHERE url=?", (data["url"],))
        assert cur.fetchone()[0] == "Promo1"
        conn.close()
    finally:
        db.models.DB_PATH = orig_db_path
        os.unlink(db_path)

def test_save_service_data_and_retrieve():
    db_path = setup_temp_db()
    orig_db_path = DB_PATH
    try:
        import db.models
        db.models.DB_PATH = db_path
        init_db()
        data = {"url": "https://www.haascnc.com/doc1.html", "title": "Doc1", "description": "Alarm", "pdf_url": "doc1.pdf"}
        save_service_data(data)
        save_service_data(data)  # duplicate
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM service_docs WHERE url=?", (data["url"],))
        count = cur.fetchone()[0]
        assert count == 1
        cur.execute("SELECT title FROM service_docs WHERE url=?", (data["url"],))
        assert cur.fetchone()[0] == "Doc1"
        conn.close()
    finally:
        db.models.DB_PATH = orig_db_path
        os.unlink(db_path) 