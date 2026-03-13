import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request
from controller.code_controller import analyze_code
import json

app = Flask(__name__)

# 测试Python语法错误
print("测试Python语法错误")
with app.test_request_context('/api/analyze', method='POST', json={
    'code': 'hello_world():\n    print("Hello, World!")',
    'language': 'python'
}):
    response = analyze_code()
    print(f"Status code: {response[1]}")
    print(json.dumps(response[0].json, indent=2, ensure_ascii=False))

print("\n测试正确Python代码")
with app.test_request_context('/api/analyze', method='POST', json={
    'code': 'def hello_world():\n    print("Hello, World!")',
    'language': 'python'
}):
    response = analyze_code()
    print(f"Status code: {response[1]}")
    print(json.dumps(response[0].json, indent=2, ensure_ascii=False))
