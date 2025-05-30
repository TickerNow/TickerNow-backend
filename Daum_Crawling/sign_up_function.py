from pyspark.sql import Row
from pyspark.sql.functions import lit
from passlib.hash import bcrypt


def sign_up(spark, name, sex, age, birth_date, id, nickname, password, joined_at) :
    """회원 정보 DB 저장"""
    ip = "127.0.0.1"
    port = "3306" 
    user = 'root'
    passwd = '5941' # 비밀번호 변경
    db = 'news_project'
    table_name = 'user_info'

    url = f"jdbc:mysql://{ip}:{port}/{db}"
    
    hashed_password = bcrypt.hash(password) # 비밀번호를 해시 함수로 암호화 처리

    # 1) 신규 사용자 정보를 담은 Row 객체 생성
    new_user = Row(
        name=name,
        sex=sex,
        age=int(age),
        birth_date=birth_date,
        id=id,
        nickname=nickname,
        password=hashed_password, 
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
    """ID 중복 체크"""
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
    query = f"""
        select COUNT(*) as count
        from user_info
        where id = '{id}' 
        """
    
    re = spark.sql(query)
    return int(re.first()[0]) # 0이 나와야 중복 id가 없다는 것

def nickname_check(spark, nickname) : 
    """닉네임 중복 체크"""
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

    # 중복된 닉네임이 존재하는지 확인
    query = f"""
        select count(distinct(nickname)) as count
        from user_info
        where nickname = '{nickname}' 
        """
    
    nickname = spark.sql(query)

    return int(nickname.first()[0]) # 0이 나와야 중복 닉네임이 없다는 것