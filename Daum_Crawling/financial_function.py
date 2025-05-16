from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyperclip
import time
import pandas as pd

# def financial_search():
#     search = input("검색 하세요 : ")
#     page_count = input("원하는 페이지 수 : ")
#     url = 'https://finance.daum.net/domestic'
#     driver = webdriver.Chrome()
#     driver.get(url)

#     #검색창 로딩 대기 (최대 5초)
#     WebDriverWait(driver, 5).until(
#         EC.presence_of_element_located((By.XPATH, '//*[@id="inpSearchStock"]'))
#     )

#     #검색 값 복사
#     pyperclip.copy(search)

#     #검색 값 검색창에 붙여넣기
#     driver.find_element(By.XPATH, '//*[@id="inpSearchStock"]').send_keys(Keys.CONTROL + 'v')
#     time.sleep(1)

#     #검색 버튼 클릭
#     driver.find_element(By.XPATH, '//*[@id="btnSearchStock"]').click()
#     time.sleep(2)

#     try:
#         # 검색 후 들어간 페이지에서 "현재가" 클릭
#         WebDriverWait(driver, 3).until(
#             EC.presence_of_element_located((By.XPATH, '//*[@id="boxTabs"]/td[2]'))
#         )
#         driver.find_element(By.XPATH, '//*[@id="boxTabs"]/td[2]').click()
#         print("[INFO] boxTabs 2번 탭 클릭 성공")

#     except:
#         print("[INFO] boxTabs 탭 없음. 대체 경로 수행 중...")

#         try:
#         # 만약 검색을 했을 때, 여러 종목이 검색되는 경우 맨 위의 종목이 검색 되도록하기.
#             WebDriverWait(driver, 3).until(
#                 EC.element_to_be_clickable((By.XPATH, '//*[@id="boxContents"]/div[2]/div/table/tbody/tr[1]/td[2]/a'))
#             ).click()
#             print("[INFO] 대체 링크 클릭 성공")
#             time.sleep(1)

#             # 검색 후 들어간 페이지에서 "현재가" 클릭
#             WebDriverWait(driver, 3).until(
#                 EC.presence_of_element_located((By.XPATH, '//*[@id="boxTabs"]/td[2]'))
#             )
#             driver.find_element(By.XPATH, '//*[@id="boxTabs"]/td[2]').click()

#         except :
#             print("대체 요소도 존재하지 않음. 페이지 구조 확인 필요")


#     all_data = [] # 현재 주가 테이블의 정보를 담는 list

#     i=1 #페이지 버튼 클릭을 위한 변수
#     init = 0 # 현재 주가 테이블의 첫 페이지는 i가 0 부터 시작하지만 다음 페이지 부터는 3부터 시작하기 때문에 첫 페이지 구별을 위한 변수
#     count = 1 # 총 크롤링 페이지 수 카운트

#     while (count<=int(page_count)):
#         try:
#             # 1. 현재 페이지의 테이블 행 수집
#             rows = driver.find_elements(By.XPATH, '//*[@id="boxDayHistory"]/div/div[2]/div/table/tbody/tr')
#             for row in rows:
#                 tds = row.find_elements(By.TAG_NAME, "td")
#                 record = [td.text.strip() for td in tds]
#                 if len(record) == 8:  # 유효한 데이터만
#                     all_data.append(record)

#             # 2. 페이지지 버튼 클릭
#             if i == 10 and init == 0 : # 첫 번째 전체 페이지를 모두 크롤링 한 경우 다음 페이지 버튼 클릭
#                 next_btn_xpath = '//*[@id="boxDayHistory"]/div/div[2]/div/div/a[10]' # 다음 페이지 버튼 클릭 
#                 next_btn = WebDriverWait(driver, 3).until(
#                     EC.element_to_be_clickable((By.XPATH, next_btn_xpath))
#                 )
#                 next_btn.click()            
#                 i=2 # 두번 째 전체 페이지 부터는 두번째째 페이지가 인덱스가 3으로 시작
#                 init = 1 # 첫 전체 페이지지 크롤링 완료 시 init 값 변경

#             elif i>1: # 현재 숫자 페이지 숫자 페이지지 버튼 클릭
#                 if init ==0 : # 첫번 째 전체 페이지 인 경우 
#                     next_btn_xpath = f'//*[@id="boxDayHistory"]/div/div[2]/div/div/a[{i}]'
#                     next_btn = WebDriverWait(driver, 3).until(
#                         EC.element_to_be_clickable((By.XPATH, next_btn_xpath))
#                     )
#                     next_btn.click()

#                 elif init == 1 : # 첫번 째 전체 페이지를 모두 크롤링 한 다음 페이지 부터 적용
#                     if i <= 12 : # 두번 째 이상 전체 페이지에서 다음 페이지의 인덱스가 12이기때문에, 전체 다음 페이지로 넘어가서 1단계인 전체 테이블 행을 수집한 후 그 다음 페지이의 인덱스인 3부터 수집한다.
#                         next_btn_xpath = f'//*[@id="boxDayHistory"]/div/div[2]/div/div/a[{i}]'
#                         next_btn = WebDriverWait(driver, 3).until(
#                             EC.element_to_be_clickable((By.XPATH, next_btn_xpath))
#                         )
#                         next_btn.click()
#                     else :
#                         i = 2
#             print(f"[INFO] {count}페이지 데이터 수집 완료!")                             
#             i += 1
#             count += 1
#             time.sleep(2)

#         except Exception as e:
#             print(f"[INFO] 더 이상 페이지 없음 or 오류 발생: {e}")
#             break

#     # 4. DataFrame으로 변환
#     df = pd.DataFrame(all_data, columns=["일자", "시가", "고가", "저가", "종가", "전일비", "등락률", "거래량"])

#     # 5. 데이터 전처리
#     for col in ["시가", "고가", "저가", "종가", "전일비", "거래량"]:
#         df[col] = df[col].str.replace("▲", "").str.replace("▼", "").str.replace(",", "").astype(str)

#     # 적용
#     df['일자'] = df['일자'].apply(convert_date_format)

#     pd.set_option('display.max_rows', None)
#     print(df)

def financial_search():
    search = input("검색 하세요 : ")
    page_count = input("원하는 페이지 수 : ")
    url = 'https://finance.daum.net/domestic'
    driver = webdriver.Chrome()
    driver.get(url)

    #검색창 로딩 대기 (최대 5초)
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="inpSearchStock"]'))
    )

    #검색 값 복사
    pyperclip.copy(search)

    #검색 값 검색창에 붙여넣기
    driver.find_element(By.XPATH, '//*[@id="inpSearchStock"]').send_keys(Keys.CONTROL + 'v')
    time.sleep(1)

    #검색 버튼 클릭
    driver.find_element(By.XPATH, '//*[@id="btnSearchStock"]').click()
    time.sleep(2)

    try:
        # 검색 후 들어간 페이지에서 "현재가" 클릭
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="boxTabs"]/td[2]'))
        )
        driver.find_element(By.XPATH, '//*[@id="boxTabs"]/td[2]').click()
        print("[INFO] boxTabs 2번 탭 클릭 성공")

    except:
        print("[INFO] boxTabs 탭 없음. 대체 경로 수행 중...")

        try:
        # 만약 검색을 했을 때, 여러 종목이 검색되는 경우 맨 위의 종목이 검색 되도록하기.
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="boxContents"]/div[2]/div/table/tbody/tr[1]/td[2]/a'))
            ).click()
            print("[INFO] 대체 링크 클릭 성공")
            time.sleep(1)

            # 검색 후 들어간 페이지에서 "현재가" 클릭
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="boxTabs"]/td[2]'))
            )
            driver.find_element(By.XPATH, '//*[@id="boxTabs"]/td[2]').click()

        except :
            print("대체 요소도 존재하지 않음. 페이지 구조 확인 필요")


    all_data = [] # 현재 주가 테이블의 정보를 담는 list

    i=1 #페이지 버튼 클릭을 위한 변수
    init = 0 # 현재 주가 테이블의 첫 페이지는 i가 0 부터 시작하지만 다음 페이지 부터는 3부터 시작하기 때문에 첫 페이지 구별을 위한 변수
    count = 1 # 총 크롤링 페이지 수 카운트

    while (count<int(page_count)+1):
        try:
            # 1. 현재 페이지의 테이블 행 수집
            rows = driver.find_elements(By.XPATH, '//*[@id="boxDayHistory"]/div/div[2]/div/table/tbody/tr')
            for row in rows:
                tds = row.find_elements(By.TAG_NAME, "td")
                record = [td.text.strip() for td in tds]
                if len(record) == 8:  # 유효한 데이터만
                    all_data.append(record)

            # 2. 페이지지 버튼 클릭
            if init ==0 : # 첫번 째 전체 페이지 인 경우 
                if i == 10 : # 첫번 째 페이지를 모두 크롤링 한 경우 다음 페이지 버튼 클릭하고 init과 i 변수 초기화
                    next_btn_xpath = '//*[@id="boxDayHistory"]/div/div[2]/div/div/a[10]' # 다음 페이지 버튼 클릭 
                    next_btn = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, next_btn_xpath))
                    )
                    next_btn.click()            
                    i=2 # 두번 째 전체 페이지 부터는 두번째째 페이지가 인덱스가 3으로 시작
                    init = 1 # 첫 전체 페이지지 크롤링 완료 시 init 값 변경
                
                else : # 페이지를 전부 크롤링 하지 않은 경우, 다음 숫자 페이지 버튼 클릭
                    next_btn_xpath = f'//*[@id="boxDayHistory"]/div/div[2]/div/div/a[{i}]'
                    next_btn = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, next_btn_xpath))
                    )
                    next_btn.click()


            elif init == 1 : # 첫번 째 전체 페이지를 모두 크롤링 한 다음 페이지 부터 적용
                if i <= 12 : # 두번 째 이상 전체 페이지에서 다음 페이지의 인덱스가 12이기때문에, 전체 다음 페이지로 넘어가서 1단계인 전체 테이블 행을 수집한 후 그 다음 페지이의 인덱스인 3부터 수집한다.
                    next_btn_xpath = f'//*[@id="boxDayHistory"]/div/div[2]/div/div/a[{i}]'
                    next_btn = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, next_btn_xpath))
                    )
                    next_btn.click()
                else : # 두번 째 이상 페이지에서 해당 전체 페이지를 모두 크롤링 한 경우 i 초기화
                    i = 2
            print(f"[INFO] {count}페이지 데이터 수집 완료!")                             
            i += 1
            count += 1
            time.sleep(2)

        except Exception as e:
            print(f"[INFO] 더 이상 페이지 없음 or 오류 발생: {e}")
            break

    # 4. DataFrame으로 변환
    df = pd.DataFrame(all_data, columns=["일자", "시가", "고가", "저가", "종가", "전일비", "등락률", "거래량"])

    # 5. 데이터 전처리
    for col in ["시가", "고가", "저가", "종가", "전일비", "거래량"]:
        df[col] = df[col].str.replace("▲", "").str.replace("▼", "").str.replace(",", "").astype(str)

    # 적용
    df['일자'] = df['일자'].apply(convert_date_format)

    pd.set_option('display.max_rows', None)
    print(df)

def convert_date_format(date_str): #기존 25.01.01 형식 날짜 형식을 2025-01-01 형식으로 변환하는 함수
    try:
        return pd.to_datetime("20" + date_str, format='%Y.%m.%d').strftime('%Y-%m-%d')
    except:
        return None  # 변환 실패 시 None
