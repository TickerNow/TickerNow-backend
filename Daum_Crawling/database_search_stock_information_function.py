import json

def get_stock_data_from_db(spark, stock_name):
    '''DB를 조회하여 기업 주식 정보를 리턴'''
    ip = "127.0.0.1"
    port = "3306" 
    user = 'root'
    passwd = '5941' # 비밀번호 수정
    db = 'news_project'
    table_name = 'daum_financial_stock_table'

    url = f"jdbc:mysql://{ip}:{port}/{db}"

    #데이터 읽기
    df = (spark.read.format("jdbc")
        .option("url", url)
        .option("driver", "com.mysql.cj.jdbc.Driver")
        .option("dbtable", table_name)
        .option("user", user)
        .option("password", passwd)
        .load()
    )

    # SQL문을 사용하기 위해 View를 생성
    df.createOrReplaceTempView("daum_financial_stock_table")

    # 중복된 id가 존재하는지 확인
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