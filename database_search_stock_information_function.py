import json

def get_stock_data_from_db(spark, stock_name):
    '''DB를 조회하여 기업 주식 정보 및 뉴스 정보를 JSON으로 리턴'''
    
    # 주식 데이터 쿼리
    query_stock = f"""
        SELECT *
        FROM daum_financial_stock_table
        WHERE name = '{stock_name}' 
        ORDER BY date DESC
    """
    df_stock = spark.sql(query_stock)

    # 뉴스 데이터 쿼리
    query_news = f"""
        SELECT *
        FROM search_information
        WHERE search = '{stock_name}' 
        ORDER BY date DESC
    """
    df_news = spark.sql(query_news)

    # JSON 변환
    stock_json = [json.loads(row) for row in df_stock.toJSON().collect()]
    news_json = [json.loads(row) for row in df_news.toJSON().collect()]

    # 두 JSON 리스트를 하나의 딕셔너리로 묶어서 반환
    return {
        "stock_data": stock_json,
        "news_data": news_json
    }