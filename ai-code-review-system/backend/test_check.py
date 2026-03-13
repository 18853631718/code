from service.code_analyzer import CodeAnalyzer

a = CodeAnalyzer()

code = '''def hello_world():
    return student.name

if __name__ == "__main__":
    hello_world()'''

print("Testing code:")
print(code)
print("\n--- Results ---")
print("Syntax error:", a.detect_syntax_error(code, 'python'))
features = a.extract_features(code, 'python')
print("Issues:", features.get('issues', []))
