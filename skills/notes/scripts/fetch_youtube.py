# /// script
# requires-python = ">=3.10"
# dependencies = ["yt-dlp", "youtube-transcript-api"]
# ///
"""Fetch a YouTube video's metadata and timestamped transcript.

Prints the metadata as JSON to stdout and writes the transcript to <out_dir>/<video_id>.txt,
one "[mm:ss] text" line per caption, so long videos don't flood the context.

Run with: uv run fetch_youtube.py <url> <out_dir>
"""
import json
import os
import re
import sys

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

VIDEO_ID_PATTERN = re.compile(r"(?:v=|youtu\.be/|shorts/|live/|embed/)([A-Za-z0-9_-]{11})")


def extract_video_id(url: str) -> str:
    match = VIDEO_ID_PATTERN.search(url)
    if match is None:
        raise ValueError(f"No YouTube video id found in {url}")
    video_id = match.group(1)
    return video_id


def fetch_metadata(url: str) -> dict | None:
    options = {"quiet": True, "skip_download": True, "no_warnings": True}
    try:
        with yt_dlp.YoutubeDL(options) as downloader:
            info = downloader.extract_info(url, download=False)
    except yt_dlp.utils.DownloadError:
        return None  # Metadata is nice-to-have; the transcript is what matters
    upload_date = info.get("upload_date")  # YYYYMMDD
    published = None
    if upload_date is not None:
        published = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"
    metadata = {
        "title": info.get("title"),
        "channel": info.get("channel"),
        "duration": info.get("duration_string"),
        "published": published,
        "description": (info.get("description") or "")[:1500],
    }
    return metadata


def format_caption_line(start: float, text: str) -> str:
    minutes = int(start // 60)
    seconds = int(start % 60)
    line = f"[{minutes:02d}:{seconds:02d}] {text}"
    return line


def fetch_transcript_lines(video_id: str) -> tuple[list[str], str]:
    api = YouTubeTranscriptApi()
    transcript_list = api.list(video_id)
    language_codes = [transcript.language_code for transcript in transcript_list]
    preferred = ["en", "en-GB", "en-US"] + language_codes  # English first, else whatever exists
    transcript = transcript_list.find_transcript(preferred)
    snippets = transcript.fetch()
    lines = [format_caption_line(snippet.start, snippet.text) for snippet in snippets]
    return lines, transcript.language_code


def main() -> None:
    url = sys.argv[1]
    out_dir = sys.argv[2]
    video_id = extract_video_id(url)
    metadata = fetch_metadata(url)
    lines, language = fetch_transcript_lines(video_id)
    os.makedirs(out_dir, exist_ok=True)
    transcript_path = os.path.join(out_dir, f"{video_id}.txt")
    with open(transcript_path, "w") as transcript_file:
        transcript_file.write("\n".join(lines))
    word_count = sum(len(line.split()) - 1 for line in lines)
    summary = {
        "video_id": video_id,
        "metadata": metadata,
        "transcript_language": language,
        "transcript_path": transcript_path,
        "transcript_lines": len(lines),
        "transcript_words": word_count,
    }
    print(json.dumps(summary, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
