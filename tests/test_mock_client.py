from __future__ import annotations

from youtube_search.client import MockYouTubeClient


def test_mock_client_filters_by_keyword_in_title() -> None:
    client = MockYouTubeClient()

    results = client.search("python")

    assert len(results) > 0
    assert all("python" in v.title.lower() for v in results)


def test_mock_client_falls_back_to_full_list_when_no_match() -> None:
    client = MockYouTubeClient()

    results = client.search("zzz_no_such_keyword_zzz")

    assert len(results) > 0


def test_mock_client_respects_max_results() -> None:
    client = MockYouTubeClient()

    results = client.search("python", max_results=1)

    assert len(results) == 1
