from __future__ import annotations

from youtube_search.models import Video
from youtube_search.service import search_by_views


class FakeClient:
    def __init__(self, videos: list[Video]) -> None:
        self._videos = videos

    def search(self, keyword: str, max_results: int = 10) -> list[Video]:
        return self._videos[:max_results]


def make_video(video_id: str, view_count: int) -> Video:
    return Video(
        video_id=video_id,
        title=f"video {video_id}",
        channel="channel",
        view_count=view_count,
        published_at="2024-01-01",
        url=f"https://www.youtube.com/watch?v={video_id}",
    )


def test_search_by_views_sorts_descending() -> None:
    client = FakeClient([make_video("a", 100), make_video("b", 900), make_video("c", 500)])

    results = search_by_views(client, "anything")

    assert [v.video_id for v in results] == ["b", "c", "a"]


def test_search_by_views_respects_max_results() -> None:
    client = FakeClient([make_video("a", 100), make_video("b", 900), make_video("c", 500)])

    results = search_by_views(client, "anything", max_results=2)

    assert len(results) == 2
