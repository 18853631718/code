import requests
import json

# 测试前端API
def test_frontend():
    # 测试分析接口
    url = 'http://localhost:5000/api/analyze'
    
    # 测试Python语法错误
    python_code_with_error = '''
hello_world():
    print("Hello")
'''
    
    data = {
        'code': python_code_with_error,
        'language': 'python'
    }
    
    print("Testing Python syntax error detection...")
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Result: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 测试正确的Python代码
    print("\nTesting correct Python code...")
    correct_code = '''
def hello_world():
    print("Hello")
'''
    
    data = {
        'code': correct_code,
        'language': 'python'
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Result: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_frontend()
