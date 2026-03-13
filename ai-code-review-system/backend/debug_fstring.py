"""
调试f-string检测
"""
import re

code = 'def search(query):\n    return f"SELECT * FROM products WHERE name = \'{query}\'"'
code_lower = code.lower()

# 测试各种f-string模式
patterns = [
    (r'f".*\{.*\}.*(select|insert|update|delete)', 'Pattern 1'),
    (r'f".*select', 'Pattern 2'),
    (r'f".*\{.*select', 'Pattern 3'),
]

for pattern, name in patterns:
    match = re.search(pattern, code_lower)
    print(f"{name}: {match}")

print("\n" + code)
print(code_lower)
