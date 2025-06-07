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
from pyspark.sql.functions import *
import pandas as pd
import pyperclip
from selenium.webdriver.chrome.options import Options

def daum_news_load(spark, search, page_count):
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

    #검색 버튼 클릭
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
    save_news_data_to_db(spark, search, news_data, table_name="search_information") #DB에 바로 적재

    ##csv 파일 저장 후 적재 함수
    # save_to_csv(news_data,f"daum_news_{search}.csv") #다음 검색 -> 수집한 타이틀, 내용, 날짜, 링크를 csv파일로 저장
    # save_to_database_search_information(spark, search)
    

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
            
            writer.writerow(news)
    
    print(f"[INFO] {full_path} 파일로 저장 완료!")

def save_to_database_search_information(spark, search):
    '''MySQL의 DB에 기업 관련 뉴스를 저장하는 함수 -> daum_search() 함수에 사용'''
    os.environ["PYSPARK_PYTHON"] = "C:/Users/jaehy/anaconda3/python.exe" # 파이썬 경로를 지정하니까 코드가 돌아감

    #읽어올 csv 파일 설정
    file_path = f'C:/JaeHyeok/Crawling/Daum_Crawling/csv_folder/daum_news_data/daum_news_{search}.csv'
        
    #spark DataFrame으로 변환, 
    sdf = (spark.read.option("header", True)
            .option("multiLine", True)            # 여러 줄 텍스트 처리
            .option("escape", '"')                # 큰따옴표로 감싼 데이터 인식
            .option("quote", '"')                 # 문자열 구분 따옴표
            .csv(file_path))
    
    # DB에 적재하기 위한 date 형식 변환
    sdf = sdf.withColumn("date", to_timestamp(col("date"), "yyyy. M. d. HH:mm"))
    sdf = sdf.withColumn("date", date_format(col("date"), "yyyy-MM-dd")) 

    #jdbc를 사용하여 MySQL 연결
    sdf.write.format("jdbc").options(
        url="jdbc:mysql://localhost:3306/news_project",  # DB 정보
        driver="com.mysql.cj.jdbc.Driver",
        dbtable="search_information",  # 저장할 테이블 이름
        user="root",
        password= 5941
    ).mode("append").save()


def save_news_data_to_db(spark, search, news_data, table_name="search_information"):
    """크롤링한 뉴스 데이터를 DB에 직접 저장 (CSV 파일 없이)"""
    # Pandas DataFrame으로 변환
    pdf = pd.DataFrame(news_data)

    pdf.insert(0, "search", search)
    
    # Spark DataFrame으로 변환
    sdf = spark.createDataFrame(pdf)

    # 날짜 컬럼 가공: 문자열 → Timestamp → yyyy-MM-dd 형식
    sdf = sdf.withColumn("date", to_timestamp("date", "yyyy. M. d. HH:mm"))
    sdf = sdf.withColumn("date", date_format("date", "yyyy-MM-dd"))

    # DB 적재
    sdf.write.format("jdbc").options(
        url="jdbc:mysql://localhost:3306/news_project",
        driver="com.mysql.cj.jdbc.Driver",
        dbtable=table_name,
        user="root",
        password="5941",
        batchsize="1000",
        numPartitions="10",
        partitionColumn="id",
        lowerBound="1",
        upperBound="100000"
    ).mode("append").save()

    print("[INFO] DB에 뉴스 데이터 저장 완료!")