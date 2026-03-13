#!/usr/bin/env python3
"""
项目功能演示测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_api():
    # 1. 健康检查
    print_header("1. 健康检查测试")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✓ 健康检查成功: {response.json()}")
    except Exception as e:
        print(f"✗ 健康检查失败: {e}")
        return

    # 2. 测试用例1: 语法错误检测
    print_header("2. 语法错误检测")
    code1 = """def hello_world(
    print("Hello")
"""
    try:
        response = requests.post(f"{BASE_URL}/api/analyze", json={
            "code": code1,
            "language": "python"
        })
        result = response.json()
        print(f"代码:\n{code1}")
        print(f"\n结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"✗ 测试失败: {e}")

    # 3. 测试用例2: 未定义变量检测
    print_header("3. 未定义变量检测")
    code2 = """# Example Python code 
def hello_world():
    return student.name

if __name__ == "__main__":
    hello_world()
"""
    try:
        response = requests.post(f"{BASE_URL}/api/analyze", json={
            "code": code2,
            "language": "python"
        })
        result = response.json()
        print(f"代码:\n{code2}")
        print(f"\n结果: {json.dumps(result, indent=2, ensure_ascii=False)")
    except Exception as e:
        print(f"✗ 测试失败: {e}")

    # 4. 测试用例3: 空指针检测
    print_header("4. 空指针检测")
    code3 = """def process():
    user = None
    return user.name
"""
    try:
        response = requests.post(f"{BASE_URL}/api/analyze", json={
            "code": code3,
            "language": "python"
        })
        result = response.json()
        print(f"代码:\n{code3}")
        print(f"\n结果: {json.dumps(result, indent=2, ensure_ascii=False)")
    except Exception as e:
        print(f"✗ 测试失败: {e}")

    # 5. 测试用例4: SQL注入检测
    print_header("5. SQL注入检测")
    code4 = """def get_user(name):
    query = f"SELECT * FROM users WHERE name = '{name}'"
    return query
"""
    try:
        response = requests.post(f"{BASE_URL}/api/analyze", json={
            "code": code4,
            "language": "python"
        })
        result = response.json()
        print(f"代码:\n{code4}")
        print(f"\n结果: {json.dumps(result, indent=2, ensure_ascii=False)")
    except Exception as e:
        print(f"✗ 测试失败: {e}")

    # 6. 测试用例5: 内存泄漏检测
    print_header("6. 内存泄漏检测")
    code5 = """def read_file():
    f = open('test.txt', 'r')
    data = f.read()
    return data
"""
    try:
        response = requests.post(f"{BASE_URL}/api/analyze", json={
            "code": code5,
            "language": "python"
        })
        result = response.json()
        print(f"代码:\n{code5}")
        print(f"\n结果: {json.dumps(result, indent=2, ensure_ascii=False)")
    except Exception as e:
        print(f"✗ 测试失败: {e}")

    # 7. 测试统计接口
    print_header("7. 统计数据接口")
    try:
        response = requests.get(f"{BASE_URL}/api/analysis/statistics")
        print(f"统计数据: {json.dumps(response.json(), indent=2, ensure_ascii=False}")
    except Exception as e:
        print(f"✗ 获取统计数据失败: {e}")

    # 8. 测试语言列表
    print_header("8. 支持的语言列表")
    try:
        response = requests.get(f"{BASE_URL}/api/code/languages")
        print(f"支持的语言: {json.dumps(response.json(), indent=2, ensure_ascii=False}")
    except Exception as e:
        print(f"✗ 获取语言列表失败: {e}")

    print_header("测试完成！")

if __name__ == "__main__":
    test_api()
