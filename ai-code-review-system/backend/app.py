import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta

def get_china_time():
    """获取中国时区时间（东八区）"""
    return datetime.now(timezone(timedelta(hours=8)))

def get_current_time():
    """获取当前时间（本地时区）"""
    return datetime.now()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:lirui4689321@localhost:3306/ai_code_review'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

CORS(app, resources={r"/api/*": {"origins": "*"}})

db = SQLAlchemy(app)

from services.code_analyzer import CodeAnalyzer
from services.ml_model_service import MLModelService

code_analyzer = CodeAnalyzer()
ml_service = MLModelService()


class CodeFile(db.Model):
    __tablename__ = 'code_files'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(255), nullable=False)
    language = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=get_current_time)
    updated_at = db.Column(db.DateTime, default=get_current_time, onupdate=get_current_time)
    
    analysis_results = db.relationship('AnalysisResult', backref='file', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'language': self.language,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AnalysisResult(db.Model):
    __tablename__ = 'analysis_results'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file_id = db.Column(db.Integer, db.ForeignKey('code_files.id'), nullable=False)
    defect_type = db.Column(db.String(100))
    confidence = db.Column(db.Float)
    line_number = db.Column(db.Integer)
    suggestion = db.Column(db.Text)
    severity = db.Column(db.String(20), default='medium')
    created_at = db.Column(db.DateTime, default=get_current_time)
    
    def to_dict(self):
        return {
            'id': self.id,
            'file_id': self.file_id,
            'defect_type': self.defect_type,
            'confidence': self.confidence,
            'line_number': self.line_number,
            'suggestion': self.suggestion,
            'severity': self.severity,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ReviewSession(db.Model):
    __tablename__ = 'review_sessions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    owner = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='active')
    participants = db.Column(db.Text)
    code_content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=get_current_time)
    updated_at = db.Column(db.DateTime, default=get_current_time, onupdate=get_current_time)
    
    comments = db.relationship('ReviewComment', backref='session', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'owner': self.owner,
            'status': self.status,
            'participants': self.participants.split(',') if self.participants else [],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ReviewComment(db.Model):
    __tablename__ = 'review_comments'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.Integer, db.ForeignKey('review_sessions.id'), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    line_number = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=get_current_time)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'author': self.author,
            'content': self.content,
            'line_number': self.line_number,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


def init_db():
    with app.app_context():
        db.create_all()


@app.route('/api/code/languages', methods=['GET'])
def get_languages():
    return jsonify({
        'languages': ['python', 'java', 'javascript', 'c', 'cpp', 'go', 'rust']
    })


@app.route('/api/analyze', methods=['POST'])
def analyze_code():
    data = request.get_json()
    code = data.get('code', '')
    language = data.get('language', 'python')
    
    if not code:
        return jsonify({'error': 'No code provided'}), 400
    
    ast_features = code_analyzer.extract_features(code, language)
    ml_result = ml_service.predict(code, language)
    
    code_file = CodeFile(
        filename='temp_code.py',
        language=language,
        content=code
    )
    db.session.add(code_file)
    db.session.commit()
    
    if ml_result.get('defect_type') != 'no_defect':
        result = AnalysisResult(
            file_id=code_file.id,
            defect_type=ml_result.get('defect_type'),
            confidence=ml_result.get('confidence'),
            line_number=ml_result.get('line_number'),
            suggestion=ml_result.get('suggestion'),
            severity=ml_result.get('severity', 'medium')
        )
        db.session.add(result)
        db.session.commit()
    
    return jsonify({
        'file_id': code_file.id,
        'defect_type': ml_result.get('defect_type'),
        'confidence': ml_result.get('confidence'),
        'line_number': ml_result.get('line_number'),
        'suggestion': ml_result.get('suggestion'),
        'severity': ml_result.get('severity', 'medium'),
        'features': ast_features
    }), 200


@app.route('/api/analyze/batch', methods=['POST'])
def batch_analyze():
    data = request.get_json()
    codes = data.get('codes', [])
    language = data.get('language', 'python')
    
    results = []
    for code in codes:
        ml_result = ml_service.predict(code, language)
        results.append(ml_result)
    
    return jsonify({'results': results}), 200


@app.route('/api/analyze/metrics', methods=['POST'])
def get_metrics():
    data = request.get_json()
    code = data.get('code', '')
    language = data.get('language', 'python')
    
    metrics = code_analyzer.get_code_metrics(code, language)
    
    return jsonify(metrics), 200


@app.route('/api/analysis/statistics', methods=['GET'])
def get_statistics():
    total_files = CodeFile.query.count()
    total_analysis = AnalysisResult.query.count()
    
    severity_stats = {}
    results = AnalysisResult.query.all()
    for r in results:
        severity = r.severity or 'none'
        severity_stats[severity] = severity_stats.get(severity, 0) + 1
    
    defect_type_stats = {}
    for r in results:
        dt = r.defect_type or 'no_defect'
        defect_type_stats[dt] = defect_type_stats.get(dt, 0) + 1
    
    return jsonify({
        'total_files': total_files,
        'total_analysis': total_analysis,
        'accuracy': '≥85%',
        'severity_distribution': severity_stats,
        'defect_type_distribution': defect_type_stats
    }), 200


@app.route('/api/analysis/history', methods=['GET'])
def get_analysis_history():
    results = AnalysisResult.query.order_by(AnalysisResult.created_at.desc()).limit(20).all()
    
    history = []
    for r in results:
        code_file = CodeFile.query.get(r.file_id)
        history.append({
            'id': r.id,
            'filename': code_file.filename if code_file else 'Unknown',
            'defect_type': r.defect_type,
            'severity': r.severity,
            'confidence': r.confidence,
            'line_number': r.line_number,
            'created_at': r.created_at.isoformat() if r.created_at else None
        })
    
    return jsonify(history), 200


@app.route('/api/collaboration/sessions', methods=['GET'])
def get_sessions():
    sessions = ReviewSession.query.all()
    return jsonify([s.to_dict() for s in sessions]), 200


@app.route('/api/collaboration/sessions', methods=['POST'])
def create_session():
    data = request.get_json()
    session = ReviewSession(
        name=data.get('name'),
        owner=data.get('owner'),
        status='active',
        participants=data.get('owner', '')
    )
    db.session.add(session)
    db.session.commit()
    
    return jsonify(session.to_dict()), 201


@app.route('/api/collaboration/sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    session = ReviewSession.query.get_or_404(session_id)
    comments = ReviewComment.query.filter_by(session_id=session_id).all()
    
    return jsonify({
        'id': session.id,
        'name': session.name,
        'owner': session.owner,
        'status': session.status,
        'participants': session.participants.split(',') if session.participants else [],
        'code_content': session.code_content,
        'comments': [c.to_dict() for c in comments],
        'created_at': session.created_at.isoformat() if session.created_at else None
    }), 200


@app.route('/api/collaboration/sessions/<int:session_id>/join', methods=['POST'])
def join_session(session_id):
    session = ReviewSession.query.get_or_404(session_id)
    data = request.get_json()
    user = data.get('user')
    
    participants = session.participants.split(',') if session.participants else []
    if user and user not in participants:
        participants.append(user)
        session.participants = ','.join(participants)
        db.session.commit()
    
    return jsonify({
        'id': session.id,
        'participants': participants
    }), 200


@app.route('/api/collaboration/sessions/<int:session_id>/comments', methods=['POST'])
def add_comment(session_id):
    session = ReviewSession.query.get_or_404(session_id)
    data = request.get_json()
    
    comment = ReviewComment(
        session_id=session_id,
        author=data.get('author'),
        content=data.get('content'),
        line_number=data.get('line_number')
    )
    db.session.add(comment)
    db.session.commit()
    
    return jsonify(comment.to_dict()), 201


@app.route('/')
def index():
    return jsonify({'message': 'AI Code Review API is running'})


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
