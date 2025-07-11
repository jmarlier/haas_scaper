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
            print(f"⚠️ Ignored line (malformed): {line}")

    queue_file.write_text("\n".join(cleaned_lines) + "\n", encoding="utf-8")
    print(f"✅ Cleaning complete: {len(cleaned_lines)} valid lines kept.")
else:
    print("❌ The file 'url_queue.jsonl' was not found.")