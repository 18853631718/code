#!/usr/bin/env python3
"""
简单的功能测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:5000"

print("=" * 60)
print("  AI代码检测平台 - 功能测试")
print("=" * 60)

# 1. 健康检查
print("\n1. 健康检查...")
try:
    resp = requests.get(f"{BASE_URL}/")
    print(f"✓ 健康检查成功: {resp.json()}")
except Exception as e:
    print(f"✗ 健康检查失败: {e}")
    exit(1)

# 2. 测试未定义变量
print("\n2. 测试未定义变量检测...")
code = """# Example Python code 
def hello_world():
    return student.name

if __name__ == "__main__":
    hello_world()
"""
try:
    resp = requests.post(f"{BASE_URL}/api/analyze", json={"code": code, "language": "python"})
    result = resp.json()
    print("✓ 测试成功!")
    print("  发现的问题:")
    for issue in result.get('issues', []):
        print(f"    - 第{issue.get('line')}行: {issue.get('message')}")
except Exception as e:
    print(f"✗ 测试失败: {e}")

# 3. 测试语法错误
print("\n3. 测试语法错误检测...")
code = """def hello_world(
    print("Hello")
"""
try:
    resp = requests.post(f"{BASE_URL}/api/analyze", json={"code": code, "language": "python"})
    result = resp.json()
    print("✓ 测试成功!")
    print(f"  缺陷类型: {result.get('defect_type')}")
    print(f"  错误信息: {result.get('suggestion')}")
except Exception as e:
    print(f"✗ 测试失败: {e}")

# 4. 测试统计接口
print("\n4. 测试统计接口...")
try:
    resp = requests.get(f"{BASE_URL}/api/analysis/statistics")
    stats = resp.json()
    print("✓ 统计数据获取成功!")
    print(f"  总分析次数: {stats.get('total_analyses')}")
    print(f"  平均置信度: {stats.get('average_confidence')}")
except Exception as e:
    print(f"✗ 测试失败: {e}")

print("\n" + "=" * 60)
print("  所有测试完成!")
print("=" * 60)
