import daum_search_function as f
import OpenAI as op
import stock_load_function as slf
import stock_news_function as snf
import sign_up_function as suf
import database_search_stock_information_function as dbf
import login_function as lf

from flask import Flask, jsonify, request, make_response
from pyspark.sql import SparkSession
import os
import signal
import threading
from flask_cors import CORS  # 추가
import traceback
import jwt
from dotenv import load_dotenv

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

ip = "127.0.0.1"
port = "3306" 
user = 'root'
passwd = '5941'
db = 'news_project'

url = f"jdbc:mysql://{ip}:{port}/{db}"

#주식 정보 view 생성
table_name = 'daum_financial_stock_table'
df = (spark.read.format("jdbc")
    .option("url", url)
    .option("driver", "com.mysql.cj.jdbc.Driver")
    .option("dbtable", table_name)
    .option("user", user)
    .option("password", passwd)
    .load()
)
df.createOrReplaceTempView("daum_financial_stock_table")

#회원 정보 view 생성
table_name = 'user_info'
df = (spark.read.format("jdbc")
    .option("url", url)
    .option("driver", "com.mysql.cj.jdbc.Driver")
    .option("dbtable", table_name)
    .option("user", user)
    .option("password", passwd)
    .load()
)
df.createOrReplaceTempView("user_info")

#기업 뉴스 정보
table_name = 'search_information'
df = (spark.read.format("jdbc")
    .option("url", url)
    .option("driver", "com.mysql.cj.jdbc.Driver")
    .option("dbtable", table_name)
    .option("user", user)
    .option("password", passwd)
    .load()
)
df.createOrReplaceTempView("search_information")

#OpenAI 대화 기록 view 생성
table_name = 'conversation_history'
df = (spark.read.format("jdbc")
    .option("url", url)
    .option("driver", "com.mysql.cj.jdbc.Driver")
    .option("dbtable", table_name)
    .option("user", user)
    .option("password", passwd)
    .load()
)
df.createOrReplaceTempView("conversation_history")

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

app = Flask(__name__)

CORS(
    app,
    #resources={r"/*": {"origins": "*"}},  # 모든 경로에 대해 모든 origin 허용
    resources={r"/*": {"origins": "https://baf7-124-216-101-107.ngrok-free.app"}},
    allow_headers=["Content-Type", "Authorization", "ngrok-skip-browser-warning"],
    expose_headers=["Authorization"],
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
        }), 200

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
        }), 200

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
        }), 200

        else : 
            return jsonify({
            "message": "중복된 아이디가 존재 합니다!"
        }), 400            

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
        }), 200

        else : 
            return jsonify({
            "message": "중복된 닉네임이 존재 합니다!"
        }), 400         

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/sign_up', methods=['POST'])
def run_sign_up():
    '''회원가입 로직'''
    try:
        data = request.get_json()
        name = data.get("name")
        sex = data.get("sex")
        birth_date = data.get("birth_date")
        id = data.get("id")
        nickname = data.get("nickname")  # 닉네임도 받아야 함
        password = data.get("password")
        joined_at = data.get("joined_at") #or datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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
        suf.sign_up(spark, name, sex, birth_date, id, nickname, password, joined_at)

        return jsonify({
            "message": "회원가입이 완료되었습니다.",
        }), 200

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({
            "error": "회원가입 중 오류가 발생했습니다."
        }), 500
    
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
            token = lf.generate_jwt(login_result["id"], login_result['nickname'], login_result["is_admin"], SECRET_KEY)

            # 응답 본문과 헤더 설정
            response = make_response(jsonify({
                "message": "로그인이 완료되었습니다.",
                "is_admin": login_result["is_admin"],
                "nickname" : login_result['nickname']
            }), 200)
            response.headers["Authorization"] = f"Bearer {token}"
            return response

        else:
            return jsonify({"error": login_result}), 401

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_id = data.get("user_id")
    message = data.get("message")
    search = data.get("search") #주식 종목 받아오기

    if not user_id or not message:
        return jsonify({"error": "user_id와 message는 필수입니다."}), 400

    try:
        reply = op.ask_gpt(spark, search, user_id, message)
        return jsonify({"reply": reply}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route("/check-auth", methods=["GET"])
def check_auth():
    try:
        # 1. 헤더에서 토큰 추출
        auth_header = request.headers.get("Authorization")
        #print(request.headers)
        if not auth_header : #or not auth_header.startswith("Bearer "):
            return jsonify({"error": "토큰이 없거나 형식이 올바르지 않습니다."}), 401

        token = auth_header

        # 2. JWT 디코딩 및 검증
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        # 3. 사용자 정보 확인 및 반환
        return jsonify({
            "user_id": payload.get("user_id"),
            "is_admin": payload.get("is_admin"),
            "nickname" : payload.get('nickname')
        }), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "토큰이 만료되었습니다."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "유효하지 않은 토큰입니다."}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/shutdown', methods=['POST'])
def shutdown():
    def stop_server():
        os.kill(os.getpid(), signal.SIGINT)
    threading.Thread(target=stop_server).start()
    return "서버가 종료 중입니다..."

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=False, use_reloader=False)