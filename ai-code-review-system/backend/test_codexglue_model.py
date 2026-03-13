#!/usr/bin/env python3
"""
测试CodeXGLUE训练的模型
"""
import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ml_model_service import MLModelService

def test_model_loading():
    """测试模型加载"""
    print("=" * 60)
    print("测试CodeXGLUE模型加载")
    print("=" * 60)
    
    service = MLModelService()
    print(f"模型服务初始化完成")
    
    # 测试几个代码样本
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
    
    print("\n测试模型预测:")
    print("=" * 60)
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        print(f"代码: {test_case['code']}")
        
        result = service.predict(test_case['code'], 'python')
        print(f"结果: {result['defect_type']}")
        print(f"置信度: {result['confidence']:.2f}")
        print(f"方法: {result['method']}")
        if 'suggestion' in result:
            print(f"建议: {result['suggestion']}")
        print("-" * 40)

if __name__ == "__main__":
    test_model_loading()
