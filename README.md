# Openroad Website + GitHub News Feed (news.json + Markdown Posts)

This repository generates a simple, token-free news feed for a shipped application.

**Source of truth:** a Discord channel (announcements/news)  
**Output:** `news.json` (index) + `posts/*.md` (full posts)  
**Sync:** GitHub Actions (scheduled + manual trigger)  
**Consumption:** any client can fetch the static files (no secrets in the app)

## Why this exists

Shipping an app to third parties means **no tokens/secrets** can be embedded in the client.  
Instead, we keep Discord as the "editor UI" and GitHub as the static hosting.

The Discord bot token is stored **only** in GitHub Secrets and is used by a scheduled workflow that:
1. Fetches recent Discord messages
2. Converts them into `news.json` and `posts/*.md`
3. Commits the changes to this repository

## Repository structure

```
.
├── news.json                  # generated index used by the app
├── posts/                     # generated markdown posts
├── tools/
│   └── sync_discord.py         # sync script (Discord -> files)
└── .github/workflows/
    └── sync-discord.yml        # GitHub Action (schedule + manual)
```

## Prerequisites (Discord)

1. Create a Discord application + bot (Discord Developer Portal)
2. Add the bot to your server
3. Grant the bot **only** the minimum permissions in the target channel:
   - View Channel
   - Read Message History
4. Enable **MESSAGE CONTENT INTENT** for the bot (required to read message content).

## GitHub setup

### Secrets
Add these repository secrets:
- `DISCORD_BOT_TOKEN` – Discord bot token
- `DISCORD_CHANNEL_ID` – channel id to read from

### Workflow permissions
The workflow must be allowed to push commits:
- workflow includes `permissions: contents: write`

## How it works

### Extraction rules
The sync script processes the latest N messages (default: 100):

- Title/body are derived from message content:
  - Title = first meaningful line
  - Body = remaining text
  - If the first line looks like a greeting mentioning `@everyone` and ends with a comma (e.g. "Hey @everyone,"), it is skipped.
- If a message has link preview embeds, the script may append the first embed URL/title/description to the markdown body.
- Messages are deduplicated using Discord `message.id` (`discord_id`) stored in `news.json`.

### Output format (`news.json`)
`news.json` is a JSON array. Each entry typically looks like:

```json
{
  "timestamp": "202411181340",
  "author": "ferdoran",
  "discord_id": "1308064186517028894",
  "title": "We decided to open source SilkRust.",
  "md": "posts/202411181340-we-decided-to-open-source-silkrust.md"
}
```

## Running locally

### macOS/Linux
```bash
python -m pip install -U requests python-dateutil
DISCORD_BOT_TOKEN="..." DISCORD_CHANNEL_ID="..." python tools/sync_discord.py
```

### Optional environment variables
- `DISCORD_LIMIT` (default `100`) – how many recent messages to scan (max 100 per Discord request)
- `KEEP_MAX` (default `200`) – keep only newest N items in `news.json`

Example:
```bash
DISCORD_LIMIT=50 KEEP_MAX=50 DISCORD_BOT_TOKEN="..." DISCORD_CHANNEL_ID="..." python tools/sync_discord.py
```

## Running in GitHub Actions

- Manual trigger: Repo → **Actions** → workflow → **Run workflow**
- Scheduled: configured in `.github/workflows/sync-discord.yml`

## Client usage (token-free)

Clients fetch the static file via:
- Raw GitHub: `https://raw.githubusercontent.com/<user>/<repo>/main/news.json`
- or GitHub Pages (recommended if enabled): `https://<user>.github.io/<repo>/news.json`

No authentication is needed.

## Security

- Never commit tokens.
- Store the bot token only in GitHub Secrets.
- If a token was ever exposed, **reset it immediately** in the Discord Developer Portal.

## Troubleshooting

### `news.json` stays empty
- Verify the channel contains messages with text content.
- Ensure **MESSAGE CONTENT INTENT** is enabled for the bot.
- Check workflow logs for:
  - `discord status: 200`
  - `msgs: <number>`
  - `new items: <number>`

### 401 / 403 errors
- 401: wrong/invalid token
- 403: missing permissions on the channel (View Channel + Read Message History)

## License
TBD / add your project license here.
