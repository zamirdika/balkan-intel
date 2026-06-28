import streamlit as st
import sqlite3
import pandas as pd

# --- UI TRANSLATION DICTIONARY ---
UI_TEXT = {
    "English": {
        "topics": ["All Topics", "Politics", "Economy", "Technology", "Culture", "Entertainment", "Sports", "Crime & Accidents"],
        "geos": ["All Regions", "North Macedonia", "Kosovo", "Albania", "Serbia", "Bosnia and Herzegovina", "Montenegro", "Regional"],
        "geo_labels": ["🌍 Global", "🇲🇰 MKD", "🇽🇰 KOS", "🇦🇱 ALB", "🇷🇸 SRB", "🇧🇦 BIH", "🇲🇪 MNE", "🗺️ Balkans"],
        "lang_header": "🌐 Language", "geo_header": "📍 Geography", "db_header": "📬 Daily Briefing",
        "search_label": "🔍 Search News...",
        "db_sub": "Narrative blindspots delivered straight to your inbox.", "api_header": "⚙️ Enterprise API",
        "api_sub": "Integrate real-time narrative clustering into your dashboards.", "subscribe": "Subscribe",
        "success": "Thank you! You are subscribed.", "api_btn": "View API Docs", "blindspots_btn": "👁️ Blindspots",
        "blindspots": "Strategic Blindspots", "blindspots_sub": "Regional narratives and crucial information updates you might have missed completely from mainstream local coverage.",
        "modal_title": "Deep Dive Analysis", "pw": "Pro-Western", "obj": "Objectivity", "btn_back": "Close",
        "sources": "Original Sources", "how_ai_works": "🧠 How AI Works", 
        "analysis_title": "Narrative Summary",
        "pw_help": "Measures alignment with EU/US/NATO geopolitical positions.",
        "obj_help": "Measures factual reporting vs. emotional or biased language.",
        "divergence": "Divergence",
        "div_help": "Measures how much this story is omitted or selectively framed compared to the regional baseline.",
        "read_source": "Read Original ↗",
        "ai_desc": "<b>Core Data Aggregation:</b> Balkan Intel continuously aggregates automated RSS feeds across the Western Balkans region.<br><br><b>AI Synthesis Engine:</b> The raw source text is securely structured and analyzed using Google's Gemini 2.5 Flash model to extract language neutral narrative properties, evaluate western strategic alignment metrics, and measure objective factual presentation.",
        "db_col_title": "title_en", "db_col_bullets": "bullets_en", "db_col_persp": "perspective_en"
    },
    "Shqip": {
        "topics": ["Të gjitha", "Politikë", "Ekonomi", "Teknologji", "Kulturë", "Show Biz", "Sport", "Kronika e Zezë"],
        "geos": ["Të gjitha", "Maqedonia e Veriut", "Kosova", "Shqipëria", "Serbia", "Bosnja dhe Hercegovina", "Mali i Zi", "Rajonale"],
        "geo_labels": ["🌍 Global", "🇲🇰 MKD", "🇽🇰 KOS", "🇦🇱 ALB", "🇷🇸 SRB", "🇧🇦 BIH", "🇲🇪 MNE", "🗺️ Ballkan"],
        "lang_header": "🌐 Gjuha", "geo_header": "📍 Gjeografia", "db_header": "📬 Informimi Ditor",
        "search_label": "🔍 Kërko...",
        "db_sub": "Të pathënat e narrativave direkt në emailin tuaj.", "api_header": "⚙️ API për Biznese",
        "api_sub": "Integroni grupimin e narrativave në kohë reale.", "subscribe": "Abonohu",
        "success": "Faleminderit! Jeni abonuar.", "api_btn": "Shiko Dokumentacionin", "blindspots_btn": "👁️ Të pathënat",
        "blindspots": "Të pathënat Strategjike", "blindspots_sub": "Narrativa rajonale strategjike dhe informacione jetike që mund t'i keni anashkaluar plotësisht nga mbulimi kryesor medial lokal.",
        "modal_title": "Analiza e Thelluar", "pw": "Pro-Perëndimor", "obj": "Objektiviteti", "btn_back": "Mbyll",
        "sources": "Burimet Origjinale", "how_ai_works": "🧠 Si funksionon AI?", 
        "analysis_title": "Përmbledhja e Narrativës",
        "pw_help": "Mat përafrimin me qëndrimet gjeopolitike të BE/SHBA/NATO-s.",
        "obj_help": "Mat raportimin faktik kundrejt gjuhës emocionale apo të anashme.",
        "divergence": "Divergjenca",
        "div_help": "Mat shkallën në të cilën kjo ngjarje anashkalohet ose kornizohet në mënyrë selektive krahasuar me rajonin.",
        "read_source": "Lexo Origjinalin ↗",
        "ai_desc": "<b>Grumbullimi i të Dhënave:</b> Balkan Intel grumbullon në mënyrë të vazhdueshme lajmet automatike nga rajoni i Ballkanit Perëndimor përmes RSS.<br><br><b>Motori i Inteligjencës Artificiale:</b> Teksti bruto i burimit strukturohet dhe analizohet duke përdorur modelin Gemini 2.5 Flash të Google.",
        "db_col_title": "title_sq", "db_col_bullets": "bullets_sq", "db_col_persp": "perspective_sq"
    },
    "Македонски": {
        "topics": ["Сите Теми", "Политика", "Економија", "Технологија", "Култура", "Забава", "Спорт", "Црна Хроника"],
        "geos": ["Сите Региони", "Северна Македонија", "Косово", "Албанија", "Србија", "Босна и Херцеговина", "Црна Гора", "Регионално"],
        "geo_labels": ["🌍 Глобално", "🇲🇰 MKD", "🇽🇰 KOS", "🇦🇱 ALB", "🇷🇸 SRB", "🇧🇦 BIH", "🇲🇪 MNE", "🗺️ Балкан"],
        "lang_header": "🌐 Јазик", "geo_header": "📍 Географија", "db_header": "📬 Дневен Брифинг",
        "search_label": "🔍 Пребарај...",
        "db_sub": "Наративни слепи точки доставени директно во вашето сандаче.", "api_header": "⚙️ Enterprise API",
        "api_sub": "Интегрирајте групирање на наративи во реално време.", "subscribe": "Претплати се",
        "success": "Ви благодариме! Претплатени сте.", "api_btn": "Види API Документација", "blindspots_btn": "👁️ Игнорирани вести",
        "blindspots": "Игнорирани вести", "blindspots_sub": "Регионални наративи и клучни информации кои можеби целосно сте ги пропуштеле во главните локални медиуми.",
        "modal_title": "Длабинска Анализа", "pw": "Про-Западно", "obj": "Објективност", "btn_back": "Затвори",
        "sources": "Оригинални Извори", "how_ai_works": "🧠 Како работи ВИ?", 
        "analysis_title": "Наративно Резиме",
        "pw_help": "Го мери усогласувањето со геополитичките позиции на ЕУ/САД/НАТО.",
        "obj_help": "Го мери фактуелното известување наспроти емотивниот или пристрасен јазик.",
        "divergence": "Дивергенција",
        "div_help": "Мери колку оваа вест е изоставена или селективно врамена во споредба со регионалниот просек.",
        "read_source": "Оригинален Напис ↗",
        "ai_desc": "<b>Агрегација на податоци:</b> Balkan Intel континуирано собира автоматизирани RSS извори низ регионот на Западен Балкан.",
        "db_col_title": "title_mk", "db_col_bullets": "bullets_mk", "db_col_persp": "perspective_mk"
    },
    "Srpski": {
        "topics": ["Sve Teme", "Politika", "Ekonomija", "Tehnologija", "Kultura", "Zabava", "Sport", "Crna Hronika"],
        "geos": ["Svi Regioni", "Severna Makedonija", "Kosovo", "Albanija", "Srbija", "Bosna i Hercegovina", "Crna Gora", "Regionalno"],
        "geo_labels": ["🌍 Globalno", "🇲🇰 MKD", "🇽🇰 KOS", "🇦🇱 ALB", "🇷🇸 SRB", "🇧🇦 BIH", "🇲🇪 MNE", "🗺️ Balkan"],
        "lang_header": "🌐 Jezik", "geo_header": "📍 Geografija", "db_header": "📬 Dnevni Brifing",
        "search_label": "🔍 Pretraži...",
        "db_sub": "Narativi koje ste možda propustili direktno u vaš inbox.", "api_header": "⚙️ Enterprise API",
        "api_sub": "Integrišite grupisanje narativa u realnom vremenu.", "subscribe": "Pretplati se",
        "success": "Hvala! Pretplatili ste se.", "api_btn": "Vidi API Dokumentaciju", "blindspots_btn": "👁️ Slepe tačke",
        "blindspots": "Slepe tačke", "blindspots_sub": "Narativi koje ste možda propustili.",
        "modal_title": "Dubinska Analiza", "pw": "Pro-Zapadno", "obj": "Objektivnost", "btn_back": "Zatvori",
        "sources": "Originalni Izvori", "how_ai_works": "🧠 Kako radi AI?", 
        "analysis_title": "Narativni Sažetak",
        "pw_help": "Meri usklađenost sa geopolitičkim pozicijama EU/SAD/NATO.",
        "obj_help": "Meri činjenično izveštavanje naspram emotivnog ili pristrasnog jezika.",
        "divergence": "Divergencija",
        "div_help": "Meri koliko je ova vest izostavljena ili selektivno uokvirena u poređenju sa regionalnim prosekom.",
        "read_source": "Pročitaj Original ↗",
        "ai_desc": "Balkan Intel agregira RSS vesti i koristi Gemini 2.5 Flash za izvlačenje geopolitičkih metrika.",
        "db_col_title": "title_sr", "db_col_bullets": "bullets_sr", "db_col_persp": "perspective_sr"
    },
    "Bosanski": {
        "topics": ["Sve Teme", "Politika", "Ekonomija", "Tehnologija", "Kultura", "Zabava", "Sport", "Crna Hronika"],
        "geos": ["Svi Regioni", "Sjeverna Makedonija", "Kosovo", "Albanija", "Srbija", "Bosna i Hercegovina", "Crna Gora", "Regionalno"],
        "geo_labels": ["🌍 Globalno", "🇲🇰 MKD", "🇽🇰 KOS", "🇦🇱 ALB", "🇷🇸 SRB", "🇧🇦 BIH", "🇲🇪 MNE", "🗺️ Balkan"],
        "lang_header": "🌐 Jezik", "geo_header": "📍 Geografija", "db_header": "📬 Dnevni Briefing",
        "search_label": "🔍 Pretraži...",
        "db_sub": "Narativi koje ste možda propustili direktno u vaš inbox.", "api_header": "⚙️ Enterprise API",
        "api_sub": "Integrišite grupisanje narativa u realnom vremenu.", "subscribe": "Pretplati se",
        "success": "Hvala! Pretplatili ste se.", "api_btn": "Vidi API Dokumentaciju", "blindspots_btn": "👁️ Slijepe tačke",
        "blindspots": "Slijepe tačke", "blindspots_sub": "Narativi koje ste možda propustili.",
        "modal_title": "Dubinska Analiza", "pw": "Pro-Zapadno", "obj": "Objektivnost", "btn_back": "Zatvori",
        "sources": "Originalni Izvori", "how_ai_works": "🧠 Kako radi AI?", 
        "analysis_title": "Narativni Sažetak",
        "pw_help": "Mjeri usklađenost sa geopolitičkim pozicijama EU/SAD/NATO.",
        "obj_help": "Mjeri činjenično izvještavanje naspram emotivnog ili pristrasnog jezika.",
        "divergence": "Divergencija",
        "div_help": "Mjeri koliko je ova vijest izostavljena ili selektivno uokvirena u poređenju sa regionalnim prosjekom.",
        "read_source": "Pročitaj Original ↗",
        "ai_desc": "Balkan Intel agregira RSS vijesti i koristi Gemini 2.5 Flash za izvlačenje geopolitičkih metrika.",
        "db_col_title": "title_sr", "db_col_bullets": "bullets_sr", "db_col_persp": "perspective_sr"
    }
}

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
               MAX(bullets_mk) as bullets_mk, MAX(bullets_sr) as bullets_sr,
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
    try:
        df = pd.read_sql_query(query, conn)
    except Exception as e:
        st.error(f"⚠️ SQL Database Error: {e}")
        df = pd.DataFrame()
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

# --- TOP LEVEL DIALOG MODALS ---
@st.dialog(" ", width="large")
def open_article_modal(row, clean_bullets, perspective_text, bg_style, t_dict):
    st.markdown(f"<h3 style='margin-top:-20px; margin-bottom:15px;'>{t_dict.get('modal_title')}</h3>", unsafe_allow_html=True)
    header_col1, header_col2 = st.columns([1, 1.5], gap="small")
    pw = int(float(row.get('avg_pro_western', 0.5)) * 100)
    obj = int(float(row.get('avg_objectivity', 0.5)) * 100) 
    
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
            for b in clean_bullets[:4]: 
                st.markdown(f"<div style='margin-bottom: 8px; font-size: 0.95rem; line-height: 1.5; opacity: 0.85;'>• {b}</div>", unsafe_allow_html=True)
        
        if perspective_text:
            st.markdown(f"""
            <div style='margin-top: 16px; margin-bottom: 16px; padding-top: 16px; border-top: 1px solid rgba(148, 163, 184, 0.3);'>
                <h4 style='font-size: 0.85rem; font-weight: 800; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.05em; opacity: 0.7;'>{t_dict.get('analysis_title')}</h4>
                <div style='font-size: 0.95rem; line-height: 1.6; opacity: 0.9;'>{perspective_text}</div>
            </div>
            """, unsafe_allow_html=True)

        titles = str(row.get('orig_titles', '')).split("||")
        urls = str(row.get('orig_urls', '')).split("||")
        sources_raw = str(row.get('sources', '')).split(", ")

        seen, links_html = set(), ""
        for t, s, u in zip(titles, sources_raw, urls):
            if t and t not in seen and u and str(u).startswith('http'):
                seen.add(t)
                links_html += f"<a href='{u}' target='_blank' style='text-decoration: none; color: inherit;'><div class='source-link-card'><div style='font-size: 0.7rem; color: #3B82F6; font-weight: 800; text-transform: uppercase; margin-bottom: 4px; letter-spacing: 0.05em;'>🔗 {s}</div><div style='font-size: 0.85rem; font-weight: 600; line-height: 1.3;'>{t}</div></div></a>"
                
        if links_html:
            st.markdown(f"<div style='border-top: 1px solid rgba(148, 163, 184, 0.3); padding-top: 12px;'><h4 style='font-size: 0.85rem; font-weight: 800; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.05em; opacity: 0.7;'>{t_dict.get('sources')}</h4>{links_html}</div>", unsafe_allow_html=True)
            
    if st.button(t_dict.get("btn_back")):
        st.rerun()

@st.dialog(" ", width="large")
def open_blindspots_modal(t_dict):
    st.markdown(f"<h3 style='margin-top:-20px; margin-bottom:15px;'>{t_dict.get('blindspots')}</h3>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.9rem; opacity: 0.7; margin-bottom: 1.5rem;'>{t_dict.get('blindspots_sub')}</div>", unsafe_allow_html=True)
    
    for idx, row in get_blindspot_stories().iterrows():
        col_title = t_dict.get("db_col_title", "title_en")
        b_title = row.get(col_title) or row.get('title_en') or "Title Missing"
        
        db_cat = row.get('cluster_category', 'News')
        # Handle the merged infrastructure tag logic here as well
        if db_cat == 'Infrastructure':
            db_cat = 'Economy'
            
        if db_cat in UI_TEXT["English"]["topics"]:
            cat_idx = UI_TEXT["English"]["topics"].index(db_cat)
            display_tag = t_dict["topics"][cat_idx]
        else:
            display_tag = db_cat

        col_bullets = t_dict.get("db_col_bullets", "bullets_en")
        raw_b = str(row.get(col_bullets) or row.get('bullets_en') or "").split("||")[0]
        clean_b = [b.strip().lstrip('-*• ') for b in raw_b.split('\n') if b.strip()]
        
        bullets_html = ""
        for b in clean_b[:3]:
            bullets_html += f"<div style='margin-bottom: 6px; font-size: 0.9rem; line-height: 1.4; opacity: 0.9;'>• {b}</div>"

        # Inject the perspective text directly into the blindspot summary
        col_persp = t_dict.get("db_col_persp", "perspective_en")
        persp_text = row.get(col_persp) or row.get('perspective_en') or ""
        
        persp_html = ""
        if persp_text:
            persp_html = f"<div style='margin-top: 12px; margin-bottom: 16px; padding: 12px; background-color: rgba(59, 130, 246, 0.05); border-left: 3px solid #3B82F6; border-radius: 0 8px 8px 0; font-size: 0.9rem; line-height: 1.5; opacity: 0.9;'>{persp_text}</div>"

        source_domain = row.get('source_domain', 'Unknown Source')
        orig_url = row.get('original_url', '#')
        div_score = int(float(row.get('narrative_divergence_score', 0.8)) * 100)

        card_html = f"""<div style='background: #FFFFFF; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #EF4444; margin-bottom: 1.2rem; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0;'>
<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
<div style='font-size: 0.75rem; font-weight: 800; color: #EF4444; text-transform: uppercase;'>{display_tag}</div>
</div>
<div style='font-weight: 800; font-size: 1.1rem; line-height: 1.4; margin-bottom: 12px; color: #0F172A;'>
{b_title}
</div>
<div style='margin-bottom: 8px;'>
{bullets_html}
</div>
{persp_html}
<div style='display: flex; align-items: center; margin-bottom: 16px; font-size: 0.85rem; font-weight: 700; color: #475569;'>
<span>{t_dict.get('divergence')} <span class="tooltip-sup" data-tooltip="{t_dict.get('div_help')}">?</span> : <span style="color: #EF4444;">{div_score}%</span></span>
</div>
<div style='border-top: 1px solid #E2E8F0; padding-top: 12px; display: flex; justify-content: space-between; align-items: center;'>
<div style='font-size: 0.8rem; font-weight: 700; color: #64748B;'>{source_domain}</div>
<a href="{orig_url}" target="_blank" style="text-decoration: none; font-size: 0.85rem; font-weight: 700; color: #3B82F6; background: #EFF6FF; padding: 6px 12px; border-radius: 6px; transition: background 0.2s;">
{t_dict.get('read_source')}
</a>
</div>
</div>"""
        st.markdown(card_html, unsafe_allow_html=True)

@st.dialog(" ", width="small")
def open_methodology_modal(t_dict):
    st.markdown(f"<h3 style='margin-top:-20px; margin-bottom:15px;'>{t_dict.get('how_ai_works')}</h3>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.95rem; line-height: 1.6; opacity: 0.9;'>{t_dict.get('ai_desc')}</div>", unsafe_allow_html=True)

# --- MAIN APP EXECUTION ---
def run_app():
    st.set_page_config(page_title="Balkan Intel", layout="wide", initial_sidebar_state="expanded")
    SIDEBAR_HEADER_STYLE = "font-size: 0.75rem; font-weight: 800; color: #94A3B8; text-transform: uppercase; margin-bottom: 10px; letter-spacing: 0.05em; display: block;"

    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #FAFAFA; scroll-behavior: smooth; }
        header[data-testid="stHeader"] { background: transparent !important; box-shadow: none !important; z-index: 99999 !important; pointer-events: none !important; }
        [data-testid="collapsedControl"] { pointer-events: auto !important; }
        .stAppDeployButton, [data-testid="stMainMenu"] { display: none !important; }
        footer { visibility: hidden; }
        .block-container { padding-top: 0rem !important; padding-bottom: 2rem !important; max-width: 100% !important; padding-left: 2.5rem !important; padding-right: 2.5rem !important; }
        
        [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B !important; padding-top: 1rem !important; }
        [data-testid="stSidebar"] * { color: #F8FAFC !important; }
        [data-testid="stSidebar"] svg { fill: #F8FAFC !important; }
        [data-testid="stSidebar"] input { color: #0F172A !important; background-color: #FFFFFF !important; text-align: center; }
        [data-testid="stForm"] { border: none !important; padding: 0 !important; }
        [data-testid="stForm"] button { background-color: #3B82F6 !important; border: none !important; border-radius: 8px !important; width: 100% !important; margin-top: 4px; padding: 10px !important; }
        [data-testid="stForm"] button p { color: #FFFFFF !important; font-weight: 700 !important; font-size: 0.85rem !important; }

        [data-testid="stMainBlockContainer"] div[role="radiogroup"] {
            display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; align-items: center !important;
            overflow-x: auto !important; scrollbar-width: none !important; padding-bottom: 8px !important; gap: 6px !important;
        }
        [data-testid="stMainBlockContainer"] div[role="radiogroup"] label {
            display: inline-flex !important; background-color: #FFFFFF !important; border: 1px solid #CBD5E1 !important; border-radius: 8px !important; padding: 8px 16px !important; white-space: nowrap !important;
        }
        [data-testid="stMainBlockContainer"] div[role="radiogroup"] label p { color: #0F172A !important; font-weight: 700 !important; font-size: 0.85rem !important; }
        [data-testid="stMainBlockContainer"] div[role="radiogroup"] label:has(input:checked) { background-color: #3B82F6 !important; border-color: #3B82F6 !important; }
        [data-testid="stMainBlockContainer"] div[role="radiogroup"] label:has(input:checked) p { color: #FFFFFF !important; }
        
        [data-testid="stSidebar"] div[role="radiogroup"] { display: grid !important; grid-template-columns: repeat(2, 1fr) !important; gap: 8px !important; width: 100% !important; }
        [data-testid="stSidebar"] div[role="radiogroup"] label { background-color: #1E293B !important; border: 1px solid #334155 !important; border-radius: 8px !important; padding: 8px 4px !important; display: inline-flex !important; justify-content: center !important; width: 100% !important; }
        div[role="radiogroup"] label > div:first-child { display: none !important; }
        [data-testid="stSidebar"] div[role="radiogroup"] label p { color: #94A3B8 !important; font-weight: 700 !important; font-size: 0.8rem !important; text-align: center; }
        [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) { background-color: #3B82F6 !important; border-color: #3B82F6 !important; }
        [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p { color: #FFFFFF !important; }
        
        .particle-card { background: #FFFFFF; border-radius: 20px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); border: 1px solid #F1F5F9; transition: transform 0.25s ease, box-shadow 0.25s ease; height: 380px; display: flex; flex-direction: column; overflow: hidden; position: relative; }
        .particle-card:hover { transform: translateY(-5px); box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08); }
        .card-img-area { height: 280px; background-color: #1E293B; background-size: cover; background-position: center; position: relative; display: flex; flex-direction: column; justify-content: flex-end; padding: 20px 24px; }
        .card-img-area::after { content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to top, rgba(0,0,0, 0.9) 0%, rgba(0,0,0, 0.5) 25%, rgba(0,0,0, 0) 45%); z-index: 1; }
        .card-img-content { position: relative; z-index: 2; width: 100%; }
        .card-tag { background: #3B82F6; color: #FFFFFF; font-size: 0.65rem; font-weight: 800; padding: 4px 10px; border-radius: 6px; text-transform: uppercase; display: inline-block; margin-bottom: 12px; }
        .card-title { font-size: clamp(1.05rem, 1.15vw, 1.2rem); font-weight: 800; color: #FFFFFF !important; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; text-shadow: 0 2px 6px rgba(0,0,0,0.8) !important; }
        .card-footer { height: 100px; padding: 16px 24px; background: #FFFFFF; display: flex; flex-direction: column; justify-content: center; gap: 8px; }

        /* ADVANCED HYBRID DESKTOP/MOBILE TOOLTIP ARCHITECTURE */
        .tooltip-sup {
            font-size: 0.65rem;
            vertical-align: super;
            background-color: #CBD5E1;
            color: #0F172A;
            border-radius: 50%;
            width: 14px;
            height: 14px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-left: 4px;
            font-weight: 800;
            cursor: pointer;
            position: relative;
        }
        .tooltip-sup::after {
            content: attr(data-tooltip);
            position: absolute;
            bottom: 150%;
            left: 50%;
            transform: translateX(-50%);
            background-color: #1E293B;
            color: #FFFFFF;
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 0.75rem;
            font-weight: 500;
            line-height: 1.3;
            width: 180px;
            white-space: normal;
            z-index: 999999 !important;
            box-shadow: 0 4px 16px rgba(0,0,0,0.2);
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.15s ease-in-out;
            text-align: center;
        }
        .tooltip-sup::before {
            content: "";
            position: absolute;
            bottom: 110%;
            left: 50%;
            transform: translateX(-50%);
            border-width: 5px;
            border-style: solid;
            border-color: #1E293B transparent transparent transparent;
            z-index: 999999 !important;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.15s ease-in-out;
        }
        .tooltip-sup:hover::after, .tooltip-sup:hover::before,
        .tooltip-sup:active::after, .tooltip-sup:active::before {
            opacity: 1;
        }

        div[data-testid="stButton"]:has(button[kind="primary"]) { margin: 0 !important; padding: 0 !important; height: 0px !important; overflow: visible !important; }
        button[kind="primary"] { position: absolute !important; background: transparent !important; border: none !important; color: transparent !important; height: 0px !important; padding: 0 !important; box-shadow: none !important; }
        button[kind="primary"]::after { content: ""; position: absolute; bottom: 0; left: 0; width: 100%; height: 380px; z-index: 99; cursor: pointer; }
        button[kind="secondary"] { background: transparent !important; border: none !important; font-weight: 800 !important; font-size: 0.9rem !important; padding: 0 !important; display: flex !important; align-items: center; border-radius: 0px !important; }
        .b2b-btn { display: block; text-align: center; background: #3B82F6; color: #FFFFFF !important; padding: 12px; border-radius: 8px; font-size: 0.85rem; font-weight: 700; text-decoration: none; margin-top: 4px; }
        
        button[kind="secondary"]:has(div:contains("🧠")) { 
            border: 1px solid #334155 !important; background-color: transparent !important; color: #F8FAFC !important; justify-content: center !important; 
            border-radius: 8px !important; padding: 8px !important; width: 100%; margin-top: 10px !important;
        }
        button[kind="secondary"]:has(div:contains("🧠")) p { font-size: 0.8rem !important; font-weight: 700 !important; color: #F8FAFC !important; }
        
        button[kind="secondary"]:has(div:contains("👁️")) {
            background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-left: 4px solid #EF4444 !important; color: #0F172A !important; 
            border-radius: 8px !important; padding: 10px 16px !important; margin-bottom: 12px !important; justify-content: flex-start !important; display: inline-flex !important;
        }
        button[kind="secondary"]:has(div:contains("👁️")) p { color: #0F172A !important; font-size: 0.95rem !important; font-weight: 700 !important; margin:0 !important; }

        .scroll-top-btn { position: fixed; bottom: 25px; right: 25px; background-color: #3B82F6; color: white !important; width: 45px; height: 45px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4); z-index: 99999; font-weight: bold; text-decoration: none !important; }
    </style>
    <div id="top-anchor"></div>
    """, unsafe_allow_html=True)

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

    with st.sidebar:
        LANG_OPTIONS = ["🇬🇧 EN", "🇦🇱 SQ", "🇲🇰 MK", "🇷🇸 SR", "🇧🇦 BS"]
        LANG_MAP = {"🇬🇧 EN": "English", "🇦🇱 SQ": "Shqip", "🇲🇰 MK": "Македонски", "🇷🇸 SR": "Srpski", "🇧🇦 BS": "Bosanski"}
        
        current_lang_code = st.session_state.get("lang_choice", "🇬🇧 EN")
        current_dict = UI_TEXT[LANG_MAP[current_lang_code]]
        
        st.markdown(f"<div style='{SIDEBAR_HEADER_STYLE}'>{current_dict['lang_header']}</div>", unsafe_allow_html=True)
        short_lang = st.radio("Lang", LANG_OPTIONS, horizontal=True, label_visibility="collapsed", key="lang_choice")
        t = UI_TEXT[LANG_MAP[short_lang]]

        st.markdown("<hr style='margin: 0.75rem 0; border-color: #1E293B;'/>", unsafe_allow_html=True)
        # SEARCH BAR ADDED HERE
        search_term = st.text_input(t.get('search_label', "🔍 Search..."), key="search_bar")
        
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
        st.markdown(f"<a href='#' class='b2b-btn'>{t['api_btn']}</a>", unsafe_allow_html=True)

        st.markdown("<hr style='margin: 0.75rem 0; border-color: #1E293B;'/>", unsafe_allow_html=True)
        if st.button(t.get('how_ai_works'), type="secondary", use_container_width=True):
            open_methodology_modal(t)

    if st.button(t.get('blindspots_btn'), key="bs_trigger"):
        open_blindspots_modal(t)

    display_cat = st.radio("Topics", t["topics"], horizontal=True, label_visibility="collapsed")
    cat_index = t["topics"].index(display_cat)
    backend_cat = UI_TEXT["English"]["topics"][cat_index]

    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    filtered_df = df.copy()

    # APPLY SEARCH FILTER IF TEXT ENTERED
    if search_term and not filtered_df.empty:
        filtered_df = filtered_df[
            filtered_df['title_en'].str.contains(search_term, case=False, na=False) |
            filtered_df['title_sq'].str.contains(search_term, case=False, na=False) |
            filtered_df['title_mk'].str.contains(search_term, case=False, na=False) |
            filtered_df['title_sr'].str.contains(search_term, case=False, na=False)
        ]

    # APPLY GEOGRAPHY FILTER
    if backend_geo != "All Regions" and not filtered_df.empty: 
        target_geo = backend_geo.strip().lower()
        filtered_df = filtered_df[filtered_df['cluster_geo_scope'].apply(lambda x: target_geo in str(x).strip().lower())]
        
    # APPLY CATEGORY FILTER (INTEGRATING INFRASTRUCTURE INTO ECONOMY)
    if backend_cat != "All Topics" and not filtered_df.empty: 
        if backend_cat == "Economy":
            filtered_df = filtered_df[filtered_df['cluster_category'].isin(["Economy", "Infrastructure"])]
        else:
            target_cat = backend_cat.strip().lower()
            filtered_df = filtered_df[filtered_df['cluster_category'].apply(lambda x: target_cat in str(x).strip().lower())]

    if filtered_df.empty:
        st.warning("No articles found matching the current filters or search.")
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
            fallback = "https://images.unsplash.com/photo-1555949963-aa79dcee981c?q=80&w=800&auto=format&fit=crop"
            bg = f"url('{fallback}')" if pd.isna(row.get('cluster_image')) or raw_img in ('None', 'nan', '') or not raw_img.startswith('http') else f"url('{raw_img}'), url('{fallback}')"

            pw = int(float(row.get('avg_pro_western', 0.5)) * 100)
            obj = int(float(row.get('avg_objectivity', 0.5)) * 100)

            db_cat = row.get('cluster_category', 'News')
            # Ensure "Infrastructure" renders as "Economy" locally
            if db_cat == 'Infrastructure': db_cat = 'Economy'
            if db_cat in UI_TEXT["English"]["topics"]:
                cat_idx_display = UI_TEXT["English"]["topics"].index(db_cat)
                display_tag = t["topics"][cat_idx_display]
            else:
                display_tag = db_cat

            with (grid_col1 if idx % 2 == 0 else grid_col2):
                card_html = f"""
                <div class="particle-card">
                    <div class="card-img-area" style="background-image: {bg};">
                        <div class="card-img-content">
                            <span class="card-tag">{display_tag}</span>
                            <div class="card-title">{display_title}</div>
                        </div>
                    </div>
                    <div class="card-footer">
                        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 700; color: #475569; margin-bottom: 6px;">
                            <span>🇪🇺 {t.get("pw")} : <span style="color:#0F172A;">{pw}%</span></span>
                            <span>🔍 {t.get("obj")} : <span style="color:#0F172A;">{obj}%</span></span>
                        </div>
                        <div style="display: flex; width: 100%; height: 6px; background-color: #E2E8F0; border-radius: 999px; overflow: hidden;">
                            <div style="width: 50%; display: flex; justify-content: flex-start; border-right: 1px solid #FFFFFF;">
                                <div style="width: {pw}%; background-color: #3B82F6; height: 100%;"></div>
                            </div>
                            <div style="width: 50%; display: flex; justify-content: flex-end;">
                                <div style="width: {obj}%; background-color: #10B981; height: 100%;"></div>
                            </div>
                        </div>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                
                if st.button(" ", key=f"btn_{row.get('cluster_id', idx)}_{idx}", type="primary", use_container_width=True):
                    row_dict = row.to_dict()
                    row_dict['display_title'] = display_title 
                    open_article_modal(row_dict, clean_b, persp_text, bg, t)
                
                st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    st.markdown('<a href="#top-anchor" class="scroll-top-btn">▲</a>', unsafe_allow_html=True)

if __name__ == "__main__":
    run_app()
