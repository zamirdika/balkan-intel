import streamlit as st
import sqlite3
import pandas as pd
import re
import unicodedata
from difflib import SequenceMatcher

# --- UI TRANSLATION DICTIONARY ---
UI_TEXT = {
    "English": {
        "topics": ["All Topics", "Politics", "Economy", "Infrastructure", "Technology", "Culture", "Entertainment"],
        "geos": ["All Regions", "North Macedonia", "Kosovo", "Albania", "Regional", "International"],
        "geo_labels": ["🌍 All", "🇲🇰 MKD", "🇽🇰 KOS", "🇦🇱 ALB", "🗺️ Balkans", "🌐 INT"],
        "lang_header": "🌐 Language",
        "geo_header": "📍 Geography",
        "db_header": "📬 Daily Briefing",
        "db_sub": "Narrative blindspots delivered straight to your inbox.",
        "api_header": "⚙️ Enterprise API",
        "api_sub": "Integrate real-time narrative clustering into your dashboards.",
        "subscribe": "Subscribe",
        "success": "Thank you! You are subscribed.",
        "api_btn": "View API Docs",
        "blindspots": "Blindspots",
        "blindspots_sub": "Narratives you might have missed.",
        "modal_title": "Deep Dive Analysis",
        "pw": "Pro-Western",
        "obj": "Objectivity",
        "div": "Divergence Level",
        "btn_back": "« Back",
        "db_col_title": "title_en",
        "db_col_bullets": "bullets_en",
        "db_col_persp": "perspective_en"
    },
    "Shqip": {
        "topics": ["Të gjitha", "Politikë", "Ekonomi", "Infrastrukturë", "Teknologji", "Kulturë", "Show Biz"],
        "geos": ["Të gjitha", "Maqedonia e Veriut", "Kosova", "Shqipëria", "Rajonale", "Ndërkombëtare"],
        "geo_labels": ["🌍 Të gjitha", "🇲🇰 MKD", "🇽🇰 KOS", "🇦🇱 ALB", "🗺️ Ballkani", "🌐 INT"],
        "lang_header": "🌐 Gjuha",
        "geo_header": "📍 Gjeografia",
        "db_header": "📬 Informimi Ditor",
        "db_sub": "Të pathënat e narrativave direkt në emailin tuaj.",
        "api_header": "⚙️ API për Biznese",
        "api_sub": "Integroni grupimin e narrativave në kohë reale.",
        "subscribe": "Abonohu",
        "success": "Faleminderit! Jeni abonuar.",
        "api_btn": "Shiko Dokumentacionin",
        "blindspots": "Të pathënat",
        "blindspots_sub": "Lajme ndoshta të anashkaluara.",
        "modal_title": "Analiza e Thelluar",
        "pw": "Pro-Perëndimit",
        "obj": "Objektiviteti",
        "div": "Anashkalimi",
        "btn_back": "« Kthehu",
        "db_col_title": "title_sq",
        "db_col_bullets": "bullets_sq",
        "db_col_persp": "perspective_en"
    },
    "Македонски": {
        "topics": ["Сите Теми", "Политика", "Економија", "Инфраструктура", "Технологија", "Култура", "Забава"],
        "geos": ["Сите Региони", "Северна Македонија", "Косово", "Албанија", "Регионално", "Меѓународно"],
        "geo_labels": ["🌍 Сите", "🇲🇰 MKD", "🇽🇰 KOS", "🇦🇱 ALB", "🗺️ Балкан", "🌐 INT"],
        "lang_header": "🌐 Јазик",
        "geo_header": "📍 Географија",
        "db_header": "📬 Дневен Брифинг",
        "db_sub": "Наративни слепи точки доставени директно во вашето сандаче.",
        "api_header": "⚙️ Enterprise API",
        "api_sub": "Интегрирајте групирање на наративи во реално време.",
        "subscribe": "Претплати се",
        "success": "Ви благодариме! Претплатени сте.",
        "api_btn": "Види API Документација",
        "blindspots": "Слепи точки",
        "blindspots_sub": "Наративи што можеби сте ги пропуштиле.",
        "modal_title": "Длабинска Анализа",
        "pw": "Про-Западно",
        "obj": "Објективност",
        "div": "Дивергенција",
        "btn_back": "« Назад",
        "db_col_title": "title_mk",
        "db_col_bullets": "bullets_en",
        "db_col_persp": "perspective_en"
    },
    "Srpski": {
        "topics": ["Sve Teme", "Politika", "Ekonomija", "Infrastruktura", "Tehnologija", "Kultura", "Zabava"],
        "geos": ["Svi Regioni", "Severna Makedonija", "Kosovo", "Albanija", "Regionalno", "Međunarodno"],
        "geo_labels": ["🌍 Sve", "🇲🇰 MKD", "🇽🇰 KOS", "🇦🇱 ALB", "🗺️ Balkan", "🌐 INT"],
        "lang_header": "🌐 Jezik",
        "geo_header": "📍 Geografija",
        "db_header": "📬 Dnevni Brifing",
        "db_sub": "Narativi koje ste možda propustili direktno u vaš inbox.",
        "api_header": "⚙️ Enterprise API",
        "api_sub": "Integrišite grupisanje narativa u realnom vremenu.",
        "subscribe": "Pretplati se",
        "success": "Hvala! Pretplatili ste se.",
        "api_btn": "Vidi API Dokumentaciju",
        "blindspots": "Slepe tačke",
        "blindspots_sub": "Narativi koje ste možda propustili.",
        "modal_title": "Dubinska Analiza",
        "pw": "Pro-Zapadno",
        "obj": "Objektivnost",
        "div": "Divergencija",
        "btn_back": "« Nazad",
        "db_col_title": "title_sr",
        "db_col_bullets": "bullets_en",
        "db_col_persp": "perspective_en"
    },
    "Bosanski": {
        "topics": ["Sve Teme", "Politika", "Ekonomija", "Infrastruktura", "Tehnologija", "Kultura", "Zabava"],
        "geos": ["Svi Regioni", "Sjeverna Makedonija", "Kosovo", "Albanija", "Regionalno", "Međunarodno"],
        "geo_labels": ["🌍 Sve", "🇲🇰 MKD", "🇽🇰 KOS", "🇦🇱 ALB", "🗺️ Balkan", "🌐 INT"],
        "lang_header": "🌐 Jezik",
        "geo_header": "📍 Geografija",
        "db_header": "📬 Dnevni Brifing",
        "db_sub": "Narativi koje ste možda propustili direktno u vaš inbox.",
        "api_header": "⚙️ Enterprise API",
        "api_sub": "Integrišite grupisanje narativa u realnom vremenu.",
        "subscribe": "Pretplati se",
        "success": "Hvala! Pretplatili ste se.",
        "api_btn": "Vidi API Dokumentaciju",
        "blindspots": "Slijepe tačke",
        "blindspots_sub": "Narativi koje ste možda propustili.",
        "modal_title": "Dubinska Analiza",
        "pw": "Pro-Zapadno",
        "obj": "Objektivnost",
        "div": "Divergencija",
        "btn_back": "« Nazad",
        "db_col_title": "title_sr", 
        "db_col_bullets": "bullets_en",
        "db_col_persp": "perspective_en"
    }
}

# --- HELPER FUNCTIONS ---
def is_similar_title(new_title, seen_titles, threshold=0.75):
    if pd.isna(new_title): return False
    new_t = re.sub(r'[^\w\s]', '', ''.join(c for c in unicodedata.normalize('NFD', str(new_title).lower()) if unicodedata.category(c) != 'Mn'))
    for seen in seen_titles:
        if SequenceMatcher(None, new_t, seen).ratio() > threshold: return True
    return False

def get_connection():
    return sqlite3.connect('news_aggregator.db')

def get_database_data():
    conn = get_connection()
    query = """
        SELECT cluster_id, cluster_category, cluster_geo_scope,
               MAX(title_en) as title_en, MAX(title_sq) as title_sq, 
               MAX(title_mk) as title_mk, MAX(title_sr) as title_sr,
               MAX(bullets_en) as bullets_en, MAX(bullets_sq) as bullets_sq,
               MAX(perspective_en) as perspective_en,
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
            WHERE title_en != 'Gabim në përpunim' AND title_en IS NOT NULL
            ORDER BY narrative_divergence_score DESC 
            LIMIT 3
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

# --- PAGE CONFIG ---
st.set_page_config(page_title="Balkan Intel", layout="wide", initial_sidebar_state="expanded")

# --- CSS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #FAFAFA; }
    header[data-testid="stHeader"] { background: transparent !important; box-shadow: none !important; z-index: 99999 !important; pointer-events: none !important; }
    [data-testid="collapsedControl"] { pointer-events: auto !important; }
    .stAppDeployButton, [data-testid="stMainMenu"] { display: none !important; }
    footer { visibility: hidden; }
    .block-container { padding-top: 0rem !important; padding-bottom: 2rem !important; max-width: 100% !important; padding-left: 2.5rem !important; padding-right: 2.5rem !important; }
    [data-testid="collapsedControl"] { background-color: #FFFFFF !important; border-radius: 50% !important; box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important; top: 1rem !important; left: 1rem !important; transition: all 0.2s ease; }
    [data-testid="collapsedControl"] svg { fill: #0F172A !important; }
    [data-testid="collapsedControl"]:hover { transform: scale(1.05); }
    
    /* --- SIDEBAR TEXT & BG --- */
    [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B !important; padding-top: 1rem !important; }
    [data-testid="stSidebar"] * { color: #F8FAFC !important; }
    [data-testid="stSidebar"] svg { fill: #F8FAFC !important; }

    /* --- TABS BEHAVIOR (SWIPE VS WRAP) --- */
    /* MAIN AREA: Single Row Horizontal Swipe */
    [data-testid="stMainBlockContainer"] div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important; 
        overflow-x: auto !important;   
        -webkit-overflow-scrolling: touch !important; 
        scrollbar-width: none !important; 
        padding-bottom: 4px !important;
    }
    [data-testid="stMainBlockContainer"] div[role="radiogroup"]::-webkit-scrollbar { display: none !important; }
    [data-testid="stMainBlockContainer"] div[role="radiogroup"] label { flex: 0 0 auto !important; }

    [data-testid="stSidebar"] div[role="radiogroup"] {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 6px !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        width: 100% !important; 
        margin: 0 !important;
        padding: 6px 2px !important; 
        justify-content: center !important;
        text-align: center !important;
        background-color: transparent !important;
        border-radius: 999px !important;
        border: 1px solid #475569 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }

    div[role="radiogroup"] label > div:first-child { display: none !important; }
    
    div[role="radiogroup"] label p {
        color: #94A3B8 !important; 
        font-weight: 700 !important;
        font-size: 0.78rem !important; 
        margin: 0 !important;
        white-space: nowrap !important; 
        letter-spacing: -0.02em !important;
    }

    div[role="radiogroup"] label:has(input:checked) {
        background-color: #3B82F6 !important;
        border-color: #3B82F6 !important;
    }
    div[role="radiogroup"] label:has(input:checked) p {
        color: #FFFFFF !important; 
    }
    
    /* --- CARD STYLING --- */
    .particle-card { background: #FFFFFF; border-radius: 20px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); border: 1px solid #F1F5F9; transition: transform 0.25s ease, box-shadow 0.25s ease; height: 380px; display: flex; flex-direction: column; overflow: hidden; margin-bottom: 0px; position: relative; }
    .particle-card:hover { transform: translateY(-5px); box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08); }
    .card-img-area { height: 300px; background-color: #1E293B; background-size: cover; background-position: center; position: relative; display: flex; flex-direction: column; justify-content: flex-end; padding: 20px 24px; }
    .card-img-area::after { content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to top, rgba(0,0,0, 0.9) 0%, rgba(0,0,0, 0.5) 25%, rgba(0,0,0, 0) 45%); z-index: 1; }
    .card-img-content { position: relative; z-index: 2; width: 100%; }
    .card-tag { background: #3B82F6; color: #FFFFFF; font-size: 0.65rem; font-weight: 800; padding: 4px 10px; border-radius: 6px; text-transform: uppercase; letter-spacing: 0.05em; display: inline-block; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
    .card-title { font-size: clamp(1.05rem, 1.15vw, 1.2rem); font-weight: 800; color: #FFFFFF !important; line-height: 1.4; margin: 0; display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; text-shadow: 0 2px 6px rgba(0,0,0,0.9) !important; }
    .card-footer { height: 80px; padding: 12px 24px; background: #FFFFFF; display: flex; flex-direction: column; justify-content: center; }
    
    .source-link-card { padding: 10px 12px; background: transparent; border: 1px solid rgba(148, 163, 184, 0.3); border-radius: 8px; margin-bottom: 8px; transition: all 0.2s ease; cursor: pointer; }
    .source-link-card:hover { border-color: #3B82F6; background-color: rgba(59, 130, 246, 0.05); transform: translateX(2px); }
    
    div[data-testid="stButton"]:has(button[kind="primary"]) { margin: 0 !important; padding: 0 !important; height: 0px !important; min-height: 0px !important; overflow: visible !important; }
    button[kind="primary"] { position: absolute !important; background: transparent !important; border: none !important; color: transparent !important; height: 0px !important; min-height: 0px !important; padding: 0 !important; box-shadow: none !important; }
    button[kind="primary"]::after { content: ""; position: absolute; bottom: 0; left: 0; width: 100%; height: 380px; z-index: 99; cursor: pointer; }
    
    button[kind="secondary"] { background: transparent !important; border: none !important; font-weight: 800 !important; font-size: 0.9rem !important; padding: 0 !important; box-shadow: none !important; display: flex !important; align-items: center !important; justify-content: flex-start !important; width: auto !important; text-transform: uppercase; letter-spacing: 0.05em; }
    
    .b2b-btn { display: block; text-align: center; background: #3B82F6; color: #FFFFFF; padding: 12px; border-radius: 8px; font-size: 0.85rem; font-weight: 700; text-decoration: none; transition: all 0.2s ease; margin-top: 10px; }
    [data-testid="stForm"] { border: none !important; padding: 0 !important; box-shadow: none !important; margin-bottom: 0 !important; }
    
    /* THE PREMIUM INTELLIGENCE BLINDSPOTS BUTTON */
    button[kind="secondary"]:has(div:contains("👁️")) {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%) !important;
        border: 1px solid #334155 !important;
        border-left: 4px solid #EF4444 !important;
        color: #F8FAFC !important;
        justify-content: center !important;
        border-radius: 12px !important;
        padding: 10px !important; 
        margin-top: 0 !important; 
        margin-bottom: 0 !important; 
        box-shadow: 0 8px 16px rgba(0,0,0,0.1) !important;
        transition: all 0.3s ease !important;
    }
    button[kind="secondary"]:has(div:contains("👁️")) p {
        font-size: 1rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.05em !important;
        color: #F8FAFC !important;
    }
    button[kind="secondary"]:has(div:contains("👁️")):hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 20px rgba(0,0,0,0.15) !important;
        border-left: 4px solid #DC2626 !important;
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%) !important;
    }
    
    /* MODAL POLISH: Custom Back Button (Invisible footprint) */
    div[data-testid="stDialog"] div[data-testid="stButton"] button {
        background: transparent !important;
        border: none !important;
        color: #94A3B8 !important;
        padding: 0 !important;
        min-height: 0 !important;
        height: auto !important;
        margin-top: -15px !important;
        margin-bottom: 10px !important;
        font-size: 0.8rem !important;
        transition: color 0.2s ease !important;
    }
    div[data-testid="stDialog"] div[data-testid="stButton"] button:hover { color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

# STANDARD HEADER STYLE FOR CONSISTENCY
SIDEBAR_HEADER_STYLE = "font-size: 0.75rem; font-weight: 800; color: #94A3B8; text-transform: uppercase; margin-bottom: 10px; letter-spacing: 0.05em;"
THIN_DIVIDER = "<div style='height: 1px; background-color: #1E293B; margin: 16px 0;'></div>"

# --- DEEP DIVE MODAL ---
def open_article_modal(row, clean_bullets, perspective_html, src_str, bg_style, t_dict):
    @st.dialog(t_dict.get("modal_title", "Deep Dive"), width="large")
    def render_modal():
        # Sleek text-only back button
        if st.button(t_dict.get("btn_back", "« Back"), key="close_modal_btn"):
            st.session_state.modal_is_open = False
            st.rerun()

        header_col1, header_col2 = st.columns([1, 1.5], gap="small")
        pw = int(float(row.get('avg_pro_western', 0.5)) * 100)
        obj = int(float(row.get('avg_objectivity', 0.5)) * 100) 
        
        # Translate the geography pin dynamically based on dictionary index
        db_geo = row.get('cluster_geo_scope', '')
        geo_idx = UI_TEXT["English"]["geos"].index(db_geo) if db_geo in UI_TEXT["English"]["geos"] else -1
        display_geo_pin = t_dict["geos"][geo_idx] if geo_idx != -1 else db_geo

        spectrum_html = "".join([
            '<div style="background-color: transparent; border: 1px solid rgba(148, 163, 184, 0.3); padding: 12px; border-radius: 12px; margin-top: 4px;">',
            '<div style="font-size: 0.75rem; font-weight: 800; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.05em; opacity: 0.7;">📊 Analiza e Tekstit</div>',
            f'<div style="margin-bottom: 8px;"><div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 700; margin-bottom: 4px;"><span>🇪🇺 Pro-Perëndimit: {pw}%</span></div><div style="width: 100%; height: 6px; background-color: rgba(148, 163, 184, 0.3); border-radius: 999px; display: flex;"><div style="width: {pw}%; background-color: #3B82F6;"></div></div></div>',
            f'<div><div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 700; margin-bottom: 4px;"><span>🔍 Objektiviteti: {obj}%</span></div><div style="width: 100%; height: 6px; background-color: rgba(148, 163, 184, 0.3); border-radius: 999px; display: flex;"><div style="width: {obj}%; background-color: #10B981;"></div></div></div>',
            '</div>'
        ])

        with header_col1:
            st.markdown(f"""<div style="width: 100%; height: 220px; border-radius: 16px; background-color: #1E293B; background-image: {bg_style}; background-size: cover; background-position: center; margin-bottom: 8px;"></div>""", unsafe_allow_html=True)
            st.markdown(f"""<div style="display: flex; gap: 0.5rem;"><span style="background: rgba(148, 163, 184, 0.2); padding: 4px 10px; border-radius: 8px; font-size: 0.75rem; font-weight: 700;">📍 {display_geo_pin}</span></div>""", unsafe_allow_html=True)
            st.markdown(spectrum_html, unsafe_allow_html=True)
            
        with header_col2:
            st.markdown(f"<h3 style='margin-top: 4px; margin-bottom: 8px; font-weight: 800; font-size: 1.4rem; line-height: 1.2;'>{row['cluster_title_sq']}</h3>", unsafe_allow_html=True)
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
                st.markdown(f"<div style='margin-top: 16px; border-top: 1px solid rgba(148, 163, 184, 0.3); padding-top: 12px;'><h4 style='font-size: 0.85rem; font-weight: 800; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.05em; opacity: 0.7;'>Burimet Origjinale</h4>{links_html}</div>", unsafe_allow_html=True)
                
    render_modal()

# --- BLINDSPOTS MODAL ---
@st.dialog("👁️ Të pathënat / Blindspots", width="large")
def open_blindspots_modal(t_dict):
    st.markdown(f"<div style='font-size:0.9rem; opacity: 0.7; margin-bottom: 1.5rem;'>{t_dict.get('blindspots_sub', 'Narratives you might have missed.')}</div>", unsafe_allow_html=True)
    
    for idx, row in get_blindspot_stories().iterrows():
        b_title = row.get('cluster_title_sq') or row.get('title_en') or "Titulli Mungon"
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

if "modal_is_open" not in st.session_state: st.session_state.modal_is_open = False

# --- NATIVE IN-FLOW HEADER ---
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

# Data Fetch & Dedup
df = get_database_data()
if not df.empty:
    df = df[df['title_en'] != "Gabim në përpunim"]
    
# --- SIDEBAR ---
with st.sidebar:
    LANG_OPTIONS = ["🇬🇧 EN", "🇦🇱 SQ", "🇲🇰 MK", "🇷🇸 SR", "🇧🇦 BS"]
    LANG_MAP = {"🇬🇧 EN": "English", "🇦🇱 SQ": "Shqip", "🇲🇰 MK": "Македонски", "🇷🇸 SR": "Srpski", "🇧🇦 BS": "Bosanski"}
    
    # Grab the current language from session state to translate headers before the radio renders
    current_lang_code = st.session_state.get("lang_choice", "🇬🇧 EN")
    current_dict = UI_TEXT[LANG_MAP[current_lang_code]]
    
    st.markdown(f"<div style='{SIDEBAR_HEADER_STYLE}'>{current_dict['lang_header']}</div>", unsafe_allow_html=True)
    
    # Render the radio button once, using the session_state key
    short_lang = st.radio("Lang", LANG_OPTIONS, horizontal=True, label_visibility="collapsed", key="lang_choice")
    t = UI_TEXT[LANG_MAP[short_lang]]
    
    # Reduced spacer
    st.markdown("<hr style='margin: 0.75rem 0; border-color: #1E293B;'/>", unsafe_allow_html=True)
    
    st.markdown(f"<div style='{SIDEBAR_HEADER_STYLE}'>{t['geo_header']}</div>", unsafe_allow_html=True)
    
    display_geo = st.radio("Geo", t["geo_labels"], label_visibility="collapsed")
    geo_index = t["geo_labels"].index(display_geo)
    backend_geo = UI_TEXT["English"]["geos"][geo_index]

    # Reduced spacer
    st.markdown("<hr style='margin: 0.75rem 0; border-color: #1E293B;'/>", unsafe_allow_html=True)
    
    # --- NEWSLETTER INTEGRATION ---
    st.markdown(f"<div style='{SIDEBAR_HEADER_STYLE}'>{t['db_header']}</div>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 0.75rem; color: #94A3B8; margin-bottom: 8px; line-height: 1.3;'>{t['db_sub']}</p>", unsafe_allow_html=True)
    with st.form("newsletter_form", clear_on_submit=True):
        email = st.text_input("Email", placeholder="your@email.com", label_visibility="collapsed")
        submitted = st.form_submit_button(t['subscribe'], use_container_width=True)
        if submitted:
            st.success(t['success'])

    # Reduced spacer
    st.markdown("<hr style='margin: 0.75rem 0; border-color: #1E293B;'/>", unsafe_allow_html=True)

    # --- B2B API INTEGRATION ---
    st.markdown(f"<div style='{SIDEBAR_HEADER_STYLE}'>{t['api_header']}</div>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 0.75rem; color: #94A3B8; margin-bottom: 8px; line-height: 1.3;'>{t['api_sub']}</p>", unsafe_allow_html=True)
    st.markdown(f"<a href='http://localhost:8000/docs' target='_blank' class='b2b-btn' style='margin-top:0;'>{t['api_btn']}</a>", unsafe_allow_html=True)
    
    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

# --- MAIN INTERFACE ---
# Category Selector
display_cat = st.radio("Topics", t["topics"], horizontal=True, label_visibility="collapsed")
cat_index = t["topics"].index(display_cat)
backend_cat = UI_TEXT["English"]["topics"][cat_index]

# Blindspots Button
if st.button(f"👁️ {t.get('blindspots')} (3)", type="secondary", use_container_width=True):
    open_blindspots_modal(t)

# Negative margin to pull the grid up to the button
st.markdown("<div style='margin-top: -12px;'></div>", unsafe_allow_html=True)

# Filtering Logic
filtered_df = df.copy()

if backend_geo != "All Regions": 
    target_geo = backend_geo.strip().lower()
    filtered_df = filtered_df[filtered_df['cluster_geo_scope'].apply(lambda x: target_geo in str(x).strip().lower())]
    
if backend_cat != "All Topics": 
    target_cat = backend_cat.strip().lower()
    filtered_df = filtered_df[filtered_df['cluster_category'].apply(lambda x: target_cat in str(x).strip().lower())]

# Main News Grid
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
        clean_b = [b.strip().lstrip('-*• ') for b in raw_b.split('\n') if b.strip() and len(b) > 15]
        
        persp_text = row.get(col_persp) or row.get('perspective_en') or ""
        persp = f"<div style='padding: 12px; border-left: 3px solid #3B82F6; font-size: 0.9rem; font-style: italic; border-radius: 0 8px 8px 0; opacity: 0.85;'>{persp_text}</div>" if persp_text else ""
        
        raw_img = str(row.get('cluster_image', '')).strip()
        unique_seed = row.get('cluster_id', f"rand_{idx}")
        fallback = f"https://picsum.photos/seed/{unique_seed}/800/500"
        
        if pd.isna(row.get('cluster_image')) or raw_img in ('None', 'nan', '') or not raw_img.startswith('http'):
            bg = f"url('{fallback}')"
        else:
            bg = f"url('{raw_img}'), url('{fallback}')"

        pw = int(float(row.get('avg_pro_western', 0.5)) * 100)
        obj = int(float(row.get('avg_objectivity', 0.5)) * 100)

        with (grid_col1 if idx % 2 == 0 else grid_col2):
            card_html = "".join([
                '<div class="particle-card">',
                f'<div class="card-img-area" style="background-image: {bg};">',
                    '<div class="card-img-content">',
                        f'<span class="card-tag">{row.get("cluster_category", "News")}</span>',
                        f'<div class="card-title">{display_title}</div>',
                    '</div>',
                '</div>',
                '<div class="card-footer">',
                    '<div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 700; color: #475569; margin-bottom: 6px;">',
                        f'<span>🇪🇺 {t.get("pw", "Pro-Western")}: <span style="color:#0F172A;">{pw}%</span></span>',
                        f'<span>🔍 {t.get("obj", "Objectivity")}: <span style="color:#0F172A;">{obj}%</span></span>',
                    '</div>',
                    '<div style="width: 100%; height: 6px; background-color: #E2E8F0; border-radius: 999px; display: flex;">',
                        f'<div style="width: {pw}%; background: linear-gradient(90deg, #3B82F6, #10B981);"></div>',
                    '</div>',
                '</div>',
                '</div>'
            ])
            st.markdown(card_html, unsafe_allow_html=True)
            
            if st.button(" ", key=f"btn_{row.get('cluster_id', idx)}", type="primary", use_container_width=True):
                row_dict = row.to_dict()
                row_dict['cluster_title_sq'] = display_title 
                open_article_modal(row_dict, clean_b, persp, "", bg, t)
            
            st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)