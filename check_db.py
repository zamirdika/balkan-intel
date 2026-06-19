import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect("news_aggregator.db")

# Query to count how many articles belong to each geographic tag
query = """
    SELECT cluster_geo_scope, COUNT(*) as total_articles 
    FROM articles 
    GROUP BY cluster_geo_scope
"""

df = pd.read_sql_query(query, conn)
print("\n--- GJEOGRAFIA E LAJMEVE NË DATABAZË ---")
print(df)
print("----------------------------------------\n")

conn.close()