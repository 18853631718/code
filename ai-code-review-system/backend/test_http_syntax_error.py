from service.code_analyzer import CodeAnalyzer
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# 模拟HTTP请求测试
def test_http_syntax_error():
    analyzer = CodeAnalyzer()
    
    # 测试缺少def的情况
    code_without_def = '''
hello_world():
    print("Hello, World!")
'''
    
    # 模拟HTTP请求数据
    data = {
        'code': code_without_def,
        'language': 'python'
    }
    
    # 手动调用分析逻辑
    print("Testing HTTP-like analysis...")
    ast_features = analyzer.extract_features(code_without_def, 'python')
    print(f"Features: {ast_features}")
    print(f"Issues: {ast_features.get('issues', [])}")
    
    # 检查是否有语法错误
    issues = ast_features.get('issues', [])
    print(f"Number of issues: {len(issues)}")
    
    syntax_errors = []
    for issue in issues:
        print(f"Issue: {issue}")
        if isinstance(issue, dict):
            print(f"Issue type: {issue.get('type')}")
            if issue.get('type') == 'syntax_error':
                syntax_errors.append(issue)
    
    print(f"Syntax errors: {syntax_errors}")
    print(f"Number of syntax errors: {len(syntax_errors)}")
    
    if syntax_errors:
        print("Syntax error detected!")
    else:
        print("No syntax error detected!")

if __name__ == "__main__":
    test_http_syntax_error()
