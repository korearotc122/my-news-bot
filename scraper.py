import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

TARGET_URL = "https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258"

def scrape_news():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    try:
        resp = requests.get(TARGET_URL, headers=headers)
        resp.encoding = 'euc-kr'
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        new_articles = []
        items = soup.select('dl') 

        for item in items:
            subject = item.select_one('.articleSubject a')
            if not subject: continue
            
            title = subject.get_text(strip=True)
            href = subject['href']
            link = href if href.startswith('http') else f"https://finance.naver.com{href if href.startswith('/') else '/' + href}"
            
            wdate = item.select_one('.wdate')
            pub_time = wdate.get_text(strip=True) if wdate else datetime.now().strftime("%Y.%m.%d %H:%M")
            
            new_articles.append({"title": title, "link": link, "pub_time": pub_time})

        db_file = 'news.json'
        db = []
        if os.path.exists(db_file):
            with open(db_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    try: db = json.loads(content)
                    except: db = []

        existing_titles = {a['title'] for a in db}
        added_count = 0
        for a in new_articles:
            if a['title'] not in existing_titles:
                db.insert(0, a)
                added_count += 1
        
        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump(db[:300], f, ensure_ascii=False, indent=4)
            
        print(f"성공: 새로운 뉴스 {added_count}개 추가됨.")

    except Exception as e:
        print(f"에러: {e}")
        exit(1)

if __name__ == "__main__":
    scrape_news()
