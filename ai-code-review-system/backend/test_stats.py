import requests

# 测试统计接口
r = requests.get('http://localhost:5000/api/analysis/statistics')
print("Statistics:", r.status_code, r.json())

# 测试历史接口
r = requests.get('http://localhost:5000/api/analysis/history')
print("History:", r.status_code, r.json())
