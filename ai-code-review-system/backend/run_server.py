import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 清除所有可能的缓存模块
for mod in list(sys.modules.keys()):
    if any(mod.startswith(prefix) for prefix in ['controller', 'service', 'entity', 'repository', 'config', 'database']):
        try:
            del sys.modules[mod]
        except:
            pass

from flask import Flask, jsonify, request
from flask_cors import CORS

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# 配置CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 直接在这里导入和配置
from service.code_analyzer import CodeAnalyzer
from service.ml_model_service import MLModelService

code_analyzer = CodeAnalyzer()
ml_service = MLModelService()

# 根路由
@app.route('/')
def index():
    return jsonify({'message': 'AI Code Review API is running'})

# 测试语法错误检测
@app.route('/test-syntax-error', methods=['POST'])
def test_syntax_error():
    data = request.get_json()
    code = data.get('code', '')
    language = data.get('language', 'python')
    
    syntax_error = code_analyzer.detect_syntax_error(code, language)
    print(f"Test syntax error - Syntax error: {syntax_error}")
    
    if syntax_error:
        return jsonify({
            'defect_type': 'syntax_error',
            'message': syntax_error.get('message'),
            'line': syntax_error.get('line')
        }), 200
    else:
        return jsonify({
            'defect_type': 'no_defect',
            'message': 'No syntax error detected'
        }), 200

# 主分析接口
@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    code = data.get('code', '')
    language = data.get('language', 'python')
    
    # 提取特征（包括issues检测）
    features = code_analyzer.extract_features(code, language)
    issues = features.get('issues', [])
    
    # 首先检测语法错误
    syntax_error = code_analyzer.detect_syntax_error(code, language)
    
    if syntax_error:
        return jsonify({
            'defect_type': 'syntax_error',
            'confidence': 1.0,
            'line_number': syntax_error.get('line'),
            'suggestion': f'Syntax error: {syntax_error.get("message")}',
            'severity': 'high',
            'method': 'ast',
            'features': features,
            'issues': issues
        }), 200
    
    # 使用ML模型分析
    ml_result = ml_service.predict(code, language)
    
    # 合并issues
    all_issues = issues.copy() if issues else []
    if ml_result.get('defect_type') != 'no_defect':
        all_issues.append({
            'type': ml_result.get('defect_type'),
            'message': ml_result.get('suggestion'),
            'severity': ml_result.get('severity', 'medium')
        })
    
    return jsonify({
        'defect_type': ml_result.get('defect_type'),
        'confidence': ml_result.get('confidence'),
        'line_number': ml_result.get('line_number'),
        'suggestion': ml_result.get('suggestion'),
        'severity': ml_result.get('severity', 'medium'),
        'method': ml_result.get('method', 'unknown'),
        'features': features,
        'issues': all_issues
    }), 200

# 代码语言列表
@app.route('/api/code/languages', methods=['GET'])
def get_languages():
    return jsonify({
        'languages': ['python', 'java', 'javascript', 'c', 'cpp', 'go', 'rust']
    })

# 统计接口
@app.route('/api/analysis/statistics', methods=['GET'])
def get_statistics():
    return jsonify({
        'total_analyses': 100,
        'defects_by_type': {
            'syntax_error': 10,
            'possibly_undefined': 20,
            'python_print': 15,
            'no_defect': 55
        },
        'languages': {
            'python': 40,
            'java': 30,
            'javascript': 20,
            'cpp': 10
        },
        'average_confidence': 0.75
    })

# 历史记录
@app.route('/api/analysis/history', methods=['GET'])
def get_history():
    return jsonify({
        'history': [
            {'id': 1, 'code': 'def hello(): pass', 'result': 'no_defect', 'time': '2024-01-01 10:00'},
            {'id': 2, 'code': 'print(x)', 'result': 'python_print', 'time': '2024-01-01 10:05'},
            {'id': 3, 'code': 'return student.name', 'result': 'possibly_undefined', 'time': '2024-01-01 10:10'}
        ]
    })

if __name__ == '__main__':
    print("Starting server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
