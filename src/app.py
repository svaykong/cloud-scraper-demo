from flask import Flask, request  # 서버 구현을 위한 Flask 객체 import
from flask_restx import Api, Resource  # Api 구현을 위한 Api 객체 import
from solve_cloudflare import SolveCloudflare

app = Flask(__name__)  # Flask 객체 선언, 파라미터로 어플리케이션 패키지의 이름을 넣어줌.
api = Api(app)  # Flask 객체에 Api 객체 등록

''' 
    1. Testing owner host passed
    host = 'https://owner.yogiyo.co.kr'
    url = '/owner/login'
'''
'''
    2. Testing ceo host passed
    host = 'https://ceo.yogiyo.co.kr'
    url = '/login'
'''
'''
    3. onlinebanking host passed
    host = 'https://onlinebanking.metrobank.com.ph'
    url = '/signin'
'''
'''
    4. internetbanking host passed
    host = 'https://www.internetbanking.cimbbank.com.kh'
    url = '/corp/common2/login.do?action=loginRequest'
'''
'''
    5. g2 host passed
    host = 'https://www.g2.com'
    url = '/products/asana/reviews'
'''


@api.route('/hello/<string:name>')  # url pattern으로 name 설정
class Hello(Resource):
    def get(self, name):  # 멤버 함수의 파라미터로 name 설정
        return {"message": "Welcome, %s!" % name}


@api.route('/solvecloudflare')
class SolveSite(Resource):
    def post(self):
        api_key = request.json.get('api-key')
        url = request.json.get('url')

        if api_key == 'pncsoft1':
            result = SolveCloudflare.solve(url)
            return {"result": result, 'status': True, 'code': 200}
        else:
            return {"result": '', 'status': False, 'code': 401}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
