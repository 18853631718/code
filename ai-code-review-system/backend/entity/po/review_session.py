from database import db
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

class ReviewSession(db.Model):
    __tablename__ = 'review_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    owner = Column(String(100), nullable=False)
    status = Column(String(20), default='active')
    participants = Column(Text)
    code_content = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    comments = relationship('ReviewComment', backref='session', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'owner': self.owner,
            'status': self.status,
            'participants': self.participants.split(',') if self.participants else [],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
