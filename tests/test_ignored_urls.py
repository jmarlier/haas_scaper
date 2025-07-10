from utils.queue_manager import is_ignored_url

def test_should_ignore_localized_urls():
    assert is_ignored_url("https://www.haascnc.com/fr/machines.html") is True
    assert is_ignored_url("https://www.haascnc.com/de/index.html") is True

def test_should_not_ignore_machine_page():
    assert is_ignored_url("https://www.haascnc.com/machines/vf-series.html") is False