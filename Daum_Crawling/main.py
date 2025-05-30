import daum_search_function as f
import OpenAI as op
import stock_load_function as slf
import stock_news_function as snf
import sign_up_function as suf
import database_search_stock_information_function as dbf
import login_function as lf

from flask import Flask, jsonify, request
from pyspark.sql import SparkSession
import os
import signal
import threading
from pydantic import BaseModel
from typing import Optional
from flask_cors import CORS  # 추가
import traceback
from datetime import datetime

os.environ["PYSPARK_PYTHON"] = "C:/Users/jaehy/anaconda3/python.exe"

spark = SparkSession.builder \
    .appName("MySQL Export") \
    .config("spark.driver.memory", "4g") \
    .config("spark.executor.memory", "4g") \
    .config("spark.python.worker.memory", "2g") \
    .config("spark.local.ip", "127.0.0.1") \
    .config("spark.driver.host", "127.0.0.1") \
    .config("spark.driver.bindAddress", "127.0.0.1") \
    .config("spark.python.worker.reuse", "true") \
    .config("spark.driver.extraClassPath", "C:/mysql-connector-j-8.3.0/mysql-connector-j-8.3.0.jar") \
    .getOrCreate()

class Request_sign_up_body(BaseModel):
    name: str
    sex: str
    age: int
    birth_date: str        # YYYY-MM-DD 형식 문자열
    id: str
    nickname: str
    password: str
    joined_at: Optional[str] = None  # 가입일, 서버에서 자동 생성할 수도 있으니 Optional 처리

app = Flask(__name__)

CORS(
    app,
    resources={r"/*": {"origins": "*"}},  # 모든 경로에 대해 모든 origin 허용
    allow_headers=["Content-Type", "Authorization", "ngrok-skip-browser-warning"],
    supports_credentials=True
)

@app.route("/")
def index():
    return "Flask 서버가 정상적으로 작동 중입니다!"

@app.route('/stock_news', methods=['OPTIONS'])
def stock_news_options():
    response = jsonify({'message': 'CORS preflight'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, ngrok-skip-browser-warning')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

@app.route('/stock_news', methods=['GET', 'POST'])
def run_stock_news():
    '''실시간 주식 뉴스 JSON으로 변환'''
    
    try:
        json_data = snf.stock_news()
        return jsonify(json_data)  # 바로 JSON 내용 반환
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stock_load', methods=['POST'])
def run_stock_load(): # 기업 주식 정보 적재
    '''기업의 주식 정보를 Daum 증권에서 크롤링하여 DB에 적재'''
    try:
        data = request.get_json()
        search = data.get("search")

        if not search:
            return jsonify({"error": "검색어(search)가 필요합니다."}), 400

        # 크롤링 후 DB 적재 실행
        result = slf.stock_load(spark, search)

        return jsonify({
            "message": f"'{search}'에 대한 금융 정보 크롤링 및 저장이 완료되었습니다.",
            "result": result  # ff.financial_search가 리턴값이 있다면 함께 전달
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/daum_search', methods=['POST'])
def run_daum_news_load():
    '''Daum에서 기업 뉴스 크롤링 후 DB 적재'''
    try:
        data = request.get_json()
        search = data.get("search")
        page_count = data.get("page_count")

        # 유효성 검사
        if not search or not page_count:
            return jsonify({"error": "search 와 page_count 값이 필요합니다."}), 400

        # 크롤링 함수 실행 (DB 저장)
        f.daum_news_load(spark, search, int(page_count))

        return jsonify({
            "message": f"'{search}' 에 대한 뉴스 {page_count} 페이지 크롤링 및 저장 완료"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/DB_stock_search', methods=['POST'])
def run_get_stock_data_from_db():
    '''DB에서 조회한 주식 정보를 리턴'''
    try:
        data = request.get_json()
        stock_name = data.get("stock_name")

        # 유효성 검사
        if not stock_name :
            return jsonify({"error": "종목을 입력하세요."}), 400

        # DB 조회
        stock_json_list = dbf.get_stock_data_from_db(spark, stock_name)

        # DB에 해당 종목이 없는 경우
        if not stock_json_list:
            return jsonify({"message": "해당 종목 정보가 없습니다."}), 404

        return jsonify(stock_json_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sign_id_check', methods=['POST'])
def run_sign_id_check():
    '''회원가입 id 중복 확인'''
    try:
        data = request.get_json()
        id = data.get("id")

        if suf.id_check(spark, id) == 0:
            return jsonify({
            "message": "해당 아이디는 사용 가능 합니다!"
        })

        else : 
            return jsonify({
            "message": "중복된 아이디가 존재 합니다!"
        })            

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sign_nickname_check', methods=['POST'] )
def run_sign_nickname_check():
    '''회원가입 nickname 중복 확인'''
    try:
        data = request.get_json()
        nickname = data.get("nickname")

        if suf.nickname_check(spark, nickname) == 0:
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
def run_sign_up():
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
        joined_at = data.get("joined_at") or datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 아이디 중복 체크
        if suf.id_check(spark, id) != 0:
            return jsonify({
                "error": "중복된 아이디가 존재합니다. 다른 아이디를 사용해주세요."
            }), 400
        
        # 닉네임 중복 체크
        if suf.nickname_check(spark, nickname) != 0:
            return jsonify({
                "error": "중복된 닉네임이 존재합니다. 다른 닉네임을 사용해주세요."
            }), 400

        # 닉네임, 아이디 중복 없으면 회원가입 처리 (DB 저장 로직)
        suf.sign_up(spark, name, sex, age, birth_date, id, nickname, password, joined_at)

        return jsonify({
            "message": "회원가입이 완료되었습니다.",
        })

    except Exception as e:
        traceback.format_exc()
        return jsonify({"error": str(e)}), 500
    
@app.route('/login', methods=['POST'])
def run_login():
    '''로그인 로직'''
    try:
        data = request.get_json()
        id = data.get("id")
        password = data.get("password")

        if not id or not password:
            return jsonify({"error": "아이디 또는 비밀번호가 누락되었습니다."}), 400

        login_result = lf.login(spark, id, password)

        if isinstance(login_result, dict):  # 로그인 성공
            token = lf.generate_jwt(login_result["id"], login_result["is_admin"], SECRET_KEY) # jwt 토큰 발급
            return jsonify({
                "message": "로그인이 완료되었습니다.",
                "token": token,
                "is_admin": login_result["is_admin"] # is_admin 값이 1인 경우 관리자 계정, 0인 경우 일반 회원
            }), 200
        
        else:
            return jsonify({"error": login_result}), 401

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
        
#op.run(search) #OpenAI 모듈 실행       

@app.route('/shutdown', methods=['POST'])
def shutdown():
    def stop_server():
        os.kill(os.getpid(), signal.SIGINT)
    threading.Thread(target=stop_server).start()
    return "서버가 종료 중입니다..."

if __name__ == "__main__":
    #print(su.nickname_check(spark, nickname='뭐야'))
    app.run(host='0.0.0.0',debug=False, use_reloader=False)