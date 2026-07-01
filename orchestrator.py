import sqlite3
import feedparser
import requests
import json
import uuid
from datetime import datetime, timedelta
import os
import re
import time 
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

API_KEYS = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3"),
    os.getenv("GEMINI_API_KEY_4")
]
API_KEYS = [key for key in API_KEYS if key is not None]

if not API_KEYS:
    raise ValueError("CRITICAL: No API keys found in .env file.")

# ==========================================
# 1. DATABASE SETUP
# ==========================================
def init_db(db_name="news_aggregator.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            article_id TEXT PRIMARY KEY,
            cluster_id TEXT,
            original_title TEXT,
            original_url TEXT,
            source_domain TEXT,
            image_url TEXT,
            raw_text TEXT,
            title_en TEXT,
            bullets_en TEXT,
            perspective_en TEXT,
            title_sq TEXT,
            bullets_sq TEXT,
            perspective_sq TEXT,
            title_mk TEXT,
            bullets_mk TEXT,
            perspective_mk TEXT,
            title_sr TEXT,
            bullets_sr TEXT,
            perspective_sr TEXT,
            cluster_category TEXT,
            cluster_geo_scope TEXT,
            geo_pro_western REAL,
            narrative_objectivity REAL,
            narrative_divergence_score REAL,
            published_at DATETIME
        )
    ''')
    conn.commit()
    conn.close()

# ==========================================
# 2. DATA INGESTION
# ==========================================
def fetch_rss_feeds(feed_urls):
    articles = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for source_name, url in feed_urls.items():
        try:
            response = requests.get(url, headers=headers, timeout=15)
            parsed_feed = feedparser.parse(response.content)
        except Exception as e:
            print(f"Failed to fetch {source_name}: {e}")
            continue
            
        valid_entries_count = 0
        for entry in parsed_feed.entries:
            if valid_entries_count >= 10: # Keeps the 10 depth
                break
            title = entry.get('title', '').strip()
            summary = entry.get('summary', '').strip()
            raw_text = summary if summary else title
            if not title or len(raw_text) < 15 or "Titulli mungon" in title:
                continue
            
            image_url = ""
            if 'media_content' in entry and entry.media_content:
                image_url = entry.media_content[0].get('url', '')
            elif 'enclosures' in entry and entry.enclosures:
                for enc in entry.enclosures:
                    if 'image' in enc.get('type', ''):
                        image_url = enc.get('href', '')
                        break
            if not image_url and summary:
                img_match = re.search(r'<img[^>]+src=["\'](.*?)["\']', summary, re.IGNORECASE)
                if img_match:
                    image_url = img_match.group(1)
                    
            articles.append({
                "article_id": str(uuid.uuid4()),
                "original_title": title,
                "original_url": entry.get('link', ''),
                "source_domain": source_name, 
                "image_url": image_url,
                "published_at": datetime.now().isoformat(),
                "raw_text": raw_text
            })
            valid_entries_count += 1
    return articles

class ArticleAnalysis(BaseModel):
    cluster_category: str
    cluster_geo_scope: str
    title_en: str
    bullets_en: str
    perspective_en: str
    title_sq: str
    bullets_sq: str
    perspective_sq: str
    title_mk: str
    bullets_mk: str
    perspective_mk: str
    title_sr: str
    bullets_sr: str
    perspective_sr: str
    geo_pro_western: float
    narrative_objectivity: float
    narrative_divergence_score: float

class ArticleClusterMapping(BaseModel):
    clusters: list[list[str]] = Field(description="Group article_ids together if they belong to the same core story event.")

# ==========================================
# 3. AI ENGINES
# ==========================================
def analyze_article_with_llm(text):
    prompt = f"Analyze and translate this news text into English, Albanian, Macedonian, and Serbian: {text}"
    for index, key in enumerate(API_KEYS):
        try:
            client = genai.Client(api_key=key)
            response = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json", response_schema=ArticleAnalysis, temperature=0.2
                )
            )
            raw_text = response.text.strip()
            if raw_text.startswith("
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1
http://googleusercontent.com/immersive_entry_chip/2
http://googleusercontent.com/immersive_entry_chip/3

Commit this new `orchestrator.py` layout to your repository and trigger the action once. It will parse the existing 380+ rows historically, locate the matching narratives that occurred at different hours over the last two days, and bundle them together natively.
