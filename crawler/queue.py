# crawler/queue.py

import json
from pathlib import Path

QUEUE_FILE = Path("url_queue.jsonl")

def enqueue(url: str) -> None:
    with open(QUEUE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps({"url": url}))
        f.write("\n")  # Assure que chaque URL est bien sur sa propre ligne

def dequeue() -> str | None:
    if not QUEUE_FILE.exists():
        return None

    lines = QUEUE_FILE.read_text(encoding="utf-8").splitlines()
    while lines:
        line = lines.pop(0).strip()
        if not line:
            continue  # ligne vide → on saute

        try:
            url = json.loads(line)["url"]
        except json.JSONDecodeError:
            print(f"⚠️ Ligne mal formée ignorée : {line}")
            continue

        # Réécrit le fichier sans la ligne extraite
        QUEUE_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return url

    return None

def peek_all() -> list[str]:
    if not QUEUE_FILE.exists():
        return []

    urls = []
    for line in QUEUE_FILE.read_text(encoding="utf-8").splitlines():
        try:
            data = json.loads(line)
            urls.append(data["url"])
        except json.JSONDecodeError:
            print(f"⚠️ Ligne mal formée ignorée : {line[:100]}")
    return urls