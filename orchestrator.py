import sqlite3
import feedparser
import requests
import json
import uuid
from datetime import datetime
import os
import time 
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 1. DATABASE SETUP
# ==========================================
def init_db(db_name="news_aggregator.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # We drop the table to apply the new multilingual columns
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
            
            -- Localized
            title_sq TEXT,
            bullets_sq TEXT,
            title_mk TEXT,
            title_sr TEXT,
            
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
# 2. DATA INGESTION (With Clean Pre-Filtering)
# ==========================================
def fetch_rss_feeds(feed_urls):
    """Pulls recent articles from a list of RSS feeds and filters out empty data."""
    articles = []
    for url in feed_urls:
        parsed_feed = feedparser.parse(url)
        source = parsed_feed.feed.get('title', 'Unknown Source')
        
        valid_entries_count = 0
        for entry in parsed_feed.entries:
            if valid_entries_count >= 3: # Stop after finding 3 valid articles per feed
                break
                
            # Safely extract and strip text fields
            title = entry.get('title', '').strip()
            summary = entry.get('summary', '').strip()
            
            # Fallback chain for content: use summary if available, otherwise title
            raw_text = summary if summary else title
            
            # --- THE FIX: SANITY FILTER ---
            # Skip if the title is blank OR if the text is too short to be an actual news story
            if not title or len(raw_text) < 15 or "Titulli mungon" in title:
                print(f"   [!] Skipping empty/malformed entry from {source}")
                continue
                
            # Safely grab image URL if available
            image_url = ""
            if 'media_content' in entry and entry['media_content']:
                image_url = entry['media_content'][0].get('url', '')
            
            articles.append({
                "article_id": str(uuid.uuid4()),
                "original_title": title,
                "original_url": entry.get('link', ''),
                "source_domain": source,
                "image_url": image_url,
                "published_at": datetime.now().isoformat(),
                "raw_text": raw_text
            })
            valid_entries_count += 1
            
    return articles
# ==========================================
# STRICT DATA SCHEMA (Updated for Objectivity)
# ==========================================
# 1. PËRDITËSONI SKEMËN PYDANTIC (Shtoni fushën e re në fund)
class ArticleAnalysis(BaseModel):
    # 1. Master Backend Categories (Strictly English)
    cluster_category: str = Field(description="Must be exactly one of: Politics, Economy, Technology, Culture, Infrastructure, Entertainment.")  
    cluster_geo_scope: str = Field(description="Must be exactly one of: North Macedonia, Kosovo, Albania, Regional, International.")
    
    # 2. English (Base Language for API and default UI)
    title_en: str = Field(description="A strong, objective English headline.")
    bullets_en: str = Field(description="Three short English bullet points, separated by \\n.")
    perspective_en: str = Field(description="One-sentence English analysis of the underlying geopolitical or local narrative.")
    
    # 3. Localized Translations
    title_sq: str = Field(description="Albanian translation of the headline.")
    bullets_sq: str = Field(description="Albanian translation of the bullet points, separated by \\n.")
    title_mk: str = Field(description="Macedonian translation of the headline.")
    title_sr: str = Field(description="Serbian/Bosnian/Croatian translation of the headline.")
    
    # 4. Universal Metrics
    geo_pro_western: float = Field(description="Float between 0.0 and 1.0.")
    narrative_objectivity: float = Field(description="Float between 0.0 and 1.0.")
    narrative_divergence_score: float = Field(description="Float between 0.0 and 1.0.")
# ==========================================
# 3. THE AI ENGINE 
# ==========================================
def analyze_article_with_llm(article_text, max_retries=3):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("CRITICAL ERROR: Python cannot see your .env file.")
        
    client = genai.Client(api_key=api_key)  
    
    prompt = f"""
    You are an expert geopolitical intelligence analyst focusing on the Western Balkans.
    Analyze the following news text and extract the required intelligence metrics in Albanian.
    
    RAW ARTICLE TEXT:
    {article_text}
    """
    
    delay = 65 
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                # Change this BACK to 2.5
                model='gemini-2.5-flash', 
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ArticleAnalysis,
                    temperature=0.1,
                ),
            )
            return json.loads(response.text)
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "503" in error_msg:
                print(f"   [!] Gemini Quota Hit. Forcing {delay}-second hard reset (Attempt {attempt + 1}/{max_retries})...")
                time.sleep(delay)
            else:
                print(f"⚠️ Non-retryable AI Error: {e}")
                break 

    print("❌ All retries exhausted. Using fallback profile.")
    return {
        "cluster_title_sq": "Gabim në përpunim",
        "bullet_points_sq": "Sistemi tejkaloi kuotën.\nJu lutem ekzekutoni përsëri.",
        "cluster_perspective_sq": "Analiza nuk ofrohet.",
        "cluster_category": "Politikë",
        "cluster_geo_scope": "Maqedonia e Veriut", # Updated to match your new schema
        "geo_pro_western": 0.5,
        "narrative_objectivity": 0.5,
        "narrative_divergence_score": 0.5 # Added this safety fallback
    }

# ==========================================
# 4. ORCHESTRATION & DATABASE INSERTION
# ==========================================
def run_pipeline():
    init_db()
    
    target_feeds = [
        "https://alsat.mk/feed/",          
        "https://mia.mk/feed",           
        "https://telegrafi.com/feed/",     
        "https://balkaninsight.com/feed/",
        "https://top-channel.tv/feed/",
        "https://www.klix.ba/feed"  
    ]
    
    print("1. Fetching articles from RSS feeds...")
    raw_articles = fetch_rss_feeds(target_feeds)
    
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
        
        if idx < len(raw_articles) - 1:
            time.sleep(20)
        
    print("\n3. Saving to Database...")
    conn = sqlite3.connect("news_aggregator.db")
    cursor = conn.cursor()
    
    for art in processed_articles:
        cursor.execute('''
            INSERT OR REPLACE INTO articles 
            (article_id, cluster_id, original_title, original_url, source_domain, image_url, raw_text, 
             title_en, bullets_en, perspective_en, title_sq, bullets_sq, title_mk, title_sr,
             cluster_category, cluster_geo_scope, geo_pro_western, narrative_objectivity, 
             narrative_divergence_score, published_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            art['article_id'], art['cluster_id'], art['original_title'], art['original_url'], 
            art['source_domain'], art['image_url'], art['raw_text'], 
            art.get('title_en', ''), art.get('bullets_en', ''), art.get('perspective_en', ''), 
            art.get('title_sq', ''), art.get('bullets_sq', ''), art.get('title_mk', ''), art.get('title_sr', ''), 
            art.get('cluster_category', 'Politics'), art.get('cluster_geo_scope', 'Regional'), 
            art.get('geo_pro_western', 0.5), art.get('narrative_objectivity', 0.5), 
            art.get('narrative_divergence_score', 0.5), art['published_at']
        ))
        
    conn.commit()
    conn.close()
    print("✅ Pipeline Complete! Open a new terminal tab and run: streamlit run app.py")

if __name__ == "__main__":
    print("\n▶ STARTING BALKAN INTEL ORCHESTRATOR...")
    run_pipeline()