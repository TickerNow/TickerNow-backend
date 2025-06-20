from pyspark.sql import Row
from pyspark.sql.functions import lit
from passlib.hash import bcrypt
from datetime import datetime
import pymysql

def sign_up(name, sex, birth_date, id, nickname, password, joined_at):
    """회원 정보 DB 저장 """
    
    # 나이 계산
    today = datetime.today()
    birth_dt = datetime.strptime(birth_date, "%Y-%m-%d")
    age = today.year - birth_dt.year - ((today.month, today.day) < (birth_dt.month, birth_dt.day))

    # 비밀번호 해싱
    hashed_password = bcrypt.hash(password)

    # DB 연결
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='5941',
        db='news_project',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO user_info 
                (name, sex, age, birth_date, id, nickname, password, joined_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                name, sex, age, birth_date, id, nickname, hashed_password, joined_at
            ))
        conn.commit()
        return "회원가입이 완료되었습니다."
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
    
def id_check(spark, id):
    """ID 중복 체크"""
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
    # 중복된 닉네임이 존재하는지 확인
    query = f"""
        select count(distinct(nickname)) as count
        from user_info
        where nickname = '{nickname}' 
        """
    
    nickname = spark.sql(query)

    return int(nickname.first()[0]) # 0이 나와야 중복 닉네임이 없다는 것