import os

from flask import Flask, request, make_response  # 서버 구현을 위한 Flask 객체 import
from flask_restx import Api, Resource  # Api 구현을 위한 Api 객체 import
from solve_cloudflare import SolveCloudflare
from dotenv import load_dotenv
from common import set_json_data

load_dotenv()  # take environment variables from .env.

app = Flask(__name__)  # Flask 객체 선언, 파라미터로 어플리케이션 패키지의 이름을 넣어줌.
api = Api(app)  # Flask 객체에 Api 객체 등록


@api.route('/hello/<string:name>')  # url pattern으로 name 설정
class Hello(Resource):
    def get(self, name):  # 멤버 함수의 파라미터로 name 설정
        return {"message": "Welcome, %s!" % name}


@api.route('/solvecloudflare')
class SolveSite(Resource):
    def post(self):
        api_key = request.json.get('api-key')
        print('-------------------------incoming request start-------------------------')

        url = request.json.get('url')
        print(f'url: {url}')

        user_agent = request.json.get('user_agent')
        print(f'user_agent: {user_agent}')

        use_random_agent = request.json.get('use_random_agent')
        print(f'use_random_agent: {use_random_agent}')

        if use_random_agent is None:
            use_random_agent = False

        random_agent_name = request.json.get('random_agent_name')
        print(f'random_agent_name: {random_agent_name}')

        print('-------------------------incoming request end-------------------------')

        if api_key == os.environ.get("API_KEY"):
            result = SolveCloudflare.solve(url=url,
                                           user_agent=user_agent,
                                           use_random_agent=use_random_agent,
                                           random_agent_name=random_agent_name)

            return make_response(set_json_data({"result": result, 'status': True}), 200)
        else:
            return make_response(set_json_data({"result": '', 'status': False}), 401)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
