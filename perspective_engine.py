import sqlite3
import time
from google import genai
from google.genai.errors import APIError

# Configure the modern Gemini Client
client = genai.Client(api_key="AIzaSyD43sYlqO-pTk6Tkyfc7JNzmNFt5jU5O4U")

def generate_with_retry(prompt, model_name="gemini-2.5-flash", max_retries=5, base_delay=6):
    """Executes a Gemini API call with exponential backoff to handle 429 and 503 errors."""
    for attempt in range(max_retries):
        try:
            time.sleep(base_delay)
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            return response.text
        except APIError as e:
            # Handle both Rate Limits (429) and Server Overloads (503)
            if e.code in [429, 503]:
                sleep_time = base_delay * (2 ** attempt)
                print(f"🛑 Server busy ({e.code}). Backing off for {sleep_time}s (Attempt {attempt + 1}/{max_retries})...")
                time.sleep(sleep_time)
            else:
                raise e
    raise Exception("❌ Max retries reached due to persistent API unavailability.")

def run_perspective_engine():
    conn = sqlite3.connect('news_aggregator.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE articles ADD COLUMN cluster_perspective_sq TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass # Column already exists
        
    query = """
        SELECT cluster_id, GROUP_CONCAT(source_domain, '||'), GROUP_CONCAT(raw_html_content, '||')
        FROM articles
        WHERE cluster_id IS NOT NULL 
          AND cluster_perspective_sq IS NULL
        GROUP BY cluster_id
        HAVING COUNT(DISTINCT source_domain) > 1
    """
    cursor.execute(query)
    multi_source_clusters = cursor.fetchall()
    
    if not multi_source_clusters:
        print("✨ No new multi-source clusters to analyze right now.")
        conn.close()
        return

    print(f"🧠 Found {len(multi_source_clusters)} multi-source clusters ready for Perspective Analysis...")
    
    for cluster in multi_source_clusters:
        c_id = cluster[0]
        sources = cluster[1].split('||')
        contents = cluster[2].split('||')
        
        source_texts = ""
        for src, txt in zip(sources, contents):
            source_texts += f"\n--- BURIMI: {src} ---\n{txt[:1200]}\n"
        
        prompt = f"""
        You are a senior media analyst for the Western Balkans. Read the following reporting from different sources on the exact same event.
        
        {source_texts}
        
        Write a 2-3 sentence comparative analysis in grammatically perfect Albanian. 
        Do NOT summarize the event itself. Instead, focus entirely on HOW the reporting differs. 
        For example: 'Ndërsa media X fokusohet tek aspekti ekonomik i marrëveshjes, media Y e thekson si një fitore politike...'
        If they report it exactly the same way, state that both sources maintain a uniform narrative without editorial deviation.
        Return ONLY the raw Albanian text.
        """
        
        print(f"🔄 Analyzing perspectives for cluster {c_id[:8]}...")
        try:
            # Use the new robust retry mechanism
            perspective_sq = generate_with_retry(prompt, model_name="gemini-2.5-flash").strip()
            
            cursor.execute("UPDATE articles SET cluster_perspective_sq = ? WHERE cluster_id = ?", (perspective_sq, c_id))
            conn.commit()
            print("✅ Perspective generated.")
        except Exception as e:
            print(f"⚠️ Failed to generate perspective after retries: {e}")
            
    conn.close()
    print("🚀 Perspective Analysis complete!")

if __name__ == "__main__":
    run_perspective_engine()