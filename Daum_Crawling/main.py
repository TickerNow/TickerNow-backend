from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyperclip
import time
import function as f

search = input("검색 하세요 : ")
page_count = input("원하는 페이지 수 : ")
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

news_links = f.get_news_links(driver, int(page_count))  # 수집한 링크
news_data = f.get_news_contents(news_links)  # 본문 수집
# print(news_links)
# print(news_data)
f.save_to_csv(news_data,f"news_data_{search}.csv") #수집한 타이틀, 내용, 제목, 링크를 csv파일로 저장장