import requests
import json

API_URL = "http://localhost:5000/api/analyze"

TEST_CASES = [
    {
        "id": 1,
        "name": "空指针 - 基本空指针",
        "code": "def get_user():\n    user = None\n    return user.name",
        "expected": "null_pointer"
    },
    {
        "id": 2,
        "name": "空指针 - 列表索引越界",
        "code": "def get_first(items):\n    return items[0].name",
        "expected": "null_pointer"
    },
    {
        "id": 3,
        "name": "SQL注入 - 字符串拼接",
        "code": "def query(name):\n    sql = \"SELECT * FROM users WHERE name = '\" + name + \"'\"\n    return sql",
        "expected": "sql_injection"
    },
    {
        "id": 4,
        "name": "SQL注入 - f-string",
        "code": "def search(query):\n    return f\"SELECT * FROM products WHERE name = '{query}'\"",
        "expected": "sql_injection"
    },
    {
        "id": 5,
        "name": "内存泄漏 - 文件未关闭",
        "code": "def read():\n    f = open('test.txt', 'r')\n    return f.read()",
        "expected": "memory_leak"
    },
    {
        "id": 6,
        "name": "竞态条件 - 全局变量",
        "code": "counter = 0\ndef inc():\n    global counter\n    counter += 1\n    return counter",
        "expected": "race_condition"
    },
    {
        "id": 7,
        "name": "安全问题 - eval使用",
        "code": "def run(code):\n    eval(code)",
        "expected": "security"
    },
    {
        "id": 8,
        "name": "良好代码 - 空值检查",
        "code": "def get_name(user):\n    if user is not None:\n        return user.name\n    return None",
        "expected": "no_defect"
    },
    {
        "id": 9,
        "name": "良好代码 - with语句",
        "code": "def read():\n    with open('test.txt', 'r') as f:\n        return f.read()",
        "expected": "no_defect"
    },
    {
        "id": 10,
        "name": "良好代码 - 简单函数",
        "code": "def add(a, b):\n    return a + b",
        "expected": "no_defect"
    }
]

def test_detection():
    print("=" * 80)
    print("AI Code Review System - Detection Test")
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
