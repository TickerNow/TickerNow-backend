import pandas as pd
import openai
import os

# 🔐 1. API 키 설정
openai.api_key = ""

# 📥 2. CSV 파일 불러오기
def load_news_csv(filename):
    filepath = os.path.normpath(filename)
    # 파일 읽기
    print(f"[DEBUG] 불러올 파일 경로: {filepath}")
    df = pd.read_csv(filepath, encoding='utf-8-sig')  # 인코딩 안정성 확보
    return df[['title', 'content','date']]

# ✍️ 3. 프롬프트 생성 (전체 기사)
def create_prompt_all(news_df, max_count=10):
    prompt = """당신은 뛰어난 시장 분석가이며, 아래는 특정 기업 또는 산업 관련 뉴스 기사 데이터입니다.
            기사 제목과 본문을 기반으로 다음의 관점에서 종합적인 분석 보고서를 작성해주세요:
            1. 🔍 핵심 이슈 요약: 주요 사건이나 변화는 무엇인가요?
            2. 📊 시장 영향 분석: 해당 사건이 산업 전체에 어떤 영향을 미쳤나요?
            3. 🏢 기업 전략 평가: 관련 기업은 어떤 전략을 펼치고 있으며, 그 성과는 어떤가요?
            4. ⚠️ 리스크 요소: 해당 이슈로 인해 발생할 수 있는 위험 요인은 무엇인가요?
            5. 🔮 향후 전망: 시장 또는 기업의 향후 방향은 어떻게 예측되나요?\n\n"""
    
    for i, row in news_df.head(max_count).iterrows():  # 최대 max_count개까지만 사용
        prompt += f"[{i+1}] 제목: {row['title']}\n내용: {row['content'][:500]}...\n\n"  # 본문 일부만
    prompt += "전체 분석은 요약이 아닌, **전문가 시각의 통합 분석 보고서 형태**로 작성해주세요."
    return prompt

# 🤖 4. GPT 요청
def ask_gpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", #gpt-4o-mini
        messages=[
            {"role": "system", "content": "너는 투자 보고서를 작성하는 애널리스트야. 시장 흐름을 수치와 전략 중심으로 분석해."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response['choices'][0]['message']['content']

# ✅ 실행
def run(search):
    filename = os.path.join("Daum_Crawling\csv_folder", f"data_{search}.csv")
    df = load_news_csv(filename)
    prompt = create_prompt_all(df, max_count=10)
    summary = ask_gpt(prompt)

    print("📊 GPT 분석 결과:")
    print(summary)

#✔ 방법 2: 파일 경로에 한글이 포함되어 있으면 전체 경로로 지정
#df = load_news_csv(r"C:\JaeHyeok\Crawling\Daum_Crawling\news_data_최근뉴스.csv")\

