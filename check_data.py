import sqlite3

conn = sqlite3.connect("news_aggregator.db")
cursor = conn.cursor()

cursor.execute("SELECT original_title, bullet_points_sq, deep_dive_sq FROM articles WHERE processed_by_ai = 1 LIMIT 1")
row = cursor.fetchone()

if row:
    print("\n🔹 DATABASE CHECK RESULTS:")
    print(f"Title: {row[0]}")
    print(f"Bullet Points: {repr(row[1])}")
    print(f"Deep Dive: {repr(row[2])}")
else:
    print("\n❌ No AI-processed articles found. The database is empty or the AI didn't run properly.")

conn.close()