"""
Code Defect Detection - Machine Learning Training Module
使用规则引擎生成的样本进行训练
"""

import json
import random
from typing import List, Dict, Tuple
import numpy as np

TRAINING_DATA = [
    {"code": "def get_user():\n    user = None\n    return user.name", "label": "null_pointer"},
    {"code": "def fetch_data():\n    result = None\n    return result.data", "label": "null_pointer"},
    {"code": "def get_item(items):\n    if len(items) > 0:\n        return items[0].name\n    return None\nitem = None\nprint(item.name)", "label": "null_pointer"},
    {"code": "class User:\n    def __init__(self, name):\n        self.name = name\nuser = User(None)\nprint(user.name.upper())", "label": "null_pointer"},
    {"code": "def process(data):\n    return data['key'].value", "label": "null_pointer"},
    {"code": "def query_db(user_input):\n    sql = \"SELECT * FROM users WHERE name = '\" + user_input + \"'\"\n    return sql", "label": "sql_injection"},
    {"code": "def search(query):\n    return \"SELECT * FROM products WHERE name = '%\" + query + \"%'\"", "label": "sql_injection"},
    {"code": "user_id = request.GET['id']\nsql = \"DELETE FROM users WHERE id = \" + user_id", "label": "sql_injection"},
    {"code": "def get_user(name):\n    query = f\"SELECT * FROM users WHERE name = '{name}'\"\n    return query", "label": "sql_injection"},
    {"code": "cursor.execute(\"INSERT INTO logs VALUES ('\" + message + \"')\")", "label": "sql_injection"},
    {"code": "def read_file():\n    f = open('test.txt', 'r')\n    data = f.read()\n    return data", "label": "memory_leak"},
    {"code": "def get_connection():\n    conn = db.connect()\n    return conn", "label": "memory_leak"},
    {"code": "def process_data():\n    handler = open_handler()\n    data = handler.read()\n    return data", "label": "memory_leak"},
    {"code": "class DataProcessor:\n    def __init__(self):\n        self.cache = {}\n    def add(self, key, value):\n        self.cache[key] = value", "label": "memory_leak"},
    {"code": "def create_thread():\n    thread = threading.Thread(target=worker)\n    thread.start()\n    return 'done'", "label": "memory_leak"},
    {"code": "def increment():\n    global counter\n    temp = counter\n    temp = temp + 1\n    counter = temp", "label": "race_condition"},
    {"code": "balance = 0\ndef withdraw(amount):\n    if balance >= amount:\n        time.sleep(0.1)\n        balance -= amount\n    return balance", "label": "race_condition"},
    {"code": "shared_data = {}\ndef update(key, value):\n    old = shared_data.get(key, 0)\n    shared_data[key] = old + value", "label": "race_condition"},
    {"code": "class Counter:\n    count = 0\n    def inc(self):\n        self.count += 1", "label": "race_condition"},
    {"code": "cache = {}\ndef get_or_set(key, factory):\n    if key not in cache:\n        cache[key] = factory()\n    return cache[key]", "label": "race_condition"},
    {"code": "def execute_command(cmd):\n    os.system(cmd)", "label": "security"},
    {"code": "eval(user_input)", "label": "security"},
    {"code": "import pickle\ndata = pickle.loads(user_data)", "label": "security"},
    {"code": "password = 'admin123'\nif user_input == password:", "label": "security"},
    {"code": "secret_key = 'my-secret-key-12345'", "label": "security"},
    {"code": "def hello():\n    print('Hello World')\n    return True", "label": "no_defect"},
    {"code": "def add(a, b):\n    return a + b", "label": "no_defect"},
    {"code": "def is_valid_email(email):\n    import re\n    pattern = r'^[\\w.-]+@[\\w.-]+\\.\\w+$'\n    return re.match(pattern, email) is not None", "label": "no_defect"},
    {"code": "class Calculator:\n    @staticmethod\n    def add(a, b):\n        return a + b\n    @staticmethod\n    def subtract(a, b):\n        return a - b", "label": "no_defect"},
    {"code": "def process_data(data):\n    with open('output.txt', 'w') as f:\n        f.write(data)\n    return True", "label": "no_defect"},
    {"code": "def get_name(user):\n    if user is not None:\n        return user.name\n    return None", "label": "no_defect"},
    {"code": "def safe_divide(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        return None", "label": "no_defect"},
    {"code": "import logging\nlogging.basicConfig(level=logging.INFO)\nlogger = logging.getLogger(__name__)", "label": "no_defect"},
    {"code": "def greet(name: str) -> str:\n    return f'Hello, {name}!'", "label": "no_defect"},
    {"code": "def query(name):\n    cursor.execute('SELECT * FROM users WHERE name = %s', (name,))", "label": "no_defect"},
]


class SimpleMLClassifier:
    """简单的机器学习分类器 - 基于规则特征的朴素贝叶斯分类器"""
    
    def __init__(self):
        self.feature_weights = {}
        self.label_counts = {}
        self.total_samples = 0
        self.labels = ['null_pointer', 'sql_injection', 'memory_leak', 'race_condition', 'security', 'no_defect']
        
    def extract_features(self, code: str) -> Dict[str, int]:
        """提取代码特征"""
        features = {}
        
        code_lower = code.lower()
        code_upper = code.upper()
        
        features['has_null_check'] = 1 if 'is not none' in code_lower or 'is none' in code_lower else 0
        features['has_with_statement'] = 1 if 'with ' in code and 'as ' in code else 0
        features['has_string_concat'] = 1 if ' + ' in code or '+=' in code else 0
        features['has_f_string'] = 1 if 'f"' in code or "f'" in code else 0
        features['has_format'] = 1 if '.format(' in code else 0
        features['has_sql_keywords'] = 1 if any(kw in code_upper for kw in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'FROM', 'WHERE']) else 0
        features['has_eval'] = 1 if 'eval(' in code_lower else 0
        features['has_exec'] = 1 if 'exec(' in code_lower else 0
        features['has_os_system'] = 1 if 'os.system' in code_lower else 0
        features['has_subprocess'] = 1 if 'subprocess' in code_lower else 0
        features['has_open'] = 1 if 'open(' in code_lower else 0
        features['has_return_none'] = 1 if 'return none' in code_lower else 0
        features['has_global'] = 1 if 'global ' in code_lower else 0
        features['has_thread'] = 1 if 'thread' in code_lower or 'async ' in code_lower else 0
        features['has_password'] = 1 if 'password' in code_lower or 'secret' in code_lower or 'api_key' in code_lower else 0
        features['has_attribute_access'] = 1 if '.name' in code or '.data' in code or '.value' in code else 0
        features['has_try_except'] = 1 if 'try:' in code_lower and 'except' in code_lower else 0
        features['has_logging'] = 1 if 'logging' in code_lower or 'logger' in code_lower else 0
        features['has_type_hint'] = 1 if ': str' in code or ': int' in code or '-> ' in code else 0
        features['has_parameterized_query'] = 1 if '%s' in code and '(name,)' in code else 0
        features['has_dict_access'] = 1 if '[' in code and '].' in code else 0
        features['has_method_call'] = 1 if '.get(' in code or '.read(' in code or '.connect(' in code else 0
        features['has_sql_concat_in_query'] = 1 if ('select' in code_upper or 'insert' in code_upper or 'update' in code_upper) and ('+' in code or 'f"' in code) else 0
        
        return features
    
    def train(self, training_data: List[Dict], epochs: int = 10):
        """训练模型"""
        print("Training ML Classifier...")
        
        self.label_counts = {label: 0 for label in self.labels}
        self.total_samples = len(training_data)
        
        for sample in training_data:
            label = sample.get('label', 'no_defect')
            if label in self.label_counts:
                self.label_counts[label] += 1
        
        for label in self.labels:
            self.feature_weights[label] = {}
        
        for sample in training_data:
            code = sample.get('code', '')
            label = sample.get('label', 'no_defect')
            
            if label not in self.feature_weights:
                continue
                
            features = self.extract_features(code)
            
            for feature, value in features.items():
                if feature not in self.feature_weights[label]:
                    self.feature_weights[label][feature] = 0
                self.feature_weights[label][feature] += value
        
        for label in self.labels:
            if self.label_counts[label] > 0:
                for feature in self.feature_weights[label]:
                    self.feature_weights[label][feature] /= self.label_counts[label]
        
        print(f"Training completed! Total samples: {self.total_samples}")
        print(f"Label distribution: {self.label_counts}")
    
    def predict(self, code: str) -> Dict:
        """预测代码缺陷"""
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
            return {
                'defect_type': 'no_defect',
                'confidence': 0.95,
                'all_scores': scores
            }
        
        best_label = max(scores, key=scores.get)
        confidence = scores[best_label] / max(sum(scores.values()), 0.001)
        
        return {
            'defect_type': best_label,
            'confidence': min(confidence, 0.95),
            'all_scores': scores
        }
    
    def evaluate(self, test_data: List[Dict]) -> Dict:
        """评估模型"""
        correct = 0
        total = len(test_data)
        
        confusion_matrix = {label: {l: 0 for l in self.labels} for label in self.labels}
        
        for sample in test_data:
            code = sample.get('code', '')
            expected = sample.get('label', 'no_defect')
            
            prediction = self.predict(code)
            predicted = prediction['defect_type']
            
            if expected == predicted:
                correct += 1
            
            confusion_matrix[expected][predicted] += 1
        
        accuracy = correct / total if total > 0 else 0
        
        return {
            'accuracy': accuracy,
            'correct': correct,
            'total': total,
            'confusion_matrix': confusion_matrix
        }


def train_and_evaluate():
    """训练并评估模型"""
    random.shuffle(TRAINING_DATA)
    
    split_idx = int(len(TRAINING_DATA) * 0.7)
    train_data = TRAINING_DATA[:split_idx]
    test_data = TRAINING_DATA[split_idx:]
    
    print(f"Training samples: {len(train_data)}")
    print(f"Test samples: {len(test_data)}")
    
    classifier = SimpleMLClassifier()
    classifier.train(train_data)
    
    results = classifier.evaluate(test_data)
    
    print("\n" + "="*50)
    print("Model Evaluation Results")
    print("="*50)
    print(f"Accuracy: {results['accuracy']*100:.2f}%")
    print(f"Correct: {results['correct']}/{results['total']}")
    
    print("\nConfusion Matrix:")
    print("-"*50)
    header = f"{'Expected':<15}" + "".join([f"{l:<12}" for l in classifier.labels])
    print(header)
    
    for expected in classifier.labels:
        row = f"{expected:<15}"
        for predicted in classifier.labels:
            count = results['confusion_matrix'][expected][predicted]
            row += f"{count:<12}"
        print(row)
    
    print("\nSample Predictions:")
    print("-"*50)
    for i, sample in enumerate(test_data[:5]):
        code = sample['code'][:50].replace('\n', ' ')
        expected = sample['label']
        result = classifier.predict(sample['code'])
        predicted = result['defect_type']
        match = "✓" if expected == predicted else "✗"
        print(f"{match} Code: {code}...")
        print(f"  Expected: {expected}, Predicted: {predicted}")
    
    return classifier, results


def save_model(classifier, filepath: str):
    """保存模型"""
    model_data = {
        'feature_weights': classifier.feature_weights,
        'label_counts': classifier.label_counts,
        'total_samples': classifier.total_samples,
        'labels': classifier.labels
    }
    with open(filepath, 'w') as f:
        json.dump(model_data, f, indent=2)
    print(f"Model saved to {filepath}")


def load_model(filepath: str):
    """加载模型"""
    with open(filepath, 'r') as f:
        model_data = json.load(f)
    
    classifier = SimpleMLClassifier()
    classifier.feature_weights = model_data['feature_weights']
    classifier.label_counts = model_data['label_counts']
    classifier.total_samples = model_data['total_samples']
    classifier.labels = model_data['labels']
    
    return classifier


if __name__ == "__main__":
    classifier, results = train_and_evaluate()
    save_model(classifier, 'model.json')
