from typing import Optional
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.scrapers.youtube import YouTubeScraper
from app.database.repository import Repository


logger = logging.getLogger(__name__)

# Optional marker (not really needed anymore but kept for safety)
TRANSCRIPT_UNAVAILABLE_MARKER = "__UNAVAILABLE__"


def build_fallback_content(video) -> str:
    """
    Create fallback content using title + description
    """
    title = getattr(video, "title", "") or ""
    description = getattr(video, "description", "") or ""

    content = f"{title}. {description}".strip()

    # Extra safety: avoid empty content
    if not content:
        content = "No content available for this video."

    return content


def process_youtube_transcripts(limit: Optional[int] = None) -> dict:
    scraper = YouTubeScraper()
    repo = Repository()

    videos = repo.get_youtube_videos_without_transcript(limit=limit)

    processed = 0
    unavailable = 0
    failed = 0

    logger.info(f"Processing {len(videos)} YouTube videos...")

    for video in videos:
        try:
            logger.info(f"Processing video: {video.video_id}")

            transcript_result = scraper.get_transcript(video.video_id)

            # ✅ CASE 1: Transcript available
            if transcript_result and getattr(transcript_result, "text", "").strip():
                content = transcript_result.text.strip()
                processed += 1
                logger.info(f"Transcript fetched for {video.video_id}")

            # ✅ CASE 2: Fallback (NO transcript)
            else:
                content = build_fallback_content(video)
                unavailable += 1
                logger.warning(f"Transcript unavailable, using fallback for {video.video_id}")

            # Save ALWAYS (important fix)
            repo.update_youtube_video_transcript(video.video_id, content)

        except Exception as e:
            logger.error(f"Error processing video {video.video_id}: {e}")

            # ✅ FALLBACK EVEN ON ERROR
            try:
                content = build_fallback_content(video)
                repo.update_youtube_video_transcript(video.video_id, content)
                unavailable += 1
                logger.warning(f"Fallback used after error for {video.video_id}")
            except Exception as inner_e:
                failed += 1
                logger.error(f"Completely failed for {video.video_id}: {inner_e}")

    summary = {
        "total": len(videos),
        "processed": processed,
        "unavailable": unavailable,
        "failed": failed
    }

    logger.info(f"YouTube Processing Summary: {summary}")

    return summary


if __name__ == "__main__":
    result = process_youtube_transcripts()
    print(f"Total videos: {result['total']}")
    print(f"Processed: {result['processed']}")
    print(f"Unavailable (fallback used): {result['unavailable']}")
    print(f"Failed: {result['failed']}")