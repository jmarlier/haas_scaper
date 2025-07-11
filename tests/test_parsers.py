import pytest
from parsers.machine_parser import parse_machine_page
from parsers.promo_parser import parse_promo_page
from parsers.service_parser import parse_service_page
from parsers.doc_parser import parse_service_doc_page

def test_parse_machine_page():
    html = '''
    <html><body>
        <h1>VF-2</h1>
        <h2>Vertical Mill</h2>
        <div class="specifications">
            <table>
                <tr><td>Travel</td><td>30" x 16" x 20"</td></tr>
                <tr><td>Spindle</td><td>8100 rpm</td></tr>
            </table>
        </div>
        <img src="/images/vf2.png" />
        <a href="/docs/vf2.pdf">Download PDF</a>
        <div class="promo-banner">Special Offer!</div>
    </body></html>
    '''
    url = "https://www.haascnc.com/machines/vf-2.html"
    data = parse_machine_page(url, html)
    assert data["title"] == "VF-2"
    assert data["subtitle"] == "Vertical Mill"
    assert data["specs"]["Travel"] == '30" x 16" x 20"'
    assert data["specs"]["Spindle"] == "8100 rpm"
    assert data["image_url"].endswith("vf2.png")
    assert data["pdf_url"].endswith("vf2.pdf")
    assert data["promo_text"] == "Special Offer!"

def test_parse_promo_page():
    html = '''
    <html><body>
        <h1>Summer Sale</h1>
        <div class="promo-banner">Save 20% on all mills!</div>
    </body></html>
    '''
    url = "https://www.haascnc.com/special-offers.html"
    data = parse_promo_page(url, html)
    assert data["title"] == "Summer Sale"
    assert "Save 20%" in data["promo_text"]

def test_parse_service_page():
    html = '''
    <html><body>
        <h1>Spindle Alarm</h1>
        <div class="text">Check spindle lubrication system.</div>
        <a href="/docs/alarm.pdf">Alarm PDF</a>
    </body></html>
    '''
    url = "https://www.haascnc.com/service/alarm.html"
    data = parse_service_page(url, html)
    assert data["title"] == "Spindle Alarm"
    assert "lubrication" in data["description"]
    assert data["pdf_url"].endswith("alarm.pdf")

def test_parse_service_doc_page():
    html = '''
    <html><body>
        <h1>Alarm 123</h1>
        <div class="description">Spindle overload alarm.</div>
        <a href="/docs/alarm123.pdf">PDF</a>
    </body></html>
    '''
    url = "https://www.haascnc.com/service/alarm-123.html"
    data = parse_service_doc_page(url, html)
    assert data["title"] == "Alarm 123"
    assert "overload" in data["description"]
    assert data["pdf_url"].endswith("alarm123.pdf") 