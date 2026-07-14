import sqlite3
import feedparser
import requests
import json
import uuid
import pandas as pd
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
            
            # BULLETPROOF JSON PARSING: Avoids raw triple backticks to stop copy-paste breakage
            if raw_text.startswith("`" * 3 + "json"):
                raw_text = raw_text[7:]
            if raw_text.endswith("`" * 3):
                raw_text = raw_text[:-3]
                
            return json.loads(raw_text.strip())
        except Exception as e:
            continue
    return None

def run_global_clustering():
    """Pulls all recent records from the database and runs cross-run clustering analysis."""
    print("\n⚡ Initiating Global Cross-Run Clustering Engine...")
    conn = sqlite3.connect("news_aggregator.db")
    
    # Select articles from the last 48 hours to find overlaps across different time batches
    time_threshold = (datetime.now() - timedelta(hours=48)).isoformat()
    df = pd.read_sql_query("SELECT article_id, title_en, cluster_category FROM articles WHERE published_at > ?", conn, params=(time_threshold,))
    
    if df.empty or len(df) < 2:
        conn.close()
        return

    prompt = "Group these historical regional articles into lists of article_ids ONLY if they cover the exact same core event event across the region. Relax criteria slightly to allow cross-border translations of the same narrative event to match:\n\n"
    for _, row in df.iterrows():
        prompt += f"ID: {row['article_id']} | Category: {row['cluster_category']} | Headline: {row['title_en']}\n"

    try:
        client = genai.Client(api_key=API_KEYS[0])
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json", response_schema=ArticleClusterMapping, temperature=0.1
            )
        )
        raw_text = response.text.strip()
        
        # BULLETPROOF JSON PARSING
        if raw_text.startswith("`" * 3 + "json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("`" * 3):
            raw_text = raw_text[:-3]
            
        clusters = json.loads(raw_text.strip()).get("clusters", [])
        
        cursor = conn.cursor()
        for cluster_list in clusters:
            if len(cluster_list) > 1:
                new_cluster_id = f"cluster_{uuid.uuid4().hex[:8]}"
                print(f"🔗 Match Found! Merging {len(cluster_list)} cross-run stories into {new_cluster_id}")
                for a_id in cluster_list:
                    cursor.execute("UPDATE articles SET cluster_id = ? WHERE article_id = ?", (new_cluster_id, a_id))
        conn.commit()
    except Exception as e:
        print(f"⚠️ Global clustering step encountered an error: {e}")
    finally:
        conn.close()

# ==========================================
# 4. RUN PIPELINE
# ==========================================
def run_pipeline():
    init_db()
    target_feeds = {
        "MIA (MK)": "https://mia.mk/feed/", "Sitel (MK)": "https://sitel.com.mk/rss", "Alsat (MK/SQ)": "https://alsat.mk/feed/",
        "Koha (KS)": "https://koha.net/rss", "Klan Kosova (KS)": "https://klankosova.tv/feed/", "Gazeta Express (KS)": "https://www.gazetaexpress.com/feed/",
        "Top Channel (AL)": "https://top-channel.tv/feed/", "BalkanWeb (AL)": "https://balkanweb.com/feed/",
        "RTS (SR)": "https://www.rts.rs/page/stories/sr/rss.html", "Telegraf (SR)": "https://www.telegraf.rs/rss",
        "B92 (SR)": "https://www.b92.net/info/rss/vesti.xml", "Klix (BA)": "https://www.klix.ba/rss"
    }
    
    raw_articles = fetch_rss_feeds(target_feeds)
    if not raw_articles: return

    conn = sqlite3.connect("news_aggregator.db")
    cursor = conn.cursor()
    
    for idx, art in enumerate(raw_articles):
        # Prevent analyzing articles that are already in our DB from previous runs
        cursor.execute("SELECT 1 FROM articles WHERE original_title = ?", (art['original_title'],))
        if cursor.fetchone(): continue
        
        ai_data = analyze_article_with_llm(art['raw_text'])
        if not ai_data: continue
        art.update(ai_data)
        
        # Initial status: single item unique cluster ID
        art['cluster_id'] = f"unique_{uuid.uuid4().hex[:8]}"
        
        cursor.execute('''
            INSERT OR REPLACE INTO articles 
            (article_id, cluster_id, original_title, original_url, source_domain, image_url, raw_text, 
             title_en, bullets_en, perspective_en, title_sq, bullets_sq, perspective_sq, 
             title_mk, bullets_mk, perspective_mk, title_sr, bullets_sr, perspective_sr,
             cluster_category, cluster_geo_scope, geo_pro_western, narrative_objectivity, 
             narrative_divergence_score, published_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            art['article_id'], art['cluster_id'], art['original_title'], art['original_url'], art['source_domain'], art['image_url'], art['raw_text'], 
            art['title_en'], art['bullets_en'], art['perspective_en'], art['title_sq'], art['bullets_sq'], art['perspective_sq'],
            art['title_mk'], art['bullets_mk'], art['perspective_mk'], art['title_sr'], art['bullets_sr'], art['perspective_sr'],
            art['cluster_category'], art['cluster_geo_scope'], art['geo_pro_western'], art['narrative_objectivity'], art['narrative_divergence_score'], art['published_at']
        ))
        conn.commit()
        time.sleep(10)
        
    conn.close()
    
    # RUN THE GLOBAL HISTORICAL CLUSTERING LOOP OVER EVERYTHING RECENTLY ACCUMULATED
    run_global_clustering()
    print("✅ Pipeline Complete!")

if __name__ == "__main__":
    run_pipeline()
