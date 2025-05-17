from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyperclip
import time
import search_function as f
import OpenAI as op
import pandas as pd
import financial_function as ff

search = input("검색 하세요 : ")
page_count = input("원하는 페이지 수 : ")

#ff.financial_search(search, page_count) # 다음 증권 크롤링
f.daum_search(search, page_count)
#op.run(search) #OpenAI 모듈 실행