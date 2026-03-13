import os
import sys
import json
import requests

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 后端API地址
API_URL = 'http://localhost:5000/api/analyze'

# 读取Java测试用例
def read_java_test_cases():
    test_cases = []
    with open('test_java_cases.java', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 分割测试用例
    test_classes = content.split('// 测试用例')
    for i, test_class in enumerate(test_classes[1:], 1):
        lines = test_class.strip().split('\n')
        class_name = lines[0].split(': ')[1].strip()
        code = '\n'.join(lines[1:])
        test_cases.append({
            'id': i,
            'name': class_name,
            'code': code
        })
    return test_cases

# 分析单个测试用例
def analyze_code(code, language='java'):
    payload = {
        'code': code,
        'language': language
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f'API error: {response.status_code}'}
    except Exception as e:
        return {'error': str(e)}

# 批量测试
def batch_test():
    test_cases = read_java_test_cases()
    results = []
    
    print('开始批量测试Java用例...')
    print('-' * 80)
    
    for test_case in test_cases:
        print(f'测试用例 {test_case["id"]}: {test_case["name"]}')
        result = analyze_code(test_case['code'])
        results.append({
            'test_case': test_case,
            'result': result
        })
        
        if 'error' in result:
            print(f'  错误: {result["error"]}')
        else:
            defect_type = result.get('defect_type', 'no_defect')
            confidence = result.get('confidence', 0)
            method = result.get('method', 'unknown')
            print(f'  缺陷类型: {defect_type}')
            print(f'  置信度: {confidence:.2f}')
            print(f'  检测方法: {method}')
            if 'suggestion' in result:
                print(f'  修复建议: {result["suggestion"]}')
        print('-' * 80)
    
    return results

# 分析结果
def analyze_results(results):
    print('\n测试结果分析:')
    print('-' * 80)
    
    method_count = {'rule': 0, 'ml': 0, 'quick_rule': 0, 'unknown': 0}
    defect_count = {'null_pointer': 0, 'sql_injection': 0, 'memory_leak': 0, 'race_condition': 0, 'security': 0, 'no_defect': 0}
    
    for item in results:
        result = item['result']
        if 'error' not in result:
            method = result.get('method', 'unknown')
            defect_type = result.get('defect_type', 'no_defect')
            method_count[method] += 1
            defect_count[defect_type] += 1
    
    print('检测方法分布:')
    for method, count in method_count.items():
        print(f'  {method}: {count}')
    
    print('\n缺陷类型分布:')
    for defect, count in defect_count.items():
        print(f'  {defect}: {count}')
    
    print('\n检测方法说明:')
    print('  quick_rule: 快速规则检测（基于正则表达式）')
    print('  rule: 规则引擎检测（基于正则表达式）')
    print('  ml: 机器学习模型检测')
    print('  unknown: 未知检测方法')

if __name__ == '__main__':
    results = batch_test()
    analyze_results(results)
