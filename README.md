# Website Openroad

## Discord → GitHub News Feed (news.json + Markdown Posts)

This repository generates a simple, token-free news feed for a shipped application.

**Source of truth:** a Discord channel (announcements/news)  
**Output:** `news.json` (index) + `posts/*.md` (full posts)  
**Sync:** GitHub Actions (scheduled + manual trigger)  
**Consumption:** any client can fetch the static files (no secrets in the app)

### Why this exists

Shipping an app to third parties means **no tokens/secrets** can be embedded in the client.  
Instead, we keep Discord as the "editor UI" and GitHub as the static hosting.

The Discord bot token is stored **only** in GitHub Secrets and is used by a scheduled workflow that:
1. Fetches recent Discord messages
2. Converts them into `news.json` and `posts/*.md`
3. Commits the changes to this repository