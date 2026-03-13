import requests
import json

# 测试前端代理
url = 'http://localhost:3001/api/analyze'
code = '''def hello(): 
    return student.name'''

data = {'code': code, 'language': 'python'}

try:
    r = requests.post(url, json=data, timeout=10)
    print("Status:", r.status_code)
    if r.status_code == 200:
        print("Response:", json.dumps(r.json(), indent=2))
    else:
        print("Error:", r.text)
except Exception as e:
    print("Exception:", e)
