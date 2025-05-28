import search_function as f
import OpenAI as op
import financial_function as ff
import stock_news_function as snf
import sign_up_function as su
from flask import Flask, jsonify, request
from pyspark.sql import SparkSession
import os
import signal
import threading
from flask import request
import signal
from pydantic import BaseModel
from typing import Optional

spark = SparkSession.builder \
    .appName("MySQL Export") \
    .config("spark.driver.memory", "4g") \
    .config("spark.executor.memory", "4g") \
    .config("spark.local.ip", "127.0.0.1") \
    .config("spark.python.worker.memory", "2g") \
    .config("spark.driver.extraClassPath", "C:/mysql-connector-j-8.3.0/mysql-connector-j-8.3.0.jar") \
    .getOrCreate()


class Request_sign_up_body(BaseModel):
    name: str
    sex: str
    age: int
    birth_date: str        # YYYY-MM-DD 형식 문자열
    user_id: str
    nickname: str
    password: str
    joined_at: Optional[str] = None  # 가입일, 서버에서 자동 생성할 수도 있으니 Optional 처리


app = Flask(__name__)

@app.route("/")
def index():
    return "Flask 서버가 정상적으로 작동 중입니다!"

@app.route('/stock_news', methods=['GET'])
def run_stock_news():
    '''실시간 주식 뉴스 JSON으로 변환'''
    try:
        json_data = snf.stock_news()
        return jsonify(json_data)  # 바로 JSON 내용 반환
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/financial_search', methods=['POST'])
def run_financial_search(): # 기업 주식 정보 적재
    '''기업의 주식 정보를 저장'''
    try:
        data = request.get_json()
        search = data.get("search")

        if not search:
            return jsonify({"error": "검색어(search)가 필요합니다."}), 400

        # 크롤링 후 DB 적재 실행
        result = ff.financial_search(spark, search)

        return jsonify({
            "message": f"'{search}'에 대한 금융 정보 크롤링 및 저장이 완료되었습니다.",
            "result": result  # ff.financial_search가 리턴값이 있다면 함께 전달
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/daum_search', methods=['POST'])
def run_daum_search():
    '''Daum에서 기업 뉴스 크롤링 후 DB 저장'''
    try:
        data = request.get_json()
        search = data.get("search")
        page_count = data.get("page_count")

        # 유효성 검사
        if not search or not page_count:
            return jsonify({"error": "search 와 page_count 값이 필요합니다."}), 400

        # 크롤링 함수 실행 (DB 저장)
        f.daum_search(spark, search, int(page_count))

        return jsonify({
            "message": f"'{search}' 에 대한 뉴스 {page_count} 페이지 크롤링 및 저장 완료"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/sign_id_check', methods=['POST'])
def run_sign_id_check():
    '''회원가입 id 중복 확인'''
    try:
        data = request.get_json()
        id = data.get("id")

        if su.id_check(spark, id) == 0:
            return jsonify({
            "message": "해당 아이디는 사용 가능 합니다!"
        })

        else : 
            return jsonify({
            "message": "중복된 아이디가 존재 합니다!"
        })            

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sign_nickname_check', methods=['POST'], )
def run_sign_nickname_check():
    '''회원가입 nickname 중복 확인'''
    try:
        data = request.get_json()
        nickname = data.get("nickname")

        if su.nickname_check(spark, nickname) == 0:
            return jsonify({
            "message": "해당 닉네임은 사용 가능 합니다!"
        })

        else : 
            return jsonify({
            "message": "중복된 닉네임이 존재 합니다!"
        })            

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/sign_up', methods=['POST'])
def run_sign_up(request_body : Request_sign_up_body):
    '''회원가입 로직'''
    try:
        data = request.get_json()
        name = data.get("name")
        sex = data.get("sex")
        age = data.get("age")
        birth_date = data.get("birth_date")
        id = data.get("id")
        nickname = data.get("nickname")  # 닉네임도 받아야 함
        password = data.get("password")
        joined_at = data.get("joined_at")

        # 닉네임 중복 체크
        if su.nickname_check(spark, nickname) != 0:
            return jsonify({
                "error": "중복된 닉네임이 존재합니다. 다른 닉네임을 사용해주세요."
            }), 400

        # 아이디 중복 체크
        if su.id_check(spark, id) != 0:
            return jsonify({
                "error": "중복된 아이디가 존재합니다. 다른 아이디를 사용해주세요."
            }), 400

        # 닉네임, 아이디 중복 없으면 회원가입 처리 (DB 저장 로직)
        result = su.sign_up(spark, name, sex, age, birth_date, id, nickname, password, joined_at)

        return jsonify({
            "message": "회원가입이 완료되었습니다.",
            "message": result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
#op.run(search) #OpenAI 모듈 실행       

@app.route('/shutdown', methods=['POST'])
def shutdown():
    def stop_server():
        os.kill(os.getpid(), signal.SIGINT)
    threading.Thread(target=stop_server).start()
    return "서버가 종료 중입니다..."

if __name__ == "__main__":
    print(su.nickname_check(spark, nickname='뭐야'))
    app.run(debug=False, use_reloader=False)