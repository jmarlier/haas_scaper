import pytest
from utils.queue_manager import URLQueue
import sqlite3
import os

def make_queue():
    # Use an in-memory SQLite DB for isolation
    return URLQueue(db_path=":memory:")

def test_add_and_is_known():
    queue = make_queue()
    url = "https://www.haascnc.com/machines/vf-2.html"
    assert not queue.is_known(url)
    queue.add_url(url)
    assert queue.is_known(url)

def test_mark_done_and_failed():
    queue = make_queue()
    url = "https://www.haascnc.com/machines/vf-2.html"
    queue.add_url(url)
    queue.mark_done(url)
    # Should not be in next batch
    assert url not in queue.get_next_batch()
    queue.mark_failed(url, reason="test fail")
    # Should still not be in next batch
    assert url not in queue.get_next_batch()

def test_mark_requeued():
    queue = make_queue()
    url = "https://www.haascnc.com/machines/vf-2.html"
    queue.add_url(url)
    queue.mark_failed(url, reason="fail")
    queue.mark_requeued(url)
    # Should be back in next batch
    assert url in queue.get_next_batch()

def test_get_next_batch_and_count_by_status():
    queue = make_queue()
    urls = [f"https://www.haascnc.com/machines/vf-{i}.html" for i in range(5)]
    for url in urls:
        queue.add_url(url)
    batch = queue.get_next_batch(limit=3)
    assert len(batch) == 3
    stats = queue.count_by_status()
    assert stats.get("queued", 0) >= 2

def test_get_failed_urls():
    queue = make_queue()
    urls = [f"https://www.haascnc.com/machines/vf-{i}.html" for i in range(3)]
    for url in urls:
        queue.add_url(url)
        queue.mark_failed(url, reason="fail")
    failed = queue.get_failed_urls(limit=2)
    assert len(failed) == 2
    for url in failed:
        assert url.startswith("https://www.haascnc.com/machines/vf-")