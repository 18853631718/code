import requests

API_URL = "http://localhost:5000/api/analyze"

TEST_CASES = [
    {
        "id": 11,
        "name": "安全 - 硬编码密码",
        "code": "DB_PASSWORD = 'mysecretpassword123'",
        "expected": "security"
    },
    {
        "id": 12,
        "name": "安全 - 硬编码API密钥",
        "code": "API_KEY = 'sk-abcdefghijklmnopqrstuvwxyz123456'",
        "expected": "security"
    },
    {
        "id": 13,
        "name": "安全 - pickle反序列化",
        "code": "import pickle\ndata = pickle.loads(user_data)",
        "expected": "security"
    },
    {
        "id": 14,
        "name": "SQL注入 - format方法",
        "code": "def query(name):\n    sql = \"SELECT * FROM users WHERE name = {}\".format(name)",
        "expected": "sql_injection"
    },
    {
        "id": 15,
        "name": "SQL注入 - %格式化",
        "code": "def query(name):\n    sql = \"SELECT * FROM users WHERE name = '%s'\" % name",
        "expected": "sql_injection"
    },
    {
        "id": 16,
        "name": "内存泄漏 - 数据库连接未关闭",
        "code": "def get_connection():\n    conn = sqlite3.connect('test.db')\n    return conn",
        "expected": "memory_leak"
    },
    {
        "id": 17,
        "name": "内存泄漏 - HTTP连接未关闭",
        "code": "import urllib\ndef fetch():\n    response = urllib.urlopen('http://example.com')\n    return response.read()",
        "expected": "memory_leak"
    },
    {
        "id": 18,
        "name": "竞态条件 - 异步函数",
        "code": "import asyncio\nasync def fetch_data():\n    await asyncio.sleep(1)\n    return data",
        "expected": "race_condition"
    },
    {
        "id": 19,
        "name": "空指针 - 字典访问",
        "code": "def get_value(d, key):\n    return d[key].value",
        "expected": "null_pointer"
    },
    {
        "id": 20,
        "name": "空指针 - 函数返回值未检查",
        "code": "def get_user():\n    return None\n\nname = get_user()\nprint(name.upper())",
        "expected": "null_pointer"
    },
    {
        "id": 21,
        "name": "安全 - os.system调用",
        "code": "import os\nos.system('ls -la')",
        "expected": "security"
    },
    {
        "id": 22,
        "name": "空指针 - 可选链前未检查",
        "code": "def process(user):\n    return user.profile.name",
        "expected": "null_pointer"
    },
    {
        "id": 23,
        "name": "良好 - 参数化查询",
        "code": "def query(name):\n    cursor.execute('SELECT * FROM users WHERE name = %s', (name,))",
        "expected": "no_defect"
    },
    {
        "id": 24,
        "name": "良好 - try-except保护",
        "code": "def safe_divide(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        return None",
        "expected": "no_defect"
    },
    {
        "id": 25,
        "name": "良好 - 日志记录",
        "code": "import logging\nlogging.basicConfig(level=logging.INFO)\nlogger = logging.getLogger(__name__)",
        "expected": "no_defect"
    },
    {
        "id": 26,
        "name": "空指针 - None比较后返回",
        "code": "def find_user(users, name):\n    for u in users:\n        if u.name == name:\n            return u\n    return None\n\nuser = find_user([], 'test')\nprint(user.name)",
        "expected": "null_pointer"
    },
    {
        "id": 27,
        "name": "内存泄漏 - 线程未join",
        "code": "import threading\ndef run():\n    t = threading.Thread(target=worker)\n    t.start()\n    return 'done'",
        "expected": "memory_leak"
    },
    {
        "id": 28,
        "name": "竞态条件 - 共享字典修改",
        "code": "cache = {}\ndef update(key, value):\n    old = cache.get(key, 0)\n    cache[key] = old + value",
        "expected": "race_condition"
    },
    {
        "id": 29,
        "name": "安全 - 命令注入",
        "code": "import subprocess\nsubprocess.call('ls ' + user_input, shell=True)",
        "expected": "security"
    },
    {
        "id": 30,
        "name": "良好 - 类型注解",
        "code": "def greet(name: str) -> str:\n    return f'Hello, {name}!'",
        "expected": "no_defect"
    }
]

def test_detection():
    print("=" * 80)
    print("AI Code Review System - Extended Detection Test (20 more cases)")
    print("=" * 80)
    
    results = []
    
    for test in TEST_CASES:
        print(f"\n[测试 {test['id']}] {test['name']}")
        print(f"预期结果: {test['expected']}")
        print(f"代码:\n{test['code']}")
        
        try:
            response = requests.post(
                API_URL,
                json={"code": test['code'], "language": "python"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                detected = result.get('defect_type', 'unknown')
                confidence = result.get('confidence', 0)
                severity = result.get('severity', 'unknown')
                line = result.get('line_number', 'N/A')
                
                match = "✓ 匹配" if detected == test['expected'] else "✗ 不匹配"
                
                print(f"检测结果: {detected}")
                print(f"置信度: {confidence}")
                print(f"严重程度: {severity}")
                print(f"行号: {line}")
                print(f"匹配: {match}")
                
                results.append({
                    "id": test['id'],
                    "name": test['name'],
                    "expected": test['expected'],
                    "actual": detected,
                    "match": detected == test['expected']
                })
            else:
                print(f"错误: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"请求错误: {e}")
    
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    
    matched = sum(1 for r in results if r['match'])
    total = len(results)
    
    for r in results:
        status = "✓" if r['match'] else "✗"
        print(f"{status} 测试{r['id']}: {r['name']} - 预期:{r['expected']} 实际:{r['actual']}")
    
    print(f"\n匹配率: {matched}/{total} ({matched*100//total}%)")

if __name__ == "__main__":
    test_detection()
