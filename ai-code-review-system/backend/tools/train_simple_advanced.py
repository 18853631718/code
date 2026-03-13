#!/usr/bin/env python3
"""
简化的高级模型训练脚本 - 不使用类结构
"""
import os
import sys
import json
import random
import re
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
import joblib

def load_training_data():
    """加载训练数据"""
    # 生成多样化的代码样本
    null_pointer_samples = [
        "def process():\n    user = None\n    return user.name",
        "def fetch_data():\n    result = None\n    return result.data",
        "def get_item(items):\n    return items[0].name",
        "user = None\nprint(user.name)",
        "def process(data):\n    return data['key'].value"
    ]
    
    sql_injection_samples = [
        "def query_db(user_input):\n    sql = \"SELECT * FROM users WHERE name = '\" + user_input + \"'\"\n    return sql",
        "def search(query):\n    return \"SELECT * FROM products WHERE name = '%\" + query + \"%'\"",
        "user_id = request.GET['id']\nsql = \"DELETE FROM users WHERE id = \" + user_id",
        "def get_user(name):\n    query = f\"SELECT * FROM users WHERE name = '{name}'\"\n    return query",
        "cursor.execute(\"INSERT INTO logs VALUES ('\" + message + \"')\")"
    ]
    
    memory_leak_samples = [
        "def read_file():\n    f = open('test.txt', 'r')\n    data = f.read()\n    return data",
        "def get_connection():\n    conn = db.connect()\n    return conn",
        "def process_data():\n    handler = open_handler()\n    data = handler.read()\n    return data",
        "class DataProcessor:\n    def __init__(self):\n        self.cache = {}\n    def add(self, key, value):\n        self.cache[key] = value",
        "def create_thread():\n    thread = threading.Thread(target=worker)\n    thread.start()\n    return 'done'"
    ]
    
    race_condition_samples = [
        "def increment():\n    global counter\n    temp = counter\n    temp = temp + 1\n    counter = temp",
        "balance = 0\ndef withdraw(amount):\n    if balance >= amount:\n        time.sleep(0.1)\n        balance -= amount\n    return balance",
        "shared_data = {}\ndef update(key, value):\n    old = shared_data.get(key, 0)\n    shared_data[key] = old + value",
        "class Counter:\n    count = 0\n    def inc(self):\n        self.count += 1",
        "cache = {}\ndef get_or_set(key, factory):\n    if key not in cache:\n        cache[key] = factory()\n    return cache[key]"
    ]
    
    security_samples = [
        "def execute_command(cmd):\n    os.system(cmd)",
        "eval(user_input)",
        "import pickle\ndata = pickle.loads(user_data)",
        "password = 'admin123'\nif user_input == password:",
        "secret_key = 'my-secret-key-12345'"
    ]
    
    no_defect_samples = [
        "def hello():\n    print('Hello World')\n    return True",
        "def add(a, b):\n    return a + b",
        "def process_data(data):\n    with open('output.txt', 'w') as f:\n        f.write(data)\n    return True",
        "def get_name(user):\n    if user is not None:\n        return user.name\n    return None",
        "def safe_divide(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        return None",
        "def query(name):\n    cursor.execute('SELECT * FROM users WHERE name = %s', (name,))"
    ]
    
    # 为每个样本生成多样化的代码
    defect_samples = {
        'null_pointer': null_pointer_samples,
        'sql_injection': sql_injection_samples,
        'memory_leak': memory_leak_samples,
        'race_condition': race_condition_samples,
        'security': security_samples
    }
    
    # 构建训练数据
    training_data = []
    
    # 生成缺陷样本
    for label, samples in defect_samples.items():
        for i in range(200):  # 每个缺陷类型生成200个样本
            code = random.choice(samples)
            # 添加一些变体
            if random.random() > 0.5:
                code = code.replace('user', 'data')
            if random.random() > 0.5:
                code = code.replace('name', 'value')
            training_data.append({
                'code': code,
                'label': label
            })
    
    # 添加无缺陷样本
    for i in range(1000):  # 生成1000个无缺陷样本
        code = random.choice(no_defect_samples)
        # 添加一些变体
        if random.random() > 0.5:
            code = code.replace('user', 'data')
        if random.random() > 0.5:
            code = code.replace('name', 'value')
        training_data.append({
            'code': code,
            'label': 'no_defect'
        })
    
    print(f"处理后样本数: {len(training_data)}")
    return training_data

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

def train_model():
    """训练模型"""
    print("=" * 60)
    print("训练简化的高级代码缺陷检测模型")
    print("=" * 60)
    
    # 加载数据
    training_data = load_training_data()
    
    if not training_data:
        print("没有找到可用的训练数据！")
        return
    
    # 准备数据
    X = [sample['code'] for sample in training_data]
    y = [sample['label'] for sample in training_data]
    
    # 标签编码
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # 分割数据
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    print(f"训练集: {len(X_train)} 样本")
    print(f"测试集: {len(X_test)} 样本")
    
    # 创建Pipeline - 使用默认分词器，避免依赖外部函数
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=10000,
            stop_words='english',
            token_pattern=r'\b\w+\b|[{}()\[\];.,:+=\-*/]'
        )),
        ('clf', RandomForestClassifier(
            n_estimators=200,
            max_depth=50,
            min_samples_split=5,
            random_state=42,
            class_weight='balanced'
        ))
    ])
    
    # 超参数调优
    param_grid = {
        'tfidf__ngram_range': [(1, 2), (1, 3)],
        'clf__n_estimators': [100, 200],
        'clf__max_depth': [30, 50]
    }
    
    grid_search = GridSearchCV(
        pipeline,
        param_grid,
        cv=5,
        scoring='accuracy',
        n_jobs=-1
    )
    
    grid_search.fit(X_train, y_train)
    
    best_pipeline = grid_search.best_estimator_
    print(f"最佳参数: {grid_search.best_params_}")
    
    # 评估模型
    y_pred = best_pipeline.predict(X_test)
    accuracy = np.mean(y_pred == y_test)
    
    print(f"\n准确率: {accuracy*100:.2f}%")
    print("\n分类报告:")
    print(classification_report(
        y_test, y_pred, 
        target_names=label_encoder.classes_
    ))
    
    # 保存模型
    model_data = {
        'pipeline': best_pipeline,
        'label_encoder': label_encoder,
        'labels': list(label_encoder.classes_)
    }
    joblib.dump(model_data, 'trained_model_simple_advanced.joblib')
    print(f"模型已保存到 trained_model_simple_advanced.joblib")
    
    print(f"\n最终准确率: {accuracy*100:.2f}%")
    
    # 测试一些样本
    print("\n" + "=" * 60)
    print("测试模型")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "空指针引用",
            "code": "def process():\n    user = None\n    return user.name"
        },
        {
            "name": "SQL注入",
            "code": "def get_user(user_id):\n    query = f'SELECT * FROM users WHERE id = {user_id}'\n    return query"
        },
        {
            "name": "内存泄漏",
            "code": "def read_file():\n    f = open('data.txt', 'r')\n    content = f.read()\n    return content"
        },
        {
            "name": "安全代码",
            "code": "def process(user):\n    if user is not None:\n        return user.name\n    return None"
        }
    ]
    
    for test_case in test_cases:
        y_pred = best_pipeline.predict([test_case['code']])
        y_pred_proba = best_pipeline.predict_proba([test_case['code']])[0]
        defect_type = label_encoder.inverse_transform(y_pred)[0]
        confidence = max(y_pred_proba)
        
        print(f"\n测试: {test_case['name']}")
        print(f"代码: {test_case['code']}")
        print(f"结果: {defect_type}")
        print(f"置信度: {confidence:.2f}")

if __name__ == "__main__":
    train_model()
