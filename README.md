# 🕷️ HaasCNC Web Scraper

An **asynchronous**, **resilient**, and **production-ready** web scraper targeting [https://www.haascnc.com](https://www.haascnc.com) – English content only.

## 🚀 Project Goal

This scraper aims to:
- Aggressively crawl the HaasCNC website (ignoring robots.txt),
- Classify pages by **template type** (machine, promo, docs, etc.),
- Extract **main content** (excluding headers, footers, nav, cookie banners),
- Parse and extract **structured data**: tables, specs, PDFs, JSON-LD,
- Store all extracted data in a **normalized SQLite database**.

## 🧱 Project Structure

- `main.py` – main crawler loop
- `crawler/`
- `crawler.py` – URL fetching and link extraction
- `queue.py` – persistent queue handling (`url_queue.jsonl`)
- `user_agents.py` – rotating User-Agent pool
- `parsers/`
- `base.py` – template detection
- (template-specific parsers to come)
- `db.py` – (coming soon) SQLite connection and schema
- `clean_queue.py` – cleans malformed lines in the URL queue

## 🔧 Tech Stack

-  Python 3.12+
-  async HTTP client
- `BeautifulSoup4` – HTML parsing
- `sqlite3` – database
- `asyncio`, `pathlib`, `json`, `random`, etc.