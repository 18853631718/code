import requests
import json

# 测试从前端访问后端（通过代理）
proxies = {
    'http': 'http://localhost:3001',
    'https': 'http://localhost:3001'
}

# 不使用代理，直接访问后端
base = 'http://localhost:5000'

# 统计
r = requests.get(f'{base}/api/analysis/statistics')
print(f"Statistics: {r.status_code}")
if r.status_code == 200:
    print(f"  Data: {json.dumps(r.json(), indent=2)[:200]}")

# 历史
r = requests.get(f'{base}/api/analysis/history')
print(f"\nHistory: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"  History type: {type(data)}")
    if isinstance(data, list):
        print(f"  Items: {len(data)}")
    else:
        print(f"  Data: {json.dumps(data, indent=2)[:200]}")
