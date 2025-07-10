import os
import sqlite3
from utils.queue_manager import URLQueue, DB_PATH
from db.models import init_db

def test_queue_add_and_status():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
    queue = URLQueue()

    url = "https://www.haascnc.com/machines/vf-series/vf-2.html"
    queue.add_url(url)
    assert queue.is_known(url)

    queue.mark_done(url)
    conn = sqlite3.connect(DB_PATH)
    status = conn.execute("SELECT status FROM url_queue WHERE url = ?", (url,)).fetchone()[0]
    assert status == "done"


# Test that mark_failed updates status and reason
def test_queue_mark_failed():
    init_db()
    queue = URLQueue()

    url = "https://www.haascnc.com/machines/rotaries-indexers.html"
    queue.add_url(url)
    queue.mark_failed(url, reason="timeout")

    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT status, reason FROM url_queue WHERE url = ?", (url,)).fetchone()
    assert row[0] == "failed"
    assert row[1] == "timeout"


# Test that get_next_batch returns only queued URLs
def test_get_next_batch_returns_queued_only():
    init_db()
    queue = URLQueue()

    urls = [
        "https://www.haascnc.com/machines/lathe.html",
        "https://www.haascnc.com/machines/mill.html"
    ]
    for url in urls:
        queue.add_url(url)

    batch = queue.get_next_batch(limit=1)
    assert len(batch) == 1
    assert batch[0] in urls