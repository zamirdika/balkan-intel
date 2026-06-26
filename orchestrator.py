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
# 1. DATABASE SETUP (Fixed Missing Bullets)
# ==========================================
def init_db(db_name="news_aggregator.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS articles')
    cursor.execute('''
        CREATE TABLE articles (
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
            
            -- Localized (Added missing bullet columns)
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
# 2. DATA INGESTION (Upgraded Cloudflare Bypass)
# ==========================================
def fetch_rss_feeds(feed_urls):
    articles = []
    # Disguise the scraper as a real Chrome browser to bypass firewalls
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    for source_name, url in feed_urls.items():
        try:
            # Fetch the raw XML with the disguised browser first
            response = requests.get(url, headers=headers, timeout=15)
            parsed_feed = feedparser.parse(response.content)
        except Exception as e:
            print(f"Failed to fetch {source_name}: {e}")
            continue
            
        valid_entries_count = 0
        for entry in parsed_feed.entries:
            if valid_entries_count >= 3: 
                break
            title = entry.get('title', '').strip()
            summary = entry.get('summary', '').strip()
            raw_text = summary if summary else title
            if not title or len(raw_text) < 15 or "Titulli mungon" in title:
                continue
            
            # --- UPGRADED IMAGE HUNTER ---
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
            # -----------------------------
                    
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
# STRICT DATA SCHEMA (Added Missing MK/SR Bullets)
# ==========================================
class ArticleAnalysis(BaseModel):
    cluster_category: str = Field(description="Must be exactly one of: Politics, Economy, Technology, Culture, Infrastructure, Entertainment, Sports.")  
    cluster_geo_scope: str = Field(description="Must be exactly one of: North Macedonia, Kosovo, Albania, Regional, International.")
    
    title_en: str = Field(description="A strong, objective English headline.")
    bullets_en: str = Field(description="Three short English bullet points, separated by \\n.")
    perspective_en: str = Field(description="One-sentence English analysis of the underlying geopolitical narrative.")
    
    title_sq: str = Field(description="Albanian translation of the headline.")
    bullets_sq: str = Field(description="Albanian translation of the 3 bullets, separated by \\n.")
    perspective_sq: str = Field(description="Albanian translation of the perspective analysis.")
    
    title_mk: str = Field(description="Macedonian translation of the headline.")
    bullets_mk: str = Field(description="Macedonian translation of the 3 bullets, separated by \\n.")
    perspective_mk: str = Field(description="Macedonian translation of the perspective analysis.")
    
    title_sr: str = Field(description="Serbian/Bosnian/Croatian translation of the headline.")
    bullets_sr: str = Field(description="Serbian/Bosnian translation of the 3 bullets, separated by \\n.")
    perspective_sr: str = Field(description="Serbian/Bosnian/Croatian translation of the perspective analysis.")
    
    geo_pro_western: float = Field(description="Float between 0.0 and 1.0.")
    narrative_objectivity: float = Field(description="Float between 0.0 and 1.0.")
    narrative_divergence_score: float = Field(description="Float between 0.0 and 1.0.")

# ==========================================
# 3. THE AI ENGINE 
# ==========================================
def analyze_article_with_llm(text):
    prompt = f"""
    Analyze the following news text. Extract the metrics, write an objective English headline, 
    3 English summary bullets, and a 1-sentence English perspective analysis. 
    Then translate ALL elements (headline, bullets, and perspective) accurately into Albanian, Macedonian, and Serbian.

    CRITICAL LINGUISTIC RULE FOR ALL TRANSLATIONS: You MUST use strict sentence case for headlines and bullets. 
    INCORRECT: "Kryeministri I Kosovës Shkon Në Bruksel Për Bisedime" (Do not capitalize every word).
    CORRECT: "Kryeministri i Kosovës shkon në Bruksel për bisedime" (Only capitalize the first letter and proper nouns).

    Text:
    {text}
    """
    for index, key in enumerate(API_KEYS):
        for attempt in range(2):
            try:
                client = genai.Client(api_key=key)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=ArticleAnalysis,
                        temperature=0.2
                    )
                )
                
                raw_text = response.text.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                    
                return json.loads(raw_text.strip())
                
            except Exception as e:
                error_msg = str(e).lower()
                if "503" in error_msg or "unavailable" in error_msg:
                    print(f"⏳ Gemini high demand (503). Retrying key {index + 1} in 5s...")
                    time.sleep(5)
                    continue
                elif "429" in error_msg or "quota" in error_msg or "exhausted" in error_msg:
                    print(f"⚠️ Key {index + 1} reached quota. Moving to next key...")
                    break 
                else:
                    print(f"❌ AI Analysis Error on Key {index + 1}: {e}")
                    break 
                    
    print("🚨 FATAL: AI Engine failed to process this article.")
    return {
        "cluster_category": "News",
        "cluster_geo_scope": "Regional",
        "title_en": "Processing Error",
        "bullets_en": "Analysis failed.",
        "perspective_en": "Data unavailable.",
        "title_sq": "Gabim në përpunim",
        "bullets_sq": "Gabim në përpunim",
        "perspective_sq": "E dhëna e padisponueshme.",
        "title_mk": "Грешка",
        "bullets_mk": "Грешка",
        "perspective_mk": "Недостапно.",
        "title_sr": "Greška",
        "bullets_sr": "Greška",
        "perspective_sr": "Nedostupno.",
        "geo_pro_western": 0.5,
        "narrative_objectivity": 0.5,
        "narrative_divergence_score": 0.5
    }

# ==========================================
# 4. ORCHESTRATION & DATABASE INSERTION
# ==========================================
def run_pipeline():
    init_db()
    target_feeds = {
        "MIA (MK)": "https://mia.mk/feed/",
        "Alsat (MK/SQ)": "https://alsat.mk/feed/",
        "Kanal 5 (MK)": "https://kanal5.com.mk/rss",
        "Koha (KS)": "https://koha.net/rss",
        "Telegrafi (KS)": "https://telegrafi.com/feed/",
        "Gazeta Express (KS)": "https://www.gazetaexpress.com/feed/",
        "Top Channel (AL)": "https://top-channel.tv/feed/",
        "Euronews (AL)": "https://euronews.al/feed/",
        "RTS (SR)": "https://www.rts.rs/page/stories/sr/rss.html",
        "N1 Srbija (SR)": "https://n1info.rs/feed/",
        "B92 (SR)": "https://www.b92.net/info/rss/vesti.xml",
        "Klix (BA)": "https://www.klix.ba/rss",
        "N1 BiH (BA)": "https://n1info.ba/feed/",
        "Al Jazeera Balkans (BA)": "https://balkans.aljazeera.net/rss"
    }
    
    print("1. Fetching articles from RSS feeds...")
    raw_articles = fetch_rss_feeds(target_feeds)
    print(f"Total articles compiled by scraper: {len(raw_articles) if raw_articles else 0}")
    
    if not raw_articles:
        return

    print(f"2. Processing {len(raw_articles)} articles through AI Engine...")
    processed_articles = []
    
    for idx, art in enumerate(raw_articles):
        print(f" -> Processing article {idx + 1}/{len(raw_articles)}: {art['original_title'][:50]}...")
        ai_data = analyze_article_with_llm(art['raw_text'])
        art.update(ai_data)
        art['cluster_id'] = f"cluster_{idx}" 
        processed_articles.append(art)
        
        # PACE THE ROBOT: Wait 12 seconds between articles
        if idx < len(raw_articles) - 1:
            time.sleep(12)
            
    print("\n3. Saving to Database...")
    conn = sqlite3.connect("news_aggregator.db")
    cursor = conn.cursor()
    
    for art in processed_articles:
        cursor.execute('''
            INSERT OR REPLACE INTO articles 
            (article_id, cluster_id, original_title, original_url, source_domain, image_url, raw_text, 
             title_en, bullets_en, perspective_en, 
             title_sq, bullets_sq, perspective_sq, 
             title_mk, bullets_mk, perspective_mk, 
             title_sr, bullets_sr, perspective_sr,
             cluster_category, cluster_geo_scope, geo_pro_western, narrative_objectivity, 
             narrative_divergence_score, published_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            art['article_id'], art['cluster_id'], art['original_title'], art['original_url'], 
            art['source_domain'], art['image_url'], art['raw_text'], 
            art.get('title_en', ''), art.get('bullets_en', ''), art.get('perspective_en', ''), 
            art.get('title_sq', ''), art.get('bullets_sq', ''), art.get('perspective_sq', ''),
            art.get('title_mk', ''), art.get('bullets_mk', ''), art.get('perspective_mk', ''), 
            art.get('title_sr', ''), art.get('bullets_sr', ''), art.get('perspective_sr', ''),
            art.get('cluster_category', 'News'), art.get('cluster_geo_scope', 'Regional'), 
            art.get('geo_pro_western', 0.5), art.get('narrative_objectivity', 0.5), 
            art.get('narrative_divergence_score', 0.5), art['published_at']
        ))
        
    conn.commit()
    conn.close()
    print("✅ Pipeline Complete!")

if __name__ == "__main__":
    print("\n▶ STARTING BALKAN INTEL ORCHESTRATOR...")
    run_pipeline()
