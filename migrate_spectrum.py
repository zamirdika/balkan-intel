import sqlite3

conn = sqlite3.connect('news_aggregator.db')
cursor = conn.cursor()

# Shto kolonat e reja analitike ballkanike
new_columns = [
    ("geo_pro_western", "REAL DEFAULT 0.5"),
    ("editorial_state_aligned", "REAL DEFAULT 0.5"),
    ("narrative_ethno_nationalist", "REAL DEFAULT 0.5")
]

for col_name, col_type in new_columns:
    try:
        cursor.execute(f"ALTER TABLE articles ADD COLUMN {col_name} {col_type};")
        print(f"✅ Kolona {col_name} u shtua me sukses.")
    except sqlite3.OperationalError:
        print(f"ℹ️ Kolona {col_name} ekziston ose nuk mund të shtohej.")

conn.commit()
conn.close()
print("✨ Migrimi i databazës përfundoi!")