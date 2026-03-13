from typing import Optional
from datetime import datetime

class AnalysisResultVO:
    def __init__(self, id: int, filename: str, defect_type: str, severity: str, confidence: float, line_number: Optional[int], created_at: datetime):
        self.id = id
        self.filename = filename
        self.defect_type = defect_type
        self.severity = severity
        self.confidence = confidence
        self.line_number = line_number
        self.created_at = created_at

class StatisticsVO:
    def __init__(self, total_files: int, total_analysis: int, accuracy: str, severity_distribution: dict, defect_type_distribution: dict):
        self.total_files = total_files
        self.total_analysis = total_analysis
        self.accuracy = accuracy
        self.severity_distribution = severity_distribution
        self.defect_type_distribution = defect_type_distribution
