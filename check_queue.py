import sqlite3

conn = sqlite3.connect("news_aggregator.db")
cursor = conn.cursor()

# Check total counts grouped by their AI processing status
cursor.execute("SELECT processed_by_ai, COUNT(*) FROM articles GROUP BY processed_by_ai")
results = cursor.fetchall()

print("\n📊 STATUSI I BAZËS SË TË DHËNAVE:")
total = 0
for row in results:
    status = "✅ Përpunuar nga AI (Gati për Web)" if row[0] == 1 else "⏳ Në pritje të AI (Në radhë)"
    count = row[1]
    total += count
    print(f"{status}: {count} artikuj")

print(f"------------\nTotali: {total} artikuj")

conn.close()