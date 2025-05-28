from pyspark.sql import Row
from pyspark.sql.functions import lit

def sign_up(spark, name, sex, age, birth_date, id, nickname, password, joined_at) :
    ip = "127.0.0.1"
    port = "3306" 
    user = 'root'
    passwd = '5941'
    db = 'news_project'
    table_name = 'user_info'

    url = f"jdbc:mysql://{ip}:{port}/{db}"

    # 1) 신규 사용자 정보를 담은 Row 객체 생성
    new_user = Row(
        name=name,
        sex=sex,
        age=int(age),
        birth_date=birth_date,
        id=id,
        nickname=nickname,
        password=password, #암호화 처리 진행 해야함
        joined_at=joined_at
    )

    # 2) 단일 Row를 DataFrame으로 변환
    new_user_df = spark.createDataFrame([new_user])

    # 3) MySQL 테이블에 append 모드로 쓰기 (INSERT)
    new_user_df.write.format("jdbc") \
        .option("url", url) \
        .option("driver", "com.mysql.cj.jdbc.Driver") \
        .option("dbtable", table_name) \
        .option("user", user) \
        .option("password", passwd) \
        .mode("append") \
        .save()

    return "회원가입이 완료 되었습니다."
    
def id_check(spark, id):
    # spark = SparkSession.builder \
    #     .appName("MySQL Export") \
    #     .config("spark.driver.memory", "4g") \
    #     .config("spark.executor.memory", "4g") \
    #     .config("spark.local.ip", "127.0.0.1") \
    #     .config("spark.python.worker.memory", "2g") \
    #     .config("spark.driver.extraClassPath", "C:/mysql-connector-j-8.3.0/mysql-connector-j-8.3.0.jar") \
    #     .getOrCreate()

    ip = "127.0.0.1"
    port = "3306" 
    user = 'root'
    passwd = '5941'
    db = 'news_project'
    table_name = 'user_info'

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
    df.createOrReplaceTempView("user_info")

    # 중복된 id가 존재하는지 확인
    query = """
        select count(distinct(id)) as count
        from user_info
        where id = '{id})' 
        """
    
    id = spark.sql(query)

    return int(id.first()[0]) # 0이 나와야 중복 id가 없다는 것

def nickname_check(spark, nickname) : 
    ip = "127.0.0.1"
    port = "3306" 
    user = 'root'
    passwd = '5941'
    db = 'news_project'
    table_name = 'user_info'

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
    df.createOrReplaceTempView("user_info")

    # 중복된 id가 존재하는지 확인
    query = """
        select count(distinct(id)) as count
        from user_info
        where nickname = '{nickname})' 
        """
    
    id = spark.sql(query)

    return int(id.first()[0]) # 0이 나와야 중복 닉네임이 없다는 것