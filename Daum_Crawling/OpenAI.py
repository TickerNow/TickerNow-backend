import pandas as pd
import openai

# 🔐 1. API 키 설정
openai.api_key = ""

# 📥 2. CSV 파일 불러오기
def load_news_csv(filename):
    df = pd.read_csv(filename)
    return df[['title', 'content','date']]

# ✍️ 3. 프롬프트 생성 (전체 기사)
def create_prompt_all(news_df, max_count=10):
    prompt = "다음은 최근 뉴스 기사 제목과 내용입니다. 전체적인 시장 흐름이나 기업 동향을 요약해 주세요.\n\n"
    for i, row in news_df.head(max_count).iterrows():  # 최대 max_count개까지만 사용
        prompt += f"[{i+1}] 제목: {row['title']}\n내용: {row['content'][:500]}...\n\n"  # 본문 일부만
    prompt += "위 뉴스들을 종합적으로 분석해 간결하게 요약해 주세요."
    return prompt

# 🤖 4. GPT 요청
def ask_gpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", #gpt-4o-mini
        messages=[
            {"role": "system", "content": "당신은 시장 동향을 분석해주는 전문가입니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response['choices'][0]['message']['content']

# ✅ 실행 예시
df = load_news_csv(r'C:\JaeHyeok\Crawling\Daum_Crawling\news_data_a.csv')
prompt = create_prompt_all(df, max_count=10)
summary = ask_gpt(prompt)

print("📊 GPT 분석 결과:")
print(summary)

#✔ 방법 2: 파일 경로에 한글이 포함되어 있으면 전체 경로로 지정
#df = load_news_csv(r"C:\JaeHyeok\Crawling\Daum_Crawling\news_data_최근뉴스.csv")\

