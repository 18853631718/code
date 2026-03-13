import requests
import json

# 测试根路由
r = requests.get('http://localhost:5000/')
print("Root:", r.status_code, r.text)

# 测试API路由
url = 'http://localhost:5000/api/analyze'
code = '''def hello(): 
    return student.name'''

data = {'code': code, 'language': 'python'}

try:
    r = requests.post(url, json=data, timeout=10)
    print("API:", r.status_code)
    if r.status_code == 200:
        print("Response:", json.dumps(r.json(), indent=2))
    else:
        print("Error:", r.text)
except Exception as e:
    print("Exception:", e)
