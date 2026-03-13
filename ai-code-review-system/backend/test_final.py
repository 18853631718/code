import requests
import json

# 测试完整URL（和前端一样）
base = 'http://localhost:5000'

# 测试所有API
tests = [
    ('GET', '/api/analysis/statistics', None),
    ('GET', '/api/analysis/history', None),
    ('GET', '/api/code/languages', None),
    ('POST', '/api/analyze', {'code': 'print(1)', 'language': 'python'}),
]

for method, path, data in tests:
    url = base + path
    try:
        if method == 'GET':
            r = requests.get(url, timeout=5)
        else:
            r = requests.post(url, json=data, timeout=5)
        print(f"{method} {path}: {r.status_code}")
        if r.status_code == 200 and method == 'GET':
            result = r.json()
            print(f"  Response keys: {list(result.keys()) if isinstance(result, dict) else 'list'}")
    except Exception as e:
        print(f"{method} {path}: Error - {e}")
