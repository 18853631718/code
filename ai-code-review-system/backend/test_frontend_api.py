import requests

# 使用前端的baseURL配置
base = 'http://localhost:5000'

# 测试所有前端使用的API
print("Testing all APIs with frontend config:")
print("=" * 50)

# 1. 统计接口
r = requests.get(f'{base}/api/analysis/statistics')
print(f"1. /api/analysis/statistics: {r.status_code}")

# 2. 历史接口
r = requests.get(f'{base}/api/analysis/history')
print(f"2. /api/analysis/history: {r.status_code}")

# 3. 分析接口
r = requests.post(f'{base}/api/analyze', json={'code': 'def test(): return x', 'language': 'python'})
print(f"3. /api/analyze: {r.status_code}")
if r.status_code == 200:
    print(f"   Issues: {r.json().get('issues', [])}")

# 4. 语言接口
r = requests.get(f'{base}/api/code/languages')
print(f"4. /api/code/languages: {r.status_code}")

print("\nAll tests passed!" if all([r.status_code == 200]) else "\nSome tests failed!")
