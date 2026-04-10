import os
import json
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Try Gemini (safe import)
try:
    from google import genai
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    GEMINI_AVAILABLE = True
except:
    GEMINI_AVAILABLE = False

load_dotenv()


class EmailIntroduction(BaseModel):
    greeting: str
    introduction: str


class RankedArticleDetail(BaseModel):
    digest_id: str
    rank: int
    relevance_score: float
    title: str
    summary: str
    url: str
    article_type: str
    reasoning: Optional[str] = None


class EmailDigestResponse(BaseModel):
    introduction: EmailIntroduction
    articles: List[RankedArticleDetail]
    total_ranked: int
    top_n: int

    def to_markdown(self) -> str:
        markdown = f"{self.introduction.greeting}\n\n"
        markdown += f"{self.introduction.introduction}\n\n---\n\n"

        for article in self.articles:
            markdown += f"## {article.title}\n\n"
            markdown += f"{article.summary}\n\n"
            markdown += f"[Read more →]({article.url})\n\n---\n\n"

        return markdown


# ✅ SAFE GEMINI CALL (NO RETRY LOOP)
def call_gemini(prompt: str) -> Optional[str]:
    if not GEMINI_AVAILABLE:
        return None

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        print("❌ Gemini failed → using fallback")
        return None


class EmailAgent:
    def __init__(self, user_profile: dict):
        self.user_profile = user_profile

    # ✅ FALLBACK INTRO (ALWAYS WORKS)
    def fallback_intro(self):
        current_date = datetime.now().strftime('%B %d, %Y')
        return EmailIntroduction(
            greeting=f"Hey {self.user_profile['name']}, here is your daily digest of AI news for {current_date}.",
            introduction="Here are the top AI news articles ranked based on your interests."
        )

    def generate_introduction(self, ranked_articles: List) -> EmailIntroduction:
        if not ranked_articles:
            return self.fallback_intro()

        current_date = datetime.now().strftime('%B %d, %Y')

        article_titles = "\n".join(
            [f"- {a.title}" for a in ranked_articles[:5]]
        )

        prompt = f"""
Write a short email introduction.

User: {self.user_profile['name']}
Date: {current_date}

Articles:
{article_titles}

Return JSON:
{{
  "greeting": "...",
  "introduction": "..."
}}
"""

        text = call_gemini(prompt)

        # ❌ If Gemini fails → fallback
        if not text:
            return self.fallback_intro()

        try:
            json_start = text.find("{")
            json_end = text.rfind("}") + 1
            parsed = json.loads(text[json_start:json_end])
            return EmailIntroduction(**parsed)
        except:
            return self.fallback_intro()

    def create_email_digest_response(
        self,
        ranked_articles: List[RankedArticleDetail],
        total_ranked: int,
        limit: int = 10
    ) -> EmailDigestResponse:

        top_articles = ranked_articles[:limit]
        introduction = self.generate_introduction(top_articles)

        return EmailDigestResponse(
            introduction=introduction,
            articles=top_articles,
            total_ranked=total_ranked,
            top_n=limit
        )