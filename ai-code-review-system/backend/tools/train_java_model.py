"""
Java Code Defect Detection - Machine Learning Training Module
使用Java代码样本训练模型
"""

import os
import sys
# 添加父目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import random
from typing import List, Dict, Tuple
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

TRAINING_DATA = [
    # Java空指针异常
    {"code": "public class NullPointerExceptionTest {\n    public static void main(String[] args) {\n        String str = null;\n        System.out.println(str.length());\n    }\n}", "label": "null_pointer"},
    {"code": "public class NullAccessTest {\n    public static void main(String[] args) {\n        Object obj = null;\n        obj.toString();\n    }\n}", "label": "null_pointer"},
    {"code": "public class NullArrayTest {\n    public static void main(String[] args) {\n        int[] arr = null;\n        System.out.println(arr.length);\n    }\n}", "label": "null_pointer"},
    
    # Java SQL注入
    {"code": "import java.sql.Connection;\nimport java.sql.Statement;\npublic class SQLInjectionTest {\n    public static void main(String[] args) throws Exception {\n        String userInput = 'admin\' OR \'1\'=\'1';\n        Connection conn = DriverManager.getConnection('jdbc:mysql://localhost:3306/test', 'root', 'password');\n        Statement stmt = conn.createStatement();\n        String sql = 'SELECT * FROM users WHERE username = \'' + userInput + '\'';\n        stmt.executeQuery(sql);\n    }\n}", "label": "sql_injection"},
    {"code": "import java.sql.Statement;\npublic class SQLInjectionTest2 {\n    public void getUser(String name) throws Exception {\n        Statement stmt = conn.createStatement();\n        String sql = 'SELECT * FROM users WHERE name = \'' + name + '\'';\n        stmt.executeQuery(sql);\n    }\n}", "label": "sql_injection"},
    
    # Java内存泄漏
    {"code": "import java.util.ArrayList;\nimport java.util.List;\npublic class MemoryLeakTest {\n    private static List<Object> list = new ArrayList<>();\n    public static void main(String[] args) {\n        while (true) {\n            list.add(new byte[1024 * 1024]);\n        }\n    }\n}", "label": "memory_leak"},
    {"code": "import java.io.FileInputStream;\npublic class ResourceLeakTest {\n    public static void main(String[] args) throws Exception {\n        FileInputStream fis = new FileInputStream('test.txt');\n        byte[] data = new byte[1024];\n        fis.read(data);\n    }\n}", "label": "memory_leak"},
    
    # Java竞态条件
    {"code": "public class RaceConditionTest {\n    private static int counter = 0;\n    public static void main(String[] args) {\n        Thread t1 = new Thread(() -> {\n            for (int i = 0; i < 1000; i++) {\n                counter++;\n            }\n        });\n        Thread t2 = new Thread(() -> {\n            for (int i = 0; i < 1000; i++) {\n                counter++;\n            }\n        });\n        t1.start();\n        t2.start();\n    }\n}", "label": "race_condition"},
    {"code": "public class RaceConditionTest2 {\n    private static int balance = 0;\n    public static void deposit(int amount) {\n        balance += amount;\n    }\n    public static void withdraw(int amount) {\n        balance -= amount;\n    }\n}", "label": "race_condition"},
    
    # Java安全问题
    {"code": "public class SecurityTest {\n    public static void main(String[] args) {\n        String password = 'secret123';\n        System.out.println('Password: ' + password);\n    }\n}", "label": "security"},
    {"code": "public class SecurityTest2 {\n    private static final String SECRET_KEY = 'my-secret-key-12345';\n    public static void main(String[] args) {\n        System.out.println(SECRET_KEY);\n    }\n}", "label": "security"},
    
    # Java数组越界
    {"code": "public class ArrayIndexOutOfBoundsTest {\n    public static void main(String[] args) {\n        int[] arr = {1, 2, 3};\n        System.out.println(arr[5]);\n    }\n}", "label": "null_pointer"},
    {"code": "public class ArrayIndexTest {\n    public static void main(String[] args) {\n        int[] arr = new int[5];\n        for (int i = 0; i <= arr.length; i++) {\n            arr[i] = i;\n        }\n    }\n}", "label": "null_pointer"},
    
    # Java逻辑错误
    {"code": "public class LogicErrorTest {\n    public static void main(String[] args) {\n        int x = 5;\n        if (x = 10) {\n            System.out.println('x is 10');\n        }\n    }\n}", "label": "null_pointer"},
    {"code": "public class LogicErrorTest2 {\n    public static void main(String[] args) {\n        int x = 5;\n        while (x > 0) {\n            System.out.println(x);\n        }\n    }\n}", "label": "memory_leak"},
    
    # 无缺陷的Java代码
    {"code": "public class GoodCodeTest {\n    public static void main(String[] args) {\n        String str = 'Hello';\n        if (str != null) {\n            System.out.println(str.length());\n        }\n    }\n}", "label": "no_defect"},
    {"code": "import java.io.FileInputStream;\nimport java.io.IOException;\npublic class GoodResourceTest {\n    public static void main(String[] args) {\n        try (FileInputStream fis = new FileInputStream('test.txt')) {\n            byte[] data = new byte[1024];\n            fis.read(data);\n        } catch (IOException e) {\n            e.printStackTrace();\n        }\n    }\n}", "label": "no_defect"},
    {"code": "import java.sql.Connection;\nimport java.sql.PreparedStatement;\npublic class GoodSQLTest {\n    public void getUser(String name) throws Exception {\n        Connection conn = DriverManager.getConnection('jdbc:mysql://localhost:3306/test', 'root', 'password');\n        String sql = 'SELECT * FROM users WHERE name = ?';\n        PreparedStatement pstmt = conn.prepareStatement(sql);\n        pstmt.setString(1, name);\n        pstmt.executeQuery();\n    }\n}", "label": "no_defect"},
    {"code": "public class GoodThreadTest {\n    private static int counter = 0;\n    private static final Object lock = new Object();\n    public static void increment() {\n        synchronized (lock) {\n            counter++;\n        }\n    }\n}", "label": "no_defect"},
    {"code": "public class GoodMathTest {\n    public static int add(int a, int b) {\n        return a + b;\n    }\n    public static void main(String[] args) {\n        System.out.println(add(1, 2));\n    }\n}", "label": "no_defect"},
]


from service.code_tokenizer import tokenize_code


def train_advanced_model():
    """训练高级机器学习模型"""
    print("Training Advanced ML Model...")
    
    # 准备数据
    X = [sample['code'] for sample in TRAINING_DATA]
    y = [sample['label'] for sample in TRAINING_DATA]
    
    # 标签编码
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # 分割数据
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.3, random_state=42)
    
    # 创建管道
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(tokenizer=tokenize_code, lowercase=False, ngram_range=(1, 2))),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    # 训练模型
    pipeline.fit(X_train, y_train)
    
    # 评估模型
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Model Accuracy: {accuracy*100:.2f}%")
    print("Classification Report:")
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))
    
    # 保存模型
    model_data = {
        'pipeline': pipeline,
        'label_encoder': label_encoder
    }
    joblib.dump(model_data, 'trained_model_java.joblib')
    print("Model saved to trained_model_java.joblib")
    
    return pipeline, label_encoder


def evaluate_model(pipeline, label_encoder):
    """评估模型"""
    # 测试Java测试用例
    test_cases = [
        {"name": "空指针异常", "code": "public class NullPointerExceptionTest {\n    public static void main(String[] args) {\n        String str = null;\n        System.out.println(str.length());\n    }\n}"},
        {"name": "SQL注入", "code": "import java.sql.Connection;\nimport java.sql.Statement;\npublic class SQLInjectionTest {\n    public static void main(String[] args) throws Exception {\n        String userInput = 'admin\' OR \'1\'=\'1';\n        Connection conn = DriverManager.getConnection('jdbc:mysql://localhost:3306/test', 'root', 'password');\n        Statement stmt = conn.createStatement();\n        String sql = 'SELECT * FROM users WHERE username = \'' + userInput + '\'';\n        stmt.executeQuery(sql);\n    }\n}"},
        {"name": "内存泄漏", "code": "import java.util.ArrayList;\nimport java.util.List;\npublic class MemoryLeakTest {\n    private static List<Object> list = new ArrayList<>();\n    public static void main(String[] args) {\n        while (true) {\n            list.add(new byte[1024 * 1024]);\n        }\n    }\n}"},
        {"name": "竞态条件", "code": "public class RaceConditionTest {\n    private static int counter = 0;\n    public static void main(String[] args) {\n        Thread t1 = new Thread(() -> {\n            for (int i = 0; i < 1000; i++) {\n                counter++;\n            }\n        });\n        Thread t2 = new Thread(() -> {\n            for (int i = 0; i < 1000; i++) {\n                counter++;\n            }\n        });\n        t1.start();\n        t2.start();\n    }\n}"},
        {"name": "安全问题", "code": "public class SecurityTest {\n    public static void main(String[] args) {\n        String password = 'secret123';\n        System.out.println('Password: ' + password);\n    }\n}"},
        {"name": "数组越界", "code": "public class ArrayIndexOutOfBoundsTest {\n    public static void main(String[] args) {\n        int[] arr = {1, 2, 3};\n        System.out.println(arr[5]);\n    }\n}"},
        {"name": "未关闭资源", "code": "import java.io.FileInputStream;\npublic class ResourceLeakTest {\n    public static void main(String[] args) throws Exception {\n        FileInputStream fis = new FileInputStream('test.txt');\n        byte[] data = new byte[1024];\n        fis.read(data);\n    }\n}"},
        {"name": "逻辑错误", "code": "public class LogicErrorTest {\n    public static void main(String[] args) {\n        int x = 5;\n        if (x = 10) {\n            System.out.println('x is 10');\n        }\n    }\n}"},
    ]
    
    print("\nTesting Java Test Cases:")
    print("="*60)
    
    correct = 0
    total = len(test_cases)
    
    for test_case in test_cases:
        code = test_case['code']
        name = test_case['name']
        
        # 预测
        prediction = pipeline.predict([code])[0]
        defect_type = label_encoder.inverse_transform([prediction])[0]
        
        # 计算置信度
        probabilities = pipeline.predict_proba([code])[0]
        confidence = max(probabilities)
        
        print(f"Test Case: {name}")
        print(f"Predicted: {defect_type} (Confidence: {confidence:.2f})")
        print("-"*60)
    
    print(f"\nTotal: {total} test cases")


if __name__ == "__main__":
    pipeline, label_encoder = train_advanced_model()
    evaluate_model(pipeline, label_encoder)