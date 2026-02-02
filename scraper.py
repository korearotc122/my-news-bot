name: 10-Min News Scraper

on:
  schedule:
    - cron: '*/10 * * * *'  # 10분마다 자동으로 실행
  workflow_dispatch:        # 수동 실행 버튼 활성화

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: 코드 체크아웃
        uses: actions/checkout@v3

      - name: Python 설치
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: 라이브러리 설치
        run: |
          pip install requests beautifulsoup4 pandas openpyxl

      - name: 뉴스 수집 실행
        run: python scraper.py

      - name: 변경사항 저장 및 업로드
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          
          # [핵심] 원격 저장소의 최신 내용을 먼저 가져와 합칩니다 (충돌 방지)
          git pull --rebase origin main
          
          git add news.json
          
          # 저장할 내용이 있는 경우에만 커밋하고 푸시합니다.
          if [ -n "$(git status --porcelain)" ]; then
            git commit -m "Update news data"
            git push
          else
            echo "변경사항이 없어 푸시를 생략합니다."
          fi
