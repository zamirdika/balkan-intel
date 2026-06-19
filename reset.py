import sqlite3

# Lidhemi me databazën e lajmeve
conn = sqlite3.connect('news_aggregator.db')
cursor = conn.cursor()

# Kthejmë ID-të e grupeve në NULL që artikujt të ri-analizohen nga motori i ri gjeopolitik
cursor.execute('UPDATE articles SET cluster_id = NULL;')

conn.commit()
conn.close()

print("✨ Databaza u pastrua me sukses! Artikujt janë gati për analizën e re ballkanike.")