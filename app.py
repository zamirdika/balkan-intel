import streamlit as st
import sqlite3
import pandas as pd

# --- UI TRANSLATION DICTIONARY ---
UI_TEXT = {
    "English": {
        "nav_home": "🏠 Home", "nav_search": "🔍 Search", "nav_lang": "🌐 Lang & Geo",
        "topics": ["All Topics", "Politics", "Economy", "Technology", "Culture", "Entertainment", "Sports", "Crime & Accidents"],
        "geos": ["All Regions", "North Macedonia", "Kosovo", "Albania", "Serbia", "Bosnia and Herzegovina", "Montenegro", "Regional"],
        "geo_labels": ["🌍 Global", "🇲🇰 MKD", "🇽🇰 KOS", "🇦🇱 ALB", "🇷🇸 SRB", "🇧🇦 BIH", "🇲🇪 MNE", "🗺️ Balkans"],
        "lang_header": "Language Settings", "geo_header": "Region Focus",
        "search_label": "Search narratives, topics, or keywords...",
        "filter_cat": "Categories",
        "blindspots_btn": "👁️ Blindspots", "blindspots": "Strategic Blindspots", 
        "blindspots_sub": "Regional narratives and crucial information updates you might have missed.",
        "modal_title": "Deep Dive Analysis", "pw": "Pro-Western", "obj": "Objectivity", "btn_back": "Close",
        "sources": "Original Sources", "analysis_title": "Narrative Summary",
        "pw_help": "Measures alignment with EU/US/NATO geopolitical positions.",
        "obj_help": "Measures factual reporting vs. emotional or biased language.",
        "divergence": "Divergence",
        "div_help": "Measures how much this story is omitted or selectively framed compared to the regional baseline.",
        "read_source": "Read Original ↗",
        "db_col_title": "title_en", "db_col_bullets": "bullets_en", "db_col_persp": "perspective_en"
    },
    "Shqip": {
        "nav_home": "🏠 Kryefaqja", "nav_search": "🔍 Kërko", "nav_lang": "🌐 Gjuha & Rajoni",
        "topics": ["Të gjitha", "Politikë", "Ekonomi", "Teknologji", "Kulturë", "Show Biz", "Sport", "Kronika e Zezë"],
        "geos": ["Të gjitha", "Maqedonia e Veriut", "Kosova", "Shqipëria", "Serbia", "Bosnja dhe Hercegovina", "Mali i Zi", "Rajonale"],
        "geo_labels": ["🌍 Global", "🇲🇰 MKD", "🇽🇰 KOS", "🇦🇱 ALB", "🇷🇸 SRB", "🇧🇦 BIH", "🇲🇪 MNE", "🗺️ Ballkan"],
        "lang_header": "Gjuha", "geo_header": "Fokusi Rajonal",
        "search_label": "Kërko narrativa, tema ose fjalë kyçe...",
        "filter_cat": "Kategoritë",
        "blindspots_btn": "👁️ Të pathënat", "blindspots": "Të pathënat Strategjike", 
        "blindspots_sub": "Narrativa rajonale strategjike dhe informacione jetike që mund t'i keni anashkaluar.",
        "modal_title": "Analiza e Thelluar", "pw": "Pro-Perëndimor", "obj": "Objektiviteti", "btn_back": "Mbyll",
        "sources": "Burimet Origjinale", "analysis_title": "Përmbledhja e Narrativës",
        "pw_help": "Mat përafrimin me qëndrimet gjeopolitike të BE/SHBA/NATO-s.",
        "obj_help": "Mat raportimin faktik kundrejt gjuhës emocionale apo të anashme.",
        "divergence": "Divergjenca",
        "div_help": "Mat shkallën në të cilën kjo ngjarje anashkalohet ose kornizohet në mënyrë selektive.",
        "read_source": "Lexo Origjinalin ↗",
        "db_col_title": "title_sq", "db_col_bullets": "bullets_sq", "db_col_persp": "perspective_sq"
    },
    "Македонски": {
        "nav_home": "🏠 Дома", "nav_search": "🔍 Пребарај", "nav_lang": "🌐 Јазик и Регион",
        "topics": ["Сите Теми", "Политика", "Економија", "Технологија", "Култура", "Забава", "Спорт", "Црна Хроника"],
        "geos": ["Сите Региони", "Северна Македонија", "Косово", "Албанија", "Србија", "Босна и Херцеговина", "Црна Гора", "Регионално"],
        "geo_labels": ["🌍 Глобално", "🇲🇰 MKD", "🇽🇰 KOS", "🇦🇱 ALB", "🇷🇸 SRB", "🇧🇦 BIH", "🇲🇪 MNE", "🗺️ Балкан"],
        "lang_header": "Јазик", "geo_header": "Регионален Фокус",
        "search_label": "Пребарајте наративи, теми или клучни зборови...",
        "filter_cat": "Категории",
        "blindspots_btn": "👁️ Игнорирани", "blindspots": "Игнорирани вести", 
        "blindspots_sub": "Регионални наративи и клучни информации кои можеби целосно сте ги пропуштиле.",
        "modal_title": "Длабинска Анализа", "pw": "Про-Западно", "obj": "Објективност", "btn_back": "Затвори",
        "sources": "Оригинални Извори", "analysis_title": "Наративно Резиме",
        "pw_help": "Го мери усогласувањето со геополитичките позиции на ЕУ/САД/НАТО.",
        "obj_help": "Го мери фактуелното известување наспроти емотивниот или пристрасен јазик.",
        "divergence": "Дивергенција",
        "div_help": "Мери колку оваа вест е изоставена или селективно врамена во споредба со регионалниот просек.",
        "read_source": "Оригинален Напис ↗",
        "db_col_title": "title_mk", "db_col_bullets": "bullets_mk", "db_col_persp": "perspective_mk"
    },
    "Srpski": {
        "nav_home": "🏠 Početna", "nav_search": "🔍 Pretraga", "nav_lang": "🌐 Jezik i Region",
        "topics": ["Sve Teme", "Politika", "Ekonomija", "Tehnologija", "Kultura", "Zabava", "Sport", "Crna Hronika"],
        "geos": ["Svi Regioni", "Severna Makedonija", "Kosovo", "Albanija", "Srbija", "Bosna i Hercegovina", "Crna Gora", "Regionalno"],
        "geo_labels": ["🌍 Globalno", "🇲🇰 MKD", "🇽🇰 KOS", "🇦🇱 ALB", "🇷🇸 SRB", "🇧🇦 BIH", "🇲🇪 MNE", "🗺️ Balkan"],
        "lang_header": "Jezik", "geo_header": "Regionalni Fokus",
        "search_label": "Pretraži narative, teme ili ključne reči...",
        "filter_cat": "Kategorije",
        "blindspots_btn": "👁️ Slepe tačke", "blindspots": "Slepe tačke", 
        "blindspots_sub": "Narativi koje ste možda propustili.",
        "modal_title": "Dubinska Analiza", "pw": "Pro-Zapadno", "obj": "Objektivnost", "btn_back": "Zatvori",
        "sources": "Originalni Izvori", "analysis_title": "Narativni Sažetak",
        "pw_help": "Meri usklađenost sa geopolitičkim pozicijama EU/SAD/NATO.",
        "obj_help": "Meri činjenično izveštavanje naspram emotivnog ili pristrasnog jezika.",
        "divergence": "Divergencija", "div_help": "Meri koliko je ova vest izostavljena u poređenju sa regionom.",
        "read_source": "Pročitaj Original ↗",
        "db_col_title": "title_sr", "db_col_bullets": "bullets_sr", "db_col_persp": "perspective_sr"
    },
    "Bosanski": {
        "nav_home": "🏠 Početna", "nav_search": "🔍 Pretraga", "nav_lang": "🌐 Jezik i Region",
        "topics": ["Sve Teme", "Politika", "Ekonomija", "Tehnologija", "Kultura", "Zabava", "Sport", "Crna Hronika"],
        "geos": ["Svi Regioni", "Sjeverna Makedonija", "Kosovo", "Albanija", "Srbija", "Bosna i Hercegovina", "Crna Gora", "Regionalno"],
        "geo_labels": ["🌍 Globalno", "🇲🇰 MKD", "🇽🇰 KOS", "🇦🇱 ALB", "🇷🇸 SRB", "🇧🇦 BIH", "🇲🇪 MNE", "🗺️ Balkan"],
        "lang_header": "Jezik", "geo_header": "Regionalni Fokus",
        "search_label": "Pretraži narative, teme ili ključne riječi...",
        "filter_cat": "Kategorije",
        "blindspots_btn": "👁️ Slijepe tačke", "blindspots": "Slijepe tačke", 
        "blindspots_sub": "Narativi koje ste možda propustili.",
        "modal_title": "Dubinska Analiza", "pw": "Pro-Zapadno", "obj": "Objektivnost", "btn_back": "Zatvori",
        "sources": "Originalni Izvori", "analysis_title": "Narativni Sažetak",
        "pw_help": "Mjeri usklađenost sa geopolitičkim pozicijama EU/SAD/NATO.",
        "obj_help": "Mjeri činjenično izvještavanje naspram emotivnog ili pristrasnog jezika.",
        "divergence": "Divergencija", "div_help": "Mjeri koliko je ova vijest izostavljena u poređenju sa regionom.",
        "read_source": "Pročitaj Original ↗",
        "db_col_title": "title_sr", "db_col_bullets": "bullets_sr", "db_col_persp": "perspective_sr"
    }
}

# --- STATE MANAGEMENT ---
if 'lang_code' not in st.session_state: st.session_state.lang_code = "English"
if 'active_cat' not in st.session_state: st.session_state.active_cat = "All Topics"
if 'active_geo' not in st.session_state: st.session_state.active_geo = "All Regions"
if 'search_query' not in st.session_state: st.session_state.search_query = ""

# --- DATABASE FETCH FUNCTIONS ---
def get_connection(): return sqlite3.connect('news_aggregator.db')
def get_database_data():
    conn = get_connection()
    query = """
        SELECT cluster_id, cluster_category, cluster_geo_scope,
               MAX(title_en) as title_en, MAX(title_sq) as title_sq, MAX(title_mk) as title_mk, MAX(title_sr) as title_sr, 
               MAX(bullets_en) as bullets_en, MAX(bullets_sq) as bullets_sq, MAX(bullets_mk) as bullets_mk, MAX(bullets_sr) as bullets_sr, 
               MAX(perspective_en) as perspective_en, MAX(perspective_sq) as perspective_sq, MAX(perspective_mk) as perspective_mk, MAX(perspective_sr) as perspective_sr, 
               AVG(geo_pro_western) as avg_pro_western, AVG(narrative_objectivity) as avg_objectivity, AVG(narrative_divergence_score) as avg_divergence,
               GROUP_CONCAT(source_domain, ', ') as sources, GROUP_CONCAT(original_title, '||') as orig_titles,
               GROUP_CONCAT(original_url, '||') as orig_urls, MAX(image_url) as cluster_image
        FROM articles WHERE cluster_id IS NOT NULL GROUP BY cluster_id ORDER BY article_id DESC
    """
    try: df = pd.read_sql_query(query, conn)
    except: df = pd.DataFrame()
    conn.close()
    return df

def get_blindspot_stories():
    try:
        conn = get_connection()
        query = "SELECT * FROM articles WHERE title_en != 'Processing Error' AND title_en IS NOT NULL ORDER BY narrative_divergence_score DESC LIMIT 3"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except: return pd.DataFrame()

# --- MODALS ---
@st.dialog(" ", width="large")
def open_article_modal(row, clean_bullets, perspective_text, bg_style, t_dict):
    st.markdown(f"<h3 style='margin-top:-20px; margin-bottom:15px;'>{t_dict.get('modal_title')}</h3>", unsafe_allow_html=True)
    header_col1, header_col2 = st.columns([1, 1.5], gap="small")
    pw, obj = int(float(row.get('avg_pro_western', 0.5)) * 100), int(float(row.get('avg_objectivity', 0.5)) * 100) 
    db_geo = row.get('cluster_geo_scope', '')
    geo_idx = UI_TEXT["English"]["geos"].index(db_geo) if db_geo in UI_TEXT["English"]["geos"] else -1
    display_geo_pin = t_dict["geos"][geo_idx] if geo_idx != -1 else db_geo

    spectrum_html = "".join([
        '<div style="background-color: transparent; border: 1px solid rgba(148, 163, 184, 0.3); padding: 12px; border-radius: 12px; margin-top: 4px;">',
        f'<div style="margin-bottom: 12px;"><div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 700; margin-bottom: 4px;"><span>{t_dict.get("pw")} <span class="tooltip-sup" data-tooltip="{t_dict.get("pw_help")}">?</span> : {pw}%</span></div>',
        f'<div style="position: relative; width: 100%; height: 6px; background-color: #E2E8F0; border-radius: 999px; overflow: hidden;"><div style="position: absolute; left: 0; top: 0; height: 100%; width: {pw}%; background-color: #3B82F6;"></div></div></div>',
        f'<div><div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 700; margin-bottom: 4px;"><span>{t_dict.get("obj")} <span class="tooltip-sup" data-tooltip="{t_dict.get("obj_help")}">?</span> : {obj}%</span></div>',
        f'<div style="position: relative; width: 100%; height: 6px; background-color: #E2E8F0; border-radius: 999px; overflow: hidden;"><div style="position: absolute; left: 0; top: 0; height: 100%; width: {obj}%; background-color: #10B981;"></div></div></div>',
        '</div>'
    ])

    with header_col1:
        st.markdown(f"""<div style="width: 100%; height: 220px; border-radius: 16px; background-color: #1E293B; background-image: {bg_style}; background-size: cover; background-position: center; margin-bottom: 8px;"></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div style="display: flex; gap: 0.5rem;"><span style="background: rgba(148, 163, 184, 0.2); padding: 4px 10px; border-radius: 8px; font-size: 0.75rem; font-weight: 700;">📍 {display_geo_pin}</span></div>""", unsafe_allow_html=True)
        st.markdown(spectrum_html, unsafe_allow_html=True)
        
    with header_col2:
        st.markdown(f"<h3 style='margin-top: 4px; margin-bottom: 8px; font-weight: 800; font-size: 1.4rem; line-height: 1.2;'>{row['display_title']}</h3>", unsafe_allow_html=True)
        if clean_bullets:
            for b in clean_bullets[:4]: st.markdown(f"<div style='margin-bottom: 8px; font-size: 0.95rem; line-height: 1.5; opacity: 0.85;'>• {b}</div>", unsafe_allow_html=True)
        if perspective_text:
            st.markdown(f"""<div style='margin-top: 16px; margin-bottom: 16px; padding-top: 16px; border-top: 1px solid rgba(148, 163, 184, 0.3);'><h4 style='font-size: 0.85rem; font-weight: 800; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.05em; opacity: 0.7;'>{t_dict.get('analysis_title')}</h4><div style='font-size: 0.95rem; line-height: 1.6; opacity: 0.9;'>{perspective_text}</div></div>""", unsafe_allow_html=True)

        titles, urls, sources_raw = str(row.get('orig_titles', '')).split("||"), str(row.get('orig_urls', '')).split("||"), str(row.get('sources', '')).split(", ")
        seen, links_html = set(), ""
        for t, s, u in zip(titles, sources_raw, urls):
            if t and t not in seen and u and str(u).startswith('http'):
                seen.add(t)
                links_html += f"<a href='{u}' target='_blank' style='text-decoration: none; color: inherit;'><div class='source-link-card'><div style='font-size: 0.7rem; color: #3B82F6; font-weight: 800; text-transform: uppercase; margin-bottom: 4px; letter-spacing: 0.05em;'>🔗 {s}</div><div style='font-size: 0.85rem; font-weight: 600; line-height: 1.3;'>{t}</div></div></a>"
        if links_html: st.markdown(f"<div style='border-top: 1px solid rgba(148, 163, 184, 0.3); padding-top: 12px;'><h4 style='font-size: 0.85rem; font-weight: 800; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.05em; opacity: 0.7;'>{t_dict.get('sources')}</h4>{links_html}</div>", unsafe_allow_html=True)
            
    if st.button(t_dict.get("btn_back")): st.rerun()

@st.dialog(" ", width="large")
def open_blindspots_modal(t_dict):
    st.markdown(f"<h3 style='margin-top:-20px; margin-bottom:15px;'>{t_dict.get('blindspots')}</h3>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.9rem; opacity: 0.7; margin-bottom: 1.5rem;'>{t_dict.get('blindspots_sub')}</div>", unsafe_allow_html=True)
    
    for idx, row in get_blindspot_stories().iterrows():
        b_title = row.get(t_dict.get("db_col_title", "title_en")) or "Title Missing"
        db_cat = row.get('cluster_category', 'News')
        if db_cat == 'Infrastructure': db_cat = 'Economy'
        display_tag = t_dict["topics"][UI_TEXT["English"]["topics"].index(db_cat)] if db_cat in UI_TEXT["English"]["topics"] else db_cat

        raw_b = str(row.get(t_dict.get("db_col_bullets", "bullets_en")) or "").split("||")[0]
        clean_b = [b.strip().lstrip('-*• ') for b in raw_b.split('\n') if b.strip()]
        bullets_html = "".join([f"<div style='margin-bottom: 6px; font-size: 0.9rem; line-height: 1.4; opacity: 0.9;'>• {b}</div>" for b in clean_b[:3]])
        
        persp_text = row.get(t_dict.get("db_col_persp", "perspective_en")) or ""
        persp_html = f"<div style='margin-top: 12px; margin-bottom: 16px; padding: 12px; background-color: rgba(59, 130, 246, 0.05); border-left: 3px solid #3B82F6; border-radius: 0 8px 8px 0; font-size: 0.9rem; line-height: 1.5; opacity: 0.9;'>{persp_text}</div>" if persp_text else ""
        
        div_score = int(float(row.get('narrative_divergence_score', 0.8)) * 100)

        card_html = f"""<div style='background: #1E293B; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #EF4444; margin-bottom: 1.2rem; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #334155;'>
<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'><div style='font-size: 0.75rem; font-weight: 800; color: #EF4444; text-transform: uppercase;'>{display_tag}</div></div>
<div style='font-weight: 800; font-size: 1.1rem; line-height: 1.4; margin-bottom: 12px; color: #F8FAFC;'>{b_title}</div>
<div style='margin-bottom: 8px;'>{bullets_html}</div>{persp_html}
<div style='display: flex; align-items: center; margin-bottom: 16px; font-size: 0.85rem; font-weight: 700; color: #94A3B8;'>
<span>{t_dict.get('divergence')} <span class="tooltip-sup" data-tooltip="{t_dict.get('div_help')}">?</span> : <span style="color: #EF4444;">{div_score}%</span></span>
</div>
<div style='border-top: 1px solid #334155; padding-top: 12px; display: flex; justify-content: space-between; align-items: center;'>
<div style='font-size: 0.8rem; font-weight: 700; color: #64748B;'>{row.get('source_domain', 'Unknown')}</div>
<a href="{row.get('original_url', '#')}" target="_blank" style="text-decoration: none; font-size: 0.85rem; font-weight: 700; color: #3B82F6; background: rgba(59, 130, 246, 0.1); padding: 6px 12px; border-radius: 6px;">{t_dict.get('read_source')}</a>
</div></div>"""
        st.markdown(card_html, unsafe_allow_html=True)

# --- MAIN APP ---
def run_app():
    st.set_page_config(page_title="Balkan Intel", layout="wide", initial_sidebar_state="collapsed")
    t = UI_TEXT[st.session_state.lang_code]

    # --- CORE STYLING (FIXED CONTRAST, HEADER, AND TABS) ---
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; scroll-behavior: smooth; }
        
        /* HIDE STREAMLIT NATIVE UI */
        [data-testid="collapsedControl"], [data-testid="stSidebar"], header { display: none !important; }
        .block-container { padding-top: 1rem !important; padding-bottom: 50px !important; }

        /* HEADER MOBILE LOCK (Fixes Blindspot Button breaking row) */
        div[data-testid="stVerticalBlock"]:has(#header-anchor) > div[data-testid="stHorizontalBlock"] {
            flex-wrap: nowrap !important; align-items: center !important; 
        }
        button[kind="secondary"]:has(div:contains("👁️")) {
            padding: 4px 8px !important; min-height: 32px !important; border-radius: 8px !important;
            border: 1px solid #E2E8F0 !important; background-color: #FFFFFF !important; color: #0F172A !important;
        }
        button[kind="secondary"]:has(div:contains("👁️")) p { font-size: 0.85rem !important; font-weight: 700 !important; margin: 0 !important; }

        /* BEAUTIFUL NATIVE TABS (Replaces Radio Buttons) */
        /* We target the radio button group and restyle it entirely */
        div[data-testid="stRadio"]:has(p:contains("🏠")) > label { display: none !important; }
        div[data-testid="stRadio"]:has(p:contains("🏠")) div[role="radiogroup"] {
            display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important;
            background-color: #F1F5F9 !important; border-radius: 12px !important; padding: 4px !important; gap: 4px !important; width: 100%;
            overflow-x: auto !important; scrollbar-width: none !important;
        }
        div[data-testid="stRadio"]:has(p:contains("🏠")) label {
            background-color: transparent !important; border: none !important; padding: 8px 4px !important; border-radius: 8px !important;
            flex: 1 !important; text-align: center !important; justify-content: center !important; margin: 0 !important;
        }
        div[data-testid="stRadio"]:has(p:contains("🏠")) label div:first-child { display: none !important; } /* Hide the circle */
        div[data-testid="stRadio"]:has(p:contains("🏠")) label p { color: #64748B !important; font-size: 0.9rem !important; font-weight: 700 !important; margin: 0 !important; }
        div[data-testid="stRadio"]:has(p:contains("🏠")) label:has(input:checked) { background-color: #FFFFFF !important; box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important; }
        div[data-testid="stRadio"]:has(p:contains("🏠")) label:has(input:checked) p { color: #0F172A !important; }

        /* CATEGORY/GEO GRIDS (Same tab style, but wrapped into a grid) */
        div[data-testid="stRadio"]:has(p:contains("🌍")) > label, div[data-testid="stRadio"]:has(p:contains("Polit")) > label { display: none !important; }
        div[data-testid="stRadio"]:has(p:contains("🌍")) div[role="radiogroup"], div[data-testid="stRadio"]:has(p:contains("Polit")) div[role="radiogroup"] {
            display: flex !important; flex-wrap: wrap !important; gap: 8px !important;
        }
        div[data-testid="stRadio"]:has(p:contains("🌍")) label, div[data-testid="stRadio"]:has(p:contains("Polit")) label {
            background-color: #F8FAFC !important; border: 1px solid #E2E8F0 !important; padding: 10px !important; border-radius: 12px !important;
            flex: 1 1 calc(50% - 8px) !important; justify-content: center !important; margin: 0 !important;
        }
        div[data-testid="stRadio"]:has(p:contains("🌍")) label div:first-child, div[data-testid="stRadio"]:has(p:contains("Polit")) label div:first-child { display: none !important; }
        div[data-testid="stRadio"]:has(p:contains("🌍")) label p, div[data-testid="stRadio"]:has(p:contains("Polit")) label p { color: #0F172A !important; font-size: 0.85rem !important; font-weight: 700 !important; text-align: center !important; margin: 0 !important; }
        div[data-testid="stRadio"]:has(p:contains("🌍")) label:has(input:checked), div[data-testid="stRadio"]:has(p:contains("Polit")) label:has(input:checked) { background-color: #3B82F6 !important; border-color: #3B82F6 !important; }
        div[data-testid="stRadio"]:has(p:contains("🌍")) label:has(input:checked) p, div[data-testid="stRadio"]:has(p:contains("Polit")) label:has(input:checked) p { color: #FFFFFF !important; }

        /* DARK THEME FOR NEWS CARDS */
        .particle-card { background: #1E293B; border-radius: 20px; border: 1px solid #334155; height: 380px; display: flex; flex-direction: column; overflow: hidden; position: relative; }
        .particle-card:hover { transform: translateY(-5px); box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2); }
        .card-img-area { height: 280px; background-color: #0F172A; background-size: cover; background-position: center; position: relative; display: flex; flex-direction: column; justify-content: flex-end; padding: 20px 24px; }
        .card-img-area::after { content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to top, rgba(15,23,42, 0.95) 0%, rgba(15,23,42, 0.5) 30%, rgba(15,23,42, 0) 50%); z-index: 1; }
        .card-img-content { position: relative; z-index: 2; width: 100%; }
        .card-tag { background: #3B82F6; color: #FFFFFF; font-size: 0.65rem; font-weight: 800; padding: 4px 10px; border-radius: 6px; text-transform: uppercase; display: inline-block; margin-bottom: 12px; }
        .card-title { font-size: clamp(1.05rem, 1.15vw, 1.2rem); font-weight: 800; color: #F8FAFC !important; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; text-shadow: 0 2px 6px rgba(0,0,0,0.8) !important; }
        .card-footer { height: 100px; padding: 16px 24px; background: #1E293B; display: flex; flex-direction: column; justify-content: center; gap: 8px; border-top: 1px solid #334155; }
        
        /* INVISIBLE CLICK ELEMENT TRIGGER FOR CARDS */
        div[data-testid="stButton"]:has(button[kind="primary"]) { margin: 0 !important; padding: 0 !important; height: 0px !important; overflow: visible !important; }
        button[kind="primary"] { position: absolute !important; background: transparent !important; border: none !important; color: transparent !important; height: 0px !important; padding: 0 !important; box-shadow: none !important; }
        button[kind="primary"]::after { content: ""; position: absolute; bottom: 0; left: 0; width: 100%; height: 380px; z-index: 99; cursor: pointer; }

        /* FLOATING SCROLL TO TOP BUTTON */
        .scroll-top-btn { position: fixed; bottom: 25px; right: 25px; background-color: #3B82F6; color: white !important; width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3); z-index: 999999; font-weight: bold; font-size: 1.2rem; text-decoration: none !important; border: 2px solid #FFFFFF; transition: transform 0.2s ease; }
        .scroll-top-btn:hover { transform: scale(1.1); background-color: #2563EB; }

        /* TOOLTIP */
        .tooltip-sup { font-size: 0.65rem; vertical-align: super; background-color: #334155; color: #F8FAFC; border-radius: 50%; width: 14px; height: 14px; display: inline-flex; align-items: center; justify-content: center; margin-left: 4px; font-weight: 800; cursor: pointer; position: relative; }
        .tooltip-sup::after { content: attr(data-tooltip); position: absolute; bottom: 150%; left: 50%; transform: translateX(-50%); background-color: #0F172A; color: #FFFFFF; padding: 8px 12px; border-radius: 8px; font-size: 0.75rem; font-weight: 500; line-height: 1.3; width: 180px; white-space: normal; z-index: 999999 !important; box-shadow: 0 4px 16px rgba(0,0,0,0.5); opacity: 0; pointer-events: none; text-align: center; }
        .tooltip-sup:hover::after, .tooltip-sup:active::after { opacity: 1; }
    </style>
    <div id="top-anchor"></div>
    <div id="header-anchor"></div>
    """, unsafe_allow_html=True)

    # --- TOP BAR (LOCKED) ---
    colA, colB = st.columns([3, 1])
    with colA:
        st.markdown("<h2 style='margin:0; padding:0; color:#3B82F6; font-size: 1.8rem; font-weight: 800;'>Balkan<span style='color:#0F172A;'>Intel</span></h2>", unsafe_allow_html=True)
    with colB:
        if st.button(t['blindspots_btn'], use_container_width=True):
            open_blindspots_modal(t)
    
    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    # --- NAVIGATION TABS ---
    nav_options = [t['nav_home'], t['nav_search'], t['nav_lang']]
    # Get current index safely
    try: current_idx = nav_options.index(st.session_state.get('current_nav_label', t['nav_home']))
    except ValueError: current_idx = 0

    selected_nav = st.radio("Nav", nav_options, horizontal=True, index=current_idx, key="main_nav")
    st.session_state.current_nav_label = selected_nav

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    df = get_database_data()

    # ==========================================
    # VIEW: SEARCH TAB
    # ==========================================
    if selected_nav == t['nav_search']:
        search_input = st.text_input("🔍", placeholder=t["search_label"], label_visibility="collapsed")
        if search_input:
            st.session_state.search_query = search_input
            st.session_state.active_cat = "All Topics"
            st.session_state.active_geo = "All Regions"
            st.session_state.current_nav_label = t['nav_home']
            st.rerun()

        st.markdown(f"<h4 style='font-size: 1.1rem; color: #475569; font-weight: 800; margin-top: 1rem;'>{t['filter_cat']}</h4>", unsafe_allow_html=True)
        # Using radio for Category Grid
        selected_cat = st.radio("Cat", t["topics"][1:], index=None, key="cat_grid", horizontal=True)
        if selected_cat:
            # Map back to english for backend filtering
            idx = t["topics"].index(selected_cat)
            st.session_state.active_cat = UI_TEXT["English"]["topics"][idx]
            st.session_state.search_query = ""
            st.session_state.current_nav_label = t['nav_home']
            st.rerun()

    # ==========================================
    # VIEW: LANGUAGE & GEO TAB
    # ==========================================
    elif selected_nav == t['nav_lang']:
        st.markdown(f"<h4 style='font-size: 1.1rem; color: #475569; font-weight: 800;'>{t['lang_header']}</h4>", unsafe_allow_html=True)
        lang_options = ["English", "Shqip", "Македонски", "Srpski", "Bosanski"]
        l_cols = st.columns(2)
        for i, l_opt in enumerate(lang_options):
            with l_cols[i % 2]:
                if st.button(f"{'✅ ' if st.session_state.lang_code == l_opt else ''}{l_opt}", key=f"lang_{l_opt}", use_container_width=True):
                    st.session_state.lang_code = l_opt
                    st.session_state.current_nav_label = t['nav_home']
                    st.rerun()

        st.markdown(f"<h4 style='font-size: 1.1rem; color: #475569; font-weight: 800; margin-top: 1.5rem;'>{t['geo_header']}</h4>", unsafe_allow_html=True)
        # Using radio for Geo Grid
        display_geos = [f"{t['geo_labels'][i+1].split(' ')[0]} {geo}" for i, geo in enumerate(t["geos"][1:])]
        selected_geo = st.radio("Geo", display_geos, index=None, key="geo_grid", horizontal=True)
        if selected_geo:
            idx = display_geos.index(selected_geo) + 1
            st.session_state.active_geo = UI_TEXT["English"]["geos"][idx]
            st.session_state.search_query = ""
            st.session_state.current_nav_label = t['nav_home']
            st.rerun()

    # ==========================================
    # VIEW: HOME FEED
    # ==========================================
    else:
        active_filters = []
        if st.session_state.active_cat != "All Topics": active_filters.append(t['topics'][UI_TEXT["English"]["topics"].index(st.session_state.active_cat)])
        if st.session_state.active_geo != "All Regions": active_filters.append(t['geos'][UI_TEXT["English"]["geos"].index(st.session_state.active_geo)])
        if st.session_state.search_query: active_filters.append(f'"{st.session_state.search_query}"')
        
        if active_filters:
            st.markdown(f"""
            <div style='display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap;'>
                {''.join([f"<div style='background: #3B82F6; padding: 6px 12px; border-radius: 8px; font-size: 0.8rem; font-weight: 700; color: #FFF;'>{f}</div>" for f in active_filters])}
            </div>
            """, unsafe_allow_html=True)
            if st.button("✖ Clear Filters"):
                st.session_state.active_cat = "All Topics"
                st.session_state.active_geo = "All Regions"
                st.session_state.search_query = ""
                st.rerun()

        filtered_df = df.copy()
        if st.session_state.search_query and not filtered_df.empty:
            sq = st.session_state.search_query.lower()
            filtered_df = filtered_df[
                filtered_df['title_en'].str.lower().str.contains(sq, na=False) |
                filtered_df['title_sq'].str.lower().str.contains(sq, na=False) |
                filtered_df['title_mk'].str.lower().str.contains(sq, na=False) |
                filtered_df['title_sr'].str.lower().str.contains(sq, na=False)
            ]
        if st.session_state.active_geo != "All Regions" and not filtered_df.empty: 
            target_geo = st.session_state.active_geo.strip().lower()
            filtered_df = filtered_df[filtered_df['cluster_geo_scope'].apply(lambda x: target_geo in str(x).strip().lower())]
        if st.session_state.active_cat != "All Topics" and not filtered_df.empty: 
            if st.session_state.active_cat == "Economy": filtered_df = filtered_df[filtered_df['cluster_category'].isin(["Economy", "Infrastructure"])]
            else: filtered_df = filtered_df[filtered_df['cluster_category'].apply(lambda x: st.session_state.active_cat.strip().lower() in str(x).strip().lower())]

        if filtered_df.empty:
            st.info("No articles found matching the current filters.")
        else:
            grid_col1, grid_col2 = st.columns(2, gap="small")
            for idx, row in filtered_df.reset_index(drop=True).iterrows():
                col_title = t.get("db_col_title", "title_en")
                col_bullets = t.get("db_col_bullets", "bullets_en")
                col_persp = t.get("db_col_persp", "perspective_en")
                
                display_title = row.get(col_title) or row.get('title_en') or "Title Missing"
                raw_b = str(row.get(col_bullets) or row.get('bullets_en') or "").split("||")[0]
                clean_b = [b.strip().lstrip('-*• ') for b in raw_b.split('\n') if b.strip()]
                persp_text = row.get(col_persp) or row.get('perspective_en') or ""
                
                raw_img = str(row.get('cluster_image', '')).strip()
                fallback = "https://images.unsplash.com/photo-1555949963-aa79dcee981c?q=80&w=800&auto=format&fit=crop"
                bg = f"url('{fallback}')" if pd.isna(row.get('cluster_image')) or raw_img in ('None', 'nan', '') or not raw_img.startswith('http') else f"url('{raw_img}'), url('{fallback}')"

                pw, obj = int(float(row.get('avg_pro_western', 0.5)) * 100), int(float(row.get('avg_objectivity', 0.5)) * 100)
                db_cat = row.get('cluster_category', 'News')
                if db_cat == 'Infrastructure': db_cat = 'Economy'
                display_tag = t["topics"][UI_TEXT["English"]["topics"].index(db_cat)] if db_cat in UI_TEXT["English"]["topics"] else db_cat

                with (grid_col1 if idx % 2 == 0 else grid_col2):
                    card_html = f"""
                    <div class="particle-card">
                        <div class="card-img-area" style="background-image: {bg};">
                            <div class="card-img-content"><span class="card-tag">{display_tag}</span><div class="card-title">{display_title}</div></div>
                        </div>
                        <div class="card-footer">
                            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 700; color: #94A3B8; margin-bottom: 6px;">
                                <span>🇪🇺 {t.get("pw")} : <span style="color:#F8FAFC;">{pw}%</span></span>
                                <span>🔍 {t.get("obj")} : <span style="color:#F8FAFC;">{obj}%</span></span>
                            </div>
                            <div style="display: flex; width: 100%; height: 6px; background-color: #334155; border-radius: 999px; overflow: hidden;">
                                <div style="width: 50%; display: flex; justify-content: flex-start; border-right: 1px solid #1E293B;"><div style="width: {pw}%; background-color: #3B82F6; height: 100%;"></div></div>
                                <div style="width: 50%; display: flex; justify-content: flex-end;"><div style="width: {obj}%; background-color: #10B981; height: 100%;"></div></div>
                            </div>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
                    if st.button(" ", key=f"btn_{row.get('cluster_id', idx)}_{idx}", type="primary", use_container_width=True):
                        row_dict = row.to_dict()
                        row_dict['display_title'] = display_title 
                        open_article_modal(row_dict, clean_b, persp_text, bg, t)
                    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    # FLOATING HOME BUTTON
    st.markdown('<a href="#top-anchor" class="scroll-top-btn">▲</a>', unsafe_allow_html=True)

if __name__ == "__main__":
    run_app()
