from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/add')
def add_numbers():
    # URL 쿼리 파라미터에서 x와 y 값을 가져옴
    x = request.args.get('x', type=int)
    y = request.args.get('y', type=int)

    if x is None or y is None:
        return jsonify({'error': 'x와 y 값을 숫자로 입력해주세요. 예: /add?x=10&y=20'})

    result = x + y
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)
