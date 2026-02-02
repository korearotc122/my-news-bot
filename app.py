import streamlit as st
import json
import os
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="실시간 증권 뉴스", layout="wide")

# 2. 자동 새로고침 설정 (600,000밀리초 = 10분)
# 이 코드가 있으면 10분마다 브라우저가 알아서 F5를 누릅니다.
st_autorefresh(interval=600000, key="news_refresh")

# 3. 초밀착 디자인 CSS 주입
st.markdown("""
    <style>
    /* 메인 컨테이너 여백 줄이기 */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
    }
    /* 뉴스 항목 간격 최소화 */
    .news-item {
        margin-bottom: -10px;
        line-height: 1.2;
    }
    /* 구분선(HR) 두께 및 간격 조절 */
    hr {
        margin-top: 6px !important;
        margin-bottom: 6px !important;
        border: 0;
        border-top: 1px solid rgba(49, 51, 63, 0.1);
    }
    /* 시간 텍스트 스타일 */
    .time-text {
        color: #888;
        font-size: 0.8rem;
        margin-left: 8px;
    }
    /* 제목 링크 스타일 */
    .news-link {
        text-decoration: none;
        color: #1f77b4;
        font-weight: 600;
        font-size: 0.95rem;
    }
    .news-link:hover {
        color: #ff4b4b;
        text-decoration: underline;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. 제외 키워드 목록 가져오기 함수
def get_exclude_list():
    exclude_file = 'exclude.xlsx'
    if os.path.exists(exclude_file):
        try:
            df = pd.read_excel(exclude_file)
            return df.iloc[:, 0].dropna().astype(str).tolist()
        except:
            return []
    return []

# 사이드바 구성
st.sidebar.header("🔍 설정")
search_term = st.sidebar.text_input("키워드 검색", "")
exclude_list = get_exclude_list()
st.sidebar.info(f"🚫 제외 키워드 {len(exclude_list)}개 작동 중")
st.sidebar.write(f"마지막 업데이트: {datetime.now().strftime('%H:%M:%S')}")

# 메인 화면 타이틀
st.title("🗞️ 증권 실시간 속보")

# 5. 뉴스 데이터 로드 및 출력
if os.path.exists('news.json'):
    with open('news.json', 'r', encoding='utf-8') as f:
        news_data = json.load(f)
    
    count = 0
    for news in news_data:
        # 제외 키워드 필터링
        if any(key.lower() in news['title'].lower() for key in exclude_list if key.strip()):
            continue
        # 검색어 필터링
        if search_term and search_term.lower() not in news['title'].lower():
            continue
            
        # 뉴스 항목 렌더링
        st.markdown(f"""
            <div class="news-item">
                <a class="news-link" href="{news['link']}" target="_blank">
                    • {news['title']}
                </a>
                <span class="time-text">[{news['pub_time']}]</span>
            </div>
            """, unsafe_allow_html=True)
        st.divider()
        count += 1
    
    if count == 0:
        st.info("표시할 뉴스가 없습니다.")
else:
    st.warning("데이터 파일을 찾는 중입니다. 잠시만 기다려 주세요.")
