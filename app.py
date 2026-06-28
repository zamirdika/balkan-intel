import streamlit as st
import sqlite3
import pandas as pd

# --- UI TRANSLATION DICTIONARY ---
UI_TEXT = {
    "English": {
        "nav": ["🏠 Home", "🔍 Search", "🌐 Lang"],
        "topics": ["All Topics", "Politics", "Economy", "Technology", "Culture", "Entertainment", "Sports", "Crime & Accidents"],
        "geos": ["All Regions", "North Macedonia", "Kosovo", "Albania", "Serbia", "Bosnia and Herzegovina", "Montenegro", "Regional"],
        "geo_labels": ["🌍 Global", "🇲🇰 MKD", "🇽🇰 KOS", "🇦🇱 ALB", "🇷🇸 SRB", "🇧🇦 BIH", "🇲🇪 MNE", "🗺️ Balkans"],
        "search_label": "Search narratives, topics, or keywords...",
        "filter_geo": "Geographies", "filter_cat": "Categories",
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
        "nav": ["🏠 Kryefaqja", "🔍 Kërko", "🌐 Gjuha"],
        "topics": ["Të gjitha", "Politikë", "Ekonomi", "Teknologji", "Kulturë", "Show Biz", "Sport", "Kronika e Zezë"],
        "geos": ["Të gjitha", "Maqedonia e Veriut", "Kosova", "Shqipëria", "Serbia", "Bosnja dhe Hercegovina", "Mali i Zi", "Rajonale"],
        "geo_labels": ["🌍 Global", "🇲🇰 MKD", "🇽🇰 KOS", "🇦🇱 ALB", "🇷🇸 SRB", "🇧🇦 BIH", "🇲🇪 MNE", "🗺️ Ballkan"],
        "search_label": "Kërko narrativa, tema ose fjalë kyçe...",
        "filter_geo": "Gjeografitë", "filter_cat": "Kategoritë",
        "modal_title": "Analiza e Thelluar", "pw": "Pro-Perëndimor", "obj": "Objektiviteti", "btn_back": "Mbyll",
        "sources": "Burimet Origjinale", "analysis_title": "Përmbledhja e Narrativës",
        "pw_help": "Mat përafrimin me qëndrimet gjeopolitike të BE/SHBA/NATO-s.",
        "obj_help": "Mat raportimin faktik kundrejt gjuhës emocionale apo të anashme.",
        "divergence": "Divergjenca",
        "div_help": "Mat shkallën në të cilën kjo ngjarje anashkalohet ose kornizohet në mënyrë selektive krahasuar me rajonin.",
        "read_source": "Lexo Origjinalin ↗",
        "db_col_title": "title_sq", "db_col_bullets": "bullets_sq", "db_col_persp": "perspective_sq"
    },
    "Македонски": {
        "nav": ["🏠 Дома", "🔍 Пребарај", "🌐 Јазик"],
        "topics": ["Сите Теми", "Политика", "Економија", "Технологија", "Култура", "Забава", "Спорт", "Црна Хроника"],
        "geos": ["Сите Региони", "Северна Македонија", "Косово", "Албанија", "Србија", "Босна и Херцеговина", "Црна Гора", "Регионално"],
        "geo_labels": ["🌍 Глобално", "🇲🇰 MKD", "🇽🇰 KOS", "🇦🇱 ALB", "🇷🇸 SRB", "🇧🇦 BIH", "🇲🇪 MNE", "🗺️ Балкан"],
        "search_label": "Пребарајте наративи, теми или клучни зборови...",
        "filter_geo": "Географии", "filter_cat": "Категории",
        "modal_title": "Длабинска Анализа", "pw": "Про-Западно", "obj": "Објективност", "btn_back": "Затвори",
        "sources": "Оригинални Извори", "analysis_title": "Наративно Резиме",
        "pw_help": "Го мери усогласувањето со геополитичките позиции на ЕУ/САД/НАТО.",
        "obj_help": "Го мери фактуелното известување наспроти емотивниот или пристрасен јазик.",
        "divergence": "Дивергенција",
        "div_help": "Мери колку оваа вест е изоставена или селективно врамена во споредба со регионалниот просек.",
        "read_source": "Оригинален Напис ↗",
        "db_col_title": "title_mk", "db_col_bullets": "bullets_mk", "db_col_persp": "perspective_mk"
    }
}

# --- STATE MANAGEMENT ---
if 'current_view' not in st.session_state: st.session_state.current_view = "Home"
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
               MAX(title_en) as title_en, MAX(title_sq) as title_sq, MAX(title_mk) as title_mk, 
               MAX(bullets_en) as bullets_en, MAX(bullets_sq) as bullets_sq, MAX(bullets_mk) as bullets_mk, 
               MAX(perspective_en) as perspective_en, MAX(perspective_sq) as perspective_sq, MAX(perspective_mk) as perspective_mk, 
               AVG(geo_pro_western) as avg_pro_western, AVG(narrative_objectivity) as avg_objectivity, AVG(narrative_divergence_score) as avg_divergence,
               GROUP_CONCAT(source_domain, ', ') as sources, GROUP_CONCAT(original_title, '||') as orig_titles,
               GROUP_CONCAT(original_url, '||') as orig_urls, MAX(image_url) as cluster_image
        FROM articles WHERE cluster_id IS NOT NULL GROUP BY cluster_id ORDER BY article_id DESC
    """
    try: df = pd.read_sql_query(query, conn)
    except: df = pd.DataFrame()
    conn.close()
    return df

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

# --- MAIN APP ---
def run_app():
    st.set_page_config(page_title="Balkan Intel", layout="wide", initial_sidebar_state="collapsed")
    t = UI_TEXT[st.session_state.lang_code]

    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #0B0F19; color: #F8FAFC; }
        [data-testid="collapsedControl"], [data-testid="stSidebar"] { display: none !important; }
        header { display: none !important; }
        .block-container { padding-top: 2rem !important; padding-bottom: 100px !important; }

        /* BRAND HEADER */
        .brand-header { font-size: 1.8rem; font-weight: 800; letter-spacing: -0.05em; margin-bottom: 1rem; }
        .brand-header span:first-child { color: #3B82F6; }
        .brand-header span:last-child { color: #F8FAFC; }
        
        /* BOTTOM NAVIGATION BAR ROUTING HACK */
        div[data-testid="stRadio"]:has(> label[data-testid="stWidgetLabel"] > div > p:contains("NAV_ROUTER")) {
            position: fixed; bottom: 0; left: 0; width: 100%; background: rgba(15, 23, 42, 0.95); backdrop-filter: blur(10px);
            z-index: 999999; padding: 12px 10px; border-top: 1px solid #1E293B; margin: 0; display: flex; justify-content: center;
        }
        div[data-testid="stRadio"]:has(> label[data-testid="stWidgetLabel"] > div > p:contains("NAV_ROUTER")) > label { display: none; }
        div[data-testid="stRadio"]:has(> label[data-testid="stWidgetLabel"] > div > p:contains("NAV_ROUTER")) > div[role="radiogroup"] {
            display: flex; flex-direction: row; justify-content: space-around; width: 100%; max-width: 600px;
        }
        div[data-testid="stRadio"]:has(> label[data-testid="stWidgetLabel"] > div > p:contains("NAV_ROUTER")) label {
            background: transparent !important; border: none !important; flex: 1; text-align: center; justify-content: center;
        }
        div[data-testid="stRadio"]:has(> label[data-testid="stWidgetLabel"] > div > p:contains("NAV_ROUTER")) label p {
            color: #64748B !important; font-size: 0.85rem !important; font-weight: 700 !important; display: flex; flex-direction: column; align-items: center; gap: 4px;
        }
        div[data-testid="stRadio"]:has(> label[data-testid="stWidgetLabel"] > div > p:contains("NAV_ROUTER")) label:has(input:checked) p { color: #3B82F6 !important; }

        /* SEARCH SCREEN GRID BUTTONS */
        div.stButton > button { background-color: #1E293B; color: #F8FAFC; border: 1px solid #334155; border-radius: 12px; height: 60px; font-weight: 700; width: 100%; }
        div.stButton > button:hover { border-color: #3B82F6; color: #3B82F6; background-color: #0F172A; }
        
        /* SEARCH BAR STYLING */
        div[data-testid="stTextInput"] input { background-color: #1E293B !important; color: #F8FAFC !important; border: 1px solid #334155 !important; border-radius: 20px; padding: 15px 20px; font-size: 1.1rem; }
        
        /* FEED CARDS (Dark Theme adapted) */
        .particle-card { background: #1E293B; border-radius: 20px; border: 1px solid #334155; height: 380px; display: flex; flex-direction: column; overflow: hidden; position: relative; }
        .card-img-area { height: 280px; background-color: #0F172A; background-size: cover; background-position: center; position: relative; display: flex; flex-direction: column; justify-content: flex-end; padding: 20px 24px; }
        .card-img-area::after { content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to top, rgba(15,23,42, 0.95) 0%, rgba(15,23,42, 0.5) 30%, rgba(15,23,42, 0) 50%); z-index: 1; }
        .card-img-content { position: relative; z-index: 2; width: 100%; }
        .card-tag { background: #3B82F6; color: #FFFFFF; font-size: 0.65rem; font-weight: 800; padding: 4px 10px; border-radius: 6px; text-transform: uppercase; display: inline-block; margin-bottom: 12px; }
        .card-title { font-size: clamp(1.05rem, 1.15vw, 1.2rem); font-weight: 800; color: #F8FAFC !important; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; text-shadow: 0 2px 6px rgba(0,0,0,0.8) !important; }
        .card-footer { height: 100px; padding: 16px 24px; background: #1E293B; display: flex; flex-direction: column; justify-content: center; gap: 8px; }
        
        /* INVISIBLE CLICK ELEMENT TRIGGER FOR CARDS */
        div[data-testid="stButton"]:has(button[kind="primary"]) { margin: 0 !important; padding: 0 !important; height: 0px !important; overflow: visible !important; }
        button[kind="primary"] { position: absolute !important; background: transparent !important; border: none !important; color: transparent !important; height: 0px !important; padding: 0 !important; box-shadow: none !important; }
        button[kind="primary"]::after { content: ""; position: absolute; bottom: 0; left: 0; width: 100%; height: 380px; z-index: 99; cursor: pointer; }

        /* TOOLTIP */
        .tooltip-sup { font-size: 0.65rem; vertical-align: super; background-color: #334155; color: #F8FAFC; border-radius: 50%; width: 14px; height: 14px; display: inline-flex; align-items: center; justify-content: center; margin-left: 4px; font-weight: 800; cursor: pointer; position: relative; }
    </style>
    """, unsafe_allow_html=True)

    # BRAND HEADER
    st.markdown("""<div class="brand-header"><span>Balkan</span><span>Intel</span></div>""", unsafe_allow_html=True)

    # BOTTOM NAVIGATION ROUTER
    # We use a completely hidden label text "NAV_ROUTER" so our CSS knows exactly which radio button to stick to the bottom
    nav_selection = st.radio("NAV_ROUTER", t["nav"], horizontal=True, index=t["nav"].index(next((x for x in t["nav"] if st.session_state.current_view in x), t["nav"][0])))
    
    # Update state based on nav click
    if t["nav"][0] in nav_selection: st.session_state.current_view = "Home"
    elif t["nav"][1] in nav_selection: st.session_state.current_view = "Search"
    elif t["nav"][2] in nav_selection: st.session_state.current_view = "Language"

    df = get_database_data()

    # ==========================================
    # VIEW: SEARCH & EXPLORE
    # ==========================================
    if st.session_state.current_view == "Search":
        search_input = st.text_input("🔍", placeholder=t["search_label"], label_visibility="collapsed")
        if search_input:
            st.session_state.search_query = search_input
            st.session_state.active_cat = "All Topics"
            st.session_state.active_geo = "All Regions"
            st.session_state.current_view = "Home"
            st.rerun()

        st.markdown(f"<h4 style='margin-top: 20px; font-size: 1rem; color: #94A3B8;'>{t['filter_cat']}</h4>", unsafe_allow_html=True)
        cat_cols = st.columns(2)
        for i, cat in enumerate(t["topics"][1:]): # Skip 'All Topics'
            with cat_cols[i % 2]:
                if st.button(cat, key=f"cat_{i}", use_container_width=True):
                    st.session_state.active_cat = UI_TEXT["English"]["topics"][i+1] # Save backend English tag
                    st.session_state.search_query = ""
                    st.session_state.current_view = "Home"
                    st.rerun()

        st.markdown(f"<h4 style='margin-top: 20px; font-size: 1rem; color: #94A3B8;'>{t['filter_geo']}</h4>", unsafe_allow_html=True)
        geo_cols = st.columns(2)
        for i, geo in enumerate(t["geos"][1:]): # Skip 'All Regions'
            with geo_cols[i % 2]:
                # Combine Flag and Name
                display_label = f"{t['geo_labels'][i+1].split(' ')[0]} {geo}" 
                if st.button(display_label, key=f"geo_{i}", use_container_width=True):
                    st.session_state.active_geo = UI_TEXT["English"]["geos"][i+1]
                    st.session_state.search_query = ""
                    st.session_state.current_view = "Home"
                    st.rerun()

    # ==========================================
    # VIEW: LANGUAGE SETTINGS
    # ==========================================
    elif st.session_state.current_view == "Language":
        st.markdown(f"### {t['lang_header']}")
        st.markdown("<p style='color: #94A3B8;'>Select your preferred language interface and translation perspective.</p>", unsafe_allow_html=True)
        
        lang_options = ["English", "Shqip", "Македонски"]
        for l_opt in lang_options:
            if st.button(f"{'✅ ' if st.session_state.lang_code == l_opt else ''}{l_opt}", key=f"lang_{l_opt}"):
                st.session_state.lang_code = l_opt
                st.session_state.current_view = "Home"
                st.rerun()

    # ==========================================
    # VIEW: HOME FEED
    # ==========================================
    else: # "Home"
        # Display Active Filters
        active_filters = []
        if st.session_state.active_cat != "All Topics": active_filters.append(st.session_state.active_cat)
        if st.session_state.active_geo != "All Regions": active_filters.append(st.session_state.active_geo)
        if st.session_state.search_query: active_filters.append(f'"{st.session_state.search_query}"')
        
        if active_filters:
            st.markdown(f"""
            <div style='display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap;'>
                <div style='background: #1E293B; padding: 6px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; color: #94A3B8;'>Active Filters:</div>
                {''.join([f"<div style='background: #3B82F6; padding: 6px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; color: #FFF;'>{f}</div>" for f in active_filters])}
            </div>
            """, unsafe_allow_html=True)
            if st.button("Clear Filters", type="secondary"):
                st.session_state.active_cat = "All Topics"
                st.session_state.active_geo = "All Regions"
                st.session_state.search_query = ""
                st.rerun()

        # Apply Filters to Data
        filtered_df = df.copy()
        
        if st.session_state.search_query and not filtered_df.empty:
            sq = st.session_state.search_query.lower()
            filtered_df = filtered_df[
                filtered_df['title_en'].str.lower().str.contains(sq, na=False) |
                filtered_df['title_sq'].str.lower().str.contains(sq, na=False) |
                filtered_df['title_mk'].str.lower().str.contains(sq, na=False)
            ]
            
        if st.session_state.active_geo != "All Regions" and not filtered_df.empty: 
            target_geo = st.session_state.active_geo.strip().lower()
            filtered_df = filtered_df[filtered_df['cluster_geo_scope'].apply(lambda x: target_geo in str(x).strip().lower())]
            
        if st.session_state.active_cat != "All Topics" and not filtered_df.empty: 
            if st.session_state.active_cat == "Economy":
                filtered_df = filtered_df[filtered_df['cluster_category'].isin(["Economy", "Infrastructure"])]
            else:
                target_cat = st.session_state.active_cat.strip().lower()
                filtered_df = filtered_df[filtered_df['cluster_category'].apply(lambda x: target_cat in str(x).strip().lower())]

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
                if db_cat in UI_TEXT["English"]["topics"]:
                    cat_idx_display = UI_TEXT["English"]["topics"].index(db_cat)
                    display_tag = t["topics"][cat_idx_display]
                else: display_tag = db_cat

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

if __name__ == "__main__":
    run_app()
