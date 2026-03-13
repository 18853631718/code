import requests
import json

url = 'http://localhost:5000/api/analyze'
code = '''def hello_world(): 
    return student.name 

if __name__ == "__main__": 
    hello_world()'''

data = {
    'code': code,
    'language': 'python'
}

response = requests.post(url, json=data)
print("Status:", response.status_code)
result = response.json()
print("Result:", json.dumps(result, indent=2))
