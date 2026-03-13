import os
import sys
import importlib

# 清除所有缓存的模块
for module in list(sys.modules.keys()):
    if module.startswith('controller') or module.startswith('service'):
        del sys.modules[module]

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request
from flask_cors import CORS

# 导入配置
from config import AppConfig, make_celery

# 导入数据库
from database import db

# 导入控制器
from controller import code_bp, analysis_bp, collaboration_bp

# 导入实体类
from entity.po import CodeFile, AnalysisResult, ReviewSession, ReviewComment

# 导入服务和仓库
from service import CodeAnalyzer, MLModelService
from repository import CodeRepository

# 创建Flask应用
app = Flask(__name__)
app.config.from_object(AppConfig)

# 配置CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 初始化数据库
db.init_app(app)

# 先导入控制器模块，确保它们的repository实例被创建
from controller.code_controller import code_repository as code_controller_repo
from controller.analysis_controller import code_repository as analysis_controller_repo
from controller.collaboration_controller import code_repository as collaboration_controller_repo

# 初始化服务和仓库
code_analyzer = CodeAnalyzer()
ml_service = MLModelService()
code_repository = CodeRepository()

# 将db.session传递给所有控制器的repository实例
with app.app_context():
    code_controller_repo.set_db(db.session)
    analysis_controller_repo.set_db(db.session)
    collaboration_controller_repo.set_db(db.session)

# 根路由 - 必须在注册蓝图之前
@app.route('/')
def index():
    return jsonify({'message': 'AI Code Review API is running'})

# 测试语法错误检测的路由 - 必须在注册蓝图之前
@app.route('/test-syntax-error', methods=['POST'])
def test_syntax_error():
    data = request.get_json()
    code = data.get('code', '')
    language = data.get('language', 'python')
    
    print(f"Test syntax error - Received code: {code}")
    print(f"Test syntax error - Received language: {language}")
    
    from service.code_analyzer import CodeAnalyzer
    analyzer = CodeAnalyzer()
    syntax_error = analyzer.detect_syntax_error(code, language)
    print(f"Test syntax error - Syntax error detected: {syntax_error}")
    
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

# 注册蓝图
app.register_blueprint(code_bp)
app.register_blueprint(analysis_bp)
app.register_blueprint(collaboration_bp)

# 初始化Celery
celery = make_celery(app)

# 初始化数据库表
def init_db():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
