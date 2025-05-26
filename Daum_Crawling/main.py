import search_function as f
import OpenAI as op
import financial_function as ff
import stock_news_function as snf
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/stock_news', methods=['GET'])
def run_stock_news():
    '''실시간 주식 뉴스 JSON으로 변환'''
    try:
        json_data = snf.stock_news()
        return jsonify(json_data)  # 🔥 바로 JSON 내용 반환
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
        result = ff.financial_search(search)

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
        f.daum_search(search, int(page_count))

        return jsonify({
            "message": f"'{search}' 에 대한 뉴스 {page_count} 페이지 크롤링 및 저장 완료"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#op.run(search) #OpenAI 모듈 실행       

if __name__ == '__main__':
    app.run(debug=True)