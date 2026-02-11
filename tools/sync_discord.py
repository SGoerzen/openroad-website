#!/usr/bin/env python3
import os
import json
import re
import requests
from dateutil import parser as dt

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
CHANNEL_ID = os.environ["DISCORD_CHANNEL_ID"]
HEADERS = {"Authorization": f"Bot {TOKEN}"}

# How many recent messages to scan each run
LIMIT = int(os.environ.get("DISCORD_LIMIT", "100"))
# Keep only the newest N items in news.json (optional)
KEEP_MAX = int(os.environ.get("KEEP_MAX", "200"))

def ts_yyyymmddhhmm(iso_ts: str) -> str:
    d = dt.parse(iso_ts)
    return d.strftime("%Y%m%d%H%M")

def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:60] or "post"

def load_existing():
    """
    Loads existing news.json and returns (items_list, set_of_discord_ids).
    Supports older entries that may not have discord_id.
    """
    if not os.path.exists("news.json"):
        return [], set()

    with open("news.json", "r", encoding="utf-8") as f:
        items = json.load(f)

    ids = set()
    for it in items:
        did = it.get("discord_id")
        if did:
            ids.add(did)
    return items, ids

def extract_title_body(content: str):
    """
    Turn a Discord message content into (title, body).
    Heuristic:
      - title = first meaningful line
      - if first line is a greeting mentioning @everyone and ends with comma, skip it
      - body = rest
    """
    content = (content or "").strip()
    if not content:
        return None

    lines = [ln.rstrip() for ln in content.splitlines() if ln.strip() != ""]
    if not lines:
        return None

    first = lines[0].strip()

    # Greeting line like: "Good day @everyone," / "Hey @everyone,"
    if "@everyone" in first and first.endswith(",") and len(lines) > 1:
        title = lines[1].strip()
        body = "\n".join(lines[2:]).strip()
    else:
        title = first
        body = "\n".join(lines[1:]).strip()

    # fallback if body got empty
    if not body and len(lines) > 1:
        body = "\n".join(lines[1:]).strip()

    return title or "News", body

def embed_summary(m) -> str:
    """
    Optional: append first embed url + title/description if present.
    Keeps it simple and stable.
    """
    embeds = m.get("embeds") or []
    if not embeds:
        return ""

    e0 = embeds[0] or {}
    parts = []
    url = e0.get("url")
    if url:
        parts.append(url)
    etitle = (e0.get("title") or "").strip()
    edesc = (e0.get("description") or "").strip()

    if etitle and not url:
        parts.append(etitle)
    if edesc:
        parts.append(edesc)

    return "\n\n".join([p for p in parts if p]).strip()

def main():
    os.makedirs("posts", exist_ok=True)

    # Fetch messages
    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages?limit={min(LIMIT, 100)}"
    r = requests.get(url, headers=HEADERS, timeout=30)
    print("discord status:", r.status_code)
    print("discord head:", r.text[:120].replace("\n", "\\n"))
    r.raise_for_status()
    msgs = r.json()
    print("msgs:", len(msgs))

    existing, existing_ids = load_existing()

    new_items = []
    for m in msgs:
        discord_id = m.get("id")
        if not discord_id or discord_id in existing_ids:
            continue

        content = (m.get("content") or "").strip()

        extracted = extract_title_body(content)
        if not extracted:
            # If you want to include even empty messages in the index, uncomment:
            # author = (m.get("author") or {}).get("username", "unknown")
            # timestamp = ts_yyyymmddhhmm(m["timestamp"])
            # new_items.append({"timestamp": timestamp, "author": author, "discord_id": discord_id})
            continue

        title, body = extracted

        # Add embed info if present (e.g., link preview)
        extra = embed_summary(m)
        if extra:
            body = (body + "\n\n" + extra).strip()

        author = (m.get("author") or {}).get("username", "unknown")
        timestamp = ts_yyyymmddhhmm(m["timestamp"])

        md_path = f"posts/{timestamp}-{slugify(title)}.md"
        if not os.path.exists(md_path):
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n")
                f.write(f"*{timestamp}* — {author}\n\n")
                f.write((body or "").strip() + "\n")

        new_items.append({
            "timestamp": timestamp,
            "author": author,
            "discord_id": discord_id,
            "title": title,
            "md": md_path
        })

    merged = existing + new_items
    merged.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    if KEEP_MAX > 0:
        merged = merged[:KEEP_MAX]

    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    print("new items:", len(new_items))
    print("total items:", len(merged))

if __name__ == "__main__":
    main()