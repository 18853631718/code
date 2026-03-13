import requests
import json

# 测试新的语法错误检测路由
def test_new_route():
    url = 'http://localhost:5000/test-syntax-error'
    
    # 测试缺少def的情况
    code_without_def = '''
hello_world():
    print("Hello, World!")
'''
    
    # 发送HTTP请求
    data = {
        'code': code_without_def,
        'language': 'python'
    }
    
    print("Testing new route with Python code without def...")
    response = requests.post(url, json=data)
    
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {json.dumps(response.json(), indent=2)}")
    
    # 检查是否检测到语法错误
    if response.json().get('defect_type') == 'syntax_error':
        print("✓ Syntax error detected successfully!")
    else:
        print("✗ Syntax error not detected!")
    
    # 测试正确的Python代码
    correct_code = '''
def hello_world():
    print("Hello, World!")
'''
    
    data = {
        'code': correct_code,
        'language': 'python'
    }
    
    print("\nTesting new route with correct Python code...")
    response = requests.post(url, json=data)
    
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {json.dumps(response.json(), indent=2)}")
    
    # 检查是否没有检测到语法错误
    if response.json().get('defect_type') != 'syntax_error':
        print("✓ Correct code passed successfully!")
    else:
        print("✗ Correct code incorrectly flagged as syntax error!")

if __name__ == "__main__":
    test_new_route()
