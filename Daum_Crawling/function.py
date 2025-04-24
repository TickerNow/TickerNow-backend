#뉴스 링크를 리스트로 저장장
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
from bs4 import BeautifulSoup
import csv
import os

def get_news_links(driver, pages):
    """뉴스 링크 수집 함수"""
    news_links = []
    page_num = 0

    while page_num < pages:
        time.sleep(2)

        # 뉴스 기사 링크 수집
        articles = driver.find_elements(By.CSS_SELECTOR, 'ul.c-list-basic div.item-title a')
        for article in articles:
            link = article.get_attribute('href')
            if link and link not in news_links: #중복된 링크나, 공백 링크 등 제외
                news_links.append(link)
        
        print(f"{page_num+1} 페이지 뉴스 주소 크롤링 완료")
        page_num += 1
        try :
            if page_num<3 :   #next 페이지 버튼이 4페이지 이상부터 a의 인덱스가 3으로 동일하다. #1233333...
                driver.find_element(By.XPATH, f'//*[@id="dnsColl"]/div[2]/div/div/a[{page_num}]').click()
            else :
                driver.find_element(By.XPATH, f'//*[@id="dnsColl"]/div[2]/div/div/a[3]').click()
        except : 
            continue
        
    return news_links


def get_news_contents(link_list):
    """get_news_links에서 반환된 뉴스 링크 사이트에 접속해서 내용 가져오기"""
    results = []

    for url in link_list:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')

            # 제목
            title_tag = soup.find('h3', class_='tit_view') or soup.find('h2', class_='tit_view')
            title = title_tag.get_text().strip() if title_tag else "제목 없음"

            # 날짜
            date_tag = soup.find('span', class_='num_date')
            date = date_tag.get_text().strip()

            # 본문
            content_tag = soup.find('section', class_='news_view') or soup.find('div', class_='article_view')
            paragraphs = content_tag.find_all('p') if content_tag else []
            content = ' '.join([p.get_text().strip() for p in paragraphs])

            results.append({
                'url': url,
                'title': title,
                'date' : date,
                'content': content
            })
        except Exception as e:
            print(f"[ERROR] 크롤링 실패: {url} | {e}")

    return results


def save_to_csv(news_data, filename="data.csv"):
    # 현재 실행 중인 .py 파일의 디렉토리 기준
    base_dir = os.path.dirname(os.path.abspath(__file__))

    folder_path = os.path.join(base_dir, "csv_folder")
    
    os.makedirs(folder_path, exist_ok=True)  # 폴더 없으면 생성

    full_path = os.path.join(folder_path, filename)

    with open(full_path, mode='w', encoding='utf-8-sig', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['title', 'content', 'date', 'url'])
        writer.writeheader()
        for news in news_data:
            writer.writerow(news)
    
    print(f"[INFO] {full_path} 파일로 저장 완료!")

