## 📈 StockSight : 기업 뉴스와 주가 데이터를 통해 인사이트를 제공하는 서비스

사용자가 관심 있는 기업의 **주식 정보** 와 **주요 뉴스**를 쉽고 빠르게 확인하고, OpenAI와의 대화를 통해 필요한 정보를 신속하게 얻을 수 있도록 구성된 자동화 크롤링 및 데이터 분석 프로젝트입니다.

---

## 📂 파일 구성

- `main.py` : 전체 기능을 실행하는 메인 진입점
- `database_search_stock_information_function.py` : DB에서 주식 정보를 조회하여 JSON 타입을 반환하는 모듈
- `login_function.py` : 로그인을 위해 DB에서 정보를 조회하는 모듈
- `sign_up.py` : 회원 가입 절차와 검증 모듈
- `stock_load_function.py` : Daum 증권에서 종목 정보를 크롤링하는 모듈
- `daum_search_function.py` : Daum 포털에서 기업명을 검색하여 관련 뉴스 정보를 수집하는 모듈
- `stock_news_function.py` : Daum 증권의 최신 주식 뉴스를 불러오는 모듈
- `OpenAI.py` : OpenAI API를 활용하여 수집된 뉴스를 기반으로 인사이트를 제공하며, 사용자와 대화 기능을 수행하는 모듈

---

## 📌 주요 기능

- 수집된 정보를 기반으로 기업 소식을 전달하고, 주가 정보를 그래프로 시각화하여 제공
- 웹 기반 회원가입 및 로그인 시스템
- Daum 금융에서 주식 정보 실시간 크롤링
- 기업명을 기반으로 최신 뉴스 기사 자동 수집
- OpenAI API를 활용한 수집된 뉴스를 바탕으로 사용자와의 대화 기능 제공
- Apache Spark를 활용한 수집 데이터 가공 및 저장
- MySQL 연동을 통한 주식 정보, 뉴스, 회원 정보 통합 저장 및 관리

---

## 🛠 사용 기술

<p align="left">
  <img src="https://img.shields.io/badge/Apache%20Spark-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white" alt="Apache Spark Badge"/>
  <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL Badge"/>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Badge"/>
  <img src="https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white" alt="Selenium Badge"/>
  <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI Badge"/>
  <img src="https://img.shields.io/badge/JSON-000000?style=for-the-badge&logo=json&logoColor=white" alt="JSON Badge"/>
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask Badge"/>
</p>


