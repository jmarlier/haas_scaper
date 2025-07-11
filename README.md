# 🕷️ HaasCNC Web Scraper

An **asynchronous**, **resilient**, and **production-ready** web scraper targeting [https://www.haascnc.com](https://www.haascnc.com) – English content only.

---

## 🚀 Project Goal

This scraper aims to:

- Aggressively crawl the HaasCNC website (ignoring robots.txt)
- Classify pages by **template type** (machine, promo, docs, etc.)
- Extract **main content** (excluding headers, footers, nav, cookie banners)
- Parse and extract **structured data**: tables, specs, PDFs, JSON-LD
- Store all extracted data in a **normalized SQLite database**

---

## 🧱 Project Structure

- `main.py` – Example entry point for parsing a single page
- `crawl_machines.py` – Main machine crawler (async, resumable, JSON export)
- `crawl_promos.py` – Promo pages crawler
- `crawl_docs.py` – Service/support docs crawler
- `parsers/` – All page-type-specific parsers and template detection
- `utils/` – Networking, proxies, user-agents, queue management
- `db/` – DB schema and utility functions
- `tests/` – Pytest suite for ignore-list, parsers, DB, proxies, queue
- `requirements.txt` – Python dependencies
- `README.md` – This file

---

## 🔧 Installation

1. **Clone the repo**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) **Set up proxies** (see below)

---

## 🚦 Usage

### Crawl all machines

```bash
python crawl_machines.py
```

### Crawl promos

```bash
python crawl_promos.py
```

### Crawl service/support docs

```bash
python crawl_docs.py
```

### Options

- Set `DRY_RUN = True` in the script to simulate without writing to DB
- Set `EXPORT_JSON = True` to export results as JSON

---

## 🌐 Proxy Setup

- Add your proxies (one per line) in a file named `proxies.txt` in the project root.
- Supported format: `http://user:pass@host:port` or `http://host:port`
- The scraper will rotate proxies and user-agents automatically.

---

## 🗄️ Database Structure

- **SQLite file**: `haasSiteData.db`
- **Tables**:
  - `machines` (id, url, title, subtitle, image_url, pdf_url, promo_text)
  - `machine_specs` (id, machine_id, label, value)
  - `promos` (id, url, title, promo_text)
  - `service_docs` (id, url, title, description, pdf_url)
- **Full-text indexes** for fast search

---

## 🧪 Testing

- Run all tests:
  ```bash
  pytest tests/
  ```
- Coverage:
  - Ignore-list filtering
  - Parsers (machine, promo, service, doc)
  - Queue logic
  - DB utility functions
  - Proxy/user-agent rotation

---

## 📦 Deliverables

- `haasSiteData.db` – Example SQLite database
- `crawl_results.json`, `crawl_promos_results.json`, `crawl_docs_results.json` – Example exports
- `crawler.log` – Example log file
- `README.md`, `requirements.txt`
- `tests/` – Full test suite

---

## 🤝 Contact & Support

For questions, issues, or support, please contact the project maintainer.

---

## 🛠️ Tech Stack

- Python 3.12+
- `httpx`, `asyncio` – Async HTTP client
- `BeautifulSoup4` – HTML parsing
- `sqlite3` – Database
- `pytest` – Testing
- `lxml`, `random`, `json`, etc.
