import sqlite3
import datetime

def seed_database():
    conn = sqlite3.connect('news_aggregator.db')
    cursor = conn.cursor()

    # 1. Create the exact table structure expected by the app
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        article_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cluster_id TEXT,
        cluster_title_sq TEXT,
        cluster_category TEXT,
        cluster_geo_scope TEXT,
        agency_ratio REAL,
        geo_pro_western REAL,
        editorial_state_aligned REAL,
        narrative_ethno_nationalist REAL,
        source_domain TEXT,
        original_title TEXT,
        original_url TEXT,
        bullet_points_sq TEXT,
        cluster_perspective_sq TEXT,
        image_url TEXT,
        published_timestamp DATETIME
    )
    ''')

    # Clear old test data to ensure a clean presentation state
    cursor.execute('DELETE FROM articles')

    # 2. Realistic, multi-perspective Balkan data clusters
    mock_data = [
        # Cluster 1: High Pro-Western, Civic (Geopolitics)
        ("C-001", "Samiti i BE-së konfirmon planin e rritjes për Ballkanin Perëndimor", "Politikë", "Rajonale", 
         0.8, 0.95, 0.10, 0.05, 
         "euronews.al, koha.net", "Plani i BE-së për Ballkanin||Ndihma financiare miratohet", "http://euronews.al/1||http://koha.net/1",
         "• BE miraton një paketë prej 6 miliardë eurosh për rajonin.\n• Kushti kryesor mbetet zbatimi i reformave në drejtësi.\n• Udhëheqësit rajonalë theksojnë nevojën për integrim të përshpejtuar.",
         "Fokusi mediatik anon fuqishëm drejt integrimit evropian, me burimet e pavarura që theksojnë mungesën e reformave të brendshme si pengesë.",
         "https://images.unsplash.com/photo-1555899434-94d1368aa7af?q=80&w=1000"),
        
        # Cluster 2: High Ethno-Nationalist, State-Aligned (The Blindspot candidate)
        ("C-002", "Tensione mbi kurrikulat e reja të historisë në shkollat e mesme", "Kulturë", "Lokale", 
         0.2, 0.30, 0.85, 0.90, 
         "rtk.live, mia.mk", "Ndryshimet në librat e historisë ngjallin reagime||Protesta për kurrikulat", "http://rtk.live/1||http://mia.mk/1",
         "• Ministria e Arsimit prezanton tekstet e reja shkollore.\n• Grupet e shoqërisë civile akuzojnë për shtrembërim faktesh.\n• Disa komuna refuzojnë shpërndarjen e librave të rinj.",
         "Një ndarje e thellë narrative: Mediat e lidhura me shtetin e quajnë 'modernizim', ndërsa mediat lokale e shohin si fshirje të identitetit etnik.",
         "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?q=80&w=1000"),

        # Cluster 3: Infrastructure / Economy
        ("C-003", "Korridori 8: Fillon faza e dytë e ndërtimit të autostradës", "Infrastrukturë", "Ndërkufitare", 
         0.5, 0.60, 0.70, 0.20, 
         "top-channel.tv, alsat.mk", "Rinisin punimet në Korridorin 8||Autostrada drejt përfundimit", "http://top-channel.tv/1||http://alsat.mk/1",
         "• Kompanitë ndërkombëtare marrin përsipër segmentin e ri.\n• Opozita ngre dyshime mbi transparencën e tenderëve.\n• Pritet që rruga të shkurtojë kohën e udhëtimit me 40%.",
         "Këndvështrimi është kryesisht i përqendruar tek zhvillimi ekonomik, megjithëse portalet opozitare theksojnë kostot e fryra financiare.",
         "https://images.unsplash.com/photo-1541888086425-d81bb19240f5?q=80&w=1000"),

        # Cluster 4: High Eastern Skeptic (Energy)
        ("C-004", "Rritja e çmimit të energjisë rrit varësinë nga importet e huaja", "Ekonomi", "Rajonale", 
         0.4, 0.20, 0.40, 0.30, 
         "balkaninsight.com, rferl.org", "Kriza energjetike godet rajonin||Importet thellojnë deficitin", "http://balkaninsight.com/1||http://rferl.org/1",
         "• Prodhimi vendas i energjisë bie me 15% këtë tremujor.\n• Qeveritë hezitojnë të rrisin faturat për qytetarët para zgjedhjeve.\n• Kontratat e reja me furnizuesit lindorë ngjallin debate.",
         "Një shqetësim në rritje vihet re në mediat e pavarura mbi ndikimin gjeopolitik që sjellin kontratat afatgjata të energjisë me vende jashtë BE-së.",
         "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?q=80&w=1000"),
         
        # Cluster 5: Tech & Startups
        ("C-005", "Tre startup-e nga Ballkani fitojnë fonde nga Silicon Valley", "Teknologji", "Rajonale", 
         0.9, 0.85, 0.10, 0.05, 
         "techcrunch.com, klan.al", "Miliona euro për inovacionin||Rinia ballkanike në tech", "http://techcrunch.com/1||http://klan.al/1",
         "• Një platformë e inteligjencës artificiale siguron 2 milionë euro.\n• Investitorët vlerësojnë talentin inxhinierik në rajon.\n• Ikja e trurit (brain drain) mbetet një rrezik i madh.",
         "Një mbulim tërësisht pozitiv dhe progresiv, që thekson lidhjen e fortë të rajonit me tregjet perëndimore të teknologjisë.",
         "https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1000")
    ]

    now = datetime.datetime.now()
    
    # Insert data
    for item in mock_data:
        # We duplicate each item 3 times with slightly different source names to simulate multiple articles forming a "cluster"
        for i in range(3):
            cursor.execute('''
            INSERT INTO articles (
                cluster_id, cluster_title_sq, cluster_category, cluster_geo_scope,
                agency_ratio, geo_pro_western, editorial_state_aligned, narrative_ethno_nationalist,
                source_domain, original_title, original_url, bullet_points_sq, cluster_perspective_sq, image_url, published_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item[0], item[1], item[2], item[3],
                item[4], item[5], item[6], item[7],
                item[8].split(', ')[i % 2], item[9].split('||')[i % 2], item[10].split('||')[i % 2], 
                item[11], item[12], item[13], now
            ))

    conn.commit()
    conn.close()
    print("✅ Success! The 'Balkan Intel' database has been seeded with 5 high-quality news clusters.")

if __name__ == "__main__":
    seed_database()