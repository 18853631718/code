from service import CodeAnalyzer

code_analyzer = CodeAnalyzer()

# 测试Python语法错误
test_code = '''
hello_world():
    print("Hello, World!")
'''

features = code_analyzer.extract_features(test_code, 'python')
print("Python语法错误测试结果:")
print(f"Issues: {features.get('issues', [])}")
print(f"Has syntax error: {'syntax_error' in [issue.get('type') for issue in features.get('issues', [])]}")

# 测试正确的Python代码
test_code_correct = '''
def hello_world():
    print("Hello, World!")
'''

features = code_analyzer.extract_features(test_code_correct, 'python')
print("\n正确Python代码测试结果:")
print(f"Issues: {features.get('issues', [])}")
print(f"Has syntax error: {'syntax_error' in [issue.get('type') for issue in features.get('issues', [])]}")
