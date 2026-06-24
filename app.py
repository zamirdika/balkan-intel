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
        "geos": ["All Regions", "North Macedonia", "Kosovo", "Albania", "Regional", "International"],
        "geo_labels": ["Global", "MK", "XK", "AL", "Balkans", "INT"],
        "lang_header": "System Language",
        "geo_header": "Geographic Focus",
        "db_header": "Daily Briefing",
        "db_sub": "Narrative blindspots delivered straight to your inbox.",
        "api_header": "Enterprise API",
        "api_sub": "Integrate real-time narrative clustering into your dashboards.",
        "subscribe": "Subscribe to Briefing",
        "success": "Success! You are subscribed.",
        "api_btn": "View API Docs",
        "blindspots": "Blindspots Dashboard",
        "blindspots_sub": "Strategic regional narratives you might have missed.",
        "modal_title": "Deep Dive Analysis",
        "pw": "Pro-Western Alignment",
        "obj": "Factual Objectivity",
        "div": "Divergence Level",
        "btn_back": "« Back to Feed",
        "db_col_title": "title_en",
        "db_col_bullets": "bullets_en",
        "db_col_persp": "perspective_en"
    },
    "Shqip": {
        "topics": ["Të gjitha", "Politikë", "Ekonomi", "Infrastrukturë", "Teknologji", "Kulturë", "Show Biz", "Sport"],
        "geos": ["Të gjitha", "Maqedonia e Veriut", "Kosova", "Shqipëria", "Rajonale", "Ndërkombëtare"],
        "geo_labels": ["Global", "MK", "XK", "AL", "Ballkan", "INT"],
        "lang_header": "Gjuha e Sistemit",
        "geo_header": "Fokusi Gjeografik",
        "db_header": "Informimi Ditor",
        "db_sub": "Të pathënat e narrativave direkt në emailin tuaj.",
        "api_header": "API për Biznese",
        "api_sub": "Integroni grupimin e narrativave në kohë reale.",
        "subscribe": "Abonohu Tani",
        "success": "Faleminderit! Jeni abonuar.",
        "api_btn": "Shiko Dokumentacionin",
        "blindspots": "Paneli i të Pathënave",
        "blindspots_sub": "Narrativa rajonale strategjike që mund t'i keni anashkaluar.",
        "modal_title": "Analiza e Thelluar",
        "pw": "Qëndrimi Pro-Perëndimor",
        "obj": "Objektiviteti Faktik",
        "div": "Anashkalimi",
        "btn_back": "« Kthehu te Lajmet",
        "db_col_title": "title_sq",
        "db_col_bullets": "bullets_sq",
        "db_col_persp": "perspective_sq"
    },
    "Македонски": {
        "topics": ["Сите Теми", "Политика", "Економија", "Инфраструктура", "Технологија", "Култура", "Забава", "Спорт"],
        "geos": ["Сите Региони", "Северна Македонија", "Косово", "Албанија", "Регионално", "Меѓународно"],
        "geo_labels": ["Глобално", "MK", "XK", "AL", "Балкан", "INT"],
        "lang_header": "Јазик на Системот",
        "geo_header": "Географски Филтер",
        "db_header": "Дневен Брифинг",
        "db_sub": "Наративни слепи точки доставени директно во вашето сандаче.",
        "api_header": "Enterprise API",
        "api_sub": "Интегрирајте групирање на наративи во реално време.",
        "subscribe": "Претплати се",
        "success": "Ви благодариме! Претплатени сте.",
        "api_btn": "Види API Документација",
        "blindspots": "Слепи Точки",
        "blindspots_sub": "Наративи што можеби сте ги пропуштиле.",
        "modal_title": "Длабинска Анализа",
        "pw": "Про-Западна Ориентација",
        "obj": "Фактуелна Објективност",
        "div": "Дивергенција",
        "btn_back": "« Назад кон Новости",
        "db_col_title": "title_mk",
        "db_col_bullets": "bullets_en",
        "db_col_persp": "perspective_mk"
    },
    "Srpski": {
        "topics": ["Sve Teme", "Politika", "Ekonomija", "Infrastruktura", "Tehnologija", "Kultura", "Zabava", "Sport"],
        "geos": ["Svi Regioni", "Severna Macedonia", "Kosovo", "Albanija", "Regionalno", "Međunarodno"],
        "geo_labels": ["Globalno", "MK", "XK", "AL", "Balkan", "INT"],
        "lang_header": "Jezik Sistema",
        "geo_header": "Geografski Filter",
        "db_header": "Dnevni Brifing",
        "db_sub": "Narativi koje ste možda propustili direktno u vaš inbox.",
        "api_header": "Enterprise API",
        "api_sub": "Integrišite grupisanje narativa u realnom vremenu.",
        "subscribe": "Pretplati se",
        "success": "Hvala! Pretplatili ste se.",
        "api_btn": "Vidi API Dokumentaciju",
        "blindspots": "Slepe Tačke",
        "blindspots_sub": "Narativi koje ste možda propustili.",
        "modal_title": "Dubinska Analiza",
        "pw": "Pro-Zapadna Orijentacija",
        "obj": "Faktualna Objektivnost",
        "div": "Divergencija",
        "btn_back": "« Nazad",
        "db_col_title": "title_sr",
        "db_col_bullets": "bullets_en",
        "db_col_persp": "perspective_sr"
    },
    "Bosanski": {
        "topics": ["Sve Teme", "Politika", "Ekonomija", "Infrastruktura", "Tehnologija", "Kultura", "Zabava", "Sport"],
        "geos": ["Svi Regioni", "Sjeverna Makedonija", "Kosovo", "Albanija", "Regionalno", "Međunarodno"],
        "geo_labels": ["Globalno", "MK", "XK", "AL", "Balkan", "INT"],
        "lang_header": "Jezik Sistema",
        "geo_header": "Geografski Filter",
        "db_header": "Dnevni Brifing",
        "db_sub": "Narativi koje ste možda propustili direktno u vaš inbox.",
        "api_header": "Enterprise API",
        "api_sub": "Integrišite grupisanje narativa u realnom vremenu.",
        "subscribe": "Pretplati se",
        "success": "Hvala! Pretplatili ste se.",
        "api_btn": "Vidi API Dokumentaciju",
        "blindspots": "Slijepe Tačke",
        "blindspots_sub": "Narativi koje ste možda propustili.",
        "modal_title": "Dubinska Analiza",
        "pw": "Pro-Zapadna Orijentacija",
        "obj": "Faktualna Objektivnost",
        "div": "Divergencija",
        "btn_back": "« Nazad",
        "db_col_title": "title_sr", 
        "db_col_bullets": "bullets_en",
        "db_col_persp": "perspective_sr"
    }
}

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

st.set_page_config(page_title="Balkan Intel", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #FAFAFA; scroll-behavior: smooth; }
    header[data-testid="stHeader"] { background: transparent !important; box-shadow: none !important; z-index: 99999 !important; pointer-events: none !important; pointer-events: none !important; }
    [data-testid="collapsedControl"] { pointer-events: auto !important; }
    .stAppDeployButton, [data-testid="stMainMenu"] { display: none !important; }
    footer { visibility: hidden; }
    .block-container { padding-top: 0rem !important; padding-bottom: 4rem !important; max-width: 100% !important; padding-left: 2.5rem !important; padding-right: 2.5rem !important; }
    
    /* --- SIDEBAR STYLE --- */
    [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B !important; padding-top: 1rem !important; }
    [data-testid="stSidebar"] * { color: #F8FAFC !important; }
    [data-testid="stSidebar"] svg { fill: #F8FAFC !important; }

    /* --- RADIO BUTTONS (BADGES) --- */
    div[role="radiogroup"] { display: flex !important; flex-wrap: wrap !important; gap: 8px !important; }
    div[role="radiogroup"] label { background-color: #F1F5F9 !important; border: 1px solid #CBD5E1 !important; border-radius: 8px !important; padding: 6px 14px !important; cursor: pointer !important; transition: all 0.2s ease !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] label { background-color: #1E293B !important; border: 1px solid #334155 !important; flex: 1 1 30% !important; min-width: 60px; text-align: center; justify-content: center; }
    
    div[role="radiogroup"] label > div:first-child { display: none !important; }
    div[role="radiogroup"] label p { color: #334155 !important; font-weight: 700 !important; font-size: 0.8rem !important; margin: 0 !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] label p { color: #94A3B8 !important; }
    
    div[role="radiogroup"] label:has(input:checked) { background-color: #3B82F6 !important; border-color: #3B82F6 !important; }
    div[role="radiogroup"] label:has(input:checked) p { color: #FFFFFF !important; }
    
    /* --- INVISIBLE FOOTPRINT PRIMARY BUTTON --- */
    div[data-testid="stButton"]:has(button[kind="primary"]) { margin: 0 !important; padding: 0 !important; height: 0px !important; overflow: visible !important; }
    button[kind="primary"] { position: absolute !important; background: transparent !important; border: none !important; color: transparent !important; height: 0px !important; padding: 0 !important; box-shadow: none !important; }
    button[kind="primary"]::after { content: ""; position: absolute; bottom: 0; left: 0; width: 100%; height: 380px; z-index: 99; cursor: pointer; }
    
    /* --- FORM SUBMIT BUTTON VISIBILITY FIX --- */
    button[data-testid="stFormSubmitButton"] { background-color: #3B82F6 !important; color: white !important; font-weight: 700 !important; border: none !important; border-radius: 8px !important; padding: 10px !important; width: 100% !important; transition: background 0.2s; }
    button[data-testid="stFormSubmitButton"]:hover { background-color: #2563EB !important; }

    /* --- CARDS --- */
    .particle-card { background: #FFFFFF; border-radius: 20px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); border: 1px solid #F1F5F9; transition: transform 0.25s ease, box-shadow 0.25s ease; height: 380px; display: flex; flex-direction: column; overflow: hidden; position: relative; }
    .particle-card:hover { transform: translateY(-5px); box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08); }
    .card-img-area { height: 300px; background-color: #1E293B; background-size: cover; background-position: center; position: relative; display: flex; flex-direction: column; justify-content: flex-end; padding: 20px 24px; }
    .card-img-area::after { content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to top, rgba(0,0,0, 0.9) 0%, rgba(0,0,0, 0.5) 25%, rgba(0,0,0, 0) 45%); z-index: 1; }
    .card-img-content { position: relative; z-index: 2; width: 100%; }
    .card-tag { background: #3B82F6; color: #FFFFFF; font-size: 0.65rem; font-weight: 800; padding: 4px 10px; border-radius: 6px; text-transform: uppercase; display: inline-block; margin-bottom: 12px; }
    .card-title { font-size: clamp(1.05rem, 1.15vw, 1.2rem); font-weight: 800; color: #FFFFFF !important; line-height: 1.4; margin: 0; display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; }
    .card-footer { height: 80px; padding: 12px 24px; background: #FFFFFF; display: flex; flex-direction: column; justify-content: center; }
    
    button[kind="secondary"] { background: transparent !important; border: none !important; font-weight: 800 !important; font-size: 0.9rem !important; padding: 0 !important; display: flex !important; text-transform: uppercase; }
    .b2b-btn { display: block; text-align: center; background: #3B82F6; color: #FFFFFF; padding: 12px; border-radius: 8px; font-size: 0.85rem; font-weight: 700; text-decoration: none; margin-top: 10px; }
    
    button[kind="secondary"]:has(div:contains("👁️")) { background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%) !important; border: 1px solid #334155 !important; border-left: 4px solid #EF4444 !important; color: #F8FAFC !important; justify-content: center !important; border-radius: 12px !important; padding: 10px !important; width: 100%; box-shadow: 0 8px 16px rgba(0,0,0,0.1) !important; }
    button[kind="secondary"]:has(div:contains("👁️")) p { font-size: 1rem !important; font-weight: 800 !important; color: #F8FAFC !important; }
    
    .scroll-top-btn { position: fixed; bottom: 25px; right: 25px; background-color: #3B82F6; color: white !important; width: 45px; height: 45px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4); z-index: 99999; font-weight: bold; text-decoration: none !important; }
</style>
<div id="top-anchor"></div>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 10px 0 10px;">
    <div style="font-size: 1.8rem; font-weight: 800; letter-spacing: -0.05em;"><span style="color: #3B82F6;">Balkan</span><span style="color: #94A3B8;">Intel</span></div>
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

# --- SIDEBAR ---
with st.sidebar:
    LANG_OPTIONS = ["EN", "SQ", "MK", "SR", "BS"]
    LANG_MAP = {"EN": "English", "SQ": "Shqip", "MK": "Македонски", "SR": "Srpski", "BS": "Bosanski"}
    
    current_lang_code = st.session_state.get("lang_choice", "EN")
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
    st.markdown(f"<p style='font-size: 0.75rem; color: #94A3B8; margin-bottom: 8px;'>{t['db_sub']}</p>", unsafe_allow_html=True)
    with st.form("newsletter_form", clear_on_submit=True):
        email = st.text_input("Email", placeholder="your@email.com", label_visibility="collapsed")
        submitted = st.form_submit_button(t['subscribe'])
        if submitted:
            st.success(t['success'])

    st.markdown("<hr style='margin: 0.75rem 0; border-color: #1E293B;'/>", unsafe_allow_html=True)
    st.markdown(f"<div style='{SIDEBAR_HEADER_STYLE}'>{t['api_header']}</div>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 0.75rem; color: #94A3B8;'>{t['api_sub']}</p>", unsafe_allow_html=True)
    st.markdown(f"<a href='#' class='b2b-btn'>{t['api_btn']}</a>", unsafe_allow_html=True)

# --- MAIN FEED ---
display_cat = st.radio("Topics", t["topics"], horizontal=True, label_visibility="collapsed")
cat_index = t["topics"].index(display_cat)
backend_cat = UI_TEXT["English"]["topics"][cat_index]

if st.button(f"👁️ {t.get('blindspots')}", type="secondary"):
    open_blindspots_modal(t)

filtered_df = df.copy()
if backend_geo != "All Regions": 
    filtered_df = filtered_df[filtered_df['cluster_geo_scope'].str.lower().str.contains(backend_geo.lower())]
if backend_cat != "All Topics": 
    filtered_df = filtered_df[filtered_df['cluster_category'].str.lower().str.contains(backend_cat.lower())]

if filtered_df.empty:
    st.warning("No articles found.")
else:
    grid_col1, grid_col2 = st.columns(2, gap="medium")
    for idx, row in filtered_df.reset_index(drop=True).iterrows():
        col_title = t.get("db_col_title", "title_en")
        col_bullets = t.get("db_col_bullets", "bullets_en")
        col_persp = t.get("db_col_persp", "perspective_en")
        
        display_title = row.get(col_title) or row.get('title_en') or "Title Missing"
        raw_b = str(row.get(col_bullets) or row.get('bullets_en') or "").split("||")[0]
        clean_b = [b.strip().lstrip('-*• ') for b in raw_b.split('\n') if b.strip()]
        persp_text = row.get(col_persp) or row.get('perspective_en') or ""
        
        raw_img = str(row.get('cluster_image', '')).strip()
        fallback = f"https://picsum.photos/seed/{row.get('cluster_id', idx)}/800/500"
        bg = f"url('{fallback}')" if raw_img in ('None', 'nan', '') else f"url('{raw_img}'), url('{fallback}')"

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
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 700; color: #475569;">
                        <span>⚖️ {t.get("pw")}: {pw}%</span>
                        <span>🔍 {t.get("obj")}: {obj}%</span>
                    </div>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            if st.button(" ", key=f"btn_{row.get('cluster_id', idx)}", type="primary"):
                open_article_modal(row.to_dict(), clean_b, persp_text, "", bg, t)
            st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

st.markdown('<a href="#top-anchor" class="scroll-top-btn">▲</a>', unsafe_allow_html=True)
