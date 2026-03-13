from config import celery_app
from service import CodeAnalyzer, MLModelService
from entity.po import CodeFile, AnalysisResult
from main import db
import time

code_analyzer = CodeAnalyzer()
ml_service = MLModelService()

@celery_app.task(bind=True)
def analyze_code_task(self, file_id: int):
    try:
        self.update_state(state='PROCESSING', meta={'progress': 0, 'status': 'Loading code file'})
        
        code_file = CodeFile.query.get(file_id)
        if not code_file:
            return {'status': 'error', 'message': 'Code file not found'}
        
        self.update_state(state='PROCESSING', meta={'progress': 30, 'status': 'Extracting features'})
        
        features = code_analyzer.extract_features(code_file.content, code_file.language)
        
        self.update_state(state='PROCESSING', meta={'progress': 60, 'status': 'Running ML model'})
        
        result = ml_service.predict(code_file.content, code_file.language)
        
        self.update_state(state='PROCESSING', meta={'progress': 80, 'status': 'Saving results'})
        
        analysis_result = AnalysisResult(
            file_id=file_id,
            defect_type=result.get('defect_type'),
            confidence=result.get('confidence'),
            line_number=result.get('line_number'),
            suggestion=result.get('suggestion'),
            severity=result.get('severity', 'medium')
        )
        db.session.add(analysis_result)
        db.session.commit()
        
        return {
            'status': 'completed',
            'progress': 100,
            'result': {
                'id': analysis_result.id,
                'defect_type': analysis_result.defect_type,
                'confidence': analysis_result.confidence,
                'line_number': analysis_result.line_number,
                'suggestion': analysis_result.suggestion,
                'severity': analysis_result.severity,
                'features': features
            }
        }
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@celery_app.task(bind=True)
def batch_analyze_task(self, file_ids: list):
    total = len(file_ids)
    results = []
    
    for i, file_id in enumerate(file_ids):
        try:
            self.update_state(
                state='PROCESSING',
                meta={
                    'progress': int((i / total) * 100),
                    'status': f'Processing file {i+1}/{total}'
                }
            )
            
            result = analyze_code_task.delay(file_id)
            results.append({
                'file_id': file_id,
                'status': 'submitted',
                'task_id': result.id
            })
            
        except Exception as e:
            results.append({
                'file_id': file_id,
                'status': 'error',
                'message': str(e)
            })
    
    return {
        'status': 'completed',
        'total': total,
        'results': results
    }

@celery_app.task
def train_model_task(train_data_path: str, epochs: int = 10):
    try:
        import json
        
        with open(train_data_path, 'r') as f:
            train_data = json.load(f)
        
        ml_service.train(train_data, epochs)
        
        return {'status': 'completed', 'message': 'Model trained successfully'}
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@celery_app.task
def generate_report_task(file_id: int):
    try:
        code_file = CodeFile.query.get(file_id)
        results = AnalysisResult.query.filter_by(file_id=file_id).all()
        
        report = {
            'filename': code_file.filename,
            'language': code_file.language,
            'total_defects': len(results),
            'defects': [r.to_dict() for r in results],
            'severity_summary': {}
        }
        
        for r in results:
            severity = r.severity
            report['severity_summary'][severity] = report['severity_summary'].get(severity, 0) + 1
        
        return {'status': 'completed', 'report': report}
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
