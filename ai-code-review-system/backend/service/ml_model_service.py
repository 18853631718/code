import json
import os
import numpy as np
from typing import Dict, List, Any, Optional
import re
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

def tokenize_code(code):
    """代码分词"""
    # 移除注释
    code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
    # 分词
    tokens = re.findall(r'\b\w+\b|[{}()\[\];.,:+=\-*/]', code)
    # 提取特征词
    features = []
    for token in tokens:
        if token.isalpha() and len(token) > 1:
            features.append(token.lower())
        elif token in ['=', '==', '!=', 'is', 'not', 'in', 'for', 'if', 'else', 'while', 'def', 'class']:
            features.append(token)
    return features

class DefectDetectionModel:
    def __init__(self):
        self.defect_types = [
            'null_pointer',
            'buffer_overflow',
            'memory_leak',
            'race_condition',
            'sql_injection',
            'no_defect'
        ]
    
    def predict_defect(self, code: str) -> Dict[str, Any]:
        return {
            'defect_type': 'no_defect',
            'confidence': 0.95,
            'all_probabilities': {dt: 0.0 for dt in self.defect_types}
        }


class MLClassifier:
    """基于特征的朴素贝叶斯分类器"""
    
    def __init__(self):
        self.feature_weights = {}
        self.label_counts = {}
        self.total_samples = 0
        self.labels = ['null_pointer', 'sql_injection', 'memory_leak', 'race_condition', 'security', 'no_defect']
        self.is_trained = False
        self.advanced_model = None
    
    def load_model(self, filepath: str = 'trained_model_enhanced.json'):
        """加载训练好的模型"""
        # 优先尝试加载简化的高级模型
        try:
            import joblib
            advanced_model_path = 'trained_model_simple_advanced.joblib'
            if os.path.exists(advanced_model_path):
                # 直接加载模型数据
                self.advanced_model = advanced_model_path
                self.is_trained = True
                print(f"高级ML模型已加载: {advanced_model_path}")
                return True
        except Exception as e:
            print(f"高级模型加载失败: {e}")
        
        # 尝试多个可能的模型文件
        possible_files = [
            filepath,
            'trained_model_enhanced.json',
            'trained_model.json',
            'trained_model_codexglue.json',
            os.path.join(os.path.dirname(__file__), filepath)
        ]
        
        for filepath in possible_files:
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        model_data = json.load(f)
                    self.feature_weights = model_data.get('feature_weights', {})
                    self.label_counts = model_data.get('label_counts', {})
                    self.total_samples = model_data.get('total_samples', 0)
                    self.labels = model_data.get('labels', self.labels)
                    self.is_trained = True
                    print(f"ML模型已加载: {filepath}")
                    return True
                except Exception as e:
                    print(f"模型加载失败: {e}")
                    continue
        return False
    
    def extract_features(self, code: str) -> Dict[str, int]:
        """提取代码特征"""
        features = {}
        
        code_lower = code.lower()
        code_upper = code.upper()
        
        # 空指针相关特征
        features['has_null_check'] = 1 if any(p in code_lower for p in ['is not none', 'is none', 'if ', 'else:', 'try:', 'except:', '!= null', '== null', 'null !=', 'null ==']) else 0
        features['has_none_assignment'] = 1 if 'none' in code_lower or 'null' in code_lower else 0
        features['has_attribute_access'] = 1 if re.search(r'\w+\.\w+', code) else 0
        features['has_method_call'] = 1 if re.search(r'\w+\(.*?\)', code) else 0
        features['has_null_assignment_then_access'] = 1 if re.search(r'=\s*null\s*\n.*\.\w+', code_lower) else 0
        features['has_direct_null_access'] = 1 if re.search(r'null\.\w+', code_lower) else 0
        
        # SQL注入相关特征
        features['has_sql_keywords'] = 1 if any(kw in code_upper for kw in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'FROM', 'WHERE', 'TABLE', 'JDBC', 'STATEMENT', 'PREPAREDSTATEMENT']) else 0
        features['has_string_concat'] = 1 if ' + ' in code or '+=' in code else 0
        features['has_f_string'] = 1 if 'f"' in code or "f'" in code else 0
        features['has_format'] = 1 if '.format(' in code else 0
        features['has_percent_format'] = 1 if ' % ' in code or '%s' in code or '%d' in code else 0
        features['has_parameterized'] = 1 if re.search(r'%\s*[,\)]', code) or re.search(r',\s*\([^)]+\)\s*\)', code) or 'preparedstatement' in code_lower else 0
        
        # 内存泄漏特征
        features['has_open'] = 1 if 'open(' in code_lower else 0
        features['has_with'] = 1 if 'with ' in code and ' as ' in code else 0
        features['has_connect'] = 1 if '.connect(' in code_lower or 'sqlite3.connect' in code_lower or 'drivermanager.getconnection' in code_lower else 0
        features['has_thread'] = 1 if 'thread' in code_lower or 'async ' in code or 'runnable' in code_lower else 0
        features['has_resource_leak'] = 1 if ('fileinputstream' in code_lower or 'fileoutputstream' in code_lower) and 'close()' not in code_lower else 0
        features['has_infinite_loop'] = 1 if re.search(r'while\s*\(\s*true\s*\)', code_lower) else 0
        features['has_memory_allocation'] = 1 if re.search(r'new\s+\w+\(\s*\d+\s*\)', code_lower) else 0
        features['has_list_append'] = 1 if 'list.add(' in code_lower or 'arraylist.add(' in code_lower else 0
        
        # 竞态条件特征
        features['has_global'] = 1 if 'global ' in code_lower or 'static' in code_lower else 0
        features['has_lock'] = 1 if 'lock' in code_lower or 'mutex' in code_lower or 'synchronized' in code_lower else 0
        features['has_thread_start'] = 1 if 'thread.start()' in code_lower or 'start()' in code_lower else 0
        features['has_multiple_threads'] = 1 if code_lower.count('thread') > 1 else 0
        features['has_static_variable'] = 1 if re.search(r'static\s+\w+\s*=', code_lower) else 0
        features['has_counter_increment'] = 1 if 'counter++' in code_lower or 'counter += 1' in code_lower else 0
        
        # 安全特征
        features['has_eval'] = 1 if 'eval(' in code_lower else 0
        features['has_exec'] = 1 if 'exec(' in code_lower else 0
        features['has_os_system'] = 1 if 'os.system' in code_lower or 'subprocess' in code_lower else 0
        features['has_password'] = 1 if any(p in code_lower for p in ['password', 'secret', 'api_key', 'token', 'key =', 'password =', 'secret =']) else 0
        features['has_pickle'] = 1 if 'pickle' in code_lower else 0
        
        # 数组越界特征
        features['has_array_access'] = 1 if re.search(r'\[\d+\]', code) else 0
        features['has_array_length'] = 1 if 'length' in code_lower and '[' in code else 0
        
        # 逻辑错误特征
        features['has_assignment_in_condition'] = 1 if re.search(r'if\s*\([^)]*=\s*[^)]*\)', code) else 0
        features['has_equality_comparison'] = 1 if re.search(r'==', code) else 0
        features['has_assignment'] = 1 if re.search(r'=', code) else 0
        features['has_if_statement'] = 1 if 'if (' in code else 0
        
        # 良好代码特征
        features['has_type_hint'] = 1 if re.search(r':\s*(str|int|bool|list|dict)\b', code) or '->' in code or any(t in code for t in ['int ', 'String ', 'boolean ', 'void ', 'double ']) else 0
        features['has_logging'] = 1 if 'logging' in code_lower or 'logger' in code_lower else 0
        features['has_try_except'] = 1 if 'try:' in code_lower and 'except' in code_lower or 'try {' in code_lower and 'catch (' in code_lower else 0
        features['has_resource_management'] = 1 if 'try ((' in code_lower or 'try-with-resources' in code_lower else 0
        
        return features
    
    def predict(self, code: str) -> Dict:
        """使用ML模型预测"""
        if not self.is_trained:
            return None
        
        # 如果有高级模型，使用它
        if self.advanced_model:
            try:
                import joblib
                # 加载完整的高级模型数据
                model_data = joblib.load(self.advanced_model)
                pipeline = model_data['pipeline']
                label_encoder = model_data['label_encoder']
                
                # 预测
                y_pred = pipeline.predict([code])
                y_pred_proba = pipeline.predict_proba([code])[0]
                
                # 获取预测结果
                defect_type = label_encoder.inverse_transform(y_pred)[0]
                confidence = max(y_pred_proba)
                
                # 构建所有分数
                all_scores = {}
                for label, score in zip(label_encoder.classes_, y_pred_proba):
                    all_scores[label] = score
                
                return {
                    'defect_type': defect_type,
                    'confidence': min(confidence, 0.99),
                    'all_scores': all_scores
                }
            except Exception as e:
                print(f"高级模型预测失败: {e}")
        
        # 回退到传统模型
        features = self.extract_features(code)
        
        scores = {}
        for label in self.labels:
            score = 0
            for feature, value in features.items():
                weight = self.feature_weights.get(label, {}).get(feature, 0)
                score += value * weight
            
            prior = self.label_counts.get(label, 1) / max(self.total_samples, 1)
            scores[label] = score * prior
        
        if max(scores.values()) == 0:
            return None
        
        best_label = max(scores, key=scores.get)
        confidence = scores[best_label] / max(sum(scores.values()), 0.001)
        
        return {
            'defect_type': best_label,
            'confidence': min(confidence, 0.95),
            'all_scores': scores
        }


class CodeBERTAnalyzer:
    def __init__(self):
        self.is_loaded = False
        self.ml_classifier = MLClassifier()
        
        # 尝试加载训练好的ML模型
        model_loaded = self.ml_classifier.load_model('trained_model_codexglue.json')
        if not model_loaded:
            model_loaded = self.ml_classifier.load_model('trained_model_enhanced.json')
        if model_loaded:
            self.is_loaded = True
    
    def analyze(self, code: str) -> Dict[str, Any]:
        # 首先尝试使用ML模型（优先使用机器学习）
        if self.is_loaded:
            ml_result = self.ml_classifier.predict(code)
            # 提高ML模型置信度阈值到0.5，确保机器学习优先
            if ml_result and ml_result['confidence'] > 0.5:
                return {
                    'defect_type': ml_result['defect_type'],
                    'confidence': ml_result['confidence'],
                    'line_number': self._find_defect_line(code, ml_result['defect_type']),
                    'suggestion': self._get_suggestion(ml_result['defect_type']),
                    'severity': self._get_severity(ml_result['defect_type']),
                    'method': 'ml'
                }
        
        # 然后使用快速规则引擎作为辅助
        rule_result = self._quick_rule_check(code)
        if rule_result:
            return rule_result
        
        # 最后使用完整规则引擎作为兜底
        return self._rule_based_analysis(code)
    
    def _quick_rule_check(self, code: str) -> Optional[Dict[str, Any]]:
        """快速规则检查"""
        code_lower = code.lower()
        
        # 明显的安全问题
        if re.search(r'\beval\s*\(', code_lower):
            return self._make_result('security', 0.95, self._find_line(code, r'\beval\s*\('), 'Use of eval() is dangerous')
        
        if re.search(r'\bos\.system\s*\(', code_lower):
            return self._make_result('security', 0.95, self._find_line(code, r'\bos\.system\s*\('), 'Use of os.system() is dangerous')
        
        # 硬编码密码
        if re.search(r'(password|secret[_-]?key|api[_-]?key)\s*=\s*["\']', code_lower):
            return self._make_result('security', 0.90, self._find_line(code, r'(password|secret|api[_-]?key)\s*='), 'Hardcoded credentials detected')
        
        # 明显的SQL注入 (包括f-string)
        if re.search(r'(select|insert|update|delete).*\+', code_lower):
            return self._make_result('sql_injection', 0.90, self._find_line(code, r'.*\+'), 'SQL string concatenation detected')
        
        # f-string SQL注入 - 检测f-string中包含SQL关键字
        if re.search(r'f".*?(select|insert|update|delete)', code_lower) or re.search(r"f'.*?(select|insert|update|delete)", code_lower):
            return self._make_result('sql_injection', 0.90, self._find_line(code, r'f"'), 'f-string SQL injection detected')
        
        # Java SQL注入
        if re.search(r'Statement.*executeQuery\s*\([^)]*\+', code_lower):
            return self._make_result('sql_injection', 0.90, self._find_line(code, r'Statement'), 'Java SQL string concatenation detected')
        
        # 明显的空指针 - None赋值后直接访问
        if re.search(r'= none\s*\n.*return\s+\w+\.', code):
            return self._make_result('null_pointer', 0.85, self._find_line(code, r'= none'), 'Potential null pointer')
        
        # Java空指针
        if re.search(r'=\s*null\s*\n.*\.\w+\s*\(', code):
            return self._make_result('null_pointer', 0.85, self._find_line(code, r'=\s*null'), 'Java potential null pointer')
        
        # 明显的列表/字典元素访问
        if re.search(r'\[[\w\]]+\]\.\w+', code):
            return self._make_result('null_pointer', 0.80, self._find_line(code, r'\[[\w\]]+\]\.\w+'), 'List/dict access without check')
        
        # Java数组越界
        if re.search(r'\[\d+\]', code) and not re.search(r'length', code_lower):
            return self._make_result('null_pointer', 0.80, self._find_line(code, r'\[\d+\]'), 'Potential array index out of bounds')
        
        # 直接访问null对象
        if re.search(r'null\.\w+', code_lower):
            return self._make_result('null_pointer', 0.90, self._find_line(code, r'null\.\w+'), 'Direct null object access')
        
        # 空指针异常 - 变量赋值为null后直接访问
        if re.search(r'(\w+)\s*=\s*null\s*;.*\n.*\1\.\w+\s*\(', code, re.DOTALL):
            return self._make_result('null_pointer', 0.90, self._find_line(code, r'\w+\s*=\s*null'), 'Null pointer exception: variable assigned null then accessed')
        
        # 明显的竞态条件
        if re.search(r'\bglobal\s+\w+', code_lower):
            return self._make_result('race_condition', 0.85, self._find_line(code, r'\bglobal\s+'), 'Global variable modification')
        
        # Java竞态条件
        if re.search(r'static\s+\w+\s*=', code_lower) and re.search(r'thread', code_lower):
            return self._make_result('race_condition', 0.85, self._find_line(code, r'static\s+'), 'Java static variable in multi-threaded environment')
        
        # 多线程竞态条件
        if code_lower.count('thread') > 1 and re.search(r'(static\s+\w+|counter\+\+|counter\s*\+=\s*1)', code_lower):
            return self._make_result('race_condition', 0.85, self._find_line(code, r'thread'), 'Multi-threaded race condition')
        
        # 明显的文件泄漏
        if re.search(r'open\([^)]+\)(?!\s*as\s)', code_lower) and 'with' not in code:
            return self._make_result('memory_leak', 0.85, self._find_line(code, r'open\('), 'File opened without "with" statement')
        
        # Java资源泄漏
        if re.search(r'(FileInputStream|FileOutputStream|Connection)\s+\w+\s*=', code_lower) and 'close()' not in code_lower:
            return self._make_result('memory_leak', 0.85, self._find_line(code, r'(FileInputStream|FileOutputStream|Connection)'), 'Java resource not closed')
        
        # 无限循环内存泄漏
        if re.search(r'while\s*\(\s*true\s*\)', code_lower) and re.search(r'(new\s+\w+|list\.add|arraylist\.add)', code_lower):
            return self._make_result('memory_leak', 0.85, self._find_line(code, r'while\s*\(\s*true\s*\)'), 'Infinite loop with memory allocation')
        
        # 静态列表内存泄漏
        if re.search(r'static\s+List\s*<', code_lower) and re.search(r'while\s*\(\s*true\s*\)', code_lower) and re.search(r'list\.add\(new\s+', code_lower):
            return self._make_result('memory_leak', 0.90, self._find_line(code, r'while\s*\(\s*true\s*\)'), 'Memory leak: infinite loop adding objects to static list')
        
        # 良好的空值检查
        if re.search(r'if\s+\w+\s+is\s+not\s+None', code_lower):
            return self._make_result('no_defect', 0.95, None, 'Proper null check')
        
        if re.search(r'if\s+\w+\s+is\s+None', code_lower):
            return self._make_result('no_defect', 0.95, None, 'Proper null check')
        
        # Java空值检查
        if re.search(r'if\s+\w+\s*!=\s*null', code_lower) or re.search(r'if\s+null\s*!=\s*\w+', code_lower):
            return self._make_result('no_defect', 0.95, None, 'Proper Java null check')
        
        # 明显的良好代码 - with语句
        if 'with ' in code and ' as ' in code:
            if 'open(' in code_lower or 'connect' in code_lower:
                return self._make_result('no_defect', 0.95, None, 'Proper resource management with "with" statement')
        
        # Java try-with-resources
        if re.search(r'try\s*\([^)]*\)', code_lower) and re.search(r'FileInputStream|FileOutputStream|Connection', code_lower):
            return self._make_result('no_defect', 0.95, None, 'Proper Java resource management with try-with-resources')
        
        # 明显的参数化查询
        if re.search(r'execute\s*\([^)]*%s.*,\s*\([^)]*\)\s*\)', code):
            return self._make_result('no_defect', 0.95, None, 'Parameterized query - safe')
        
        # Java参数化查询
        if re.search(r'PreparedStatement', code_lower) and re.search(r'set\w+\s*\(', code_lower):
            return self._make_result('no_defect', 0.95, None, 'Java parameterized query - safe')
        
        # 类型注解 - 良好代码
        if re.search(r':\s*(str|int|bool|list|dict)\s*\)', code) or re.search(r'->\s*(str|int|bool|list|dict)\s*:', code):
            if 'select' not in code_lower and 'insert' not in code_lower:
                return self._make_result('no_defect', 0.90, None, 'Type hints present - good practice')
        
        # Java类型声明
        if re.search(r'(int|String|boolean|void|double)\s+\w+', code):
            if 'select' not in code_lower and 'insert' not in code_lower:
                return self._make_result('no_defect', 0.90, None, 'Java type declarations present - good practice')
        
        # 简单函数 - 无缺陷
        if re.search(r'def\s+\w+\([^)]*\):\s*\n\s*return', code) and 'None' not in code:
            return self._make_result('no_defect', 0.90, None, 'Simple function - no defects')
        
        # Java简单方法
        if re.search(r'(public|private|protected)\s+(int|String|boolean|void|double)\s+\w+\([^)]*\)\s*\{', code) and 'null' not in code_lower:
            return self._make_result('no_defect', 0.90, None, 'Simple Java method - no defects')
        
        # 逻辑错误 - 条件中的赋值
        if re.search(r'if\s*\([^)]*=\s*[^)]*\)', code) and not re.search(r'if\s*\([^)]*==\s*[^)]*\)', code):
            return self._make_result('null_pointer', 0.85, self._find_line(code, r'if\s*\('), 'Potential logical error: assignment in condition')
        
        # Java逻辑错误 - 条件中的赋值
        if re.search(r'if\s*\(\s*\w+\s*=\s*[^)]*\)', code):
            return self._make_result('null_pointer', 0.85, self._find_line(code, r'if\s*\('), 'Java logical error: assignment in condition')
        
        return None
    
    def _make_result(self, defect_type: str, confidence: float, line_num: Optional[int], suggestion: str) -> Dict[str, Any]:
        return {
            'defect_type': defect_type,
            'confidence': confidence,
            'line_number': line_num,
            'suggestion': self._get_suggestion(defect_type, suggestion),
            'severity': self._get_severity(defect_type),
            'method': 'quick_rule'
        }
    
    def _find_line(self, code: str, pattern: str) -> Optional[int]:
        match = re.search(pattern, code, re.IGNORECASE)
        if match:
            return code[:match.start()].count('\n') + 1
        return None
    
    def _find_defect_line(self, code: str, defect_type: str) -> Optional[int]:
        patterns = {
            'null_pointer': [r'\w+\s*\.\w+', r'\[.*?\]\.'],
            'sql_injection': [r'\+.*"\'', r'f"', r'\.format\('],
            'memory_leak': [r'open\(', r'\.connect\('],
            'race_condition': [r'global\s+\w+', r'thread'],
            'security': [r'eval\(', r'os\.system', r'password\s*='],
        }
        
        if defect_type in patterns:
            lines = code.splitlines()
            for i, line in enumerate(lines, 1):
                for pattern in patterns[defect_type]:
                    if re.search(pattern, line, re.IGNORECASE):
                        return i
        
        return None
    
    def _rule_based_analysis(self, code: str) -> Dict[str, Any]:
        lines = code.splitlines()
        
        if self._is_good_code(code):
            return {
                'defect_type': 'no_defect',
                'confidence': 0.95,
                'line_number': None,
                'suggestion': 'Code follows best practices.',
                'severity': 'none',
                'method': 'rule'
            }
        
        return self._detect_defects(code, lines)
    
    def _is_good_code(self, code: str) -> bool:
        # 检查是否有良好的编程实践
        good_patterns = [
            r'if\s+\w+\s+is\s+not\s+None',
            r'if\s+\w+\s+is\s+None',
            r'if\s+not\s+\w+:',
            r'try:.*?except',
            r'with\s+.*\s+as\s+',
            r'execute\s*\([^)]*%s.*,\s*\(',
        ]
        
        for pattern in good_patterns:
            if re.search(pattern, code, re.IGNORECASE | re.DOTALL):
                return True
        
        return False
    
    def _detect_defects(self, code: str, lines: List[str]) -> Dict[str, Any]:
        defect_priority = [
            ('security', [
                (r'eval\s*\(', 'Avoid using eval() - security risk'),
                (r'exec\s*\(', 'Avoid using exec() - security risk'),
                (r'os\.system\s*\(', 'Avoid using os.system() - security risk'),
                (r'subprocess\.call\s*\([^)]*shell\s*=\s*True', 'Avoid shell=True in subprocess'),
                (r'password\s*=\s*["\'][^"\']{3,}["\']', 'Hardcoded password detected'),
                (r'secret[_-]?key\s*=\s*["\'][^"\']+["\']', 'Hardcoded secret key detected'),
                (r'Password\s*=\s*["\'][^"\']{3,}["\']', 'Java hardcoded password detected'),
            ]),
            ('sql_injection', [
                (r'".*SELECT.*\+', 'SQL string concatenation detected'),
                (r'".*INSERT.*\+', 'SQL string concatenation detected'),
                (r'".*UPDATE.*\+', 'SQL string concatenation detected'),
                (r"'.*SELECT.*\+", 'SQL string concatenation detected'),
                (r'f".*SELECT', 'f-string in SQL query'),
                (r"f'.*SELECT", 'f-string in SQL query'),
                (r'Statement.*executeQuery\s*\([^)]*\+', 'Java SQL string concatenation detected'),
            ]),
            ('memory_leak', [
                (r'open\s*\([^)]+\)\s*(?!.*with)', 'File opened without "with" statement'),
                (r'\.connect\s*\(\s*\)', 'Database connection opened without "with"'),
                (r'sqlite3\.connect\s*\(', 'Database connection opened without "with"'),
                (r'threading\.Thread\s*\(', 'Thread started without join()'),
                (r'(FileInputStream|FileOutputStream)\s+\w+\s*=', 'Java file stream not closed'),
                (r'Connection\s+\w+\s*=', 'Java database connection not closed'),
                (r'DriverManager\.getConnection\s*\(', 'Java database connection not closed'),
            ]),
            ('race_condition', [
                (r'^global\s+\w+\s*$', 'Global variable modification'),
                (r'shared[_-]?data\s*=', 'Shared data modification'),
                (r'^async\s+def', 'Async function - potential race condition'),
                (r'static\s+\w+\s*=', 'Java static variable modification'),
                (r'Thread\s+\w+\s*=\s*new\s+Thread', 'Java thread without synchronization'),
            ]),
            ('null_pointer', [
                (r'\w+\s*=\s*None\s*\n.*return\s+\w+\.\w+', 'Potential null pointer after assignment'),
                (r'return\s+\w+\.\w+(?!\s*\()', 'Direct attribute access without null check'),
                (r'\w+\s*=\s*null\s*\n.*\.\w+\s*\(', 'Java potential null pointer'),
                (r'\[\d+\]', 'Java potential array index out of bounds'),
                (r'\w+\.length\s*\+', 'Java array length manipulation'),
            ]),
        ]
        
        for defect_type, patterns in defect_priority:
            for pattern, suggestion in patterns:
                match = re.search(pattern, code, re.IGNORECASE | re.MULTILINE)
                if match:
                    line_num = code[:match.start()].count('\n') + 1
                    
                    return {
                        'defect_type': defect_type,
                        'confidence': 0.85,
                        'line_number': line_num,
                        'suggestion': self._get_suggestion(defect_type, suggestion),
                        'severity': self._get_severity(defect_type),
                        'method': 'rule'
                    }
        
        # 检查Java逻辑错误
        if re.search(r'if\s*\([^)]*=\s*[^)]*\)', code):
            line_num = code.find('if') // code[:code.find('if')].count('\n') + 1
            return {
                'defect_type': 'null_pointer',
                'confidence': 0.85,
                'line_number': line_num,
                'suggestion': 'Potential logical error: assignment in condition',
                'severity': 'medium',
                'method': 'rule'
            }
        
        return {
            'defect_type': 'no_defect',
            'confidence': 0.95,
            'line_number': None,
            'suggestion': 'No obvious defects detected.',
            'severity': 'none',
            'method': 'rule'
        }
    
    def _get_suggestion(self, defect_type: str, specific: str = '') -> str:
        suggestions = {
            'null_pointer': 'Add null check before dereferencing. Use "if variable is not None:"',
            'sql_injection': 'Use parameterized queries: cursor.execute("SELECT * WHERE id = %s", (id,))',
            'memory_leak': 'Use "with" statement for resource management',
            'race_condition': 'Use proper locking mechanisms',
            'security': specific or 'Follow security best practices',
            'buffer_overflow': 'Use bounds checking'
        }
        return suggestions.get(defect_type, 'Review code for potential issues')
    
    def _get_severity(self, defect_type: str) -> str:
        severities = {
            'null_pointer': 'high',
            'buffer_overflow': 'high',
            'memory_leak': 'medium',
            'sql_injection': 'high',
            'security': 'high',
            'race_condition': 'medium'
        }
        return severities.get(defect_type, 'medium')


class MLModelService:
    def __init__(self):
        self.defect_model = DefectDetectionModel()
        self.codebert = CodeBERTAnalyzer()
        self.language_models = {}
        self._load_language_models()
    
    def _load_language_models(self):
        """加载不同语言的模型"""
        # 导入tokenize_code函数，确保模型加载时能够找到它
        from service.code_tokenizer import tokenize_code
        
        # 尝试加载Java模型
        try:
            import joblib
            java_model_path = 'trained_model_java.joblib'
            if os.path.exists(java_model_path):
                model_data = joblib.load(java_model_path)
                self.language_models['java'] = model_data
                print(f"Java ML模型已加载: {java_model_path}")
        except Exception as e:
            print(f"Java模型加载失败: {e}")
        
        # 尝试加载Python模型
        try:
            import joblib
            python_model_path = 'trained_model_simple_advanced.joblib'
            if os.path.exists(python_model_path):
                model_data = joblib.load(python_model_path)
                self.language_models['python'] = model_data
                print(f"Python ML模型已加载: {python_model_path}")
        except Exception as e:
            print(f"Python模型加载失败: {e}")
    
    def predict(self, code: str, language: str) -> Dict[str, Any]:
        # 首先尝试使用语言特定的ML模型
        if language in self.language_models:
            try:
                model_data = self.language_models[language]
                pipeline = model_data['pipeline']
                label_encoder = model_data['label_encoder']
                
                # 预测
                y_pred = pipeline.predict([code])
                y_pred_proba = pipeline.predict_proba([code])[0]
                
                # 获取预测结果
                defect_type = label_encoder.inverse_transform(y_pred)[0]
                confidence = max(y_pred_proba)
                
                # 构建结果
                result = {
                    'defect_type': defect_type,
                    'confidence': min(confidence, 0.99),
                    'line_number': self.codebert._find_defect_line(code, defect_type),
                    'suggestion': self.codebert._get_suggestion(defect_type),
                    'severity': self.codebert._get_severity(defect_type),
                    'method': 'ml'
                }
                
                if result['defect_type'] != 'no_defect':
                    result['suggestion'] = self.codebert._get_suggestion(result['defect_type'])
                    result['severity'] = self.codebert._get_severity(result['defect_type'])
                
                return result
            except Exception as e:
                print(f"ML模型预测失败: {e}")
        
        # 回退到规则引擎
        result = self.codebert.analyze(code)
        
        if result['defect_type'] != 'no_defect':
            result['suggestion'] = self.codebert._get_suggestion(result['defect_type'])
            result['severity'] = self.codebert._get_severity(result['defect_type'])
        
        return result
    
    def batch_predict(self, codes: List[str], language: str) -> List[Dict[str, Any]]:
        return [self.predict(code, language) for code in codes]
    
    def train(self, train_data: List[Dict[str, Any]], epochs: int = 10):
        print("Training not available in this version")
    
    def save_model(self, path: str):
        print("Model saving not available in this version")
    
    def load_model(self, path: str):
        print("Model loading not available in this version")
