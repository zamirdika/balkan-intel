import sqlite3
import time
from datetime import datetime
import feedparser
import uuid
import re
import random
import requests
import base64
from bs4 import BeautifulSoup
# import google.generativeai as genai  <-- UNCOMMENT AND CONFIGURE YOUR KEY LATER

DB_NAME = "news_aggregator.db"

# ---------------------------------------------------------
# REGIONAL RSS SOURCES (Western Balkans)
# ---------------------------------------------------------
RSS_FEEDS = {
    "MIA": "https://mia.mk/feed/",
    "Alsat": "https://alsat.mk/feed/",
    "ATA": "https://ata.gov.al/feed/",
    "Euronews AL": "https://euronews.al/feed/",
    "Klan": "https://tvklan.al/feed/",
    "RTK": "https://www.rtklive.com/sq/rss.xml",
    "Telegrafi": "https://telegrafi.com/feed/",
    "RTS": "https://www.rts.rs/page/stories/sr/rss.html",
    "B92": "https://www.b92.net/info/rss/",
    "Klix": "https://www.klix.ba/rss",
    "Avaz": "https://avaz.ba/rss",
    "RTCG": "https://rtcg.me/rss",
    "Vijesti": "https://www.vijesti.me/rss"
}

# Domain mapping for relative URLs
DOMAIN_MAP = {
    "Klix": "https://www.klix.ba", "Euronews AL": "https://euronews.al",
    "MIA": "https://mia.mk", "Alsat": "https://alsat.mk", "ATA": "https://ata.gov.al",
    "Klan": "https://tvklan.al", "RTK": "https://www.rtklive.com", "Telegrafi": "https://telegrafi.com",
    "RTS": "https://www.rts.rs", "B92": "https://www.b92.net", "Avaz": "https://avaz.ba",
    "RTCG": "https://rtcg.me", "Vijesti": "https://www.vijesti.me"
}

# ---------------------------------------------------------
# 1. DATABASE INITIALIZATION
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            article_id TEXT PRIMARY KEY, 
            source_domain TEXT, 
            original_title TEXT,
            original_url TEXT, 
            image_url TEXT, 
            published_timestamp INTEGER,
            translated_snippet_sq TEXT, 
            cluster_id TEXT, 
            cluster_title_sq TEXT, 
            cluster_category TEXT, 
            cluster_geo_scope TEXT, 
            bullet_points_sq TEXT, 
            agency_ratio REAL, 
            divergent_perspectives_sq TEXT, 
            deep_dive_sq TEXT, 
            processed_by_ai INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# 2. FETCHING LOGIC (Scraping Regional Feeds)
# ---------------------------------------------------------
def fetch_rss_feeds():
    print(f"\n--- Po skanohen {len(RSS_FEEDS)} burime rajonale ---")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    new_articles_count = 0
    
    for source_name, feed_url in RSS_FEEDS.items():
        try:
            parsed_feed = feedparser.parse(feed_url)
            for entry in parsed_feed.entries[:5]: 
                article_id = str(uuid.uuid5(uuid.NAMESPACE_URL, entry.link))
                
                cursor.execute("SELECT article_id FROM articles WHERE article_id = ?", (article_id,))
                if cursor.fetchone() is None:
                    
                    img_url = ""
                    potential_images = []
                    
                    if 'enclosures' in entry:
                        potential_images.extend([enc.get('url', '') for enc in entry.enclosures if enc.get('url')])
                    
                    if 'media_content' in entry:
                        potential_images.extend([m.get('url', '') for m in entry.media_content if m.get('url')])

                    html_content = entry.get('description', '') + entry.get('summary', '')
                    if 'content' in entry and len(entry.content) > 0:
                        html_content += entry.content[0].get('value', '')
                        
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    for iframe in soup.find_all('iframe'):
                        src = iframe.get('src', '')
                        if 'youtube' in src or 'youtu.be' in src:
                            yt_match = re.search(r'(?:youtube\.com\/embed\/|youtu\.be\/)([a-zA-Z0-9_-]{11})', src)
                            if yt_match: potential_images.append(f"https://img.youtube.com/vi/{yt_match.group(1)}/hqdefault.jpg")
                    
                    for video in soup.find_all('video'):
                        if video.get('poster'): potential_images.append(video['poster'])
                            
                    for img in soup.find_all('img'):
                        src = img.get('data-src') or img.get('data-original') or img.get('src') or ''
                        potential_images.append(src)
                                
                    # 🛡️ THE BULLETPROOF GAUNTLET
                    valid_image_found = False
                    
                    for p_img in potential_images:
                        if not p_img: continue
                        p_img = str(p_img).strip()
                        p_img_lower = p_img.lower()
                        
                        if p_img.startswith('//'): p_img = 'https:' + p_img
                        elif p_img.startswith('/'): p_img = DOMAIN_MAP.get(source_name, "https://google.com") + p_img
                            
                        if not p_img_lower.startswith('http'): continue
                        if not any(ext in p_img_lower for ext in ['.jpg', '.jpeg', '.png', '.webp']): continue
                        if any(bad in p_img_lower for bad in ['gif', 'svg', '1x1', 'pixel', 'logo', 'icon', 'tracker']): continue
                            
                        # 🚀 THE NUCLEAR OPTION: Base64 Downloader
                        clean_url = p_img.replace(" ", "%20")
                        try:
                            # We disguise our script as a real Google Chrome browser
                            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                            res = requests.get(clean_url, headers=headers, timeout=5)
                            
                            # THE ULTIMATE CHECK: Did Klix actually send an image, or a 403 Forbidden HTML error?
                            if res.status_code == 200 and 'image' in res.headers.get('Content-Type', '').lower():
                                mime = res.headers.get('Content-Type', 'image/jpeg')
                                # Convert the image bytes directly into a Base64 text string
                                b64_data = base64.b64encode(res.content).decode('utf-8')
                                img_url = f"data:{mime};base64,{b64_data}"
                                valid_image_found = True
                                break 
                        except Exception:
                            continue # Try the next image if this one was blocked
                    
                    if not valid_image_found:
                        img_url = ""
                                
                    cursor.execute('''
                        INSERT INTO articles 
                        (article_id, source_domain, original_title, original_url, image_url, published_timestamp, processed_by_ai) 
                        VALUES (?, ?, ?, ?, ?, ?, 0)
                    ''', (
                        article_id, 
                        source_name, 
                        entry.get('title', 'Pa titull'), 
                        entry.link, 
                        img_url, 
                        int(time.time())
                    ))
                    new_articles_count += 1
        except Exception as e:
            pass 
            
    conn.commit()
    conn.close()
    print(f"✅ Skanimi përfundoi: U shtuan {new_articles_count} lajme të reja.")

# ---------------------------------------------------------
# 3. AI PROCESSING LOGIC 
# ---------------------------------------------------------
def apply_particle_intelligence():
    print("\n--- Po fillon përpunimi me Inteligjencë Artificiale ---")
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT article_id, original_title, source_domain FROM articles WHERE processed_by_ai = 0")
    unprocessed_articles = cursor.fetchall()
    
    if not unprocessed_articles:
        print("Të gjitha lajmet janë përpunuar tashmë.")
        conn.close()
        return

    for article in unprocessed_articles:
        art_id = article['article_id']
        title = article['original_title']
        
        try:
            lista_kategorive = ["Politikë & Drejtësi", "Ekonomi & Financë", "Integrimi Evropian", "Gjeopolitikë & Siguri", "Kulturë & Sport", "Të tjera"]
            lista_rajoneve = ["Maqedonia e Veriut", "Kosova", "Shqipëria", "Ballkani Perëndimor", "Glob"]
            
            ai_cluster_id = "cluster_" + str(uuid.uuid4())[:8]
            ai_category = random.choice(lista_kategorive)
            ai_geo = random.choice(lista_rajoneve) 
            
            ai_bullets = "• Gjeneruar nga AI: Pika kryesore e parë e këtij raportimi.\n• Analiza e AI: Ndikimi i kësaj ngjarje në rajon."
            ai_deep_dive = "Ky është një tekst demonstrues për fazën e prototipit. Në versionin final, motori i Inteligjencës Artificiale do të lexojë lajmin origjinal dhe do të gjenerojë një analizë të thelluar për këtë ngjarje bazuar në burimet rajonale."
            
            cursor.execute('''
                UPDATE articles SET 
                    cluster_id = ?, cluster_title_sq = ?, cluster_category = ?,
                    cluster_geo_scope = ?, bullet_points_sq = ?, deep_dive_sq = ?,
                    processed_by_ai = 1
                WHERE article_id = ?
            ''', (ai_cluster_id, title, ai_category, ai_geo, ai_bullets, ai_deep_dive, art_id))
            conn.commit()
            print(f"✅ Procesuar: {title[:40]}...")
            
        except Exception as e:
            print(f"❌ Gabim gjatë përpunimit: {e}")
            
        time.sleep(5) 
        
    conn.close()
    print("--- Përpunimi me AI përfundoi ---")

# ---------------------------------------------------------
# 4. DATABASE PRUNING & AUTOMATION
# ---------------------------------------------------------
def prune_database(days_to_keep=7):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cutoff_time = int(time.time()) - (days_to_keep * 24 * 60 * 60)
    try:
        cursor.execute("DELETE FROM articles WHERE published_timestamp < ?", (cutoff_time,))
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()

def run_sync_cycle():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[{current_time}] ⚙️ Fillon sinkronizimi automatik...")
    try:
        fetch_rss_feeds()
        apply_particle_intelligence()
        prune_database(days_to_keep=7)
    except Exception as e:
        print(f"❌ Gabim: {e}")

if __name__ == "__main__":
    init_db()
    print("🟢 Motori i grumbullimit u nis me Base64 Downloader!")
    run_sync_cycle()
    
    WAIT_INTERVAL_SECONDS = 1800 
    while True:
        time.sleep(WAIT_INTERVAL_SECONDS)
        run_sync_cycle()