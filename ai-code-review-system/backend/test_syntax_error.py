import requests
import json

# 测试Python语法错误
test_code = 'hello_world():\n    print("Hello, World!")'
print(f"Test code: {repr(test_code)}")
print(f"Test code length: {len(test_code)}")

response = requests.post('http://localhost:5000/api/analyze', json={
    'code': test_code,
    'language': 'python'
})
print(f"Response status code: {response.status_code}")

print("Python语法错误测试结果:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# 测试正确的Python代码
test_code_correct = '''
def hello_world():
    print("Hello, World!")
'''

response = requests.post('http://localhost:5000/api/analyze', json={
    'code': test_code_correct,
    'language': 'python'
})

print("\n正确Python代码测试结果:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
