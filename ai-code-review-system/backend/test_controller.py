from controller.code_controller import analyze_code
from flask import Flask, request
import json

app = Flask(__name__)

with app.test_request_context('/api/analyze', method='POST', json={
    'code': 'hello_world():\n    print("Hello, World!")',
    'language': 'python'
}):
    response = analyze_code()
    print("Python语法错误测试结果:")
    print(json.dumps(response[0].json, indent=2, ensure_ascii=False))
    print(f"Status code: {response[1]}")

with app.test_request_context('/api/analyze', method='POST', json={
    'code': 'def hello_world():\n    print("Hello, World!")',
    'language': 'python'
}):
    response = analyze_code()
    print("\n正确Python代码测试结果:")
    print(json.dumps(response[0].json, indent=2, ensure_ascii=False))
    print(f"Status code: {response[1]}")
