import pandas as pd
import openai
import os
from datetime import datetime
from pyspark.sql import  Row
from pyspark.sql.functions import lit
from dotenv import load_dotenv

db_properties = {
    "driver": "com.mysql.cj.jdbc.Driver",
    "user": "root",
    "password": "5941"
}

load_dotenv()
OpenAI_KEY = os.getenv("OpenAI_KEY")

#  1. API 키 설정
openai.api_key = OpenAI_KEY

def ask_gpt(spark, search, user_id, user_message):
    '''질문하고 응답 받기'''
    # 1. 대화 히스토리 불러오기
    history = load_history_from_spark(spark, search, user_id)

    # 2. 기업 뉴스 요약 데이터 포함
    news_summary = fetch_news_summary(spark, search, max_count=5)

    messages = [
        {
            "role": "system",
            "content": (
                "당신은 금융 시장 전문가이며, 특히 기업 뉴스, 재무 데이터, 산업 트렌드를 기반으로 "
                "주식에 대한 종합적 분석과 예측을 수행하는 AI 주식 애널리스트입니다. "
                "다음 항목을 기준으로 사용자의 질문에 답변하세요:\n\n"
                "1. 🔍 핵심 이슈 분석\n"
                "2. 📊 수치 기반 설명\n"
                "3. 🧠 통찰 제공\n"
                "4. ⚠️ 리스크 판단\n"
                "5. 🔮 향후 전망\n\n"
                f"다음은 '{search}'에 대한 최근 뉴스 요약입니다:\n\n"
                f"{news_summary}\n\n"
                "이 뉴스를 바탕으로 사용자의 질문에 분석적으로 답해주세요."
            )
        }
    ]

    # 3. 이전 대화 기록 반영
    messages += [{"role": row["role"].strip(), "content": row["content"]} for row in history]

    # 4. 사용자 질문 추가
    messages.append({"role": "user", "content": user_message})

    # 5. GPT 호출
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    reply = response["choices"][0]["message"]["content"]

    # 6. 대화 저장
    save_message_to_spark(spark, search, user_id, "user", user_message)
    save_message_to_spark(spark, search, user_id, "assistant", reply)

    return reply

def load_history_from_spark(spark, search, user_id):
    '''DB에서 대화 기록 불러오기'''
    try:
        query = f"""
            SELECT role, content FROM conversation_history
            WHERE user_id = '{user_id} and search = {search}'
            ORDER BY timestamp DESC
            limit 10
        """
        return spark.sql(query).collect()
    except Exception as e:
        print("[ERROR] History Load Failed:", e)
        return []

def save_message_to_spark(spark, search, user_id, role, content):
    '''대화 기록 저장하기'''
    ip = "127.0.0.1"
    port = "3306" 
    db = 'news_project'

    url = f"jdbc:mysql://{ip}:{port}/{db}"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = Row(user_id=user_id, search =search, role=role, content=content, timestamp=now)
    df = spark.createDataFrame([row])

    df.write.format("jdbc").options(
        url=url,
        dbtable='conversation_history',
        **db_properties
    ).mode("append").save()

def fetch_news_summary(spark, stock_name, max_count=10):
    # DB에서 해당 기업 뉴스 가져오기
    query = f"""
        SELECT title, content, date
        FROM search_information
        WHERE search = '{stock_name}'
        ORDER BY date DESC
        LIMIT {max_count}
    """
    df = spark.sql(query)
    news_list = df.collect()

    # 텍스트로 프롬프트 구성
    prompt = f"다음은 {stock_name}에 대한 최근 뉴스입니다.\n\n"
    for i, row in enumerate(news_list, 1):
        prompt += f"[{i}] 제목: {row['title']}\n날짜: {row['date']}\n내용: {row['content'][:500]}...\n\n"

    prompt += (
        f"위 뉴스를 바탕으로 다음 질문에 전문가처럼 답해주세요.\n"
    )
    return prompt

# # 📥 2. CSV 파일 불러오기
# def load_news_csv(filename):
#     filepath = os.path.normpath(filename)
#     # 파일 읽기
#     print(f"[DEBUG] 불러올 파일 경로: {filepath}")
#     df = pd.read_csv(filepath, encoding='utf-8-sig')  # 인코딩 안정성 확보
#     return df[['title', 'content','date']]

# # ✍️ 3. 프롬프트 생성 (전체 기사)
# def create_prompt_all(news_df, max_count=10):
#     prompt = """당신은 뛰어난 시장 분석가이며, 아래는 특정 기업 또는 산업 관련 뉴스 기사 데이터입니다.
#             기사 제목과 본문을 기반으로 다음의 관점에서 종합적인 분석 보고서를 작성해주세요:
#             1. 🔍 핵심 이슈 요약: 주요 사건이나 변화는 무엇인가요?
#             2. 📊 시장 영향 분석: 해당 사건이 산업 전체에 어떤 영향을 미쳤나요?
#             3. 🏢 기업 전략 평가: 관련 기업은 어떤 전략을 펼치고 있으며, 그 성과는 어떤가요?
#             4. ⚠️ 리스크 요소: 해당 이슈로 인해 발생할 수 있는 위험 요인은 무엇인가요?
#             5. 🔮 향후 전망: 시장 또는 기업의 향후 방향은 어떻게 예측되나요?\n\n"""
    
#     for i, row in news_df.head(max_count).iterrows():  # 최대 max_count개까지만 사용
#         prompt += f"[{i+1}] 제목: {row['title']}\n내용: {row['content'][:500]}...\n\n"  # 본문 일부만
#     prompt += "전체 분석은 요약이 아닌, **전문가 시각의 통합 분석 보고서 형태**로 작성해주세요."
#     return prompt

# # 🤖 4. GPT 요청
# def ask_gpt(prompt):
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo", #gpt-4o-mini
#         messages=[
#             {"role": "system", "content": "너는 투자 보고서를 작성하는 애널리스트야. 시장 흐름을 수치와 전략 중심으로 분석해."},
#             {"role": "user", "content": prompt}
#         ],
#         temperature=0.7
#     )
#     return response['choices'][0]['message']['content']

# # ✅ 실행
# def run(search):
#     filename = os.path.join("Daum_Crawling\csv_folder", f"data_{search}.csv")
#     df = load_news_csv(filename)
#     prompt = create_prompt_all(df, max_count=10)
#     summary = ask_gpt(prompt)

#     print("📊 GPT 분석 결과:")
#     print(summary)

#✔ 방법 2: 파일 경로에 한글이 포함되어 있으면 전체 경로로 지정
#df = load_news_csv(r"C:\JaeHyeok\Crawling\Daum_Crawling\news_data_최근뉴스.csv")\

