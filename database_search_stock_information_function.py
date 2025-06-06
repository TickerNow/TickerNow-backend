import json

def get_stock_data_from_db(spark, stock_name):
    '''DB를 조회하여 기업 주식 정보를 리턴'''
    # 주식 정보 조회회
    query = f"""
        select *
        from daum_financial_stock_table
        where name = '{stock_name}' 
        ORDER BY date DESC
        """

    df = spark.sql(query)

    # Spark의 각 row를 JSON 문자열로 변환
    json_rdd = df.toJSON()

    # JSON 문자열을 Python dict로 파싱
    json_list = [json.loads(row) for row in json_rdd.collect()]

    return json_list