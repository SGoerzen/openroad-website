import os, json, re
import requests
from dateutil import parser as dt

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
CHANNEL_ID = os.environ["DISCORD_CHANNEL_ID"]
HEADERS = {"Authorization": f"Bot {TOKEN}"}

def ts_yyyymmddhhmm(iso_ts: str) -> str:
    d = dt.parse(iso_ts)
    return d.strftime("%Y%m%d%H%M")

def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:60] or "post"

def main():
    os.makedirs("posts", exist_ok=True)

    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages?limit=50"
    msgs = requests.get(url, headers=HEADERS, timeout=30).json()

    items = []
    for m in msgs:
        content = (m.get("content") or "").strip()
        if not content.startswith("[NEWS]"):
            continue

        author = m.get("author", {}).get("username", "unknown")
        timestamp = ts_yyyymmddhhmm(m["timestamp"])

        lines = content.splitlines()
        title = lines[0].replace("[NEWS]", "").strip() or "News"
        body = "\n".join(lines[1:]).strip()

        md_path = f"posts/{timestamp}-{slugify(title)}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n{body}\n")

        items.append({"timestamp": timestamp, "author": author, "title": title, "md": md_path})

    # Neueste zuerst
    items.sort(key=lambda x: x["timestamp"], reverse=True)

    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()