# /// script
# requires-python = ">=3.10"
# dependencies = ["pytest", "yt-dlp", "youtube-transcript-api"]
# ///
"""Offline tests for fetch_youtube.py (no network).

Run with: uv run test_fetch_youtube.py
"""
import sys

import pytest

from fetch_youtube import extract_video_id, format_caption_line


@pytest.mark.parametrize(
    "url",
    [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/shorts/dQw4w9WgXcQ",
        "https://www.youtube.com/live/dQw4w9WgXcQ",
        "https://www.youtube.com/embed/dQw4w9WgXcQ",
    ],
)
def test_extract_video_id_handles_url_forms(url):
    video_id = extract_video_id(url)
    assert video_id == "dQw4w9WgXcQ"


def test_extract_video_id_rejects_other_urls():
    with pytest.raises(ValueError):
        extract_video_id("https://example.com/watch")


@pytest.mark.parametrize(
    "start, expected",
    [
        (0, "[00:00] hi"),
        (61.9, "[01:01] hi"),
        (3725, "[62:05] hi"),  # Minutes keep counting past an hour
    ],
)
def test_format_caption_line_pads_minutes_and_seconds(start, expected):
    line = format_caption_line(start, "hi")
    assert line == expected


if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
