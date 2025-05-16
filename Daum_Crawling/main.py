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


ff.financial_search() # 다음 증권 크롤링
#f.daum_search()
#op.run(search) #OpenAI 모듈 실행