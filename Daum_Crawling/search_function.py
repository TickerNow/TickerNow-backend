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
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import pandas as pd
import pyperclip


def daum_search(search, page_count):
    '''셀레니움과 BeautifulSoup를 사용하여 Daum 검색창에서 기업 검색 후 해당 기업의 뉴스를 크롤링하고 csv로 저장 후 MySQL의 DB에 저장하는 함수'''
    # search = input("검색 하세요 : ")
    # page_count = input("원하는 페이지 수 : ")
    url = 'https://www.daum.net/'
    driver = webdriver.Chrome()
    driver.get(url)

    #검색창 로딩 대기 (최대 5초)
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="q"]'))
    )

    #검색 값 복사
    pyperclip.copy(search)

    #검색 값 검색창에 붙여넣기
    driver.find_element(By.XPATH, '//*[@id="q"]').send_keys(Keys.CONTROL + 'v')
    time.sleep(1)

    #검색 버튼 클릭릭
    driver.find_element(By.XPATH, '//*[@id="daumSearch"]/fieldset/div/div/button[3]').click()
    time.sleep(2)

    #다음에서 검색을 할 경우 뉴스 항목 위치가 계속 바껴서 찾는 프로세스
    li_items = driver.find_elements(By.CSS_SELECTOR, 'ul.list_tab > li')

    for li in li_items:
        try:
            if '뉴스' in li.text:
                li.click()
                break
        except:
            continue

    time.sleep(2)
    
    news_links = get_news_links(driver, int(page_count))  # 수집한 링크
    driver.close()
    news_data = get_news_contents(news_links)  # 본문 수집
    save_to_csv(news_data,f"daum_search_data_{search}.csv") #다음 검색 -> 수집한 타이틀, 내용, 날짜, 링크를 csv파일로 저장
    save_to_database_search_information(search)
    

def get_news_links(driver, pages):
    """뉴스 링크 수집 함수 -> daum_search() 함수에 사용"""
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
    """get_news_links에서 반환된 뉴스 링크 사이트에 접속해서 내용 가져오기 -> daum_search() 함수에 사용 """
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
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(base_dir, "csv_folder/daum_news_data")
    os.makedirs(folder_path, exist_ok=True)

    full_path = os.path.join(folder_path, filename)

    with open(full_path, mode='w', encoding='utf-8-sig', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['title', 'content', 'date', 'url'])
        writer.writeheader()
        
        for news in news_data:
            # date가 문자열일 경우 datetime 객체로 변환 후 포맷 변환
            # 예: 원본 '2025-04-25 10:21:00' -> '04/25/2025'
            original_date = news['date']
            if isinstance(original_date, str):
                # 원본 포맷에 맞게 파싱, 예시로 ISO 형식 가정
                dt = datetime.strptime(original_date, "%Y. %m. %d. %H:%M")
            else:
            
                dt = original_date  # 이미 datetime 객체라면 그대로 사용
                
            news['date'] = dt.strftime("%Y-%m-%d")  # MM/dd/yyyy 포맷으로 변환
            
            writer.writerow(news)
    
    print(f"[INFO] {full_path} 파일로 저장 완료!")

def save_to_database_search_information(search):
    '''MySQL의 DB에 저장하는 함수 -> daum_search() 함수에 사용'''
    os.environ["PYSPARK_PYTHON"] = "C:/Users/jaehy/anaconda3/python.exe" # 파이썬 경로를 지정하니까 코드가 돌아감

    spark = SparkSession.builder \
        .appName("MySQL Export") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "4g") \
        .config("spark.local.ip", "127.0.0.1") \
        .config("spark.python.worker.memory", "2g") \
        .config("spark.driver.extraClassPath", "C:/mysql-connector-j-8.3.0/mysql-connector-j-8.3.0.jar") \
        .getOrCreate()
        #.config("spark.jars", "file:///C:/mysql-connector-j-8.3.0/mysql-connector-j-8.3.0.jar") \

    #읽어올 csv 파일 설정
    pdf = pd.read_csv(fr'C:/JaeHyeok/Crawling/Daum_Crawling/csv_folder/daum_news_data/daum_search_data_{search}.csv') # search_information의 csv 파일

    sdf = spark.createDataFrame(pdf) #csv 파일을 스파크 데이터프레임으로 변경

    #jdbc를 사용하여 MySQL 연결
    sdf.write.format("jdbc").options(
        url="jdbc:mysql://localhost:3306/news_project",  # DB 정보
        driver="com.mysql.cj.jdbc.Driver",
        dbtable="search_information",  # 저장할 테이블 이름
        user="root",
        password= 5941
    ).mode("append").save()

    spark.stop()
