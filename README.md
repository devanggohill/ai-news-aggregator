# 🚀 AI News Aggregator – Production-Ready AI Pipeline

This project is a **complete AI-powered news aggregation system** built using modern tools like **Gemini API** and **Supabase**. It demonstrates how to design a **real-world, production-level AI pipeline** with modular architecture, fallback mechanisms, and automation.

---

## 📌 Overview

The AI News Aggregator automatically:

* Scrapes AI-related content (YouTube, blogs, RSS feeds)
* Processes and cleans raw data
* Generates summaries using LLMs (Gemini)
* Ranks articles based on user preferences
* Sends a personalized email digest

This project reflects **real-world development**, not just a tutorial.

---

## 🧠 Tech Stack

### 🔹 AI / LLM

* Gemini API (`google-genai`)
* Used for:

  * Summarization (Digest Agent)
  * Ranking (Curator Agent)
  * Email generation (Email Agent)

### 🔹 Backend

* Python
* Pydantic (data validation)
* dotenv (environment management)

### 🔹 Database

* Supabase (PostgreSQL)
* Stores:

  * Articles
  * Digests
  * Rankings

### 🔹 Data Sources

* YouTube (transcripts)
* RSS feeds (AI blogs/news)

### 🔹 Email

* SMTP-based email sending

---

## 📂 Project Structure

```bash
AI-News-Aggregator/
│
├── app/
│   ├── agents/                        # AI logic (LLM-based)
│   │   ├── __init__.py
│   │   ├── digest_agent.py
│   │   ├── curator_agent.py
│   │   └── email_agent.py
│   │
│   ├── database/                      # Database layer (Supabase)
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   ├── models.py
│   │   ├── repository.py
│   │   └── create_tables.py
│   │
│   ├── profiles/                      # User configuration
│   │   ├── __init__.py
│   │   └── user_profile.py
│   │
│   ├── scrapers/                      # Data collection
│   │   ├── __init__.py
│   │   ├── youtube_scraper.py
│   │   ├── openai_scraper.py
│   │   └── anthropic_scraper.py
│   │
│   ├── services/                      # Business logic
│   │   ├── __init__.py
│   │   ├── process_digest.py
│   │   ├── process_email.py
│   │   └── process_scrapers.py
│   │
│   ├── utils/                         # Helpers & fallback logic
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   ├── retry.py
│   │   ├── parser.py
│   │   └── config.py
│   │
│   └── daily_runner.py                # Pipeline controller
│
├── data/
│   ├── logs/
│   └── temp/
│
├── .env
├── main.py                            # Entry point
├── requirements.txt
├── pyproject.toml
├── README.md
└── uv.lock
```

---

## ⚙️ Architecture Diagram

```
                ┌────────────────────┐
                │   Data Sources     │
                │ (YouTube / RSS)    │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │   Scraper Layer    │
                │ (Fetch Articles)   │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │   Processing Layer │
                │ (Clean + Extract)  │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │   Digest Agent     │
                │ (Gemini API)       │
                │ Summarization      │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │   Supabase DB      │
                │ (Store Digests)    │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │   Curator Agent    │
                │ (Ranking via LLM)  │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │   Email Agent      │
                │ (Generate Email)   │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │   Email Service    │
                │ (Send Digest)      │
                └────────────────────┘
```

---

## 🔄 Workflow (Step-by-Step)

### 1. Scraping

* Collects data from:

  * YouTube videos
  * RSS feeds

---

### 2. Processing

* Extracts and cleans:

  * Titles
  * Transcripts
  * Content

---

### 3. Summarization (Digest Agent)

* Uses Gemini API to:

  * Generate summaries
  * Extract key insights

---

### 4. Storage

* Saves processed data into Supabase

---

### 5. Ranking (Curator Agent)

* Ranks articles based on:

  * User interests
  * Relevance score

---

### 6. Email Generation (Email Agent)

* Creates:

  * Personalized greeting
  * Summary preview

---

### 7. Delivery

* Sends final email using SMTP

---

## 🛡️ Fallback Mechanism (Very Important)

To handle API failures (like rate limits):

* If Gemini fails:

  * Use fallback summary or skip
* If ranking fails:

  * Use default sorting logic
* If email generation fails:

  * Use static template

✅ Ensures system **never crashes**
✅ Improves **reliability and robustness**

---

## 🌿 Branch Structure

* `master` → Core implementation
* `deployment` → Deployment setup
* `deployment-final` → Production-ready version

---

## 🚀 How to Run

```bash
# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run project
python main.py
```

---

## 🎯 Key Highlights

* Modular architecture (agents, services, database)
* Real-world AI pipeline design
* Gemini API integration
* Supabase database usage
* Fallback + retry mechanisms
* End-to-end automation

---

## 💡 Interview Explanation (Use This)

> “I built an AI-powered news aggregator using a modular architecture. Scrapers collect data, agents process it using Gemini API, services handle workflows, and Supabase stores results. I also implemented fallback mechanisms to handle API failures, making the system reliable and production-ready.”

---

## ⚠️ Notes

* This is a **live coding project**
* Focus is on:

  * Problem-solving
  * Real-world workflow
  * AI-assisted development

---

## 🚀 Final Thought

This project demonstrates how to build **scalable AI systems** that combine:

* Data ingestion
* LLM processing
* Ranking logic
* Automated delivery

---
