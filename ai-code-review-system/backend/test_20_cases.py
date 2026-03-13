import os
import sys
import json
import requests

# 后端API地址
API_URL = 'http://localhost:5000/api/analyze'

# 20个测试用例
test_cases = [
    # 1. 空指针异常
    {
        "name": "空指针引用",
        "code": "def process():\n    user = None\n    return user.name",
        "expected": "null_pointer"
    },
    # 2. SQL注入
    {
        "name": "SQL注入",
        "code": "def get_user(user_id):\n    query = f'SELECT * FROM users WHERE id = {user_id}'\n    return query",
        "expected": "sql_injection"
    },
    # 3. 内存泄漏
    {
        "name": "内存泄漏",
        "code": "def read_file():\n    f = open('data.txt', 'r')\n    content = f.read()\n    return content",
        "expected": "memory_leak"
    },
    # 4. 竞态条件
    {
        "name": "竞态条件",
        "code": "counter = 0\ndef increment():\n    global counter\n    counter += 1",
        "expected": "race_condition"
    },
    # 5. 安全问题
    {
        "name": "安全问题",
        "code": "def execute_cmd(cmd):\n    os.system(cmd)",
        "expected": "security"
    },
    # 6. 无缺陷代码
    {
        "name": "无缺陷代码",
        "code": "def safe_process(user):\n    if user is not None:\n        return user.name\n    return None",
        "expected": "no_defect"
    },
    # 7. 空指针异常变体
    {
        "name": "空指针异常变体",
        "code": "def get_data():\n    data = None\n    return data['key']",
        "expected": "null_pointer"
    },
    # 8. SQL注入变体
    {
        "name": "SQL注入变体",
        "code": "def search_user(name):\n    sql = \"SELECT * FROM users WHERE name = '\" + name + \"'\n    return sql",
        "expected": "sql_injection"
    },
    # 9. 内存泄漏变体
    {
        "name": "内存泄漏变体",
        "code": "def get_connection():\n    conn = db.connect()\n    return conn",
        "expected": "memory_leak"
    },
    # 10. 竞态条件变体
    {
        "name": "竞态条件变体",
        "code": "shared_data = {}\ndef update(key, value):\n    old = shared_data.get(key, 0)\n    shared_data[key] = old + value",
        "expected": "race_condition"
    },
    # 11. 安全问题变体
    {
        "name": "安全问题变体",
        "code": "def load_data(data):\n    import pickle\n    return pickle.loads(data)",
        "expected": "security"
    },
    # 12. 无缺陷代码变体
    {
        "name": "无缺陷代码变体",
        "code": "def divide(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        return None",
        "expected": "no_defect"
    },
    # 13. 空指针异常 - 数组访问
    {
        "name": "空指针异常 - 数组访问",
        "code": "def get_first_element(arr):\n    return arr[0].value",
        "expected": "null_pointer"
    },
    # 14. SQL注入 - 字符串拼接
    {
        "name": "SQL注入 - 字符串拼接",
        "code": "def delete_user(id):\n    sql = \"DELETE FROM users WHERE id = \" + str(id)\n    return sql",
        "expected": "sql_injection"
    },
    # 15. 内存泄漏 - 线程
    {
        "name": "内存泄漏 - 线程",
        "code": "def start_thread():\n    thread = threading.Thread(target=worker)\n    thread.start()\n    return 'done'",
        "expected": "memory_leak"
    },
    # 16. 竞态条件 - 类变量
    {
        "name": "竞态条件 - 类变量",
        "code": "class Counter:\n    count = 0\n    def increment(self):\n        self.count += 1",
        "expected": "race_condition"
    },
    # 17. 安全问题 - 硬编码密码
    {
        "name": "安全问题 - 硬编码密码",
        "code": "def get_connection():\n    password = \"admin123\"\n    return db.connect(password=password)",
        "expected": "security"
    },
    # 18. 无缺陷代码 - with语句
    {
        "name": "无缺陷代码 - with语句",
        "code": "def read_file_safe():\n    with open('data.txt', 'r') as f:\n        return f.read()",
        "expected": "no_defect"
    },
    # 19. 空指针异常 - 方法调用
    {
        "name": "空指针异常 - 方法调用",
        "code": "def call_method(obj):\n    obj.method()",
        "expected": "null_pointer"
    },
    # 20. 无缺陷代码 - 参数化查询
    {
        "name": "无缺陷代码 - 参数化查询",
        "code": "def safe_query(name):\n    cursor.execute('SELECT * FROM users WHERE name = %s', (name,))",
        "expected": "no_defect"
    }
]

# 分析单个测试用例
def analyze_code(code, language='python'):
    payload = {
        'code': code,
        'language': language
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f'API error: {response.status_code}'}
    except Exception as e:
        return {'error': str(e)}

# 运行测试
def run_tests():
    print('开始测试20个测试用例...')
    print('-' * 80)
    
    correct = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f'测试用例 {i}: {test_case["name"]}')
        result = analyze_code(test_case['code'])
        
        if 'error' in result:
            print(f'  错误: {result["error"]}')
        else:
            defect_type = result.get('defect_type', 'no_defect')
            confidence = result.get('confidence', 0)
            method = result.get('method', 'unknown')
            print(f'  预测: {defect_type} (置信度: {confidence:.2f}, 方法: {method})')
            print(f'  预期: {test_case["expected"]}')
            
            if defect_type == test_case['expected']:
                correct += 1
                print(f'  ✅ 正确')
            else:
                print(f'  ❌ 错误')
        
        print('-' * 80)
    
    accuracy = correct / total * 100
    print(f'\n测试结果: {correct}/{total} 正确')
    print(f'准确率: {accuracy:.2f}%')

if __name__ == '__main__':
    run_tests()
