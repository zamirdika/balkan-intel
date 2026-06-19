import sqlite3
import json
import uuid
import time
import re
from google import genai
from google.genai.errors import APIError

# Configure the modern Gemini Client
client = genai.Client(api_key="AIzaSyD43sYlqO-pTk6Tkyfc7JNzmNFt5jU5O4U")

# Ndryshoje në këtë:
def generate_with_retry(prompt, model_name="gemini-2.5-flash", max_retries=10, base_delay=20):
    for attempt in range(max_retries):
        try:
            time.sleep(base_delay)
            response = client.models.generate_content(model=model_name, contents=prompt)
            return response.text
        except APIError as e:
            if e.code == 429:
                sleep_time = base_delay * (2 ** attempt)
                print(f"🛑 Rate limit hit. Backing off for {sleep_time}s...")
                time.sleep(sleep_time)
            else:
                raise e
    raise Exception("❌ Max retries reached.")

def run_clustering_engine():
    conn = sqlite3.connect('news_aggregator.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT article_id, original_title, raw_html_content, bullet_points_sq 
        FROM articles 
        WHERE cluster_id IS NULL
    """)
    unclustered_articles = cursor.fetchall()
    
    if not unclustered_articles:
        print("✨ No articles found ready for enrichment.")
        conn.close()
        return

    print(f"📦 Processing {len(unclustered_articles)} articles using BALKAN SPECTRUM ENGINE...")
    
    model_name = 'gemini-3.5-flash'
    batch_size = 10 
    
    for i in range(0, len(unclustered_articles), batch_size):
        batch = unclustered_articles[i:i + batch_size]
        print(f"\n🔄 Processing Batch {i//batch_size + 1} ({len(batch)} articles)...")
        
        one_day_ago = int(time.time()) - 86400
        cursor.execute("""
            SELECT DISTINCT cluster_id, cluster_title_sq 
            FROM articles 
            WHERE cluster_id IS NOT NULL AND published_timestamp > ? AND cluster_title_sq IS NOT NULL
        """, (one_day_ago,))
        existing_clusters = cursor.fetchall()
        
        cluster_list_str = "None"
        if existing_clusters:
            cluster_list_str = "\n".join([f"- ID: {c[0]} | Title: {c[1]}" for c in existing_clusters])

        articles_data = []
        for art in batch:
            articles_data.append({
                "article_id": art[0],
                "title": art[1],
                "content_snippet": art[2][:600] 
            })
            
        prompt = f"""
        You are an expert Balkan news editor analyzing articles for clusters, summaries, and complex media framing landscapes.
        
        CRITICAL SUMMARY RULES:
        1. Provide a 2-3 bullet point summary for EVERY article in Albanian. Focus strictly on journalistic facts. Start each bullet point with a dash (-).
        2. DO NOT use double quotes (") inside your titles or summaries. Use single quotes (') if needed.
        
        ENTITY & CHARACTER MERGING RULE:
        If multiple articles feature quotes, statements, or interviews from the EXACT SAME INDIVIDUAL (e.g., 'Aktivisti Hoxha' or a specific politician), group them into the SAME new cluster group ('NEW_GROUP_X'). Combine their various separate points into a single 2-3 bullet point summary and give it a unified title like: '[Name]: Qëndrimet mbi [Topic 1] dhe [Topic 2]'.

        THE BALKAN SPECTRUM FRAMING RULES:
        For each article, mathematically evaluate the framing on a scale from 0.00 to 1.00 for these 3 specific Balkan fault lines:
        
        1. Geopolitical Alignment ('geo_pro_western'):
           - 0.00 = Deeply Pro-Eastern/Eurosceptic (favors Russian/Chinese narratives, expresses high skepticism toward EU/NATO).
           - 1.00 = Deeply Pro-Western/EU (highly favors NATO/EU integration, Western diplomacy, or Euro-Atlantic partnerships).
           - 0.50 = Neutral/Objective tracking.
           
        2. Editorial Stance ('editorial_state_aligned'):
           - 0.00 = Completely Independent/Critical (investigative journalism, exposing corruption, questioning state authorities).
           - 1.00 = Completely State-Aligned (acts as a government mouthpiece, relies 80%+ on official government press releases or quotes authorities without opposition voices).
           
        3. National Narrative ('narrative_ethno_nationalist'):
           - 0.00 = Civic/Regional (neutral tone, regional cooperation framing, civic-focused approach).
           - 1.00 = Ethno-Nationalist (uses ethnocentric framing, inflammatory language regarding borders, historical tensions, or local ethnic dynamics).

        Existing Active Clusters (Past 24h):
        {cluster_list_str}
        
        New Articles to Analyze:
        {json.dumps(articles_data, indent=2, ensure_ascii=False)}
        
        Respond strictly in a valid JSON array of objects. For each article, output exactly these keys:
        - 'article_id': string
        - 'matched_cluster_id': string or null (or identical 'NEW_GROUP_1' for items merged by entity/person)
        - 'title_sq': Refined Albanian headline
        - 'bullet_points_sq': Summaries matching rules
        - 'category': 'Politikë', 'Ekonomi', 'Shoqëri', 'Kulturë', 'Sport'
        - 'geo_scope': 'Layer 1: Albania, Kosovo, North Macedonia', 'Layer 2: Serbia, Montenegro, Bosnia and Herzegovina', 'Cross-Layer: Balkans Regional', or 'International'
        - 'agency_ratio': float (0.0 to 1.0)
        - 'geo_pro_western': float (0.00 to 1.00)
        - 'editorial_state_aligned': float (0.00 to 1.00)
        - 'narrative_ethno_nationalist': float (0.00 to 1.00)
        """
        
        try:
            response_text = generate_with_retry(prompt, model_name=model_name)
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            
            if json_match:
                enriched_list = json.loads(json_match.group(0))
                temp_group_map = {}
                
                for item in enriched_list:
                    a_id = item.get('article_id')
                    m_cluster_id = item.get('matched_cluster_id')
                    title_sq = item.get('title_sq', 'Lajm i ri')
                    
                    raw_bullets = item.get('bullet_points_sq', '- Përmbledhja nuk u gjenerua.')
                    if isinstance(raw_bullets, list):
                        bullet_points_sq = "\n".join([f"- {str(b).lstrip('- ')}" for b in raw_bullets])
                    else:
                        bullet_points_sq = str(raw_bullets)
                        
                    category = item.get('category', 'Shoqëri')
                    geo_scope = item.get('geo_scope', 'Cross-Layer: Balkans Regional')
                    
                    agency_ratio = float(item.get('agency_ratio', 0.5))
                    geo_pw = float(item.get('geo_pro_western', 0.5))
                    edit_sa = float(item.get('editorial_state_aligned', 0.5))
                    narr_en = float(item.get('narrative_ethno_nationalist', 0.5))
                        
                    final_cluster_id = str(uuid.uuid4())
                    if m_cluster_id:
                        if "NEW_GROUP" in m_cluster_id:
                            if m_cluster_id not in temp_group_map:
                                temp_group_map[m_cluster_id] = str(uuid.uuid4())
                            final_cluster_id = temp_group_map[m_cluster_id]
                        else:
                            final_cluster_id = m_cluster_id
                    
                    cursor.execute("""
                        UPDATE articles 
                        SET cluster_id = ?, cluster_title_sq = ?, bullet_points_sq = ?, cluster_category = ?, cluster_geo_scope = ?, agency_ratio = ?,
                            geo_pro_western = ?, editorial_state_aligned = ?, narrative_ethno_nationalist = ?
                        WHERE article_id = ?
                    """, (final_cluster_id, title_sq, bullet_points_sq, category, geo_scope, agency_ratio, geo_pw, edit_sa, narr_en, a_id))
                    
                conn.commit()
                print(f"✅ Batch {i//batch_size + 1} processed with Balkan Spectrum data.")
            else:
                print(f"⚠️ Could not find JSON array in response for Batch {i//batch_size + 1}")
        except Exception as e:
            print(f"⚠️ Batch failed: {e}")
            
    conn.close()
    print("🚀 Balkan Spectrum indexing complete!")

if __name__ == "__main__":
    run_clustering_engine()