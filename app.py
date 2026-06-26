import streamlit as st
import sqlite3
import pandas as pd

# --- UI TRANSLATION DICTIONARY (Updated with Crime & Accidents) ---
UI_TEXT = {
    "English": {
        "topics": ["All Topics", "Politics", "Economy", "Infrastructure", "Technology", "Culture", "Entertainment", "Sports", "Crime & Accidents"],
        "geos": ["All Regions", "North Macedonia", "Kosovo", "Albania", "Regional"],
        "geo_labels": ["🌍 Global", "🇲🇰 MKD", "🇽🇰 KOS", "🇦🇱 ALB", "🗺️ Balkans"],
        "lang_header": "🌐 Language",
        "geo_header": "📍 Geography",
        "db_header": "📬 Daily Briefing",
        "db_sub": "Narrative blindspots delivered straight to your inbox.",
        "api_header": "⚙️ Enterprise API",
        "api_sub": "Integrate real-time narrative clustering into your dashboards.",
        "subscribe": "Subscribe",
        "success": "Thank you! You are subscribed.",
        "api_btn": "View API Docs",
        "blindspots_btn": "👁️ Blindspots",
        "blindspots": "Strategic Blindspots",
        "blindspots_sub": "Regional narratives and crucial information updates you might have missed completely from mainstream local coverage.",
        "modal_title": "Deep Dive Analysis",
        "pw": "Pro-Western",
        "obj": "Objectivity",
        "btn_back": "Close",
        "sources": "Original Sources",
        "how_ai_works": "🧠 How AI Works",
        "db_col_title": "title_en",
        "db_col_bullets": "bullets_en",
        "db_col_persp": "perspective_en"
    },
    "Shqip": {
        "topics": ["Të gjitha", "Politikë", "Ekonomi", "Infrastrukturë", "Teknologji", "Kulturë", "Show Biz", "Sport", "Kronika e Zezë"],
        "geos": ["Të gjitha", "Maqedonia e Veriut", "Kosova", "Shqipëria", "Rajonale"],
        "geo_labels": ["🌍 Global", "🇲🇰 MKD", "🇽🇰 KOS", "🇦🇱 ALB", "🗺️ Ballkan"],
        "lang_header": "🌐 Gjuha",
        "geo_header": "📍 Gjeografia",
        "db_header": "📬 Informimi Ditor",
        "db_sub": "Të pathënat e narrativave direkt në emailin tuaj.",
        "api_header": "⚙️ API për Biznese",
        "api_sub": "Integroni grupimin e narrativave në kohë reale.",
        "subscribe": "Abonohu",
        "success": "Faleminderit! Jeni abonuar.",
        "api_btn": "Shiko Dokumentacionin",
        "blindspots_btn": "👁️ Të pathënat",
        "blindspots": "Të pathënat Strategjike",
        "blindspots_sub": "Narrativa rajonale strategjike dhe informacione jetike që mund t'i keni anashkaluar.",
        "modal_title": "Analiza e Thelluar",
        "pw": "Pro-Perëndimor",
        "obj": "Objektiviteti",
        "btn_back": "Mbyll",
        "sources": "Burimet Origjinale",
        "how_ai_works": "🧠 Si funksionon AI?",
        "db_col_title": "title_sq",
        "db_col_bullets": "bullets_sq",
        "db_col_persp": "perspective_sq"
    },
    "Македонски": {
        "topics": ["Сите Теми", "Политика", "Економија", "Инфраструктура", "Технологија", "Култура", "Забава", "Спорт", "Црна Хроника"],
        "geos": ["Сите Региони", "Северна Македонија", "Косово", "Албанија", "Регионално"],
        "geo_labels": ["🌍 Глобално", "🇲🇰 MKD", "🇽🇰 KOS", "🇦🇱 ALB", "🗺️ Балкан"],
        "lang_header": "🌐 Јазик",
        "geo_header": "📍 Географија",
        "db_header": "📬 Дневен Брифинг",
        "db_sub": "Наративни слепи точки доставени директно во вашето сандаче.",
        "api_header": "⚙️ Enterprise API",
        "api_sub": "Интегрирајте групирање на наративи во реално време.",
        "subscribe": "Претплати се",
        "success": "Ви благодариме! Претплатени сте.",
        "api_btn": "Види API Документација",
        "blindspots_btn": "👁️ Игнорирани вести",
        "blindspots": "Игнорирани вести",
        "blindspots_sub": "Регионални наративи и клучни информации кои можеби целосно сте ги пропуштиле во главните локални медиуми.",
        "modal_title": "Длабинска Анализа",
        "pw": "Про-Западно",
        "obj": "Објективност",
        "btn_back": "Затвори",
        "sources": "Оригинални Извори",
        "how_ai_works": "🧠 Како работи ВИ?",
        "db_col_title": "title_mk",
        "db_col_bullets": "bullets_mk",
        "db_col_persp": "perspective_mk"
    },
    "Srpski": {
        "topics": ["Sve Teme", "Politika", "Ekonomija", "Infrastruktura", "Tehnologija", "Kultura", "Zabava", "Sport", "Crna Hronika"],
        "geos": ["Svi Regioni", "Severna Makedonija", "Kosovo", "Albanija", "Regionalno"],
        "geo_labels": ["🌍 Globalno", "🇲🇰 MKD", "🇽🇰 KOS", "🇦🇱 ALB", "🗺️ Balkan"],
        "lang_header": "🌐 Jezik",
        "geo_header": "📍 Geografija",
        "db_header": "📬 Dnevni Brifing",
        "db_sub": "Narativi koje ste možda propustili direktno u vaš inbox.",
        "api_header": "⚙️ Enterprise API",
        "api_sub": "Integrišite grupisanje narativa u realnom vremenu.",
        "subscribe": "Pretplati se",
        "success": "Hvala! Pretplatili ste se.",
        "api_btn": "Vidi API Dokumentaciju",
        "blindspots_btn": "👁️ Slepe tačke",
        "blindspots": "Slepe tačke",
        "blindspots_sub": "Narativi koje ste možda propustili.",
        "modal_title": "Dubinska Analiza",
        "pw": "Pro-Zapadno",
        "obj": "Objektivnost",
        "btn_back": "Zatvori",
        "sources": "Originalni Izvori",
        "how_ai_works": "🧠 Kako radi AI?",
        "db_col_title": "title_sr",
        "db_col_bullets": "bullets_sr",
        "db_col_persp": "perspective_sr"
    }
}

# --- DATABASE CONNECTION ---
def get_connection(): return sqlite3.connect('news_aggregator.db')

def get_database_data():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM articles WHERE cluster_id IS NOT NULL ORDER BY article_id DESC", conn)
    conn.close()
    return df

@st.dialog(" ", width="large")
def open_article_modal(row, clean_bullets, perspective_html, bg_style, t_dict):
    st.markdown(f"<h3 style='margin-top:-20px; margin-bottom:15px;'>{t_dict.get('modal_title')}</h3>", unsafe_allow_html=True)
    header_col1, header_col2 = st.columns([1, 1.5], gap="small")
    pw = int(float(row.get('geo_pro_western', 0.5)) * 100)
    obj = int(float(row.get('narrative_objectivity', 0.5)) * 100) 
    
    with header_col1:
        st.markdown(f"""<div style="width: 100%; height: 220px; border-radius: 16px; background-image: {bg_style}; background-size: cover; background-position: center; margin-bottom: 8px;"></div>""", unsafe_allow_html=True)
        # Bar Logic: Blue starts left-to-right (50%), Green starts right-to-left (50%)
        st.markdown(f"""
        <div style="background: rgba(148, 163, 184, 0.1); padding: 12px; border-radius: 12px;">
            <div style="font-size:0.8rem; font-weight:700;">{t_dict['pw']}: {pw}%</div>
            <div style="width:100%; height:6px; background:#E2E8F0; border-radius:999px; margin-bottom:10px;"><div style="width:{pw}%; height:100%; background:#3B82F6; border-radius:999px;"></div></div>
            <div style="font-size:0.8rem; font-weight:700;">{t_dict['obj']}: {obj}%</div>
            <div style="width:100%; height:6px; background:#E2E8F0; border-radius:999px;"><div style="width:{obj}%; height:100%; background:#10B981; border-radius:999px; margin-left:auto;"></div></div>
        </div>
        """, unsafe_allow_html=True)
        
    with header_col2:
        st.markdown(f"### {row[t_dict['db_col_title']]}")
        for b in clean_bullets: st.markdown(f"• {b}")

    # Full Width Narrative Section
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("#### Strategic Analysis")
    st.markdown(f"<div style='font-size: 1.1rem; line-height: 1.7; padding: 15px; background: #F8FAFC; border-radius: 10px;'>{perspective_html}</div>", unsafe_allow_html=True)

# --- MAIN PAGE ---
def run_app():
    st.set_page_config(layout="wide")
    # ... (Rest of your app layout code remains the same) ...
    # Ensure you replace the category list in run_app() to include the new topic
