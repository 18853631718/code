from service.code_analyzer import CodeAnalyzer
from controller.code_controller import analyze_code
from flask import Flask, request
import json

app = Flask(__name__)

# 直接测试语法错误检测
def test_syntax_error_direct():
    analyzer = CodeAnalyzer()
    
    # 测试缺少def的情况
    code_without_def = '''
hello_world():
    print("Hello, World!")
'''
    
    print("Testing syntax error detection directly...")
    syntax_error = analyzer.detect_syntax_error(code_without_def, 'python')
    print(f"Syntax error detected: {syntax_error}")
    
    if syntax_error:
        print("✓ Syntax error detected successfully!")
    else:
        print("✗ Syntax error not detected!")
    
    # 测试正确的Python代码
    correct_code = '''
def hello_world():
    print("Hello, World!")
'''
    
    syntax_error_correct = analyzer.detect_syntax_error(correct_code, 'python')
    print(f"Syntax error in correct code: {syntax_error_correct}")
    
    if not syntax_error_correct:
        print("✓ Correct code passed successfully!")
    else:
        print("✗ Correct code incorrectly flagged as syntax error!")

if __name__ == "__main__":
    test_syntax_error_direct()
