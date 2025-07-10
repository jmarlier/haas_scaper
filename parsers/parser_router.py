from parsers import machine_parser, promo_parser, doc_parser
# blog_parser est optionnel, à ajouter si besoin

def parse_page_by_type(page_type: str, url: str, html: str) -> dict:
    if page_type == "machine":
        return machine_parser.parse_machine_page(url, html)
    elif page_type == "promo":
        return promo_parser.parse_promo_page(url, html)
    elif page_type == "service":
        return doc_parser.parse_service_doc_page(url, html)
    # elif page_type == "blog":
    #     return blog_parser.parse_blog_page(url, html)
    else:
        return {}


# --- Auto detection and routing ---
def detect_page_type(url: str, html: str) -> str:
    """Détecte le type de page en fonction de l'URL et du contenu HTML."""
    url_lower = url.lower()
    html_lower = html.lower()

    if "/machines/" in url_lower:
        if "Specs" in html or "Travel" in html or "Spindle" in html:
            return "machine"
    elif "/promos/" in url_lower or "promo-banner" in html_lower:
        return "promo"
    elif "/service/" in url_lower or "alarm code" in html_lower or "manual" in html_lower:
        return "service"
    return "unknown"


def route_parse(url: str, html: str) -> dict:
    """Route automatiquement vers le bon parseur en fonction du type détecté."""
    page_type = detect_page_type(url, html)
    return parse_page_by_type(page_type, url, html)