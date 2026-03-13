import os
import json
import requests
import zipfile
import shutil
from pathlib import Path
from typing import List, Dict, Optional

class DatasetDownloader:
    DATASETS = {
        'codexglue': {
            'name': 'CodeXGLUE Defect Detection',
            'url': 'https://github.com/microsoft/CodeXGLUE/archive/refs/heads/main.zip',
            'description': 'Multi-language code defect dataset from Microsoft'
        },
        'sard': {
            'name': 'NIST SARD',
            'url': 'https://samate.nist.gov/SARD/downloads.php',
            'description': 'Software Assurance Reference Dataset'
        },
        'bigfix': {
            'name': 'BigFix',
            'url': 'https://github.com/xing-hu/BigFix/archive/refs/heads/master.zip',
            'description': 'Large-scale C code defect fix dataset'
        },
        'py150': {
            'name': 'Py150',
            'url': 'https://github.com/google-research-datasets/pysentimiento/archive/refs/heads/main.zip',
            'description': '150K Python code snippets'
        }
    }
    
    def __init__(self, output_dir: str = './datasets'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def download_github_repo(self, url: str, name: str) -> Path:
        zip_path = self.output_dir / f'{name}.zip'
        extract_path = self.output_dir / name
        
        print(f'Downloading {name}...')
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(zip_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f'\rProgress: {progress:.1f}%', end='')
        
        print(f'\nExtracting {name}...')
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(self.output_dir)
        
        zip_path.unlink()
        
        return extract_path
    
    def download_all(self) -> Dict[str, Path]:
        downloaded = {}
        for key, info in self.DATASETS.items():
            try:
                path = self.download_github_repo(info['url'], key)
                downloaded[key] = path
            except Exception as e:
                print(f'Error downloading {key}: {e}')
        return downloaded
    
    def download_single(self, name: str) -> Optional[Path]:
        if name not in self.DATASETS:
            print(f'Unknown dataset: {name}')
            return None
        
        info = self.DATASETS[name]
        try:
            return self.download_github_repo(info['url'], name)
        except Exception as e:
            print(f'Error downloading {name}: {e}')
            return None


class DatasetProcessor:
    LANGUAGES = ['python', 'java', 'javascript', 'c', 'cpp', 'go']
    
    def __init__(self, dataset_dir: str = './datasets'):
        self.dataset_dir = Path(dataset_dir)
        
    def process_codexglue(self) -> List[Dict]:
        processed = []
        
        codexglue_dir = self.dataset_dir / 'CodeXGLUE-main' / 'Code-Code' / 'Defect-detection'
        if not codexglue_dir.exists():
            print(f'CodeXGLUE directory not found: {codexglue_dir}')
            return processed
        
        for json_file in codexglue_dir.rglob('*.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        processed.extend(data)
                    elif isinstance(data, dict):
                        processed.append(data)
            except Exception as e:
                print(f'Error processing {json_file}: {e}')
        
        return processed
    
    def process_sard(self) -> List[Dict]:
        processed = []
        
        sard_dir = self.dataset_dir / 'SARD'
        if not sard_dir.exists():
            print(f'SARD directory not found: {sard_dir}')
            return processed
        
        for test_case_dir in sard_dir.rglob('test_case_*'):
            if test_case_dir.is_dir():
                code_file = test_case_dir / 'test.c'
                if code_file.exists():
                    try:
                        with open(code_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            processed.append({
                                'language': 'c',
                                'code': content,
                                'source': 'sard'
                            })
                    except Exception as e:
                        print(f'Error processing {code_file}: {e}')
        
        return processed
    
    def process_py150(self) -> List[Dict]:
        processed = []
        
        py150_dir = self.dataset_dir / 'pysentimiento-main'
        if not py150_dir.exists():
            print(f'Py150 directory not found: {py150_dir}')
            return processed
        
        python_files = list(py150_dir.rglob('*.py'))[:1000]
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if len(content) > 50:
                        processed.append({
                            'language': 'python',
                            'code': content,
                            'source': 'py150'
                        })
            except Exception as e:
                print(f'Error processing {py_file}: {e}')
        
        return processed
    
    def process_all(self) -> Dict[str, List[Dict]]:
        return {
            'codexglue': self.process_codexglue(),
            'sard': self.process_sard(),
            'py150': self.process_py150()
        }
    
    def create_training_data(self, min_samples: int = 1000) -> List[Dict]:
        all_data = self.process_all()
        
        training_data = []
        
        for source, samples in all_data.items():
            for sample in samples:
                if 'code' in sample:
                    training_data.append({
                        'code': sample['code'],
                        'language': sample.get('language', 'python'),
                        'source': source
                    })
        
        return training_data[:min_samples]
    
    def save_processed_data(self, output_file: str = 'processed_data.json'):
        data = self.create_training_data()
        output_path = self.dataset_dir / output_file
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f'Saved {len(data)} samples to {output_path}')
        return output_path


if __name__ == '__main__':
    downloader = DatasetDownloader('./datasets')
    downloader.download_all()
    
    processor = DatasetProcessor('./datasets')
    processor.save_processed_data()
