"""
直接测试ML模型
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from services.ml_model_service import MLModelService

TEST_CASES = [
    {"code": "def get_user():\n    user = None\n    return user.name", "expected": "null_pointer"},
    {"code": "def get_first(items):\n    return items[0].name", "expected": "null_pointer"},
    {"code": "def query(name):\n    sql = \"SELECT * FROM users WHERE name = '\" + name + \"'\"\n    return sql", "expected": "sql_injection"},
    {"code": "def search(query):\n    return f\"SELECT * FROM products WHERE name = '{query}'\"", "expected": "sql_injection"},
    {"code": "def read():\n    f = open('test.txt', 'r')\n    return f.read()", "expected": "memory_leak"},
    {"code": "counter = 0\ndef inc():\n    global counter\n    counter += 1\n    return counter", "expected": "race_condition"},
    {"code": "def run(code):\n    eval(code)", "expected": "security"},
    {"code": "def get_name(user):\n    if user is not None:\n        return user.name\n    return None", "expected": "no_defect"},
    {"code": "def read():\n    with open('test.txt', 'r') as f:\n        return f.read()", "expected": "no_defect"},
    {"code": "def add(a, b):\n    return a + b", "expected": "no_defect"},
]

def test():
    print("="*60)
    print("Testing ML Model")
    print("="*60)
    
    service = MLModelService()
    
    results = []
    for test in TEST_CASES:
        result = service.predict(test['code'], 'python')
        detected = result.get('defect_type', 'unknown')
        expected = test['expected']
        match = detected == expected
        
        status = "✓" if match else "✗"
        print(f"\n{status} [{test['expected']}] {test['code'][:40]}...")
        print(f"   预期: {expected}, 实际: {detected}, 方法: {result.get('method', 'N/A')}")
        
        results.append({
            'expected': expected,
            'actual': detected,
            'match': match
        })
    
    matched = sum(1 for r in results if r['match'])
    total = len(results)
    
    print("\n" + "="*60)
    print(f"匹配率: {matched}/{total} ({matched*100//total}%)")
    print("="*60)

if __name__ == "__main__":
    test()
