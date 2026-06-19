from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import pandas as pd

# 1. Initialize the B2B-Ready API with Professional Documentation
app = FastAPI(
    title="Balkan Intel API",
    description="Enterprise API providing AI-structured regional news, semantic deduplication, and Balkan Spectrum geopolitical metrics.",
    version="1.0.0",
    contact={
        "name": "Balkan Intel Developer Hub",
        "url": "https://balkanintel.com/b2b",
    }
)

# Allow external apps (like your future Mobile app or Web frontend) to access this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from fastapi.responses import RedirectResponse

# --- ROOT REDIRECT ---
@app.get("/", include_in_schema=False)
async def root():
    """Automatically redirects visitors from the blank root page to the B2B Developer Portal."""
    return RedirectResponse(url="/docs")
def get_database_data():
    """Helper function to pull and aggregate the latest AI clusters."""
    conn = sqlite3.connect('news_aggregator.db')
    query = """
        SELECT 
            cluster_id,
            cluster_title_sq as title,
            cluster_category as category,
            cluster_geo_scope as geo_scope,
            AVG(agency_ratio) as avg_agency,
            AVG(geo_pro_western) as avg_pro_western,
            AVG(editorial_state_aligned) as avg_state_aligned,
            AVG(narrative_ethno_nationalist) as avg_ethno_nationalist,
            GROUP_CONCAT(source_domain, ', ') as sources,
            GROUP_CONCAT(original_url, '||') as orig_urls,
            GROUP_CONCAT(bullet_points_sq, '||') as bullets,
            MAX(image_url) as image_url
        FROM articles
        WHERE cluster_id IS NOT NULL
        GROUP BY cluster_id
        ORDER BY MAX(published_timestamp) DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# --- ENDPOINT 1: THE MOBILE "DAILY BRIEFING" FEED ---
@app.get("/api/v1/feed/mobile", tags=["Mobile Client"])
async def get_mobile_feed(limit: int = Query(20, description="Max stories to load for offline caching")):
    """
    Optimized for the Mobile App. 
    Returns lightweight summaries and strict Balkan Spectrum math for the UI Bias Bars.
    """
    df = get_database_data()
    
    if df.empty:
        return {"status": "success", "articles": []}
        
    mobile_feed = []
    # Drop semantic duplicates on the fly for the mobile feed
    df = df.drop_duplicates(subset=['title']).head(limit)
    
    for _, row in df.iterrows():
        # Clean the bullet points for the mobile "Briefing Cards"
        raw_bullets = str(row['bullets']).split("||")[0] if pd.notna(row['bullets']) else ""
        clean_bullets = [b.strip().lstrip('-*• ') for b in raw_bullets.split('\n') if len(b) > 15][:3]
        
        # Calculate the integer percentages for the UI Bars
        pw_val = int(float(row.get('avg_pro_western', 0.5)) * 100)
        sa_val = int(float(row.get('avg_state_aligned', 0.5)) * 100)
        
        mobile_feed.append({
            "cluster_id": row['cluster_id'],
            "title": row['title'],
            "category": row['category'],
            "briefing_bullets": clean_bullets,
            "image_url": row['image_url'] if pd.notna(row['image_url']) else None,
            "metrics": {
                "pro_western_pct": pw_val,
                "state_aligned_pct": sa_val
            }
        })
        
    return {"status": "success", "count": len(mobile_feed), "feed": mobile_feed}

# --- ENDPOINT 2: B2B INTELLIGENCE & DEVELOPER PORTAL ---
@app.get("/api/v1/intelligence/balkan-spectrum", tags=["B2B API"])
async def get_b2b_intelligence(
    category: str = Query(None, description="Filter by category (e.g., Politikë)"),
    min_pro_western: float = Query(0.0, description="Filter by minimum Pro-Western alignment (0.0 to 1.0)")
):
    """
    Heavy-duty endpoint for B2B Clients.
    Provides raw decimal data, all original publisher links, and deep metrics.
    Requires token authentication in production.
    """
    df = get_database_data()
    
    if category:
        df = df[df['category'] == category]
    if min_pro_western > 0:
        df = df[df['avg_pro_western'] >= min_pro_western]
        
    b2b_data = df.to_dict(orient='records')
    return {
        "license": "B2B_COMMERCIAL",
        "records_returned": len(b2b_data),
        "data": b2b_data
    }

if __name__ == "__main__":
    import uvicorn
    # Runs the server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)