import streamlit as st
import sqlite3
import pandas as pd
import re
import unicodedata
from difflib import SequenceMatcher

# --- UI TRANSLATION DICTIONARY ---
UI_TEXT = {
    "English": {
        "topics": ["All Topics", "Politics", "Economy", "Infrastructure", "Technology", "Culture", "Entertainment", "Sports"],
        "geos": ["All Regions", "North Macedonia", "Kosovo", "Albania", "Regional"],
        "geo_labels": ["Global", "Macedonia", "Kosovo", "Albania", "Balkans"],
        "lang_header": "System Language",
        "geo_header": "Geographic Focus",
        "db_header": "Daily Briefing",
        "db_sub": "Narrative blindspots delivered straight to your inbox.",
        "api_header": "Enterprise API",
        "api_sub": "Integrate real-time narrative clustering into your dashboards.",
        "subscribe": "Subscribe",
        "success": "Thank you! You are subscribed.",
        "api_btn": "View API Docs",
        "blindspots_btn": "👁️ Blindspots",
        "blindspots": "Strategic Blindspots",
        "blindspots_sub": "Regional narratives and crucial information updates you might have missed completely from mainstream local coverage.",
        "modal_title": "Deep Dive Analysis",
        "pw": "Pro-Western Alignment",
        "obj": "Factual Objectivity",
        "div": "Divergence Level",
        "btn_back": "« Back",
        "sources": "Original Sources Matrix",
        "how_ai_works": "🔬 How Platform AI Works",
        "ai_desc": "<b>Core Data Aggregation:</b> Balkan Intel continuously aggregates automated RSS feeds across the Western Balkans region.<br><br><b>AI Synthesis Engine:</b> The raw source text is securely structured and analyzed using Google's Gemini 2.5 Flash model to extract language neutral narrative properties, evaluate western strategic alignment metrics, and measure objective factual presentation.<br><br><b>What is a Blindspot?</b> A Blindspot is a high-impact regional development that carries a high divergence score, meaning the story is being significantly omitted, downplayed, or selectively framed by specific local media clusters compared to the baseline factual event timeline.",
        "db_col_title": "title_en",
        "db_col_bullets": "bullets_en",
        "db_col_persp": "perspective_en"
    },
    "Shqip": {
        "topics": ["Të gjitha", "Politikë", "Ekonomi", "Infrastrukturë", "Teknologji", "Kulturë", "Show Biz", "Sport"],
        "geos": ["Të gjitha", "Maqedonia e Veriut", "Kosova", "Shqipëria", "Rajonale"],
        "geo_labels": ["Global", "Macedonia", "Kosovo", "Albania", "Balkans"],
        "lang_header": "Gjuha e Sistemit",
        "geo_header": "Fokusi Gjeografik",
        "db_header": "Informimi Ditor",
        "db_sub": "Të pathënat e narrativave direkt në emailin tuaj.",
        "api_header": "API për Biznese",
        "api_sub": "Integroni grupimin e narrativave në kohë reale.",
        "subscribe": "Abonohu",
        "success": "Faleminderit! Jeni abonuar.",
        "api_btn": "Shiko Dokumentacionin",
        "blindspots_btn": "👁️ Të pathënat",
        "blindspots": "Të pathënat Strategjike",
        "blindspots_sub": "Narrativa rajonale strategjike dhe informacione jetike që mund t'i keni anashkaluar plotësisht nga mbulimi kryesor medial lokal.",
        "modal_title": "Analiza e Thelluar",
        "pw": "Qëndrimi Pro-Perëndimor",
        "obj": "Objektiviteti Faktik",
        "div": "Anashkalimi",
        "btn_back": "« Kthehu",
        "sources": "Burimet Origjinale",
        "how_ai_works": "🔬 Si funksionon AI?",
        "ai_desc": "<b>Grumbullimi i të Dhënave:</b> Balkan Intel grumbullon në mënyrë të vazhdueshme lajmet automatike nga rajoni i Ballkanit Perëndimor përmes RSS.<br><br><b>Motori i Inteligjencës Artificiale:</b> Teksti bruto i burimit strukturohet dhe analizohet duke përdorur modelin Gemini 2.5 Flash të Google për të nxjerrë metrika të qëndrimit gjeopolitik dhe për të vlerësuar objektivitetin faktik.<br><br><b>Çfarë është një e Pathënë (Blindspot)?</b> Një 'E Pathënë' përfaqëson një zhvillim rajonal me ndikim të lartë që mbart një shkallë të lartë divergjence, që do të thotë se ngjarja po anashkalohet ose po kornizohet në mënyrë selektive nga klastere të caktuara mediale lokale në krahasim me rrjedhën bazë të fakteve.",
        "db_col_title": "title_sq",
        "db_col_bullets": "bullets_sq",
        "db_col_persp": "perspective_sq"
    },
    "Македонски": {
        "topics": ["Сите Теми", "Политика", "Економија", "Инфраструктура", "Технологија", "Култура", "Забава", "Спорт"],
        "geos": ["Сите Региони", "Северна Македонија", "Косово", "Албанија", "Регионално"],
        "geo_labels": ["Глобално", "Macedonia", "Kosovo", "Albania", "Balkans"],
        "lang_header": "Јазик на Системот",
        "geo_header": "Географски Филтер",
        "db_header": "Дневен Брифинг",
        "db_sub": "Наративни слепи точки доставени директно во вашето сандаче.",
        "api_header": "Enterprise API",
        "api_sub": "Интегрирајте групирање на наративи во реално време.",
        "subscribe": "Претплати се",
        "success": "Ви благодариме! Претплатени сте.",
        "api_btn": "Види API Документација",
        "blindspots_btn": "👁️ Игнорирани вести",
        "blindspots": "Стратешки Игнорирани Вести",
        "blindspots_sub": "Регионални наративи и клучни информации кои можеби целосно сте ги пропуштиле во главните локални медиуми.",
        "modal_title": "Длабинска Анализа",
        "pw": "Про-Западна Ориентација",
        "obj": "Фактуелна Објективност",
        "div": "Дивергенција",
        "btn_back": "« Назад",
        "sources": "Оригинални Извори",
        "how_ai_works": "🔬 Како работи ВИ?",
        "ai_desc": "<b>Агрегација на податоци:</b> Balkan Intel континуирано собира автоматизирани RSS извори низ регионот на Западен Балкан.<br><br><b>Аналитички мотор на ВИ:</b> Текстот се анализира со помош на моделот Gemini 2.5 Flash на Google за да се извлечат геополитички метрики и да се оцени фактуелната објективност.<br><br><b>Што е Игнорирана вест (Blindspot)?</b> Тоа е значаен регионален настан кој има висок резултат на дивергенција, што значи дека настанот е испуштен или селективно прикажан од одредени локални медиуми во споредба со реалните факти.",
        "db_col_title": "title_mk",
        "db_col_bullets": "bullets_en",
        "db_col_persp": "perspective_mk"
    }
}

# --- HELPER DATABASE CONNECTIONS ---
def get_connection():
    return sqlite3.connect('news_aggregator.db')

def get_database_data():
    conn = get_connection()
    query = """
        SELECT cluster_id, cluster_category, cluster_geo_scope,
               MAX(title_en) as title_en, MAX(title_sq) as title_sq, 
               MAX(title_mk) as title_mk, MAX(title_sr) as title_sr,
               MAX(bullets_en) as bullets_en, MAX(bullets_sq) as bullets_sq,
               MAX(perspective_en) as perspective_en, MAX(perspective_sq) as perspective_sq,
               MAX(perspective_mk) as perspective_mk, MAX(perspective_sr) as perspective_sr,
               AVG(geo_pro_western) as avg_pro_western, 
               AVG(narrative_objectivity) as avg_objectivity,
               AVG(narrative_divergence_score) as avg_divergence,
               GROUP_CONCAT(source_domain, ', ') as sources, 
               GROUP_CONCAT(original_title, '||') as orig_titles,
               GROUP_CONCAT(original_url, '||') as orig_urls, 
               MAX(image_url) as cluster_image
        FROM articles WHERE cluster_id IS NOT NULL GROUP BY cluster_id ORDER BY article_id DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_blindspot_stories():
    try:
        conn = get_connection()
        query = """
            SELECT * FROM articles 
            WHERE title_en != 'Processing Error' AND title_en IS NOT NULL
            ORDER BY narrative_divergence_score DESC 
            LIMIT 3
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

# --- INTERFACE APPLICATION SYSTEM MATRIX ---
def run_app():
    # Style Variables Setup
    SIDEBAR_HEADER_STYLE = "font-size: 0.75rem; font-weight: 800; color: #94A3B8; text-transform: uppercase; margin-bottom: 10px; letter-spacing: 0.05em; display: block; text-align: center;"

    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #FAFAFA; scroll-behavior: smooth; }
        header[data-testid="stHeader"] { background: transparent !important; box-shadow: none !important; z-index: 99999 !important; pointer-events: none !important; }
        [data-testid="collapsedControl"] { pointer-events: auto !important; }
        .stAppDeployButton, [data-testid="stMainMenu"] { display: none !important; }
        footer { visibility: hidden; }
        .block-container { padding-top: 0rem !important; padding-bottom: 2rem !important; max-width: 100% !important; padding-left: 2.5rem !important; padding-right: 2.5rem !important; }
        
        /* --- SIDEBAR CONFIGURATION ARCHITECTURE --- */
        [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B !important; padding-top: 1rem !important; }
        [data-testid="stSidebar"] * { color: #F8FAFC !important; }
        [data-testid="stSidebar"] svg { fill: #F8FAFC !important; }

        /* --- STABLE CRITICAL STYLING FOR FORM FIELDS --- */
        [data-testid="stSidebar"] input { color: #0F172A !important; background-color: #FFFFFF !important; text-align: center; }
        [data-testid="stForm"] { border: none !important; padding: 0 !important; }
        [data-testid="stForm"] button { background-color: #3B82F6 !important; border: none !important; border-radius: 8px !important; width: 100% !important; transition: background 0.2s; margin-top: 4px; padding: 10px !important; }
        [data-testid="stForm"] button p { color: #FFFFFF !important; font-weight: 700 !important; font-size: 0.85rem !important; }
        [data-testid="stForm"] button:hover { background-color: #2563EB !important; }

        /* --- FLUID CENTER ALIGNED NAVIGATION RADIO MATRIX --- */
        div[role="radiogroup"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important; 
            overflow-x: auto !important;   
            -webkit-overflow-scrolling: touch !important; 
            scrollbar-width: none !important; 
            padding-bottom: 8px !important;
            gap: 6px !important;
            width: 100% !important;
        }
        div[role="radiogroup"]::-webkit-scrollbar { display: none !important; }
        div[role="radiogroup"] label { flex: 0 0 auto !important; background-color: #F1F5F9 !important; border: 1px solid #CBD5E1 !important; border-radius: 8px !important; padding: 6px 14px !important; cursor: pointer !important; transition: all 0.2s ease !important; display: inline-flex !important; align-items: center !important; justify-content: center !important; text-align: center !important; }
        
        /* SIDEBAR RADIO SYSTEM ALIGNMENT VERIFICATION */
        [data-testid="stSidebar"] div[role="radiogroup"] { display: grid !important; grid-template-columns: 1fr 1fr !important; gap: 6px !important; width: 100% !important; }
        [data-testid="stSidebar"] div[role="radiogroup"] label { background-color: #1E293B !important; border: 1px solid #334155 !important; border-radius: 8px !important; padding: 8px 4px !important; display: flex !important; align-items: center !important; justify-content: center !important; text-align: center !important; width: 100% !important; }

        div[role="radiogroup"] label > div:first-child { display: none !important; }
        div[role="radiogroup"] label p { color: #475569 !important; font-weight: 700 !important; font-size: 0.8rem !important; margin: 0 !important; text-align: center !important; width: 100% !important; }
        [data-testid="stSidebar"] div[role="radiogroup"] label p { color: #94A3B8 !important; }
        div[role="radiogroup"] label:has(input:checked) { background-color: #3B82F6 !important; border-color: #3B82F6 !important; }
        div[role="radiogroup"] label:has(input:checked) p { color: #FFFFFF !important; }
        
        /* --- VISUAL DISPLAY CARDS --- */
        .particle-card { background: #FFFFFF; border-radius: 20px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); border: 1px solid #F1F5F9; transition: transform 0.25s ease, box-shadow 0.25s ease; height: 380px; display: flex; flex-direction: column; overflow: hidden; position: relative; }
        .particle-card:hover { transform: translateY(-5px); box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08); }
        .card-img-area { height: 280px; background-color: #1E293B; background-size: cover; background-position: center; position: relative; display: flex; flex-direction: column; justify-content: flex-end; padding: 20px 24px; }
        .card-img-area::after { content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to top, rgba(0,0,0, 0.9) 0%, rgba(0,0,0, 0.5) 25%, rgba(0,0,0, 0) 45%); z-index: 1; }
        .card-img-content { position: relative; z-index: 2; width: 100%; }
        .card-tag { background: #3B82F6; color: #FFFFFF; font-size: 0.65rem; font-weight: 800; padding: 4px 10px; border-radius: 6px; text-transform: uppercase; display: inline-block; margin-bottom: 12px; }
        .card-title { font-size: clamp(1.05rem, 1.15vw, 1.2rem); font-weight: 800; color: #FFFFFF !important; line-height: 1.4; margin: 0; display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; text-shadow: 0 2px 6px rgba(0,0,0,0.8) !important; }
        .card-footer { height: 100px; padding: 16px 24px; background: #FFFFFF; display: flex; flex-direction: column; justify-content: center; gap: 8px; }
        
        /* DUAL BAR SEPARATION POLISH */
        .metric-track-wrapper { display: flex; flex-direction: column; gap: 2px; width: 100%; }
        .metric-label-container { display: flex; justify-content: space-between; font-size: 0.78rem; font-weight: 700; color: #475569; }
        .metric-bar-bg { width: 100%; height: 5px; background-color: #E2E8F0; border-radius: 999px; overflow: hidden; }
        .metric-bar-fill { height: 100%; border-radius: 999px; }

        /* INVISIBLE CLICK ELEMENT TRIGGER CAPABILITIES */
        div[data-testid="stButton"]:has(button[kind="primary"]) { margin: 0 !important; padding: 0 !important; height: 0px !important; overflow: visible !important; }
        button[kind="primary"] { position: absolute !important; background: transparent !important; border: none !important; color: transparent !important; height: 0px !important; padding: 0 !important; box-shadow: none !important; }
        button[kind="primary"]::after { content: ""; position: absolute; bottom: 0; left: 0; width: 100%; height: 380px; z-index: 99; cursor: pointer; }
        
        /* CLEAN TEXT HOVER ELEMENTS FOR STRATEGIC MODULES */
        button[kind="secondary"] { background: transparent !important; border: none !important; font-weight: 800 !important; font-size: 0.9rem !important; padding: 0 !important; display: flex !important; align-items: center; border-radius: 0px !important; }
        .b2b-btn { display: block; text-align: center; background: #3B82F6; color: #FFFFFF !important; padding: 12px; border-radius: 8px; font-size: 0.85rem; font-weight: 700; text-decoration: none; margin-top: 4px; }
        .b2b-btn:hover { background-color: #2563EB !important; }

        /* RE-INTEGRATED BLINDSPOT ALIGNMENT CARD SYSTEM */
        .inline-blindspot-trigger { width: 100%; background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0; border-left: 4px solid #EF4444; padding: 12px 18px; margin-bottom: 16px; cursor: pointer; display: flex; align-items: center; justify-content: space-between; transition: all 0.2s ease; }
        .inline-blindspot-trigger:hover { transform: translateX(2px); box-shadow: 0 4px 12px rgba(0,0,0,0.05); }

        /* METHODOLOGY COMPONENT SIDEBAR SYSTEM */
        button[kind="secondary"]:has(div:contains("🔬")) { border: 1px solid #334155 !important; background-color: transparent !important; color: #F8FAFC !important; justify-content: center !important; border-radius: 8px !important; padding: 8px !important; width: 100%; margin-top: 10px !important; transition: all 0.2s ease !important; }
        button[kind="secondary"]:has(div:contains("🔬")) p { font-size: 0.8rem !important; font-weight: 700 !important; color: #F8FAFC !important; }
        button[kind="secondary"]:has(div:contains("🔬")):hover { background-color: rgba(255,255,255,0.05) !important; border-color: #64748B !important; }

        /* BACK TO TOP FLOATER SCROLL SYSTEM */
        .scroll-top-btn { position: fixed; bottom: 25px; right: 25px; background-color: #3B82F6; color: white !important; width: 45px; height: 45px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4); z-index: 99999; font-weight: bold; text-decoration: none !important; transition: all 0.2s ease; }
        .scroll-top-btn:hover { transform: scale(1.1); background-color: #2563EB; }
    </style>
    <div id="top-anchor"></div>
    """, unsafe_allow_html=True)

    # --- BRAND DISPLAY MATRIX ---
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 10px 0 10px;">
        <div style="font-size: 1.8rem; font-weight: 800; letter-spacing: -0.05em;">
            <span style="color: #3B82F6;">Balkan</span><span style="color: #94A3B8;">Intel</span>
        </div>
        <div style="display: flex; gap: 1.5rem; font-size: 0.85rem; font-weight: 700; color: #64748B;">
            <a href="#" style="color: inherit; text-decoration: none;">Briefing</a>
            <a href="#" style="color: inherit; text-decoration: none;">API</a>
        </div>
    </div>
    <hr style='margin-top: 0.5rem; margin-bottom: 1rem; border-color: #E2E8F0;'/>
    """, unsafe_allow_html=True)

    # Fetch Data Assets
    df = get_database_data()
    if not df.empty:
        df = df[df['title_en'] != "Processing Error"]

    # --- SIDEBAR STRATEGIC CONTROL PIPELINE ---
    with st.sidebar:
        # Standard Language Controls
        LANG_OPTIONS = ["EN", "SQ", "MK", "SR", "BS"]
        LANG_MAP = {"EN": "English", "SQ": "Shqip", "MK": "Македонски", "SR": "Srpski", "BS": "Bosanski"}
        
        current_lang_code = st.session_state.get("lang_choice", "EN")
        current_dict = UI_TEXT[LANG_MAP[current_lang_code]]
        
        st.markdown(f"<div style='{SIDEBAR_HEADER_STYLE}'>{current_dict['lang_header']}</div>", unsafe_allow_html=True)
        short_lang = st.radio("Lang", LANG_OPTIONS, horizontal=True, label_visibility="collapsed", key="lang_choice")
        t = UI_TEXT[LANG_MAP[short_lang]]
        
        # Standard Geographic Controls
        st.markdown("<hr style='margin: 0.75rem 0; border-color: #1E293B;'/>", unsafe_allow_html=True)
        st.markdown(f"<div style='{SIDEBAR_HEADER_STYLE}'>{t['geo_header']}</div>", unsafe_allow_html=True)
        
        display_geo = st.radio("Geo", t["geo_labels"], label_visibility="collapsed")
        geo_index = t["geo_labels"].index(display_geo)
        backend_geo = UI_TEXT["English"]["geos"][geo_index]

        # Consolidated Newsletter Control System
        st.markdown("<hr style='margin: 0.75rem 0; border-color: #1E293B;'/>", unsafe_allow_html=True)
        st.markdown(f"<div style='{SIDEBAR_HEADER_STYLE}'>{t['db_header']}</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size: 0.75rem; color: #94A3B8; margin-bottom: 8px; line-height: 1.3; text-align: center;'>{t['db_sub']}</p>", unsafe_allow_html=True)
        with st.form("newsletter_form", clear_on_submit=True):
            email = st.text_input("Email", placeholder="your@email.com", label_visibility="collapsed")
            submitted = st.form_submit_button(t['subscribe'], use_container_width=True)
            if submitted:
                st.success(t['success'])

        # B2B Enterprise Strategic Entry Point
        st.markdown("<hr style='margin: 0.75rem 0; border-color: #1E293B;'/>", unsafe_allow_html=True)
        st.markdown(f"<div style='{SIDEBAR_HEADER_STYLE}'>{t['api_header']}</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size: 0.75rem; color: #94A3B8; margin-bottom: 8px; line-height: 1.3; text-align: center;'>{t['api_sub']}</p>", unsafe_allow_html=True)
        st.markdown(f"<a href='#' class='b2b-btn'>{t['api_btn']}</a>", unsafe_allow_html=True)

        # Methodology Platform Analytics Module
        st.markdown("<hr style='margin: 0.75rem 0; border-color: #1E293B;'/>", unsafe_allow_html=True)
        if st.button(t.get('how_ai_works'), type="secondary", use_container_width=True):
            open_methodology_modal(t)

    # --- MAIN APPLICATION WORKSPACE ---
    # Horizontal Swipe Navigation Layer for Content Categories
    display_cat = st.radio("Topics", t["topics"], horizontal=True, label_visibility="collapsed")
    cat_index = t["topics"].index(display_cat)
    backend_cat = UI_TEXT["English"]["topics"][cat_index]

    # Clean Integrated Left Aligned Blindspot Component Trigger
    st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
    bs_col1, bs_col2 = st.columns([1, 2.5])
    with bs_col1:
        if st.button(t.get('blindspots_btn'), type="secondary", use_container_width=True):
            open_blindspots_modal(t)
    st.markdown("<div style='margin-top: -8px;'></div>", unsafe_allow_html=True)

    # Filter Verification Execution
    filtered_df = df.copy()
    if backend_geo != "All Regions": 
        target_geo = backend_geo.strip().lower()
        filtered_df = filtered_df[filtered_df['cluster_geo_scope'].apply(lambda x: target_geo in str(x).strip().lower())]
        
    if backend_cat != "All Topics": 
        target_cat = backend_cat.strip().lower()
        filtered_df = filtered_df[filtered_df['cluster_category'].apply(lambda x: target_cat in str(x).strip().lower())]

    # Grid Build Execution Loop
    if filtered_df.empty:
        st.warning("No articles found.")
    else:
        grid_col1, grid_col2 = st.columns(2, gap="medium")
        for idx, row in filtered_df.reset_index(drop=True).iterrows():
            col_title = t.get("db_col_title", "title_en")
            col_bullets = t.get("db_col_bullets", "bullets_en")
            col_persp = t.get("db_col_persp", "perspective_en")
            
            # Extract title and apply direct sentence formatting rule safely
            raw_title = row.get(col_title) or row.get('title_en') or "Title Missing"
            display_title = raw_title.strip().capitalize()
            
            raw_b = str(row.get(col_bullets) or row.get('bullets_en') or "").split("||")[0]
            clean_b = [b.strip().lstrip('-*• ') for b in raw_b.split('\n') if b.strip()]
            
            persp_text = row.get(col_persp) or row.get('perspective_en') or ""
            persp = f"<div style='padding: 12px; border-left: 3px solid #3B82F6; font-size: 0.9rem; font-style: italic; border-radius: 0 8px 8px 0; opacity: 0.85;'>{persp_text}</div>" if persp_text else ""
            
            raw_img = str(row.get('cluster_image', '')).strip()
            unique_seed = row.get('cluster_id', f"rand_{idx}")
            fallback = f"https://picsum.photos/seed/{unique_seed}/800/500"
            bg = f"url('{fallback}')" if pd.isna(row.get('cluster_image')) or raw_img in ('None', 'nan', '') or not raw_img.startswith('http') else f"url('{raw_img}'), url('{fallback}')"

            pw = int(float(row.get('avg_pro_western', 0.5)) * 100)
            obj = int(float(row.get('avg_objectivity', 0.5)) * 100)

            with (grid_col1 if idx % 2 == 0 else grid_col2):
                card_html = f"""
                <div class="particle-card">
                    <div class="card-img-area" style="background-image: {bg};">
                        <div class="card-img-content">
                            <span class="card-tag">{row.get("cluster_category", "News")}</span>
                            <div class="card-title">{display_title}</div>
                        </div>
                    </div>
                    <div class="card-footer">
                        <div class="metric-track-wrapper">
                            <div class="metric-label-container">
                                <span>{t.get("pw")}: {pw}%</span>
                            </div>
                            <div class="metric-bar-bg">
                                <div class="metric-bar-fill" style="width: {pw}%; background-color: #3B82F6;"></div>
                            </div>
                        </div>
                        <div class="metric-track-wrapper">
                            <div class="metric-label-container">
                                <span>{t.get("obj")}: {obj}%</span>
                            </div>
                            <div class="metric-bar-bg">
                                <div class="metric-bar-fill" style="width: {obj}%; background-color: #10B981;"></div>
                            </div>
                        </div>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                
                if st.button(" ", key=f"btn_{row.get('cluster_id', idx)}", type="primary", use_container_width=True):
                    row_dict = row.to_dict()
                    row_dict['cluster_title_sq'] = display_title 
                    open_article_modal(row_dict, clean_b, persp, "", bg, t)
                
                st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    st.markdown('<a href="#top-anchor" class="scroll-top-btn">▲</a>', unsafe_allow_html=True)

if __name__ == "__main__":
    run_app()
