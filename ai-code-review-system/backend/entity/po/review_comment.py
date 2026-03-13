from database import db
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime

class ReviewComment(db.Model):
    __tablename__ = 'review_comments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('review_sessions.id'), nullable=False)
    author = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    line_number = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'author': self.author,
            'content': self.content,
            'line_number': self.line_number,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
