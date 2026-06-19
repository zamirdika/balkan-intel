import feedparser
import hashlib
import time
import json

# 1. SCOPE LIMIT: Just two feeds to test cross-lingual and regional vs. global merging
RSS_FEEDS = {
    "alsat_sq": {"url": "https://alsat.mk/feed/", "lang": "sq", "source": "Alsat-M (SQ)"},
    "bbc_world": {"url": "http://feeds.bbci.co.uk/news/world/rss.xml", "lang": "en", "source": "BBC World"}
}

def generate_article_id(url: str) -> str:
    return hashlib.md5(url.encode('utf-8')).hexdigest()

def fetch_mock_data():
    print("📡 Fetching raw articles for local cache...")
    articles = []
    
    for key, info in RSS_FEEDS.items():
        feed = feedparser.parse(info['url'])
        
        # 2. RATE LIMIT: Cap to exactly 4 articles per feed
        for entry in feed.entries[:4]:
            link = entry.get('link', '')
            if not link: continue
            
            articles.append({
                "article_id": generate_article_id(link),
                "source_domain": key,
                "original_language": info['lang'],
                "original_title": entry.get('title', ''),
                "original_url": link,
                "original_summary": entry.get('summary', '')[:200],
                "image_url": "",
                "published_timestamp": int(time.time()),
                "processed_by_ai": False # Marking as False so main.py knows to process it
            })
            
    # 3. LOCAL CACHE: Save to a static JSON file
    with open("test_data.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
        
    print(f"✅ Saved {len(articles)} articles to test_data.json.")
    print("You can now safely run your AI processing on this static file.")

if __name__ == "__main__":
    fetch_mock_data()