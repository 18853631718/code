from service.code_analyzer import CodeAnalyzer
from flask import Flask, request
import json

app = Flask(__name__)

# 测试Python语法错误检测
def test_python_syntax_error():
    analyzer = CodeAnalyzer()
    
    # 测试缺少def的情况
    code_without_def = '''
hello_world():
    print("Hello, World!")
'''
    
    features = analyzer.extract_features(code_without_def, 'python')
    print("Python code without def:")
    print(f"Issues: {features.get('issues', [])}")
    print(f"Has syntax error: {'syntax_error' in [issue.get('type') for issue in features.get('issues', [])]}")
    
    # 测试正确的Python代码
    correct_code = '''
class Test:
    def __init__(self):
        self.name = "test"
    def hello(self):
        return "Hello"
'''
    
    features_correct = analyzer.extract_features(correct_code, 'python')
    print("\nCorrect Python code:")
    print(f"Issues: {features_correct.get('issues', [])}")
    print(f"Has syntax error: {'syntax_error' in [issue.get('type') for issue in features_correct.get('issues', [])]}")

if __name__ == "__main__":
    test_python_syntax_error()
