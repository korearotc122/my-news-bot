import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# 수집할 네이버 증권 실시간 속보 URL
TARGET_URL = "https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258"

def scrape_news():
    # 로봇이 아닌 사람처럼 보이게 하기 위한 설정
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        # 1. 페이지 데이터 가져오기
        resp = requests.get(TARGET_URL, headers=headers)
        resp.encoding = 'euc-kr'  # 네이버 금융 특유의 한글 깨짐 방지
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        new_articles = []
        # 뉴스 항목들이 들어있는 'dl' 태그들을 모두 찾습니다.
        items = soup.select('dl') 

        for item in items:
            # 제목과 링크가 담긴 'a' 태그 찾기
            subject = item.select_one('.articleSubject a')
            if not subject: continue
            
            title = subject.get_text(strip=True)
            
            # [중요] 링크 주소 완성하기
            href = subject['href']
            if href.startswith('http'):
                link = href
            else:
                # /news/read... 처럼 시작하는 경우 앞에 도메인을 붙여줍니다.
                if not href.startswith('/'):
                    href = '/' + href
                link = f"https://finance.naver.com{href}"
            
            # 발행일시 추출 (예: 2026.02.02 21:00)
            wdate = item.select_one('.wdate')
            pub_time = wdate.get_text(strip=True) if wdate else datetime.now().strftime("%Y.%m.%d %H:%M")
            
            new_articles.append({
                "title": title, 
                "link": link, 
                "pub_time": pub_time
            })

        # 2. 기존 데이터(news.json) 불러오기 및 중복 제거
        db_file = 'news.json'
        if os.path.exists(db_file):
            with open(db_file, 'r', encoding='utf-8') as f:
                try:
                    db = json.load(f)
                except:
                    db = []
        else:
            db = []

        # 기존에 저장된 제목들과 대조하여 중복된 뉴스는 넣지 않습니다.
        existing_titles = {a['title'] for a in db}
        added_count = 0
        for a in new_articles:
            if a['title'] not in existing_titles:
                db.insert(0, a) # 최신 뉴스를 리스트 맨 앞에 추가
                added_count += 1
        
        # 데이터가 너무 많아지지 않게 최신순 300개만 유지합니다.
        final_db = db[:300]

        # 3. 파일로 저장
        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump(final_db, f, ensure_ascii=False, indent=4)
            
        print(f"성공: 새로운 뉴스 {added_count}개를 추가하여 총 {len(final_db)}개가 저장되었습니다.")

    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    scrape_news()
