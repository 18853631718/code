import requests

# 测试前端使用的完整URL
base_url = 'http://localhost:5000'

# 测试所有可能的路由
routes = [
    '/api/analysis/statistics',
    '/api/analysis/history',
    '/api/analyze',
    '/api/code/languages'
]

for route in routes:
    url = base_url + route
    try:
        r = requests.get(url, timeout=5)
        print(f"{route}: {r.status_code}")
    except Exception as e:
        print(f"{route}: Error - {e}")

# 测试analyze POST
try:
    r = requests.post(base_url + '/api/analyze', json={'code': 'print(1)', 'language': 'python'}, timeout=5)
    print(f"/api/analyze POST: {r.status_code}")
except Exception as e:
    print(f"/api/analyze POST: Error - {e}")
