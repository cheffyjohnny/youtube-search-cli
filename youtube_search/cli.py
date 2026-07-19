from __future__ import annotations

import click
from dotenv import load_dotenv

from .service import build_client, search_by_views

load_dotenv()


@click.group()
def cli() -> None:
    """youtube-search-cli: search YouTube and rank results by view count."""


@cli.command()
@click.argument("keyword", nargs=-1, required=True)
@click.option("--max", "max_results", default=10, show_default=True, help="Number of results to return.")
def search(keyword: tuple[str, ...], max_results: int) -> None:
    """Search YouTube for KEYWORD, sorted by views descending."""
    keyword = " ".join(keyword)
    client, is_mock = build_client()
    if is_mock:
        click.echo(
            "Mode: mock data (no YOUTUBE_API_KEY found). "
            "Set YOUTUBE_API_KEY in .env for live results.\n"
        )
    else:
        click.echo("Mode: live (YouTube Data API v3)\n")

    videos = search_by_views(client, keyword, max_results=max_results)
    if not videos:
        click.echo("No results found.")
        return

    for rank, video in enumerate(videos, start=1):
        click.echo(f"{rank}. {video.title}")
        click.echo(f"   Channel: {video.channel}  |  Views: {video.view_count:,}  |  {video.published_at}")
        click.echo(f"   {video.url}\n")


if __name__ == "__main__":
    cli()
