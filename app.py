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
        "geo_header": "📍 Region",
        "blindspots": "👁️ Blindspots",
        "blindspots_sub": "Narratives you might have missed.",
        "pw": "Pro-Western",
        "obj": "Objectivity",
        "div": "Divergence Level",
        "btn_back": "← Go Back",
        "db_col_title": "title_en",
        "db_col_bullets": "bullets_en",
        "db_col_persp": "perspective_en"
    },
    "Shqip": {
        "topics": ["Të gjitha", "Politikë", "Ekonomi", "Infrastrukturë", "Teknologji", "Kulturë", "Show Biz"],
        "geos": ["Të gjitha", "Maqedonia e Veriut", "Kosova", "Shqipëria", "Rajonale", "Ndërkombëtare"],
        "geo_header": "📍 Rajoni",
        "blindspots": "👁️ Të pathënat",
        "blindspots_sub": "Lajme ndoshta të anashkaluara.",
        "pw": "Pro-Perëndimit",
        "obj": "Objektiviteti",
        "div": "Anashkalimi",
        "btn_back": "← Kthehu",
        "db_col_title": "title_sq",
        "db_col_bullets": "bullets_sq",
        "db_col_persp": "perspective_en" # Using EN perspective until translated
    },
    "Македонски": {
        "topics": ["Сите Теми", "Политика", "Економија", "Инфраструктура", "Технологија", "Култура", "Забава"],
        "geos": ["Сите Региони", "Северна Македонија", "Косово", "Албанија", "Регионално", "Меѓународно"],
        "geo_header": "📍 Регион",
        "blindspots": "👁️ Слепи точки",
        "blindspots_sub": "Наративи што можеби сте ги пропуштиле.",
        "pw": "Про-Западно",
        "obj": "Објективност",
        "div": "Дивергенција",
        "btn_back": "← Назад",
        "db_col_title": "title_mk",
        "db_col_bullets": "bullets_en", # Using EN bullets until translated
        "db_col_persp": "perspective_en"
    },
    "Srpski/Bosanski": {
        "topics": ["Sve Teme", "Politika", "Ekonomija", "Infrastruktura", "Tehnologija", "Kultura", "Zabava"],
        "geos": ["Svi Regioni", "Severna Makedonija", "Kosovo", "Albanija", "Regionalno", "Međunarodno"],
        "geo_header": "📍 Region",
        "blindspots": "👁️ Slepe tačke",
        "blindspots_sub": "Narativi koje ste možda propustili.",
        "pw": "Pro-Zapadno",
        "obj": "Objektivnost",
        "div": "Divergencija",
        "btn_back": "← Nazad",
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
    # Përdorim kolonat e reja shumëgjuhëshe
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
        return pd.DataFrame() # Kthim i sigurt nëse databaza mungon
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
    [data-testid="stSidebar"][aria-expanded="true"] { min-width: 215px !important; max-width: 215px !important; }
    /* --- SIDEBAR DARK MODE FIX --- */
    [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B !important; }
    /* Force every text element in the sidebar to be visible */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label { 
        color: #F8FAFC !important; 
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #94A3B8 !important; }

    /* --- MOBILE SWIPEABLE TABS (PILLS) --- */
    /* Force the container to stay on one line and scroll horizontally */
    div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important; 
        overflow-x: auto !important;   
        -webkit-overflow-scrolling: touch !important; 
        gap: 12px !important;
        padding-bottom: 12px !important; 
        scrollbar-width: none !important; 
    }
    div[role="radiogroup"]::-webkit-scrollbar { display: none !important; }

    /* Style the individual pill */
    div[role="radiogroup"] label {
        background-color: transparent !important;
        padding: 8px 18px !important;
        border-radius: 999px !important;
        border: 1px solid #475569 !important;
        white-space: nowrap !important; 
        cursor: pointer !important;
        color: #94A3B8 !important; /* Make the base text light gray */
        transition: all 0.2s ease !important;
    }

    /* Hide the default radio circle */
    div[role="radiogroup"] label div:first-child { display: none !important; }

    /* FORCE the text inside the pill to be visible */
    div[role="radiogroup"] label * {
        color: inherit !important; 
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        margin: 0 !important;
    }

    /* Active/Selected Pill State - Make it pop! */
    div[role="radiogroup"] label:has(input:checked) {
        background-color: #3B82F6 !important;
        border-color: #3B82F6 !important;
        color: #FFFFFF !important; /* Force text to pure white when active */
    }
    [data-testid="stSidebar"] label { white-space: nowrap !important; }
    .particle-card { background: #FFFFFF; border-radius: 20px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); border: 1px solid #F1F5F9; transition: transform 0.25s ease, box-shadow 0.25s ease; height: 380px; display: flex; flex-direction: column; overflow: hidden; margin-bottom: 0px; position: relative; }
    .particle-card:hover { transform: translateY(-5px); box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08); }
    .card-img-area { height: 300px; background-color: #1E293B; background-size: cover; background-position: center; position: relative; display: flex; flex-direction: column; justify-content: flex-end; padding: 20px 24px; }
    .card-img-area::after { content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to top, rgba(0,0,0, 0.9) 0%, rgba(0,0,0, 0.5) 25%, rgba(0,0,0, 0) 45%); z-index: 1; }
    .card-img-content { position: relative; z-index: 2; width: 100%; }
    .card-tag { background: #3B82F6; color: #FFFFFF; font-size: 0.65rem; font-weight: 800; padding: 4px 10px; border-radius: 6px; text-transform: uppercase; letter-spacing: 0.05em; display: inline-block; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
    .card-title { font-size: clamp(1.05rem, 1.15vw, 1.2rem); font-weight: 800; color: #FFFFFF !important; line-height: 1.4; margin: 0; display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; text-shadow: 0 2px 6px rgba(0,0,0,0.9) !important; }
    .card-footer { height: 80px; padding: 12px 24px; background: #FFFFFF; display: flex; flex-direction: column; justify-content: center; }
    .source-link-card { padding: 10px 12px; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; margin-bottom: 8px; transition: all 0.2s ease; cursor: pointer; }
    .source-link-card:hover { border-color: #3B82F6; background-color: #F8FAFC; transform: translateX(2px); }
    div[data-testid="stButton"]:has(button[kind="primary"]) { margin: 0 !important; padding: 0 !important; height: 0px !important; min-height: 0px !important; overflow: visible !important; }
    button[kind="primary"] { position: absolute !important; background: transparent !important; border: none !important; color: transparent !important; height: 0px !important; min-height: 0px !important; padding: 0 !important; box-shadow: none !important; }
    button[kind="primary"]::after { content: ""; position: absolute; bottom: 0; left: 0; width: 100%; height: 380px; z-index: 99; cursor: pointer; }
    button[kind="secondary"] { background: transparent !important; border: none !important; color: #64748B !important; font-weight: 800 !important; font-size: 0.9rem !important; padding: 0 !important; box-shadow: none !important; display: flex !important; align-items: center !important; justify-content: flex-start !important; width: auto !important; margin-bottom: 1.5rem !important; text-transform: uppercase; letter-spacing: 0.05em; }
    button[kind="secondary"]:hover { color: #0F172A !important; }
    .b2b-btn { display: block; text-align: center; background: #3B82F6; color: #FFFFFF; padding: 12px; border-radius: 8px; font-size: 0.85rem; font-weight: 700; text-decoration: none; transition: all 0.2s ease; margin-top: 15px; }
    .b2b-btn:hover { background: #2563EB; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4); }
    [data-testid="stForm"] { border: none !important; padding: 0 !important; box-shadow: none !important; }
</style>
""", unsafe_allow_html=True)

# --- DEEP DIVE MODAL ---
@st.dialog("Full Coverage & Perspective Mapping", width="large")
def open_article_modal(row, clean_bullets, perspective_html, src_str, bg_style):
    if st.button("← Kthehu", type="secondary"):
        st.session_state.modal_is_open = False
        st.rerun()

    header_col1, header_col2 = st.columns([1, 1.5], gap="large")
    pw = int(float(row.get('avg_pro_western', 0.5)) * 100)
    obj = int(float(row.get('avg_objectivity', 0.5)) * 100) 
    
    spectrum_html = "".join([
        '<div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 16px; border-radius: 12px; margin-top: 12px;">',
        '<div style="font-size: 0.75rem; font-weight: 800; color: #64748B; text-transform: uppercase; margin-bottom: 12px; letter-spacing: 0.05em;">📊 Analiza e Tekstit</div>',
        f'<div style="margin-bottom: 12px;"><div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 700; color: #334155; margin-bottom: 6px;"><span>🇪🇺 Pro-Perëndimit: {pw}%</span></div><div style="width: 100%; height: 8px; background-color: #E2E8F0; border-radius: 999px; display: flex;"><div style="width: {pw}%; background-color: #3B82F6;"></div></div></div>',
        f'<div><div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 700; color: #334155; margin-bottom: 6px;"><span>🔍 Objektiviteti: {obj}%</span></div><div style="width: 100%; height: 8px; background-color: #E2E8F0; border-radius: 999px; display: flex;"><div style="width: {obj}%; background-color: #10B981;"></div></div></div>',
        '</div>'
    ])

    with header_col1:
        st.markdown(f"""<div style="width: 100%; height: 220px; border-radius: 16px; background-color: #1E293B; background-image: {bg_style}; background-size: cover; background-position: center; margin-bottom: 12px;"></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div style="display: flex; gap: 0.5rem;"><span style="background: #F1F5F9; color: #475569; padding: 4px 10px; border-radius: 8px; font-size: 0.75rem; font-weight: 700;">📍 {row['cluster_geo_scope']}</span></div>""", unsafe_allow_html=True)
        st.markdown(spectrum_html, unsafe_allow_html=True)
        
    with header_col2:
        st.markdown(f"<h3 style='margin-top: 0; margin-bottom: 16px; color: #0F172A; font-weight: 800; font-size: 1.6rem; line-height: 1.2;'>{row['cluster_title_sq']}</h3>", unsafe_allow_html=True)
        if clean_bullets:
            for b in clean_bullets[:4]: 
                st.markdown(f"<div style='margin-bottom: 10px; color: #334155; font-size: 0.95rem; line-height: 1.5;'>• {b}</div>", unsafe_allow_html=True)
        if perspective_html: 
            st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
            st.markdown(perspective_html, unsafe_allow_html=True)

        titles = str(row.get('orig_titles', '')).split("||")
        urls = str(row.get('orig_urls', '')).split("||")
        sources_raw = str(row.get('sources', '')).split(", ")

        seen, links_html = set(), ""
        for t, s, u in zip(titles, sources_raw, urls):
            if t and t not in seen and u and str(u).startswith('http'):
                seen.add(t)
                links_html += f"<a href='{u}' target='_blank' style='text-decoration: none;'><div class='source-link-card'><div style='font-size: 0.7rem; color: #3B82F6; font-weight: 800; text-transform: uppercase; margin-bottom: 4px; letter-spacing: 0.05em;'>🔗 {s}</div><div style='font-size: 0.85rem; font-weight: 600; color: #0F172A; line-height: 1.3;'>{t}</div></div></a>"
                
        if links_html:
            st.markdown(f"<div style='margin-top: 24px; border-top: 1px solid #E2E8F0; padding-top: 16px;'><h4 style='font-size: 0.85rem; font-weight: 800; color: #64748B; text-transform: uppercase; margin-bottom: 12px; letter-spacing: 0.05em;'>Burimet Origjinale</h4>{links_html}</div>", unsafe_allow_html=True)
            
    st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

if "modal_is_open" not in st.session_state: st.session_state.modal_is_open = False

# --- NATIVE IN-FLOW HEADER ---
# We use Streamlit columns to build a dynamic top navigation bar
top_col1, top_col2, top_col3 = st.columns([1.5, 2, 1], gap="medium", vertical_alignment="center")

with top_col1:
    st.markdown("""
    <div style="font-size: 1.8rem; font-weight: 800; color: #0F172A; letter-spacing: -0.05em; padding-left: 10px; padding-top: 0.2rem;">
        <span style="color: #3B82F6;">Balkan</span>Intel
    </div>
    """, unsafe_allow_html=True)

with top_col2:
    st.markdown("""
    <div style="display: flex; gap: 2rem; font-size: 0.95rem; font-weight: 600; color: #475569; justify-content: center; padding-top: 0.6rem;">
        <a href="#" style="color: inherit; text-decoration: none;">Daily Briefing</a>
        <a href="#" style="color: inherit; text-decoration: none;">API Developers</a>
    </div>
    """, unsafe_allow_html=True)

with top_col3:
    # Dictionary mapping for modern short codes
    LANG_MAP = {"EN": "English", "SQ": "Shqip", "MK": "Македонски", "SR": "Srpski/Bosanski"}
    
    st.markdown("<div style='padding-top: 0.6rem;'></div>", unsafe_allow_html=True)
    # The radio buttons will now automatically style themselves as swipeable pills thanks to our CSS!
    short_lang = st.radio("Lang", ["EN", "SQ", "MK", "SR"], horizontal=True, label_visibility="collapsed")
    
    selected_lang = LANG_MAP[short_lang]
    t = UI_TEXT[selected_lang] # Load the dictionary immediately
st.markdown("<hr style='margin-top: 0.5rem; margin-bottom: 1rem; border-color: #E2E8F0;'/>", unsafe_allow_html=True)
# Data Fetch & Dedup
df = get_database_data()
if not df.empty:
    # FILTRI BAZË: Hide only failed translations
    df = df[df['title_en'] != "Gabim në përpunim"]
    
# --- SIDEBAR ---
with st.sidebar:
    # 1. Dynamic Region Filter
    st.markdown(f"<h3 style='color: #0F172A; font-weight: 800; margin-top: -10px;'>{t['geo_header']}</h3>", unsafe_allow_html=True)
    
    # We display the localized names, but map the selection back to the English backend string
    display_geo = st.radio("Geo", t["geos"], label_visibility="collapsed")
    
    geo_index = t["geos"].index(display_geo)
    backend_geo = UI_TEXT["English"]["geos"][geo_index]
        
    st.markdown("---")
        
    with st.expander(t.get("ai_explanation_title", "ℹ️ How AI Analysis Works")):
        st.markdown("""
        <div style='font-size: 0.8rem; color: #475569; line-height: 1.5;'>
            Kjo platformë përdor modele të avancuara të gjuhës (LLM) për të vlerësuar përmbajtjen përmes analizës sasiore të tekstit:
            <br><br>
            <b>• Objektiviteti:</b> Mat mungesën e gjuhës së ngarkuar emocionalisht ose sensacionale, duke favorizuar raportimin neutral.
            <br><br>
            <b>• Anashkalimi (Blindspot):</b> Vlerëson divergjencën e narrativës. Ndërton një metrikë bazuar në atë se sa ndryshon këndvështrimi i artikullit nga rryma kryesore mediatike në Ballkan.
        </div>
        """, unsafe_allow_html=True)
# --- MAIN INTERFACE ---
main_col, sidebar_col = st.columns([2.5, 1], gap="large")

with main_col:
    # 1. Dynamic Multilingual Category Selector
    display_cat = st.radio("Topics", t["topics"], horizontal=True, label_visibility="collapsed")
    
    # Map the selected category back to English for safe database filtering
    cat_index = t["topics"].index(display_cat)
    backend_cat = UI_TEXT["English"]["topics"][cat_index]
    
    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # --- SIMULATOR WIDGET ---
    with st.expander("🎛️ Simulatori i Parametrave të AI (Live Demo)"):
        st.markdown("<div style='font-size: 0.85rem; color: #64748B; margin-bottom: 1rem;'>Ky panel demonstron heuristikën që përdor LLM për të llogaritur metrikat. Ndryshoni vlerat për të parë si ndikohet rezultati përfundimtar i një lajmi hipotetik.</div>", unsafe_allow_html=True)
        
        sim_col1, sim_col2 = st.columns(2, gap="large")
        with sim_col1:
            st.markdown("**1. Metrika e Objektivitetit**")
            fakte = st.slider("Prania e fakteve dhe burimeve", 0, 100, 80)
            emocion = st.slider("Gjuha sensacionale/emocionale", 0, 100, 20)
            obj_score = int((fakte + (100 - emocion)) / 2)
            st.markdown(f"""<div style="margin-top: 10px; padding: 10px; background-color: #F8FAFC; border-radius: 8px; border-left: 4px solid #10B981;"><div style="font-size: 0.8rem; color: #475569; font-weight: 600;">Rezultati Përfundimtar</div><div style="font-size: 1.5rem; font-weight: 800; color: #0F172A;">{obj_score}%</div></div>""", unsafe_allow_html=True)

        with sim_col2:
            st.markdown("**2. Metrika Pro-Perëndimore**")
            euro = st.slider("Gjuha pro-Integrimit (BE/NATO)", 0, 100, 70)
            anti_west = st.slider("Narrativa Anti-Perëndimore", 0, 100, 10)
            pw_score = int((euro + (100 - anti_west)) / 2)
            st.markdown(f"""<div style="margin-top: 10px; padding: 10px; background-color: #F8FAFC; border-radius: 8px; border-left: 4px solid #3B82F6;"><div style="font-size: 0.8rem; color: #475569; font-weight: 600;">Rezultati Përfundimtar</div><div style="font-size: 1.5rem; font-weight: 800; color: #0F172A;">{pw_score}%</div></div>""", unsafe_allow_html=True)
            
    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
    # --- END SIMULATOR WIDGET ---

    filtered_df = df.copy()

    # --- THE FIX: SAFE MULTILINGUAL FILTERS ---
    if backend_geo != "All Regions": 
        target_geo = backend_geo.strip().lower()
        filtered_df = filtered_df[filtered_df['cluster_geo_scope'].apply(lambda x: target_geo in str(x).strip().lower())]
        
    if backend_cat != "All Topics": 
        target_cat = backend_cat.strip().lower()
        filtered_df = filtered_df[filtered_df['cluster_category'].apply(lambda x: target_cat in str(x).strip().lower())]

    # System Status display
    st.caption(f"🔍 System Status: {len(filtered_df)} articles found for [{display_geo}] & [{display_cat}].")

    if filtered_df.empty:
        st.warning(t.get("empty_state", "No articles found matching this region and category."))
    else:
        grid_col1, grid_col2 = st.columns(2, gap="medium")
        for idx, row in filtered_df.reset_index(drop=True).iterrows():
            # 1. Fetch dynamic column names based on the selected language
            col_title = t.get("db_col_title", "title_en")
            col_bullets = t.get("db_col_bullets", "bullets_en")
            col_persp = t.get("db_col_persp", "perspective_en")
            
            # 2. Safely get text with English fallbacks if a translation is missing
            display_title = row.get(col_title) or row.get('title_en') or "Title Missing"
            
            raw_b = str(row.get(col_bullets) or row.get('bullets_en') or "").split("||")[0]
            clean_b = [b.strip().lstrip('-*• ') for b in raw_b.split('\n') if b.strip() and len(b) > 15]
            
            persp_text = row.get(col_persp) or row.get('perspective_en') or ""
            persp = f"<div style='padding: 12px; background: #F8FAFC; border-left: 3px solid #3B82F6; font-size: 0.9rem; color: #475569; font-style: italic; border-radius: 0 8px 8px 0;'>{persp_text}</div>" if persp_text else ""
            
            # 3. Dynamic Unique Image Placeholder
            raw_img = str(row.get('cluster_image', '')).strip()
            unique_seed = row.get('cluster_id', f"rand_{idx}")
            fallback = f"https://picsum.photos/seed/{unique_seed}/800/500"
            
            if pd.isna(row.get('cluster_image')) or raw_img in ('None', 'nan', '') or not raw_img.startswith('http'):
                bg = f"url('{fallback}')"
            else:
                bg = f"url('{raw_img}'), url('{fallback}')"

            # 4. Metrics
            pw = int(float(row.get('avg_pro_western', 0.5)) * 100)
            obj = int(float(row.get('avg_objectivity', 0.5)) * 100)

            # 5. Render the News Card
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
                
                # Render the hidden button for the Deep Dive Modal
                if st.button(" ", key=f"btn_{row.get('cluster_id', idx)}", type="primary", use_container_width=True):
                    # We inject the translated title so the modal doesn't break
                    row_dict = row.to_dict()
                    row_dict['cluster_title_sq'] = display_title 
                    open_article_modal(row_dict, clean_b, persp, "", bg)
                
                st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
with sidebar_col:
    st.markdown("### 👁️ Të pathënat")
    st.markdown("<span style='font-size:0.9rem; color:#64748B;'>Lajme ndoshta të anashkaluara.</span>", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
    
    for idx, row in get_blindspot_stories().iterrows():
        raw_score = row.get('narrative_divergence_score', row.get('narrative_ethno_nationalist', 0.5))
        try:
            val_float = float(raw_score)
            divergence_val = int(val_float * 100) if val_float <= 1.0 else int(val_float)
        except Exception:
            divergence_val = 50 
            
        display_title = row.get('cluster_title_sq') or row.get('cluster_title') or row.get('original_title') or row.get('title') or "Titulli Mungon"
            
        # Rreshtat brenda f\"\"\" janë shtyrë qëllimisht majtas për të shmangur Markdown Code Block
        st.markdown(f"""
<div style='background: #FFFFFF; padding: 1.2rem; border-radius: 12px; border: 1px solid #F1F5F9; border-left: 3px solid #EF4444; margin-bottom: 1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.02);'>
    <div style='font-size: 0.7rem; font-weight: 800; color: #EF4444; text-transform: uppercase; margin-bottom: 6px;'>{row.get('cluster_category', 'Tjetër')}</div>
    <a href="{row.get('original_url', '#')}" target="_blank" style="text-decoration: none;">
        <div style='font-weight: 700; color: #1E293B; font-size: 0.95rem; line-height: 1.4; margin-bottom: 8px;'>
            {display_title} <span style="color: #3B82F6; font-size: 0.8rem;">↗</span>
        </div>
    </a>
    <div style='font-size: 0.8rem; font-weight: 600; color: #64748B;'>Niveli i anashkalimit: <span style='color:#0F172A;'>{divergence_val}%</span></div>
</div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    st.markdown("""
        <div style='background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); padding: 1.5rem; border-radius: 16px; color: #FFFFFF; box-shadow: 0 10px 25px rgba(0,0,0,0.1); position: relative; overflow: hidden;'>
            <div style='position: absolute; top: -20px; right: -20px; font-size: 6rem; opacity: 0.05;'>⚙️</div>
            <div style='font-size: 0.75rem; font-weight: 800; color: #3B82F6; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.05em;'>Enterprise Solutions</div>
            <h4 style='margin: 0 0 10px 0; font-size: 1.1rem; font-weight: 800; color: #FFFFFF;'>BalkanIntel API</h4>
            <p style='font-size: 0.85rem; color: #94A3B8; line-height: 1.5; margin-bottom: 0px;'>Integrate real-time narrative clustering directly into your dashboards.</p>
            <a href="http://localhost:8000/docs" target="_blank" class="b2b-btn">View API Docs</a>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("""
        <div style='background: #FFFFFF; padding: 1.5rem 1.5rem 0.5rem 1.5rem; border-radius: 16px 16px 0 0; border: 1px solid #E2E8F0; border-bottom: none; text-align: center;'>
            <div style='font-size: 1.8rem; margin-bottom: 8px;'>📬</div>
            <h4 style='margin: 0 0 8px 0; font-size: 1.05rem; font-weight: 800; color: #0F172A;'>Daily Briefing</h4>
            <p style='font-size: 0.8rem; color: #64748B; margin-bottom: 0; line-height: 1.4;'>Narrative blindspots delivered straight to your inbox.</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div style='background: #FFFFFF; padding: 0 1.5rem 1.5rem 1.5rem; border-radius: 0 0 16px 16px; border: 1px solid #E2E8F0; border-top: none; text-align: center;'>", unsafe_allow_html=True)
        with st.form("newsletter_form", clear_on_submit=True):
            email = st.text_input("Email", placeholder="your@email.com", label_visibility="collapsed")
            submitted = st.form_submit_button("Abonohu (Subscribe)", use_container_width=True)
            if submitted:
                st.success("Faleminderit! You are subscribed.")
        st.markdown("</div>", unsafe_allow_html=True)