import streamlit as st
import sqlite3
import pandas as pd

# --- UI TRANSLATION DICTIONARY ---
UI_TEXT = {
    "English": {
        "topics": ["All Topics", "Politics", "Economy", "Infrastructure", "Technology", "Culture", "Entertainment", "Sports"],
        "geos": ["All Regions", "North Macedonia", "Kosovo", "Albania", "Regional"],
        "geo_labels": ["🌍 Global", "🇲🇰 MKD", "🇽🇰 KOS", "🇦🇱 ALB", "🗺️ Balkans"],
        "lang_header": "System Language",
        "geo_header": "Geographic Focus",
        "db_header": "Daily Briefing",
        "db_sub": "Narrative blindspots delivered straight to your inbox.",
        "api_header": "Enterprise API",
        "api_sub": "Integrate real-time narrative clustering into your dashboards.",
        "subscribe": "Subscribe",
        "success": "Thank you! You are subscribed.",
        "api_btn": "View API Docs",
        "blindspots_btn": "👁️ View Blindspots",
        "blindspots": "Strategic Blindspots",
        "blindspots_sub": "Regional narratives and crucial information updates you might have missed completely from mainstream local coverage.",
        "modal_title": "Deep Dive Analysis",
        "pw": "Pro-Western Alignment",
        "obj": "Factual Objectivity",
        "div": "Divergence Level",
        "btn_back": "Close",
        "sources": "Original Sources Matrix",
        "how_ai_works": "🧠 How Platform AI Works",
        "ai_desc": "<b>Core Data Aggregation:</b> Balkan Intel continuously aggregates automated RSS feeds across the Western Balkans region.<br><br><b>AI Synthesis Engine:</b> The raw source text is securely structured and analyzed using Google's Gemini 2.5 Flash model to extract language neutral narrative properties, evaluate western strategic alignment metrics, and measure objective factual presentation.<br><br><b>What is a Blindspot?</b> A Blindspot is a high-impact regional development that carries a high divergence score, meaning the story is being significantly omitted, downplayed, or selectively framed by specific local media clusters compared to the baseline factual event timeline.",
        "db_col_title": "title_en",
        "db_col_bullets": "bullets_en",
        "db_col_persp": "perspective_en"
    },
    "Shqip": {
        "topics": ["Të gjitha", "Politikë", "Ekonomi", "Infrastrukturë", "Teknologji", "Kulturë", "Show Biz", "Sport"],
        "geos": ["Të gjitha", "Maqedonia e Veriut", "Kosova", "Shqipëria", "Rajonale"],
        "geo_labels": ["🌍 Global", "🇲🇰 MKD", "🇽🇰 KOS", "🇦🇱 ALB", "🗺️ Ballkan"],
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
        "btn_back": "Mbyll",
        "sources": "Burimet Origjinale",
        "how_ai_works": "🧠 Si funksionon AI?",
        "ai_desc": "<b>Grumbullimi i të Dhënave:</b> Balkan Intel grumbullon në mënyrë të vazhdueshme lajmet automatike nga rajoni i Ballkanit Perëndimor përmes RSS.<br><br><b>Motori i Inteligjencës Artificiale:</b> Teksti bruto i burimit strukturohet dhe analizohet duke përdorur modelin Gemini 2.5 Flash të Google për të nxjerrë metrika të qëndrimit gjeopolitik dhe për të vlerësuar objektivitetin faktik.<br><br><b>Çfarë është një e Pathënë (Blindspot)?</b> Një 'E Pathënë' përfaqëson një zhvillim rajonal me ndikim të lartë që mbart një shkallë të lartë divergjence, që do të thotë se ngjarja po anashkalohet ose po kornizohet në mënyrë selektive nga klastere të caktuara mediale lokale në krahasim me rrjedhën bazë të fakteve.",
        "db_col_title": "title_sq",
        "db_col_bullets": "bullets_sq",
        "db_col_persp": "perspective_sq"
    },
    "Македонски": {
        "topics": ["Сите Теми", "Политика", "Економија", "Инфраструктура", "Технологија", "Култура", "Забава", "Спорт"],
        "geos": ["Сите Региони", "Северна Македонија", "Косово", "Албанија", "Регионално"],
        "geo_labels": ["🌍 Глобално", "🇲🇰 MKD", "🇽🇰 KOS", "🇦🇱 ALB", "🗺️ Балкан"],
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
        "btn_back": "Затвори",
        "sources": "Оригинални Извори",
        "how_ai_works": "🧠 Како работи ВИ?",
        "ai_desc": "<b>Агрегација на податоци:</b> Balkan Intel континуирано собира автоматизирани RSS извори низ регионот на Западен Балкан.<br><br><b>Аналитички мотор на ВИ:</b> Текстот се анализира со помош на моделот Gemini 2.5 Flash на Google за да се извлечат геополитички метрики и да се оцени фактуелната објективност.<br><br><b>Што е Игнорирана вест (Blindspot)?</b> Тоа е значаен регионален настан кој има висок резултат на дивергенција, што значи дека настанот е испуштен или селективно прикажан од одредени локални медиуми во споредба со реалните факти.",
        "db_col_title": "title_mk",
        "db_col_bullets": "bullets_en",
        "db_col_persp": "perspective_mk"
    }
}
# Defaults for SR and BS mapped internally to EN structure logic for brevity if needed.
UI_TEXT["Srpski"] = UI_TEXT["English"].copy()
UI_TEXT["Srpski"].update({"topics": ["Sve Teme", "Politika", "Ekonomija", "Infrastruktura", "Tehnologija", "Kultura", "Zabava", "Sport"], "geos": ["Svi Regioni", "Severna Makedonija", "Kosovo", "Albanija", "Regionalno"], "geo_labels": ["🌍 Globalno", "🇲🇰 MKD", "🇽🇰 KOS", "🇦🇱 ALB", "🗺️ Balkan"], "lang_header": "Jezik Sistema", "geo_header": "Geografski Filter", "db_header": "Dnevni Brifing", "blindspots_btn": "👁️ Slepe tačke", "blindspots": "Strateške Slepe Tačke", "how_ai_works": "🧠 Kako radi AI?", "db_col_title": "title_sr", "db_col_bullets": "bullets_en", "db_col_persp": "perspective_sr"})
UI_TEXT["Bosanski"] = UI_TEXT["Srpski"].copy()
UI_TEXT["Bosanski"].update({"blindspots_btn": "👁️ Slijepe tačke", "blindspots": "Strateške Slijepe Tačke", "db_header": "Dnevni Briefing"})

# --- DATABASE FETCH FUNCTIONS ---
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
        query = "SELECT * FROM articles WHERE title_en != 'Processing Error' AND title_en IS NOT NULL ORDER BY narrative_divergence_score DESC LIMIT 3"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


# --- TOP LEVEL DIALOG MODALS (Fixes NameError) ---
@st.dialog("Balkan Intel Dashboard", width="large")
def open_article_modal(row, clean_bullets, perspective_html, bg_style, t_dict):
    header_col1, header_col2 = st.columns([1, 1.5], gap="small")
    pw = int(float(row.get('avg_pro_western', 0.5)) * 100)
    obj = int(float(row.get('avg_objectivity', 0.5)) * 100) 
    
    db_geo = row.get('cluster_geo_scope', '')
    geo_idx = UI_TEXT["English"]["geos"].index(db_geo) if db_geo in UI_TEXT["English"]["geos"] else -1
    display_geo_pin = t_dict["geos"][geo_idx] if geo_idx != -1 else db_geo

    spectrum_html = "".join([
        '<div style="background-color: transparent; border: 1px solid rgba(148, 163, 184, 0.3); padding: 12px; border-radius: 12px; margin-top: 4px;">',
        f'<div style="font-size: 0.75rem; font-weight: 800; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.05em; opacity: 0.7;">📊 {t_dict.get("modal_title")}</div>',
        f'<div style="margin-bottom: 8px;"><div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 700; margin-bottom: 4px;"><span>{t_dict.get("pw")}: {pw}%</span></div><div style="width: 100%; height: 6px; background-color: rgba(148, 163, 184, 0.3); border-radius: 999px; display: flex;"><div style="width: {pw}%; background-color: #3B82F6;"></div></div></div>',
        f'<div><div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 700; margin-bottom: 4px;"><span>{t_dict.get("obj")}: {obj}%</span></div><div style="width: 100%; height: 6px; background-color: rgba(148, 163, 184, 0.3); border-radius: 999px; display: flex;"><div style="width: {obj}%; background-color: #10B981;"></div></div></div>',
        '</div>'
    ])

    with header_col1:
        st.markdown(f"""<div style="width: 100%; height: 220px; border-radius: 16px; background-color: #1E293B; background-image: {bg_style}; background-size: cover; background-position: center; margin-bottom: 8px;"></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div style="display: flex; gap: 0.5rem;"><span style="background: rgba(148, 163, 184, 0.2); padding: 4px 10px; border-radius: 8px; font-size: 0.75rem; font-weight: 700;">📍 {display_geo_pin}</span></div>""", unsafe_allow_html=True)
        st.markdown(spectrum_html, unsafe_allow_html=True)
        
    with header_col2:
        st.markdown(f"<h3 style='margin-top: 4px; margin-bottom: 8px; font-weight: 800; font-size: 1.4rem; line-height: 1.2;'>{row['display_title']}</h3>", unsafe_allow_html=True)
        if clean_bullets:
            for b in clean_bullets[:4]: 
                st.markdown(f"<div style='margin-bottom: 8px; font-size: 0.95rem; line-height: 1.5; opacity: 0.85;'>• {b}</div>", unsafe_allow_html=True)
        if perspective_html: 
            st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
            st.markdown(perspective_html, unsafe_allow_html=True)

        titles = str(row.get('orig_titles', '')).split("||")
        urls = str(row.get('orig_urls', '')).split("||")
        sources_raw = str(row.get('sources', '')).split(", ")

        seen, links_html = set(), ""
        for t, s, u in zip(titles, sources_raw, urls):
            if t and t not in seen and u and str(u).startswith('http'):
                seen.add(t)
                links_html += f"<a href='{u}' target='_blank' style='text-decoration: none; color: inherit;'><div class='source-link-card'><div style='font-size: 0.7rem; color: #3B82F6; font-weight: 800; text-transform: uppercase; margin-bottom: 4px; letter-spacing: 0.05em;'>🔗 {s}</div><div style='font-size: 0.85rem; font-weight: 600; line-height: 1.3;'>{t}</div></div></a>"
                
        if links_html:
            st.markdown(f"<div style='margin-top: 16px; border-top: 1px solid rgba(148, 163, 184, 0.3); padding-top: 12px;'><h4 style='font-size: 0.85rem; font-weight: 800; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.05em; opacity: 0.7;'>{t_dict.get('sources', 'Sources')}</h4>{links_html}</div>", unsafe_allow_html=True)
    
    if st.button(t_dict.get("btn_back", "Close")):
        st.rerun()

@st.dialog("Balkan Intel Data", width="large")
def open_blindspots_modal(t_dict):
    st.markdown(f"<h3 style='margin-top:-20px; margin-bottom:15px;'>{t_dict.get('blindspots')}</h3>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.9rem; opacity: 0.7; margin-bottom: 1.5rem;'>{t_dict.get('blindspots_sub')}</div>", unsafe_allow_html=True)
    for idx, row in get_blindspot_stories().iterrows():
        col_title = t_dict.get("db_col_title", "title_en")
        b_title = row.get(col_title) or row.get('title_en') or "Title Missing"
        st.markdown(f"""
        <div style='background: transparent; padding: 1.2rem; border-radius: 12px; border-left: 4px solid #EF4444; margin-bottom: 1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-top: 1px solid rgba(148, 163, 184, 0.3); border-right: 1px solid rgba(148, 163, 184, 0.3); border-bottom: 1px solid rgba(148, 163, 184, 0.3);'>
            <div style='font-size: 0.75rem; font-weight: 800; color: #EF4444; text-transform: uppercase; margin-bottom: 6px;'>{row.get('cluster_category', 'News')}</div>
            <a href="{row.get('original_url', '#')}" target="_blank" style="text-decoration: none; color: inherit;">
                <div style='font-weight: 800; font-size: 1rem; line-height: 1.4; margin-bottom: 8px;'>
                    {b_title} <span style="color: #3B82F6; font-size: 0.85rem;">↗</span>
                </div>
            </a>
        </div>
        """, unsafe_allow_html=True)

@st.dialog("Balkan Intel System", width="small")
def open_methodology_modal(t_dict):
    st.markdown(f"<h3 style='margin-top:-10px; margin-bottom:15px;'>{t_dict.get('how_ai_works')}</h3>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.95rem; line-height: 1.6; color: #334155;'>{t_dict.get('ai_desc')}</div>", unsafe_allow_html=True)


# --- INTERFACE APPLICATION SYSTEM MATRIX ---
def run_app():
    st.set_page_config(page_title="Balkan Intel", layout="wide", initial_sidebar_state="expanded")
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
        
        /* SIDEBAR CONFIGURATION */
        [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B !important; padding-top: 1rem !important; }
        [data-testid="stSidebar"] * { color: #F8FAFC !important; }
        [data-testid="stSidebar"] svg { fill: #F8FAFC !important; }

        /* FORM FIELDS STABILIZATION */
        [data-testid="stSidebar"] input { color: #0F172A !important; background-color: #FFFFFF !important; text-align: center; }
        [data-testid="stForm"] { border: none !important; padding: 0 !important; }
        [data-testid="stForm"] button { background-color: #3B82F6 !important; border: none !important; border-radius: 8px !important; width: 100% !important; transition: background 0.2s; margin-top: 4px; padding: 10px !important; }
        [data-testid="stForm"] button p { color: #FFFFFF !important; font-weight: 700 !important; font-size: 0.85rem !important; }
        [data-testid="stForm"] button:hover { background-color: #2563EB !important; }

        /* ALIGNED TABS SYSTEM (MOBILE & DESKTOP) */
        [data-testid="stMainBlockContainer"] div[role="radiogroup"] {
            display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; 
            overflow-x: auto !important; -webkit-overflow-scrolling: touch !important; scrollbar-width: none !important; 
            padding-bottom: 8px !important; gap: 6px !important; justify-content: flex-start !important;
        }
        [data-testid="stMainBlockContainer"] div[role="radiogroup"]::-webkit-scrollbar { display: none !important; }
        
        /* CENTERED GRID FOR SIDEBAR FILTERS (FLAGS/GEOGRAPHY) */
        [data-testid="stSidebar"] div[role="radiogroup"] { 
            display: flex !important; flex-wrap: wrap !important; justify-content: center !important; gap: 8px !important; width: 100% !important; 
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label { 
            flex: 1 1 45% !important; background-color: #1E293B !important; border: 1px solid #334155 !important; border-radius: 8px !important; 
            padding: 8px 4px !important; display: flex !important; align-items: center !important; justify-content: center !important; text-align: center !important; margin: 0 !important;
        }

        div[role="radiogroup"] label > div:first-child { display: none !important; }
        div[role="radiogroup"] label p { color: #475569 !important; font-weight: 700 !important; font-size: 0.8rem !important; margin: 0 !important; text-align: center !important; width: 100% !important; }
        [data-testid="stSidebar"] div[role="radiogroup"] label p { color: #94A3B8 !important; }
        div[role="radiogroup"] label:has(input:checked) { background-color: #3B82F6 !important; border-color: #3B82F6 !important; }
        div[role="radiogroup"] label:has(input:checked) p { color: #FFFFFF !important; }
        
        /* VISUAL DISPLAY CARDS */
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

        /* INVISIBLE CLICK ELEMENT TRIGGER */
        div[data-testid="stButton"]:has(button[kind="primary"]) { margin: 0 !important; padding: 0 !important; height: 0px !important; overflow: visible !important; }
        button[kind="primary"] { position: absolute !important; background: transparent !important; border: none !important; color: transparent !important; height: 0px !important; padding: 0 !important; box-shadow: none !important; }
        button[kind="primary"]::after { content: ""; position: absolute; bottom: 0; left: 0; width: 100%; height: 380px; z-index: 99; cursor: pointer; }
        
        button[kind="secondary"] { background: transparent !important; border: none !important; font-weight: 800 !important; font-size: 0.9rem !important; padding: 0 !important; display: flex !important; align-items: center; border-radius: 0px !important; }
        
        .b2b-btn { display: block; text-align: center; background: #3B82F6; color: #FFFFFF !important; padding: 12px; border-radius: 8px; font-size: 0.85rem; font-weight: 700; text-decoration: none; margin-top: 4px; }
        .b2b-btn:hover { background-color: #2563EB !important; }

        /* METHODOLOGY & INTEGRATED INLINE BUTTONS */
        button[kind="secondary"]:has(div:contains("🧠")), button[kind="secondary"]:has(div:contains("👁️")) { 
            border: 1px solid #334155 !important; background-color: transparent !important; color: #F8FAFC !important; justify-content: center !important; 
            border-radius: 8px !important; padding: 8px !important; width: 100%; margin-top: 10px !important; transition: all 0.2s ease !important; 
        }
        button[kind="secondary"]:has(div:contains("🧠")) p, button[kind="secondary"]:has(div:contains("👁️")) p { 
            font-size: 0.8rem !important; font-weight: 700 !important; color: #F8FAFC !important; 
        }
        button[kind="secondary"]:has(div:contains("🧠")):hover, button[kind="secondary"]:has(div:contains("👁️")):hover { 
            background-color: rgba(255,255,255,0.05) !important; border-color: #64748B !important; 
        }
        
        /* BLINDSPOT INLINE INTEGRATION (MAIN PAGE) */
        button[kind="secondary"].blindspot-inline {
            background-color: #FEF2F2 !important; border: 1px solid #FECACA !important; color: #DC2626 !important; 
            border-radius: 8px !important; padding: 6px 14px !important; margin: 0 !important; font-size: 0.8rem !important;
        }
        button[kind="secondary"].blindspot-inline p { color: #DC2626 !important; }
        button[kind="secondary"].blindspot-inline:hover { background-color: #FEE2E2 !important; }

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

    df = get_database_data()
    if not df.empty:
        df = df[df['title_en'] != "Processing Error"]

    # --- SIDEBAR STRATEGIC CONTROL PIPELINE ---
    with st.sidebar:
        LANG_OPTIONS = ["🇬🇧 EN", "🇦🇱 SQ", "🇲🇰 MK", "🇷🇸 SR", "🇧🇦 BS"]
        LANG_MAP = {"🇬🇧 EN": "English", "🇦🇱 SQ": "Shqip", "🇲🇰 MK": "Македонски", "🇷🇸 SR": "Srpski", "🇧🇦 BS": "Bosanski"}
        
        current_lang_code = st.session_state.get("lang_choice", "🇬🇧 EN")
        current_dict = UI_TEXT[LANG_MAP[current_lang_code]]
        
        st.markdown(f"<div style='{SIDEBAR_HEADER_STYLE}'>{current_dict['lang_header']}</div>", unsafe_allow_html=True)
        short_lang = st.radio("Lang", LANG_OPTIONS, horizontal=True, label_visibility="collapsed", key="lang_choice")
        t = UI_TEXT[LANG_MAP[short_lang]]
        
        st.markdown("<hr style='margin: 0.75rem 0; border-color: #1E293B;'/>", unsafe_allow_html=True)
        st.markdown(f"<div style='{SIDEBAR_HEADER_STYLE}'>{t['geo_header']}</div>", unsafe_allow_html=True)
        display_geo = st.radio("Geo", t["geo_labels"], label_visibility="collapsed")
        geo_index = t["geo_labels"].index(display_geo)
        backend_geo = UI_TEXT["English"]["geos"][geo_index]

        st.markdown("<hr style='margin: 0.75rem 0; border-color: #1E293B;'/>", unsafe_allow_html=True)
        st.markdown(f"<div style='{SIDEBAR_HEADER_STYLE}'>{t['db_header']}</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size: 0.75rem; color: #94A3B8; margin-bottom: 8px; line-height: 1.3; text-align: center;'>{t['db_sub']}</p>", unsafe_allow_html=True)
        with st.form("newsletter_form", clear_on_submit=True):
            email = st.text_input("Email", placeholder="your@email.com", label_visibility="collapsed")
            submitted = st.form_submit_button(t['subscribe'], use_container_width=True)
            if submitted:
                st.success(t['success'])

        st.markdown("<hr style='margin: 0.75rem 0; border-color: #1E293B;'/>", unsafe_allow_html=True)
        st.markdown(f"<div style='{SIDEBAR_HEADER_STYLE}'>{t['api_header']}</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size: 0.75rem; color: #94A3B8; margin-bottom: 8px; line-height: 1.3; text-align: center;'>{t['api_sub']}</p>", unsafe_allow_html=True)
        st.markdown(f"<a href='#' class='b2b-btn'>{t['api_btn']}</a>", unsafe_allow_html=True)

        st.markdown("<hr style='margin: 0.75rem 0; border-color: #1E293B;'/>", unsafe_allow_html=True)
        if st.button(t.get('how_ai_works'), type="secondary", use_container_width=True):
            open_methodology_modal(t)

    # --- MAIN APPLICATION WORKSPACE ---
    # Horizontal Swipe Navigation Layer for Content Categories & Inline Blindspots
    col_nav, col_bs = st.columns([3, 1], gap="small")
    
    with col_nav:
        display_cat = st.radio("Topics", t["topics"], horizontal=True, label_visibility="collapsed")
        cat_index = t["topics"].index(display_cat)
        backend_cat = UI_TEXT["English"]["topics"][cat_index]
        
    with col_bs:
        # Native, integrated look for the Blindspots trigger alongside Topics
        st.markdown("<div style='height: 2px;'></div>", unsafe_allow_html=True) # minor alignment tweak
        if st.button(t.get('blindspots_btn'), key="bs_trigger", help="View Strategic Omissions"):
            open_blindspots_modal(t)

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    filtered_df = df.copy()
    if backend_geo != "All Regions": 
        target_geo = backend_geo.strip().lower()
        filtered_df = filtered_df[filtered_df['cluster_geo_scope'].apply(lambda x: target_geo in str(x).strip().lower())]
        
    if backend_cat != "All Topics": 
        target_cat = backend_cat.strip().lower()
        filtered_df = filtered_df[filtered_df['cluster_category'].apply(lambda x: target_cat in str(x).strip().lower())]

    if filtered_df.empty:
        st.warning("No articles found.")
    else:
        grid_col1, grid_col2 = st.columns(2, gap="medium")
        for idx, row in filtered_df.reset_index(drop=True).iterrows():
            col_title = t.get("db_col_title", "title_en")
            col_bullets = t.get("db_col_bullets", "bullets_en")
            col_persp = t.get("db_col_persp", "perspective_en")
            
            # Reverted to Raw Original Strings (Removes broken Albanian formatting)
            display_title = row.get(col_title) or row.get('title_en') or "Title Missing"
            
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
                    row_dict['display_title'] = display_title 
                    open_article_modal(row_dict, clean_b, persp, bg, t)
                
                st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    st.markdown('<a href="#top-anchor" class="scroll-top-btn">▲</a>', unsafe_allow_html=True)

if __name__ == "__main__":
    run_app()
