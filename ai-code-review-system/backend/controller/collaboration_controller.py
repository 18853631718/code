from flask import Blueprint, jsonify, request
from entity.po import ReviewSession, ReviewComment
from repository import CodeRepository

collaboration_bp = Blueprint('collaboration', __name__, url_prefix='/api')

code_repository = CodeRepository()

@collaboration_bp.route('/collaboration/sessions', methods=['GET'])
def get_sessions():
    sessions = code_repository.find_all(ReviewSession)
    return jsonify([s.to_dict() for s in sessions]), 200

@collaboration_bp.route('/collaboration/sessions', methods=['POST'])
def create_session():
    data = request.get_json()
    session = ReviewSession(
        name=data.get('name'),
        owner=data.get('owner'),
        status='active',
        participants=data.get('owner', '')
    )
    code_repository.save(session)
    
    return jsonify(session.to_dict()), 201

@collaboration_bp.route('/collaboration/sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    session = code_repository.find_by_id(ReviewSession, session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    comments = code_repository.find_by_criteria(ReviewComment, session_id=session_id)
    
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

@collaboration_bp.route('/collaboration/sessions/<int:session_id>/join', methods=['POST'])
def join_session(session_id):
    session = code_repository.find_by_id(ReviewSession, session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    data = request.get_json()
    user = data.get('user')
    
    participants = session.participants.split(',') if session.participants else []
    if user and user not in participants:
        participants.append(user)
        session.participants = ','.join(participants)
        code_repository.update(session)
    
    return jsonify({
        'id': session.id,
        'participants': participants
    }), 200

@collaboration_bp.route('/collaboration/sessions/<int:session_id>/comments', methods=['POST'])
def add_comment(session_id):
    session = code_repository.find_by_id(ReviewSession, session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    data = request.get_json()
    
    comment = ReviewComment(
        session_id=session_id,
        author=data.get('author'),
        content=data.get('content'),
        line_number=data.get('line_number')
    )
    code_repository.save(comment)
    
    return jsonify(comment.to_dict()), 201
