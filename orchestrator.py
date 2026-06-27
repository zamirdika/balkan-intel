import sqlite3
import feedparser
import requests
import json
import uuid
from datetime import datetime
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
    # We DO NOT drop the table anymore so we can build up a database over days
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            article_id TEXT PRIMARY KEY,
            cluster_id TEXT,
            original_title TEXT,
            original_url TEXT,
            source_domain TEXT,
            image_url TEXT,
            raw_text TEXT,
            
            -- English (Master)
            title_en TEXT,
            bullets_en TEXT,
            perspective_en TEXT,
            
            -- Localized
            title_sq TEXT,
            bullets_sq TEXT,
            perspective_sq TEXT,
            
            title_mk TEXT,
            bullets_mk TEXT,
            perspective_mk TEXT,
            
            title_sr TEXT,
            bullets_sr TEXT,
            perspective_sr TEXT,
            
            -- Universal Categories & Metrics
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
            # INCREASED to 5 articles per feed to ensure overlapping news stories
            if valid_entries_count >= 5: 
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
                if not image_url:
                    image_url = entry.enclosures[0].get('href', '')
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

# ==========================================
# STRICT DATA SCHEMAS
# ==========================================
class ArticleAnalysis(BaseModel):
    cluster_category: str = Field(description="Must be exactly one of: Politics, Economy, Technology, Culture, Infrastructure, Entertainment, Sports, Crime & Accidents.")  
    cluster_geo_scope: str = Field(description="Must be exactly one of: North Macedonia, Kosovo, Albania, Serbia, Bosnia and Herzegovina, Montenegro, Regional, International.")
    title_en: str = Field(description="A strong, objective English headline.")
    bullets_en: str = Field(description="Three short English bullet points, separated by \\n.")
    perspective_en: str = Field(description="Detailed 3-4 sentence English narrative analysis of the underlying geopolitical context and bias.")
    title_sq: str = Field(description="Albanian translation of the headline.")
    bullets_sq: str = Field(description="Albanian translation of the 3 bullets, separated by \\n.")
    perspective_sq: str = Field(description="Albanian translation of the 3-4 sentence narrative analysis.")
    title_mk: str = Field(description="Macedonian translation of the headline.")
    bullets_mk: str = Field(description="Macedonian translation of the 3 bullets, separated by \\n.")
    perspective_mk: str = Field(description="Macedonian translation of the 3-4 sentence narrative analysis.")
    title_sr: str = Field(description="Serbian/Bosnian/Croatian translation of the headline.")
    bullets_sr: str = Field(description="Serbian/Bosnian translation of the 3 bullets, separated by \\n.")
    perspective_sr: str = Field(description="Serbian/Bosnian/Croatian translation of the 3-4 sentence narrative analysis.")
    geo_pro_western: float = Field(description="Float between 0.0 and 1.0.")
    narrative_objectivity: float = Field(description="Float between 0.0 and 1.0.")
    narrative_divergence_score: float = Field(description="Float between 0.0 and 1.0.")

class ArticleClusterMapping(BaseModel):
    clusters: list[list[str]] = Field(description="A list of lists. Each inner list contains the article_ids of stories that report on the EXACT SAME event.")

# ==========================================
# 3. AI ENGINES
# ==========================================
def analyze_article_with_llm(text):
    prompt = f"""
    Analyze the following news text. Extract the metrics, write an objective English headline, 
    3 English summary bullets, and a detailed 3-4 sentence English narrative summary explaining the underlying geopolitical context, potential bias, and framing. 
    Then translate ALL elements accurately into Albanian, Macedonian, and Serbian.
    CRITICAL RULE: Use strict sentence case for headlines and bullets. 
    Text: {text}
    """
    for index, key in enumerate(API_KEYS):
        for attempt in range(2):
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

