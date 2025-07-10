def classify_url(url: str, html: str = "") -> str:
    url = url.lower()

    if "/machines/" in url:
        return "machine"
    elif "/promo/" in url or "/special-offers/" in url:
        return "promo"
    elif "/service/" in url or "alarm" in url:
        return "service"
    elif "/news/" in url or "/about/" in url or "/company/" in url:
        return "blog"
    elif url.endswith(".pdf"):
        return "pdf"
    else:
        return "unknown"