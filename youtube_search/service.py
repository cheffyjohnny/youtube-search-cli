from __future__ import annotations

import os

from .client import MockYouTubeClient, RealYouTubeClient, YouTubeClient
from .models import Video


def build_client() -> tuple[YouTubeClient, bool]:
    """Picks a client based on env config. Returns (client, is_mock)."""
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if api_key:
        return RealYouTubeClient(api_key), False
    return MockYouTubeClient(), True


def search_by_views(client: YouTubeClient, keyword: str, max_results: int = 10) -> list[Video]:
    videos = client.search(keyword, max_results=max_results)
    return sorted(videos, key=lambda v: v.view_count, reverse=True)
