from typing import Optional, List

class CodeAnalysisRequest:
    def __init__(self, code: str, language: str):
        self.code = code
        self.language = language

class CodeAnalysisResponse:
    def __init__(self, file_id: int, defect_type: str, confidence: float, line_number: Optional[int], suggestion: str, severity: str):
        self.file_id = file_id
        self.defect_type = defect_type
        self.confidence = confidence
        self.line_number = line_number
        self.suggestion = suggestion
        self.severity = severity

class BatchAnalysisRequest:
    def __init__(self, codes: List[str], language: str):
        self.codes = codes
        self.language = language

class BatchAnalysisResponse:
    def __init__(self, results: List[CodeAnalysisResponse]):
        self.results = results
