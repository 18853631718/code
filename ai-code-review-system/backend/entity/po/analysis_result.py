from database import db
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from datetime import datetime

class AnalysisResult(db.Model):
    __tablename__ = 'analysis_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(Integer, ForeignKey('code_files.id'), nullable=False)
    defect_type = Column(String(100))
    confidence = Column(Float)
    line_number = Column(Integer)
    suggestion = Column(Text)
    severity = Column(String(20), default='medium')
    created_at = Column(DateTime, default=datetime.now)
    
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
