import os
import json
import time
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

USE_GEMINI = False  # ❗ FORCE OFF (no quota issues)

try:
    from google import genai
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    USE_GEMINI = True
except:
    USE_GEMINI = False


class DigestOutput(BaseModel):
    title: str
    summary: str


def local_summarizer(title: str, content: str) -> DigestOutput:
    summary = content[:300].replace("\n", " ") + "..."
    return DigestOutput(
        title=title[:80],
        summary=summary
    )


def call_gemini(prompt):
    if not USE_GEMINI:
        return None

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print("❌ Gemini failed → fallback used")
        return None


class DigestAgent:
    def generate_digest(self, title: str, content: str, article_type: str) -> Optional[DigestOutput]:

        # 🔥 ALWAYS SAFE FALLBACK FIRST
        fallback = local_summarizer(title, content)

        if not USE_GEMINI:
            return fallback

        prompt = f"""
Summarize this {article_type}

Title: {title}
Content: {content[:4000]}

Return JSON:
{{"title": "...", "summary": "..."}}
"""

        text = call_gemini(prompt)

        if not text:
            return fallback

        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            parsed = json.loads(text[start:end])
            return DigestOutput(**parsed)
        except:
            return fallback