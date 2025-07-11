

from bs4 import BeautifulSoup


def parse_service_page(url: str, html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    # Main title
    title = soup.find("h1")
    title_text = title.get_text(strip=True) if title else ""

    # Associated PDF (first .pdf link)
    pdf_url = ""
    for a in soup.find_all("a", href=True):
        if ".pdf" in a["href"]:
            pdf_url = a["href"]
            if pdf_url.startswith("/"):
                pdf_url = "https://www.haascnc.com" + pdf_url
            break

    # Summary or main paragraph
    content_block = soup.find("div", class_="text") or soup.find("p")
    description = content_block.get_text(strip=True) if content_block else ""

    return {
        "url": url,
        "title": title_text,
        "description": description,
        "pdf_url": pdf_url
    }