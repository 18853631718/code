import sys
sys.path.insert(0, '.')

from service.code_analyzer import CodeAnalyzer

analyzer = CodeAnalyzer()

# 测试语法错误检测
code = "hello_world():\n    print('Hello')"
result = analyzer.detect_syntax_error(code, 'python')
print(f"Syntax error result: {result}")

# 测试正确代码
code2 = "def hello_world():\n    print('Hello')"
result2 = analyzer.detect_syntax_error(code2, 'python')
print(f"Correct code result: {result2}")
