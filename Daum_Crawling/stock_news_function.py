import os
import json
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import time

# 1. 셀레니움으로 페이지 열기
driver = webdriver.Chrome()
driver.get("https://finance.daum.net/news#stock")
time.sleep(2)  # 페이지 렌더링 대기

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
driver.quit()

# 2. 뉴스 항목 찾기
news_items = soup.find_all('li', class_='imgB')

# 3. 뉴스 데이터를 리스트로 수집
news_data = []
for item in news_items:
    title_tag = item.find('a', class_='tit')
    title = title_tag.text.strip() if title_tag else ''

    text_tag = item.find('a', class_='txt')
    text = text_tag.text.strip() if text_tag else ''

    article_url = title_tag['href'] if title_tag else ''

    img_tag = item.find('img')
    img_url = img_tag['src'] if img_tag else ''

    date_tag = item.find('p', class_='date')
    source, date = '', ''
    if date_tag:
        parts = date_tag.text.strip().split('·')
        if len(parts) == 2:
            source = parts[0].strip()
            date = parts[1].strip()

    news_data.append({
        '제목': title,
        '요약': text,
        '이미지_URL': img_url,
        '기사_URL': article_url,
        '뉴스사': source,
        '날짜': date
    })

# 4. DataFrame 생성
df = pd.DataFrame(news_data)

# 5. JSON으로 저장
base_dir = os.path.dirname(os.path.abspath(__file__))

# 같은 디렉토리에 JSON 저장
json_path = os.path.join(base_dir, "stock_news.json")
df.to_json(json_path, orient='records', force_ascii=False, indent=4)

print("JSON 파일 저장 완료:", json_path)
