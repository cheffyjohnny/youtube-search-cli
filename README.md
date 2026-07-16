# youtube-search-cli

A CLI that searches YouTube for a keyword and returns results ranked by view count, descending.

| Area | Technology |
|---|---|
| Language | Python 3.9+ |
| CLI framework | click |
| Data source | YouTube Data API v3, with automatic offline fallback if no API key is set |
| Data | Bundled mock JSON fixture (no storage/history — this is a stateless search tool) |

## Data source

- **With `YOUTUBE_API_KEY` set**: results come from the real YouTube Data API v3. `search.list` is paged through up to 4 calls (`nextPageToken`) to build a ~200-video candidate pool per search, since a single call only returns 50 results and isn't guaranteed to return the same slice of Google's index between calls. `videos.list` then fetches view counts for that pool (batched in groups of 50, its own per-call cap), and results are sorted by actual view count before display.
- **Without a key**: the CLI falls back to a bundled ~20-video mock dataset (`data/mock_videos.json`) spanning common topics (python, cooking, gaming, music, news, etc.), filtered by keyword and sorted the same way — the tool is fully usable with zero setup.
- The CLI always prints which mode is active (`Mode: live (YouTube Data API v3)` or `Mode: mock data (...)`) so it's never ambiguous which one produced a given result.
- Widening the candidate pool costs quota: each live search spends ~400 of the API's 10,000/day free units (4 `search.list` calls @ 100 units each) instead of 100, i.e. roughly 25 searches/day instead of 100.

Client code: [`youtube_search/client.py`](youtube_search/client.py).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
```

Optional — enable live results by copying `.env.example` to `.env` and adding a [YouTube Data API v3 key](https://console.cloud.google.com/) (enable "YouTube Data API v3" for a project, then create + restrict an API key to that API):
```bash
cp .env.example .env
# edit .env with your key
```

## Commands

```bash
yt-search search <keyword> --max 10   # search, ranked by views descending
pytest                                 # run the test suite
```

## Architecture

Same repository/interface-style layering as this project's siblings, [expense-tracker-cli](../expense-tracker-cli) (TypeScript) and [bookmark-manager-cli](../bookmark-manager-cli) (Python) — here the swappable abstraction is the data source itself rather than storage:

- `youtube_search/models.py` — `Video` dataclass
- `youtube_search/client.py` — `YouTubeClient` ABC + `RealYouTubeClient` (YouTube Data API v3, paginated) + `MockYouTubeClient` (bundled fixture, no key needed)
- `youtube_search/service.py` — `build_client()` picks real vs. mock based on `YOUTUBE_API_KEY`; `search_by_views()` sorts whatever the client returns by view count descending
- `youtube_search/cli.py` — click CLI wiring, loads `.env` via `python-dotenv`, prints which mode is active

Mock video data lives in `data/mock_videos.json` (committed — it's a shipped fixture, not user-generated content, unlike the gitignored `data/` in bookmark-manager-cli).

Built with the assistance of [Claude Code](https://claude.com/claude-code).
