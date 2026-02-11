# ADR-0001: Discord → GitHub Actions → Static News Feed

## Status
Accepted

## Context
We need a lightweight "news feed" for an application distributed to third parties.

Constraints:
- The shipped client must not include any secrets/tokens.
- The feed should be maintainable with minimal operational overhead.
- The solution should be free/low-cost and reliable.
- Content should be easy to author and update.

Discord is already the community hub, so it is a natural place to author announcements.

## Decision
We synchronize announcements from a Discord channel into a GitHub repository using GitHub Actions.

- Discord acts as the content authoring surface.
- A Discord bot token is stored **only** in GitHub Secrets.
- A scheduled (and manually triggerable) GitHub Action fetches recent messages from the configured channel.
- The job generates:
  - `news.json` as an index for clients
  - `posts/*.md` as full markdown pages
- The workflow commits and pushes changes back into the repository.

Clients read the feed from GitHub (Raw or GitHub Pages) without any authentication.

## Rationale
This approach satisfies all constraints:
- **No secrets in the client:** token exists only in GitHub Secrets.
- **No server to maintain:** GitHub Actions performs the sync; GitHub serves static files.
- **Works with free tiers:** public repositories keep Actions usage effectively free for this type of workload.
- **Versionable and auditable:** `news.json` and markdown changes are tracked in Git history.
- **Simple rollback:** revert commits if needed.

## Alternatives considered

### A) Client reads directly from Discord
Rejected.
- Requires embedding a token or implementing OAuth, which is unsafe for distributed clients.

### B) Discord webhook triggers GitHub Action directly
Rejected (as primary).
- Discord webhooks are designed to send messages to Discord; they are not a reliable "message created" event push into GitHub without an extra receiver/bridge.

### C) Self-hosted service (API + DB)
Rejected.
- Adds hosting, maintenance, and operational overhead.

### D) Third-party automation platform (Zapier/Make/n8n hosted)
Rejected (optional).
- Adds external dependency and sometimes cost/limitations.

## Consequences

### Positive
- Token-free client consumption
- Minimal ops burden
- Simple content workflow (post in Discord)
- Git provides history/audit trail

### Negative
- Content appears with a delay depending on schedule (e.g., daily)
- Requires enabling Discord bot **MESSAGE CONTENT INTENT** to read message contents reliably
- Parsing heuristics can mis-detect titles; may need tweaks over time

## Implementation notes
- GitHub Action requires `permissions: contents: write`.
- Bot should have minimal channel permissions: View Channel, Read Message History.
- Deduplication is based on Discord message id stored as `discord_id` in `news.json`.
- Parsing heuristics:
  - title = first meaningful line
  - optional skip greeting line with `@everyone,`
  - append first embed URL/info to markdown body (optional)

## Follow-ups
- Consider adding schema/version field later if clients need compatibility guarantees.
- Consider ETag/If-None-Match caching on the client to reduce traffic.
