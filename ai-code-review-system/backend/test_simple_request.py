import requests
import json

# 测试端点是否可访问
def test_endpoints():
    # 先测试根路由
    r = requests.get('http://localhost:5000/')
    print(f"Root route: {r.status_code} - {r.text}")

    # 测试test-syntax-error
    data = {'code': 'hello_world():\n    print(1)', 'language': 'python'}
    r = requests.post('http://localhost:5000/test-syntax-error', json=data)
    print(f"Test syntax error: {r.status_code}")
    if r.status_code == 200:
        print(f"Response: {r.json()}")
    else:
        print(f"Response text: {r.text}")

if __name__ == '__main__':
    test_endpoints()
