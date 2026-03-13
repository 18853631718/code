"""
代码分词工具
"""

import re

def tokenize_code(code):
    """代码分词"""
    # 移除注释
    code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
    code = re.sub(r'/\*[\s\S]*?\*/', '', code)
    # 分词
    tokens = re.findall(r'\b\w+\b|[{}()\[\];.,:+*=/\-]', code)
    # 提取特征词
    features = []
    for token in tokens:
        if token.isalpha() and len(token) > 1:
            features.append(token.lower())
        elif token in ['=', '==', '!=', 'null', 'if', 'else', 'while', 'for', 'try', 'catch', 'finally', 'static', 'public', 'private', 'protected']:
            features.append(token)
    return features
