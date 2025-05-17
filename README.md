# 📈 기업 주식 정보 및 뉴스 제공 프로젝트

사용자가 관심 있는 기업의 **주식 정보**와 **주요 뉴스**를 쉽고 빠르게 확인할 수 있도록 도와주는 자동화 크롤링 및 데이터 분석 프로젝트입니다.

---

## 📂 파일 구성

- `main.py` : 전체 기능을 실행하는 메인 진입점
- `financial_function.py` : Daum 증권에서 종목 정보를 크롤링하는 함수 모듈
- `search_function.py` : Daum 포털에서 기업명을 검색하여 관련 뉴스 정보를 수집하는 함수 모듈
- `OpenAI.py` : OpenAI API를 활용한 뉴스 요약 등의 기능을 수행하는 모듈

---

## 🛠 사용 기술

<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Badge"/>
  <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL Badge"/>
  <img src="https://img.shields.io/badge/Apache%20Spark-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white" alt="Apache Spark Badge"/>
</p>

---

## 📌 주요 기능

- 종목 코드 기반 주식 정보 수집 (Daum 증권 크롤링)
- 기업명 기반 최신 뉴스 크롤링
- OpenAI API를 활용한 뉴스 요약
- 수집된 데이터의 Spark 기반 가공 및 저장
- MySQL DB 연동
