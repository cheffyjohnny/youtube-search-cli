from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path

import requests

from .models import Video

MOCK_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "mock_videos.json"

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


class YouTubeClient(ABC):
    @abstractmethod
    def search(self, keyword: str, max_results: int = 10) -> list[Video]:
        ...


class MockYouTubeClient(YouTubeClient):
    """Returns canned data so the CLI works without an API key."""

    def __init__(self, data_path: Path = MOCK_DATA_PATH) -> None:
        with open(data_path, encoding="utf-8") as f:
            raw = json.load(f)
        self._videos = [Video(**item) for item in raw]

    def search(self, keyword: str, max_results: int = 10) -> list[Video]:
        keyword_lower = keyword.lower()
        matches = [v for v in self._videos if keyword_lower in v.title.lower()]
        if not matches:
            matches = list(self._videos)
        return matches[:max_results]


class RealYouTubeClient(YouTubeClient):
    """Calls the YouTube Data API v3 (search.list, then videos.list for stats)."""

    # YouTube API's own per-call cap for both endpoints.
    CANDIDATES_PER_PAGE = 50
    # search.list's result set isn't a guaranteed-stable exhaustive scan —
    # repeated identical calls can surface a different slice of matching
    # videos as Google's index drifts. Paging through multiple calls widens
    # the candidate pool (~200 videos) so a high-view video is less likely to
    # be missed. Costs 100 quota units per page (400 total per search here)
    # against the API's 10,000/day free quota.
    MAX_PAGES = 4

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def search(self, keyword: str, max_results: int = 10) -> list[Video]:
        video_ids = self._find_video_ids(keyword)
        if not video_ids:
            return []
        videos = self._fetch_video_details(video_ids)
        videos.sort(key=lambda v: v.view_count, reverse=True)
        return videos[:max_results]

    def _find_video_ids(self, keyword: str) -> list[str]:
        video_ids: list[str] = []
        page_token = None

        for _ in range(self.MAX_PAGES):
            params = {
                "key": self._api_key,
                "q": keyword,
                "part": "snippet",
                "type": "video",
                "order": "viewCount",
                "maxResults": self.CANDIDATES_PER_PAGE,
            }
            if page_token:
                params["pageToken"] = page_token

            response = requests.get(YOUTUBE_SEARCH_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            items = data.get("items", [])
            video_ids.extend(item["id"]["videoId"] for item in items if "videoId" in item.get("id", {}))

            page_token = data.get("nextPageToken")
            if not page_token:
                break

        return video_ids

    def _fetch_video_details(self, video_ids: list[str]) -> list[Video]:
        videos: list[Video] = []

        for i in range(0, len(video_ids), self.CANDIDATES_PER_PAGE):
            batch = video_ids[i : i + self.CANDIDATES_PER_PAGE]
            response = requests.get(
                YOUTUBE_VIDEOS_URL,
                params={
                    "key": self._api_key,
                    "id": ",".join(batch),
                    "part": "snippet,statistics",
                },
                timeout=10,
            )
            response.raise_for_status()
            items = response.json().get("items", [])

            for item in items:
                snippet = item["snippet"]
                statistics = item.get("statistics", {})
                videos.append(
                    Video(
                        video_id=item["id"],
                        title=snippet["title"],
                        channel=snippet["channelTitle"],
                        view_count=int(statistics.get("viewCount", 0)),
                        published_at=snippet["publishedAt"][:10],
                        url=f"https://www.youtube.com/watch?v={item['id']}",
                    )
                )

        return videos
