import os
import json
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

USE_GEMINI = False  # ❗ FORCE OFF

try:
    from google import genai
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    USE_GEMINI = True
except:
    USE_GEMINI = False


class RankedArticle(BaseModel):
    digest_id: str
    relevance_score: float
    rank: int
    reasoning: str


def local_ranker(digests: List[dict]) -> List[RankedArticle]:
    ranked = []

    for i, d in enumerate(digests):
        score = min(10.0, 5 + len(d.get("summary", "")) / 200)

        ranked.append(RankedArticle(
            digest_id=d["id"],
            relevance_score=round(score, 2),
            rank=i + 1,
            reasoning="Ranked based on content length and recency"
        ))

    return ranked


def call_gemini(prompt):
    if not USE_GEMINI:
        return None

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text.strip()
    except:
        print("❌ Gemini failed → fallback ranking used")
        return None


class CuratorAgent:
    def __init__(self, user_profile: dict):
        self.user_profile = user_profile

    def rank_digests(self, digests: List[dict]) -> List[RankedArticle]:
        if not digests:
            return []

        # 🔥 ALWAYS SAFE
        fallback = local_ranker(digests)

        if not USE_GEMINI:
            return fallback

        prompt = f"Rank these articles:\n{digests}"

        text = call_gemini(prompt)

        if not text:
            return fallback

        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            parsed = json.loads(text[start:end])

            return [
                RankedArticle(**a)
                for a in parsed["articles"]
            ]

        except:
            return fallback