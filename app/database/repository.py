from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_

from .models import YouTubeVideo, OpenAIArticle, AnthropicArticle, Digest
from .connection import get_session


class Repository:
    def __init__(self, session: Optional[Session] = None):
        self.session = session or get_session()

    # ---------------- YOUTUBE ---------------- #

    def create_youtube_video(self, video_id: str, title: str, url: str,
                            channel_id: str, published_at: datetime,
                            description: str = "", transcript: Optional[str] = None) -> Optional[YouTubeVideo]:

        if self.session.query(YouTubeVideo).filter_by(video_id=video_id).first():
            return None

        video = YouTubeVideo(
            video_id=video_id,
            title=title,
            url=url,
            channel_id=channel_id,
            published_at=published_at,
            description=description,
            transcript=transcript
        )

        self.session.add(video)
        self.session.commit()
        return video

    def bulk_create_youtube_videos(self, videos: List[dict]) -> int:
        new_videos = []

        for v in videos:
            exists = self.session.query(YouTubeVideo).filter_by(video_id=v["video_id"]).first()
            if not exists:
                new_videos.append(YouTubeVideo(
                    video_id=v["video_id"],
                    title=v["title"],
                    url=v["url"],
                    channel_id=v.get("channel_id", ""),
                    published_at=v["published_at"],
                    description=v.get("description", ""),
                    transcript=v.get("transcript")
                ))

        if new_videos:
            self.session.add_all(new_videos)
            self.session.commit()

        return len(new_videos)

    # 🔥 FIXED FUNCTION
    def get_youtube_videos_without_transcript(self, limit: Optional[int] = None) -> List[YouTubeVideo]:
        query = self.session.query(YouTubeVideo).filter(
            or_(
                YouTubeVideo.transcript.is_(None),
                YouTubeVideo.transcript == "",
                YouTubeVideo.transcript == "__UNAVAILABLE__"
            )
        ).order_by(YouTubeVideo.published_at.desc())

        if limit:
            query = query.limit(limit)

        return query.all()

    def update_youtube_video_transcript(self, video_id: str, transcript: str) -> bool:
        video = self.session.query(YouTubeVideo).filter_by(video_id=video_id).first()

        if video:
            video.transcript = transcript
            self.session.commit()
            return True

        return False

    def get_all_youtube_videos(self, limit: Optional[int] = None) -> List[YouTubeVideo]:
        query = self.session.query(YouTubeVideo).order_by(YouTubeVideo.published_at.desc())

        if limit:
            query = query.limit(limit)

        return query.all()

    # ---------------- OPENAI ---------------- #

    def create_openai_article(self, guid: str, title: str, url: str,
                             published_at: datetime, description: str = "",
                             category: Optional[str] = None) -> Optional[OpenAIArticle]:

        if self.session.query(OpenAIArticle).filter_by(guid=guid).first():
            return None

        article = OpenAIArticle(
            guid=guid,
            title=title,
            url=url,
            published_at=published_at,
            description=description,
            category=category
        )

        self.session.add(article)
        self.session.commit()
        return article

    def bulk_create_openai_articles(self, articles: List[dict]) -> int:
        new_articles = []

        for a in articles:
            exists = self.session.query(OpenAIArticle).filter_by(guid=a["guid"]).first()
            if not exists:
                new_articles.append(OpenAIArticle(
                    guid=a["guid"],
                    title=a["title"],
                    url=a["url"],
                    published_at=a["published_at"],
                    description=a.get("description", ""),
                    category=a.get("category")
                ))

        if new_articles:
            self.session.add_all(new_articles)
            self.session.commit()

        return len(new_articles)

    # ---------------- ANTHROPIC ---------------- #

    def create_anthropic_article(self, guid: str, title: str, url: str,
                                published_at: datetime, description: str = "",
                                category: Optional[str] = None) -> Optional[AnthropicArticle]:

        if self.session.query(AnthropicArticle).filter_by(guid=guid).first():
            return None

        article = AnthropicArticle(
            guid=guid,
            title=title,
            url=url,
            published_at=published_at,
            description=description,
            category=category
        )

        self.session.add(article)
        self.session.commit()
        return article

    def bulk_create_anthropic_articles(self, articles: List[dict]) -> int:
        new_articles = []

        for a in articles:
            exists = self.session.query(AnthropicArticle).filter_by(guid=a["guid"]).first()
            if not exists:
                new_articles.append(AnthropicArticle(
                    guid=a["guid"],
                    title=a["title"],
                    url=a["url"],
                    published_at=a["published_at"],
                    description=a.get("description", ""),
                    category=a.get("category")
                ))

        if new_articles:
            self.session.add_all(new_articles)
            self.session.commit()

        return len(new_articles)

    def get_anthropic_articles_without_markdown(self, limit: Optional[int] = None) -> List[AnthropicArticle]:
        query = self.session.query(AnthropicArticle).filter(
            or_(
                AnthropicArticle.markdown.is_(None),
                AnthropicArticle.markdown == ""
            )
        )

        if limit:
            query = query.limit(limit)

        return query.all()

    def update_anthropic_article_markdown(self, guid: str, markdown: str) -> bool:
        article = self.session.query(AnthropicArticle).filter_by(guid=guid).first()

        if article:
            article.markdown = markdown
            self.session.commit()
            return True

        return False

    # ---------------- DIGEST ---------------- #

    def get_articles_without_digest(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        articles = []

        # Existing digests
        seen_ids = {
            f"{d.article_type}:{d.article_id}"
            for d in self.session.query(Digest.article_type, Digest.article_id).all()
        }

        # YouTube
        youtube_videos = self.session.query(YouTubeVideo).filter(
            YouTubeVideo.transcript.isnot(None),
            YouTubeVideo.transcript != "",
            YouTubeVideo.transcript != "__UNAVAILABLE__"
        ).all()

        for video in youtube_videos:
            key = f"youtube:{video.video_id}"
            if key not in seen_ids:
                articles.append({
                    "type": "youtube",
                    "id": video.video_id,
                    "title": video.title,
                    "url": video.url,
                    "content": video.transcript or video.description or "",
                    "published_at": video.published_at
                })

        # OpenAI
        for article in self.session.query(OpenAIArticle).all():
            key = f"openai:{article.guid}"
            if key not in seen_ids:
                articles.append({
                    "type": "openai",
                    "id": article.guid,
                    "title": article.title,
                    "url": article.url,
                    "content": article.description or "",
                    "published_at": article.published_at
                })

        # Anthropic
        anthropic_articles = self.session.query(AnthropicArticle).filter(
            AnthropicArticle.markdown.isnot(None),
            AnthropicArticle.markdown != ""
        ).all()

        for article in anthropic_articles:
            key = f"anthropic:{article.guid}"
            if key not in seen_ids:
                articles.append({
                    "type": "anthropic",
                    "id": article.guid,
                    "title": article.title,
                    "url": article.url,
                    "content": article.markdown or article.description or "",
                    "published_at": article.published_at
                })

        if limit:
            articles = articles[:limit]

        return articles

    def create_digest(self, article_type: str, article_id: str, url: str,
                      title: str, summary: str,
                      published_at: Optional[datetime] = None) -> Optional[Digest]:

        digest_id = f"{article_type}:{article_id}"

        if self.session.query(Digest).filter_by(id=digest_id).first():
            return None

        created_at = published_at or datetime.now(timezone.utc)

        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        digest = Digest(
            id=digest_id,
            article_type=article_type,
            article_id=article_id,
            url=url,
            title=title,
            summary=summary,
            created_at=created_at
        )

        self.session.add(digest)
        self.session.commit()
        return digest

    def get_recent_digests(self, hours: int = 24) -> List[Dict[str, Any]]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

        digests = self.session.query(Digest).filter(
            Digest.created_at >= cutoff
        ).order_by(Digest.created_at.desc()).all()

        return [
            {
                "id": d.id,
                "article_type": d.article_type,
                "article_id": d.article_id,
                "url": d.url,
                "title": d.title,
                "summary": d.summary,
                "created_at": d.created_at
            }
            for d in digests
        ]