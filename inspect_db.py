import sqlite3

DB_NAME = "news_aggregator.db"

def inspect_clusters():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Group everything by cluster to see your Particle structure
        cursor.execute('''
            SELECT cluster_id, cluster_title_sq, cluster_category, 
                   cluster_geo_scope, bullet_points_sq, agency_ratio,
                   source_domain, original_title
            FROM articles 
            WHERE cluster_id IS NOT NULL
            ORDER BY cluster_id
        ''')
        rows = cursor.fetchall()
        
        if not rows:
            print("🗄️ Database is initialized but contains no clustered data yet.")
            return

        print(f"📊 Database Inspection: Found {len(rows)} entries assigned to clusters.\n")
        
        current_cluster = None
        for row in rows:
            # Whenever we hit a new cluster group, print its Particle Hero layout
            if row['cluster_id'] != current_cluster:
                current_cluster = row['cluster_id']
                print("=" * 70)
                print(f"🎯 ID NGJARJES: {row['cluster_id']}")
                print(f"📌 TITULLI:     {row['cluster_title_sq']}")
                print(f"📂 KATEGORIA:   {row['cluster_category']} | 🌍 SHTRIRJA: {row['cluster_geo_scope']}")
                print(f"⚖️ BALANCA ME-DIATIKE: {row['agency_ratio']} (0.0=Portal, 1.0=Agjenci Zyrtare)")
                print("-" * 70)
                print("💡 PIKAT KRYESORE (AI Bullet Takeaways):")
                # Format bullets nicely
                bullets = row['bullet_points_sq'].split('\n')
                for b in bullets:
                    if b.strip():
                        print(f"  • {b.strip()}")
                print("-" * 70)
                print("🔗 BURIMET E SINKRONIZUARA:")
            
            # Print the specific articles feeding into this cluster
            print(f"  [Source: {row['source_domain'].upper()}] -> {row['original_title']}")
            
        print("=" * 70)

    except sqlite3.OperationalError as e:
        print(f"❌ Table error: {e}. Make sure to run main.py first to build the schema.")
    finally:
        conn.close()

if __name__ == "__main__":
    inspect_clusters()