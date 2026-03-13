"""
简化版检测服务 - 只使用规则引擎
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from typing import Dict, Any, Optional
import re

class SimpleAnalyzer:
    """简化版检测器 - 只使用规则"""
    
    def analyze(self, code: str) -> Dict[str, Any]:
        code_lower = code.lower()
        
        # 安全问题
        if re.search(r'\beval\s*\(', code_lower):
            return self._result('security', 0.95, self._find_line(code, r'\beval\s*\('), 'Use of eval() is dangerous')
        
        if re.search(r'\bos\.system\s*\(', code_lower):
            return self._result('security', 0.95, self._find_line(code, r'\bos\.system\s*\('), 'Use of os.system() is dangerous')
        
        if re.search(r'(password|secret[_-]?key|api[_-]?key)\s*=\s*["\']', code_lower):
            return self._result('security', 0.90, self._find_line(code, r'password|secret|api'), 'Hardcoded credentials detected')
        
        # SQL注入
        if re.search(r'(select|insert|update|delete).*\+', code_lower):
            return self._result('sql_injection', 0.90, self._find_line(code, r'.*\+'), 'SQL string concatenation')
        
        if re.search(r'f".*?(select|insert|update|delete)', code_lower) or re.search(r"f'.*?(select|insert|update|delete)", code_lower):
            return self._result('sql_injection', 0.90, self._find_line(code, r'f"'), 'f-string SQL injection')
        
        # 空指针 - None赋值后直接访问（包括函数内）
        if re.search(r'=\s*none\s*\n.*return\s+\w+\.\w+', code, re.MULTILINE):
            return self._result('null_pointer', 0.85, self._find_line(code, r'= none'), 'Potential null pointer')
        
        # 空指针 - None赋值
        if re.search(r'=\s*none\b', code_lower) and re.search(r'\.\w+', code):
            return self._result('null_pointer', 0.80, self._find_line(code, r'= none'), 'Potential null pointer')
        
        # 列表/字典元素访问 - 无检查
        if re.search(r'\[[\w\]]+\]\.\w+', code):
            return self._result('null_pointer', 0.80, self._find_line(code, r'\[[\w\]]+\]\.\w+'), 'List/dict access without check')
        
        # 竞态条件
        if re.search(r'\bglobal\s+\w+', code_lower):
            return self._result('race_condition', 0.85, self._find_line(code, r'\bglobal\s+'), 'Global variable modification')
        
        # 内存泄漏 - 文件未关闭
        if re.search(r'open\([^)]+\)(?!\s*as\s)', code_lower) and 'with' not in code:
            return self._result('memory_leak', 0.85, self._find_line(code, r'open\('), 'File opened without "with"')
        
        # 良好代码 - 空值检查
        if re.search(r'if\s+\w+\s+is\s+not\s+None', code_lower):
            return self._result('no_defect', 0.95, None, 'Proper null check')
        
        if re.search(r'if\s+\w+\s+is\s+None', code_lower):
            return self._result('no_defect', 0.95, None, 'Proper null check')
        
        # 良好代码 - with语句
        if 'with ' in code and ' as ' in code:
            if 'open(' in code_lower or 'connect' in code_lower:
                return self._result('no_defect', 0.95, None, 'Proper resource management')
        
        # 良好代码 - 参数化查询
        if re.search(r'execute\s*\([^)]*%s.*,\s*\([^)]*\)\s*\)', code):
            return self._result('no_defect', 0.95, None, 'Parameterized query - safe')
        
        # 良好代码 - 类型注解
        if re.search(r':\s*(str|int|bool|list|dict)\s*\)', code) or re.search(r'->\s*(str|int|bool|list|dict)\s*:', code):
            if 'select' not in code_lower and 'insert' not in code_lower:
                return self._result('no_defect', 0.90, None, 'Type hints present')
        
        # 良好代码 - 简单函数
        if re.search(r'def\s+\w+\([^)]*\):\s*\n\s*return', code):
            return self._result('no_defect', 0.90, None, 'Simple function - no defects')
        
        # 良好代码 - try-except
        if 'try:' in code_lower and 'except' in code_lower:
            return self._result('no_defect', 0.85, None, 'Proper error handling')
        
        return self._result('no_defect', 0.95, None, 'No obvious defects')
    
    def _result(self, defect_type: str, confidence: float, line_num: Optional[int], suggestion: str) -> Dict[str, Any]:
        severities = {'security': 'high', 'sql_injection': 'high', 'null_pointer': 'high', 
                      'memory_leak': 'medium', 'race_condition': 'medium', 'no_defect': 'none'}
        return {
            'defect_type': defect_type,
            'confidence': confidence,
            'line_number': line_num,
            'suggestion': suggestion,
            'severity': severities.get(defect_type, 'medium')
        }
    
    def _find_line(self, code: str, pattern: str) -> Optional[int]:
        match = re.search(pattern, code, re.IGNORECASE)
        if match:
            return code[:match.start()].count('\n') + 1
        return None


# 测试
analyzer = SimpleAnalyzer()

TEST_CASES = [
    ("def get_user():\n    user = None\n    return user.name", "null_pointer"),
    ("def get_first(items):\n    return items[0].name", "null_pointer"),
    ("def query(name):\n    sql = \"SELECT * FROM users WHERE name = '\" + name + \"'\"\n    return sql", "sql_injection"),
    ("def search(query):\n    return f\"SELECT * FROM products WHERE name = '{query}'\"", "sql_injection"),
    ("def read():\n    f = open('test.txt', 'r')\n    return f.read()", "memory_leak"),
    ("counter = 0\ndef inc():\n    global counter\n    counter += 1\n    return counter", "race_condition"),
    ("def run(code):\n    eval(code)", "security"),
    ("def get_name(user):\n    if user is not None:\n        return user.name\n    return None", "no_defect"),
    ("def read():\n    with open('test.txt', 'r') as f:\n        return f.read()", "no_defect"),
    ("def add(a, b):\n    return a + b", "no_defect"),
]

results = []
for code, expected in TEST_CASES:
    result = analyzer.analyze(code)
    detected = result['defect_type']
    match = detected == expected
    status = "✓" if match else "✗"
    print(f"{status} [{expected}] -> {detected}")
    results.append(match)

print(f"\n匹配率: {sum(results)}/{len(results)} ({sum(results)*100//len(results)}%)")
