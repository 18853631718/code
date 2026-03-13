import ast
import re
from typing import Dict, List, Any, Optional
from collections import Counter

class CodeAnalyzer:
    def __init__(self):
        self.language_extensions = {
            'python': '.py',
            'javascript': '.js',
            'java': '.java',
            'c': '.c',
            'cpp': '.cpp',
            'go': '.go',
            'rust': '.rs'
        }
    
    def detect_syntax_error(self, code: str, language: str) -> Optional[Dict[str, Any]]:
        """检测语法错误"""
        if language == 'python':
            try:
                ast.parse(code)
                return None
            except SyntaxError as e:
                return {
                    'type': 'syntax_error',
                    'message': str(e),
                    'line': e.lineno
                }
        return None
    
    def extract_features(self, code: str, language: str) -> Dict[str, Any]:
        if language == 'python':
            return self._extract_python_features(code)
        else:
            return self._extract_generic_features(code)
    
    def _extract_python_features(self, code: str) -> Dict[str, Any]:
        features = {
            'complexity': 0,
            'function_count': 0,
            'class_count': 0,
            'import_count': 0,
            'line_count': len(code.splitlines()),
            'cyclomatic_complexity': 0,
            'halstead_metrics': {},
            'maintainability_index': 0,
            'issues': []
        }
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    features['function_count'] += 1
                    features['cyclomatic_complexity'] += self._calculate_function_complexity(node)
                
                elif isinstance(node, ast.ClassDef):
                    features['class_count'] += 1
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    features['import_count'] += 1
            
            features['complexity'] = features['cyclomatic_complexity']
            
            features['maintainability_index'] = self._calculate_maintainability_index(
                features['line_count'],
                features['cyclomatic_complexity'],
                features['function_count']
            )
            
            features['issues'] = self._detect_issues(tree, code)
            
        except SyntaxError as e:
            features['issues'].append({
                'type': 'syntax_error',
                'message': str(e),
                'line': e.lineno
            })
        
        return features
    
    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _calculate_maintainability_index(self, lines: int, complexity: int, functions: int) -> float:
        if lines == 0:
            return 100.0
        
        mi = 171 - 5.2 * (lines ** 0.5) - 0.23 * complexity - 16.2 * (lines ** 0.5)
        mi = max(0, min(100, mi * 100 / 171))
        
        return round(mi, 2)
    
    def _detect_issues(self, tree: ast.AST, code: str) -> List[Dict[str, Any]]:
        issues = []
        lines = code.splitlines()
        
        # 收集已定义的名称
        defined_names = set()
        imported_names = set()
        
        for node in ast.walk(tree):
            # 收集导入的模块和名称
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_names.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported_names.add(node.module.split('.')[0])
                for alias in node.names:
                    imported_names.add(alias.name)
            
            # 收集函数和类定义
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                defined_names.add(node.name)
                # 收集函数参数
                for arg in node.args.args:
                    defined_names.add(arg.arg)
            
            # 收集赋值语句
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        defined_names.add(target.id)
        
        # 检测Name节点（变量使用）
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                name = node.id
                
                # 检测print语句
                if name == 'print':
                    issues.append({
                        'type': 'python_print',
                        'message': 'Avoid using print for debugging, use logging instead',
                        'line': node.lineno,
                        'severity': 'warning'
                    })
                
                # 检测可能未定义的变量
                # 检查函数调用中的变量是否已定义
                if isinstance(node.parent if hasattr(node, 'parent') else None, ast.Call):
                    pass  # 函数调用的情况稍后处理
                
                # 检测使用但未定义的变量
                if name not in defined_names and name not in imported_names:
                    # 排除常见内置函数和关键字
                    builtin_funcs = {'print', 'len', 'range', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple', 'bool', 'type', 'input', 'open', 'file', 'abs', 'all', 'any', 'chr', 'ord', 'hex', 'oct', 'bin', 'divmod', 'enumerate', 'eval', 'exec', 'filter', 'format', 'getattr', 'hasattr', 'hash', 'id', 'isinstance', 'issubclass', 'iter', 'map', 'max', 'min', 'next', 'pow', 'repr', 'reversed', 'round', 'setattr', 'slice', 'sorted', 'sum', 'super', 'vars', 'zip', '__import__'}
                    if name not in builtin_funcs and not name.startswith('_'):
                        issues.append({
                            'type': 'possibly_undefined',
                            'message': f'Possible reference to undefined name "{name}". Did you import or define it?',
                            'line': node.lineno,
                            'severity': 'warning'
                        })
            
            if isinstance(node, ast.Tuple):
                issues.append({
                    'type': 'literal_parentheses',
                    'message': 'Use tuple() instead of () for empty tuple',
                    'line': node.lineno
                })
            
            if isinstance(node, ast.Compare):
                if any(isinstance(n, ast.NameConstant) and n.value is None for n in node.comparators):
                    issues.append({
                        'type': 'comparison_to_none',
                        'message': 'Use "is None" instead of "== None"',
                        'line': node.lineno
                    })
        
        return issues
    
    def _extract_generic_features(self, code: str) -> Dict[str, Any]:
        features = {
            'line_count': len(code.splitlines()),
            'function_count': len(re.findall(r'\bfunction\s+\w+', code)),
            'class_count': len(re.findall(r'\bclass\s+\w+', code)),
            'import_count': len(re.findall(r'\bimport\s+', code)),
            'comment_count': len(re.findall(r'//.*$|#.*$', code, re.MULTILINE)),
            'issues': []
        }
        
        features['complexity'] = self._estimate_complexity(code)
        
        return features
    
    def _estimate_complexity(self, code: str) -> int:
        complexity = 1
        
        keywords = ['if', 'else', 'elif', 'for', 'while', 'case', 'switch', 'catch', '&&', '\|\|']
        
        for keyword in keywords:
            complexity += len(re.findall(r'\b' + keyword + r'\b', code))
        
        return complexity
    
    def extract_tokens(self, code: str, language: str) -> List[str]:
        if language == 'python':
            try:
                tree = ast.parse(code)
                return [self._get_token_type(node) for node in ast.walk(tree)]
            except:
                return []
        return []
    
    def _get_token_type(self, node: ast.AST) -> str:
        return type(node).__name__
    
    def get_code_metrics(self, code: str, language: str) -> Dict[str, Any]:
        features = self.extract_features(code, language)
        
        code_without_comments = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        code_without_whitespace = re.sub(r'\s+', '', code_without_comments)
        
        features['code_length'] = len(code_without_whitespace)
        features['comment_ratio'] = (len(code) - len(code_without_comments)) / max(len(code), 1)
        
        return features
