import streamlit as st
import json
import os
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="실시간 증권 뉴스", layout="wide")

# 2. 자동 새로고침 설정 (10분)
st_autorefresh(interval=600000, key="news_refresh")

# 3. 디자인 CSS
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; }
    .news-item { margin-bottom: 2px; line-height: 1.2; }
    .time-text { color: #888; font-size: 0.8rem; margin-left: 8px; }
    .news-link { text-decoration: none; color: #1f77b4; font-weight: 600; font-size: 0.95rem; }
    .news-link:hover { color: #ff4b4b; text-decoration: underline; }
    </style>
    """, unsafe_allow_html=True)

def get_exclude_list():
    if os.path.exists('exclude.xlsx'):
        try:
            df = pd.read_excel('exclude.xlsx')
            return df.iloc[:, 0].dropna().astype(str).tolist()
        except: return []
    return []

st.sidebar.header("🔍 설정")
search_term = st.sidebar.text_input("키워드 검색", "")
exclude_list = get_exclude_list()
st.sidebar.info(f"🚫 제외 키워드 {len(exclude_list)}개 작동 중")
st.sidebar.write(f"최근 갱신: {datetime.now().strftime('%H:%M:%S')}")

st.title("🗞️ 증권 실시간 속보")

if os.path.exists('news.json'):
    with open('news.json', 'r', encoding='utf-8') as f:
        news_data = json.load(f)
    
    count = 0
    for news in news_data:
        if any(key.lower() in news['title'].lower() for key in exclude_list if key.strip()):
            continue
        if search_term and search_term.lower() not in news['title'].lower():
            continue
            
        # [수정] st.divider() 대신 HTML의 <hr> 태그를 사용하여 에러를 방지하고 간격을 조절합니다.
        st.markdown(f"""
            <div class="news-item">
                <a class="news-link" href="{news['link']}" target="_blank">
                    • {news['title']}
                </a>
                <span class="time-text">[{news['pub_time']}]</span>
            </div>
            <hr style="margin: 8px 0; opacity: 0.2;">
            """, unsafe_allow_html=True)
        count += 1
    
    if count == 0: st.info("표시할 뉴스가 없습니다.")
else:
    st.warning("데이터 수집 중입니다...")
