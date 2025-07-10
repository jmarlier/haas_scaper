

import sqlite3
from typing import List
import os
import re

DB_PATH = "haasSiteData.db"

IGNORE_PATTERNS = [
    r"/fr/",
    r"/videos?",
    r"/community/",
    r"/myhaas/",
    r"/haasparts",
]

class URLQueue:
    def __init__(self, db_path: str = DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS url_queue (
                    url TEXT PRIMARY KEY,
                    status TEXT DEFAULT 'queued',
                    reason TEXT
                );
            """)

    def is_ignored(self, url: str) -> bool:
        return any(re.search(pattern, url) for pattern in IGNORE_PATTERNS)

    def add_url(self, url: str):
        if self.is_ignored(url):
            print(f"[IGNORED] {url}")
            return
        try:
            with self.conn:
                self.conn.execute("INSERT OR IGNORE INTO url_queue (url) VALUES (?);", (url,))
        except sqlite3.Error as e:
            print(f"Error adding URL {url}: {e}")

    def get_next_batch(self, limit: int = 10) -> List[str]:
        with self.conn:
            cursor = self.conn.execute("""
                SELECT url FROM url_queue
                WHERE status = 'queued'
                LIMIT ?;
            """, (limit,))
            return [row[0] for row in cursor.fetchall()]

    def mark_done(self, url: str):
        with self.conn:
            self.conn.execute("""
                UPDATE url_queue SET status = 'done' WHERE url = ?;
            """, (url,))

    def mark_failed(self, url: str, reason: str = ''):
        with self.conn:
            self.conn.execute("""
                UPDATE url_queue SET status = 'failed', reason = ? WHERE url = ?;
            """, (reason, url))

    def mark_requeued(self, url: str):
        """
        Remet une URL en statut 'queued' (pour retry après un échec, par exemple).
        """
        with self.conn:
            self.conn.execute("UPDATE url_queue SET status = 'queued', reason = NULL WHERE url = ?;", (url,))

    def count_by_status(self) -> dict:
        """
        Retourne un dictionnaire {status: count} pour suivre l'état de la queue.
        """
        cursor = self.conn.execute("SELECT status, COUNT(*) FROM url_queue GROUP BY status;")
        return {row[0]: row[1] for row in cursor.fetchall()}

    def get_failed_urls(self, limit: int = 10) -> list:
        """
        Retourne une liste d'URLs en échec (status 'failed'), jusqu'à 'limit'.
        """
        cursor = self.conn.execute("SELECT url FROM url_queue WHERE status = 'failed' LIMIT ?;", (limit,))
        return [row[0] for row in cursor.fetchall()]

    def close(self):
        self.conn.close()

    def is_known(self, url: str) -> bool:
        """
        Retourne True si l'URL est déjà présente dans la table url_queue (quel que soit son statut).
        """
        cursor = self.conn.execute("SELECT 1 FROM url_queue WHERE url = ? LIMIT 1;", (url,))
        return cursor.fetchone() is not None

def is_ignored_url(url: str) -> bool:
    """
    Retourne True si l'URL doit être ignorée (tooling store, vidéos, myhaas, non-anglais, etc.)
    """
    IGNORED_PATTERNS = [
        "/videos/", "/video/", "/community/", "/myhaas", "/tooling/", "/store/", "/shop/", "/cart/", "/checkout/",
        "/es/", "/fr/", "/de/", "/it/", "/ja/", "/ko/", "/pt/", "/ru/", "/zh/", "/zh_CN/", "/zh_TW/", "/es_mx/", "/es-mx/",
        "/promo-latam/", "/promo-emea/", "/promo-asia/", "/promo-japan/", "/promo-china/", "/promo-korea/",
        "/tooling-store/", "/haas-tooling/", "/haasparts/", "/haas-parts/", "/haas-service/", "/haasconnect/",
        "/haas-bar-feeder/", "/haas-robot/", "/haas-automation/", "/haas-automation-inc/", "/haas-factory-outlet/",
        "/haas-robotics/", "/haas-robotic/", "/haas-automation-europe/", "/haas-automation-asia/", "/haas-automation-japan/",
        "/haas-automation-china/", "/haas-automation-korea/", "/haas-automation-latam/", "/haas-automation-emea/",
        "/haas-automation-mexico/", "/haas-automation-brazil/", "/haas-automation-india/", "/haas-automation-russia/",
        "/haas-automation-taiwan/", "/haas-automation-turkey/", "/haas-automation-uk/", "/haas-automation-germany/",
        "/haas-automation-france/", "/haas-automation-italy/", "/haas-automation-spain/", "/haas-automation-portugal/",
        "/haas-automation-poland/", "/haas-automation-czech/", "/haas-automation-hungary/", "/haas-automation-romania/",
        "/haas-automation-bulgaria/", "/haas-automation-greece/", "/haas-automation-austria/", "/haas-automation-switzerland/",
        "/haas-automation-belgium/", "/haas-automation-netherlands/", "/haas-automation-norway/", "/haas-automation-sweden/",
        "/haas-automation-finland/", "/haas-automation-denmark/", "/haas-automation-ireland/", "/haas-automation-ukraine/",
        "/haas-automation-lithuania/", "/haas-automation-latvia/", "/haas-automation-estonia/", "/haas-automation-croatia/",
        "/haas-automation-serbia/", "/haas-automation-slovenia/", "/haas-automation-slovakia/", "/haas-automation-bosnia/",
        "/haas-automation-montenegro/", "/haas-automation-macedonia/", "/haas-automation-albania/", "/haas-automation-kosovo/",
        "/haas-automation-georgia/", "/haas-automation-armenia/", "/haas-automation-azerbaijan/", "/haas-automation-kazakhstan/",
        "/haas-automation-uzbekistan/", "/haas-automation-turkmenistan/", "/haas-automation-kyrgyzstan/", "/haas-automation-tajikistan/",
        "/haas-automation-mongolia/", "/haas-automation-china/", "/haas-automation-hongkong/", "/haas-automation-taiwan/",
        "/haas-automation-singapore/", "/haas-automation-malaysia/", "/haas-automation-thailand/", "/haas-automation-vietnam/",
        "/haas-automation-indonesia/", "/haas-automation-philippines/", "/haas-automation-australia/", "/haas-automation-newzealand/",
        "/haas-automation-southafrica/", "/haas-automation-egypt/", "/haas-automation-morocco/", "/haas-automation-tunisia/",
        "/haas-automation-algeria/", "/haas-automation-libya/", "/haas-automation-nigeria/", "/haas-automation-kenya/",
        "/haas-automation-ethiopia/", "/haas-automation-ghana/", "/haas-automation-ivorycoast/", "/haas-automation-cameroon/",
        "/haas-automation-angola/", "/haas-automation-mozambique/", "/haas-automation-zambia/", "/haas-automation-zimbabwe/",
        "/haas-automation-botswana/", "/haas-automation-namibia/", "/haas-automation-madagascar/", "/haas-automation-mauritius/",
        "/haas-automation-seychelles/", "/haas-automation-reunion/", "/haas-automation-martinique/", "/haas-automation-guadeloupe/",
        "/haas-automation-frenchguiana/", "/haas-automation-newcaledonia/", "/haas-automation-tahiti/", "/haas-automation-wallisislands/",
        "/haas-automation-futuna/", "/haas-automation-saintpierre/", "/haas-automation-miquelon/", "/haas-automation-saintbarthelemy/",
        "/haas-automation-saintmartin/", "/haas-automation-saintmartinfr/", "/haas-automation-saintmartinsintmaarten/"
    ]
    url = url.lower()
    return any(pattern in url for pattern in IGNORED_PATTERNS)