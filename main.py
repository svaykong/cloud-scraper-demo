import os

# from flask import Flask, request, make_response  # 서버 구현을 위한 Flask 객체 import
# from flask_restx import Api, Resource, fields  # Api 구현을 위한 Api 객체 import
from dotenv import load_dotenv
from src.solve_cloudflare import SolveCloudflare
from src.common import set_json_data

# app = Flask(__name__)  # Flask 객체 선언, 파라미터로 어플리케이션 패키지의 이름을 넣어줌.
# api = Api()  # Flask 객체에 Api 객체 등록
# api.init_app(app)

# resource_fields = api.model('Resource', {
#     'API_KEY': fields.String,
#     'url': fields.String,
#     'assert_element': fields.String,
# })

# @api.route('/hello/<string:name>')  # url pattern으로 name 설정
# class Hello(Resource):
#     def get(self, name):  # 멤버 함수의 파라미터로 name 설정
#         return {"message": "Welcome, %s!" % name}

# # Payload validation enabled
# @api.expect(resource_fields)
# @api.route('/solvecloudflare')
# class SolveSite(Resource):
#     def post(self):
#         api_key = request.json.get('API_KEY')
#         print('-------------------------incoming request start-------------------------')

#         url = request.json.get('url')
#         print(f'url: {url}')

#         assert_element = request.json.get('assert_element')
#         print(f'assert_element: {assert_element}')

#         user_agent = request.json.get('user_agent')
#         print(f'user_agent: {user_agent}')

#         proxy = request.json.get('proxy')
#         print(f'proxy: {proxy}')

#         print('-------------------------incoming request end-------------------------')

#         if api_key == os.environ.get("API_KEY"):
#             cloud_instance = SolveCloudflare()
#             result = ''
#             error = ''
#             try:
#                 result = cloud_instance.solve(url=url, assert_element=assert_element, user_agent=user_agent, proxy=proxy)
#             except Exception as e:
#                 print(f'solve exception: {e}')
#                 error = str(e)
#             return make_response(set_json_data({"result": result, "error": error}), 200)
#         elif assert_element is None or assert_element == '':
#             return make_response(set_json_data({"result": "", "error": "invalid assert_element"}), 401)
#         else:
#             return make_response(set_json_data({"result": "", "error": "invalid API_KEY"}), 401)


if __name__ == '__main__':
    # app.run(debug=True, host='0.0.0.0', port=8000)

    load_dotenv()  # take environment variables from .env.
    cloud_instance = SolveCloudflare()
    try:
        result = cloud_instance.solve(
            # url='https://owner.yogiyo.co.kr/owner/logout/', 
            # assert_element="img[alt=\"요기요 사장님 BI\"]", 
            url='https://onlinebanking.metrobank.com.ph/signin',
            assert_element="button[type=\"submit\"]", 
            user_agent=None, 
            proxy=None)
        print(result)
    except Exception as e:
        print(f'solve exception: {e}')

