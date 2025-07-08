from pathlib import Path
import json

queue_file = Path("url_queue.jsonl")
cleaned_lines = []

if queue_file.exists():
    for line in queue_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if "url" in obj and isinstance(obj["url"], str):
                cleaned_lines.append(json.dumps({"url": obj["url"]}))
        except json.JSONDecodeError:
            print(f"⚠️ Ligne ignorée (malformée) : {line}")

    queue_file.write_text("\n".join(cleaned_lines) + "\n", encoding="utf-8")
    print(f"✅ Nettoyage terminé : {len(cleaned_lines)} lignes valides conservées.")
else:
    print("❌ Le fichier 'url_queue.jsonl' est introuvable.")