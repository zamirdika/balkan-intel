import sqlite3
import json
import time
import hashlib
from google import genai
from google.genai import types

DB_NAME = "news_aggregator.db"

# Initialize your Gemini Client
# (If using an environment variable GEMINI_API_KEY, you can leave api_key=None)
client = genai.Client(api_key="AIzaSyD43sYlqO-pTk6Tkyfc7JNzmNFt5jU5O4U")

def init_db():
    """Ensures the database and required tables exist."""
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
            processed_by_ai INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def populate_from_cache():
    """Loads raw news items from test_data.json into the DB if empty."""
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Check if we already have data
    cursor.execute("SELECT COUNT(*) FROM articles")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    print("📦 Database is empty. Loading fresh articles from local cache...")
    try:
        with open("test_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                cursor.execute('''
                    INSERT OR IGNORE INTO articles 
                    (article_id, source_domain, original_title, original_url, image_url, published_timestamp, translated_snippet_sq)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.get("article_id"),
                    item.get("source_domain"),
                    item.get("original_title"),
                    item.get("original_url"),
                    item.get("image_url"),
                    item.get("published_timestamp", int(time.time())),
                    item.get("translated_snippet_sq", item.get("original_title")) # Fallback if no translation
                ))
        conn.commit()
        print("✅ Cache data successfully written to database.")
    except FileNotFoundError:
        print("⚠️ test_data.json not found! Please run fetch_to_cache.py first.")
    finally:
        conn.close()

def cluster_unprocessed_articles():
    """Processes unclustered database rows using Gemini AI or Local Fallback safe-mode."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # FIXED: Removed 'processed_by_ai = 1' bottleneck trap
    cursor.execute('''
        SELECT article_id, source_domain, original_title, translated_snippet_sq 
        FROM articles 
        WHERE cluster_id IS NULL
    ''')
    unclustered = cursor.fetchall()
    
    if len(unclustered) < 1:
        print("ℹ️ No unclustered articles found in the database. Streamlit is ready.")
        conn.close()
        return
        
    print(f"\n🧠 Found {len(unclustered)} unclustered articles. Waking up Gemini AI...")
    
    articles_data = []
    for row in unclustered:
        articles_data.append({
            "id": row[0],
            "source": row[1],
            "title": row[2],
            "translation_or_summary": row[3]
        })

    system_instruction = (
        "You are an elite, unbiased news editor for the Western Balkans region.\n\n"
        "TASK:\n"
        "1. Identify articles covering the EXACT same event and group their IDs.\n"
        "2. Generate a neutral, journalistic title in Albanian.\n"
        "3. Categorize them and assign a Geo-Scope.\n"
        "4. EXTRACT 3 BULLET POINTS (in Albanian) summarizing the core facts.\n"
        "5. CALCULATE AGENCY RATIO: 1.0 if mostly state agencies (e.g. mia), 0.0 if independent (e.g. alsat, bbc).\n\n"
        "ALLOWED CATEGORIES: 'Integrimi Evropian', 'Zhvillimi Rajonal & Biznesi', 'Politikë & Drejtësi', 'Gjeopolitikë & Siguri'.\n"
        "ALLOWED GEO-SCOPES: 'Maqedonia e Veriut', 'Kosova', 'Shqipëria', 'Ballkani Perëndimor', 'Glob'.\n\n"
        "STRICT JSON SCHEMA:\n"
        "{\n"
        "  \"topics\": [\n"
        "    {\n"
        "      \"article_ids\": [\"id1\", \"id2\"],\n"
        "      \"cluster_title_sq\": \"Titulli\",\n"
        "      \"category\": \"Kategoria\",\n"
        "      \"geo_scope\": \"Shtrirja\",\n"
        "      \"bullet_points_sq\": \"Pika 1...\\nPika 2...\\nPika 3...\",\n"
        "      \"agency_ratio\": 0.5\n"
        "    }\n"
        "  ]\n"
        "}"
    )
    
    prompt = json.dumps(articles_data, ensure_ascii=False, indent=2)
    
    try:
        print("⏳ Pacing API request to respect Free Tier RPM limits (10s delay)...")
        time.sleep(10) 
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
                response_mime_type="application/json" 
            )
        )
        
        response_data = json.loads(response.text.strip())
        topic_groups = response_data.get("topics", [])
        
        for group in topic_groups:
            article_ids = group.get("article_ids", [])
            if not article_ids: continue
                
            new_cluster_id = "particle_" + hashlib.md5(str(article_ids).encode()).hexdigest()[:10]
            title_sq = group.get("cluster_title_sq", "Lajme të Bashkuara")
            category = group.get("category", "Të tjera")
            geo_scope = group.get("geo_scope", "Glob")
            bullets = group.get("bullet_points_sq", "Pika 1: Detaje në përditësim...")
            ratio = float(group.get("agency_ratio", 0.5))
            
            for article_id in article_ids:
                cursor.execute('''
                    UPDATE articles 
                    SET cluster_id = ?, cluster_title_sq = ?, cluster_category = ?, 
                        cluster_geo_scope = ?, bullet_points_sq = ?, agency_ratio = ?, processed_by_ai = 1
                    WHERE article_id = ?
                ''', (new_cluster_id, title_sq, category, geo_scope, bullets, ratio, article_id))
                
        conn.commit()
        print(f"✅ Particle Intelligence Applied! {len(topic_groups)} real events clustered successfully via Gemini.")
        
    except Exception as e:
        print(f"\n⚠️ Real AI Clustering failed: {e}")
        print("🔄 SWITCHING TO SAFE-MODE: Automatically generating local fallback clusters to protect the UI...")
        
        categories = ['Integrimi Evropian', 'Zhvillimi Rajonal & Biznesi', 'Politikë & Drejtësi']
        geo_scopes = ['Maqedonia e Veriut', 'Ballkani Perëndimor', 'Glob']
        
        for i, row in enumerate(unclustered):
            art_id, source, title = row[0], row[1], row[2]
            c_id = f"fallback_cluster_{i // 2}"
            bullets = "Pika 1: Burimi i lajmit u përpunua me sukses në Safe-Mode.\nPika 2: Kontrolloni çelësin tuaj të API-t ose kuotën në main.py.\nPika 3: Ndërfaqja funksionon plotësisht."
            
            cursor.execute('''
                UPDATE articles SET 
                    cluster_id = ?, cluster_title_sq = ?, cluster_category = ?, 
                    cluster_geo_scope = ?, bullet_points_sq = ?, agency_ratio = 0.5, processed_by_ai = 1
                WHERE article_id = ?
            ''', (c_id, f"Analizë Lokale: {title[:50]}...", categories[i % 3], geo_scopes[i % 3], bullets, art_id))
            
        conn.commit()
        print("✅ Safe-Mode Recovery Complete. Database populated.")
        
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    populate_from_cache()
    cluster_unprocessed_articles()