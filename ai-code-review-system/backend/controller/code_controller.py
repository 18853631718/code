from flask import Blueprint, jsonify, request
from entity.po import CodeFile, AnalysisResult
from service import CodeAnalyzer, MLModelService
from repository import CodeRepository

code_bp = Blueprint('code', __name__, url_prefix='/api')

code_analyzer = CodeAnalyzer()
ml_service = MLModelService()
code_repository = CodeRepository()

@code_bp.route('/code/languages', methods=['GET'])
def get_languages():
    return jsonify({
        'languages': ['python', 'java', 'javascript', 'c', 'cpp', 'go', 'rust']
    })

@code_bp.route('/analyze', methods=['POST'])
def analyze_code():
    data = request.get_json()
    code = data.get('code', '')
    language = data.get('language', 'python')
    
    print(f"Received code: {code}")
    print(f"Received language: {language}")
    
    # 首先检测语法错误
    syntax_error = code_analyzer.detect_syntax_error(code, language)
    print(f"Syntax error detected: {syntax_error}")
    
    if syntax_error:
        # 如果有语法错误，优先返回语法错误信息
        print(f"Returning syntax error response: {syntax_error}")
        # 提取特征（用于返回给前端）
        ast_features = code_analyzer.extract_features(code, language)
        return jsonify({
            'file_id': None,
            'defect_type': 'syntax_error',
            'confidence': 1.0,
            'line_number': syntax_error.get('line'),
            'suggestion': f'Syntax error: {syntax_error.get("message")}',
            'severity': 'high',
            'method': 'ast',
            'features': ast_features
        }), 200
    else:
        print("No syntax errors found, continuing to ML analysis")
        # 提取特征
        ast_features = code_analyzer.extract_features(code, language)
    
    # 没有语法错误，继续进行机器学习分析
    ml_result = ml_service.predict(code, language)
    
    # 保存代码文件
    code_file = CodeFile(
        filename='temp_code.py',
        language=language,
        content=code
    )
    code_repository.save(code_file)
    
    # 保存分析结果
    if ml_result.get('defect_type') != 'no_defect':
        result = AnalysisResult(
            file_id=code_file.id,
            defect_type=ml_result.get('defect_type'),
            confidence=ml_result.get('confidence'),
            line_number=ml_result.get('line_number'),
            suggestion=ml_result.get('suggestion'),
            severity=ml_result.get('severity', 'medium')
        )
        code_repository.save(result)
    
    # 返回分析结果
    return jsonify({
        'file_id': code_file.id,
        'defect_type': ml_result.get('defect_type'),
        'confidence': ml_result.get('confidence'),
        'line_number': ml_result.get('line_number'),
        'suggestion': ml_result.get('suggestion'),
        'severity': ml_result.get('severity', 'medium'),
        'method': ml_result.get('method', 'unknown'),
        'features': ast_features
    }), 200

@code_bp.route('/analyze/batch', methods=['POST'])
def batch_analyze():
    data = request.get_json()
    codes = data.get('codes', [])
    language = data.get('language', 'python')
    
    results = []
    for code in codes:
        ml_result = ml_service.predict(code, language)
        results.append(ml_result)
    
    return jsonify({'results': results}), 200

@code_bp.route('/analyze/metrics', methods=['POST'])
def get_metrics():
    data = request.get_json()
    code = data.get('code', '')
    language = data.get('language', 'python')
    
    metrics = code_analyzer.get_code_metrics(code, language)
    
    return jsonify(metrics), 200
