import pytest
from utils.queue_manager import is_ignored_url

def test_should_ignore_localized_urls():
    assert is_ignored_url("https://www.haascnc.com/fr/machines.html") is True
    assert is_ignored_url("https://www.haascnc.com/de/index.html") is True
    assert is_ignored_url("https://www.haascnc.com/es/promo.html") is True
    assert is_ignored_url("https://www.haascnc.com/zh/service.html") is True

def test_should_ignore_tooling_and_store():
    assert is_ignored_url("https://www.haascnc.com/tooling/") is True
    assert is_ignored_url("https://www.haascnc.com/store/") is True
    assert is_ignored_url("https://www.haascnc.com/shop/") is True
    assert is_ignored_url("https://www.haascnc.com/cart/") is True
    assert is_ignored_url("https://www.haascnc.com/checkout/") is True

def test_should_ignore_videos_and_community():
    assert is_ignored_url("https://www.haascnc.com/videos/") is True
    assert is_ignored_url("https://www.haascnc.com/community/") is True
    assert is_ignored_url("https://www.haascnc.com/myhaas/") is True

def test_should_not_ignore_english_machine_page():
    assert is_ignored_url("https://www.haascnc.com/machines/vertical-mills.html") is False
    assert is_ignored_url("https://www.haascnc.com/service/troubleshooting-and-how-to.html") is False