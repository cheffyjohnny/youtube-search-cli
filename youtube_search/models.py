from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Video:
    video_id: str
    title: str
    channel: str
    view_count: int
    published_at: str
    url: str
