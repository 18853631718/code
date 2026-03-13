"""
调试ML模型
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from services.ml_model_service import MLClassifier

classifier = MLClassifier()
classifier.load_model('trained_model_enhanced.json')

# 测试代码
test_code = 'def get_name(user):\n    if user is not None:\n        return user.name\n    return None'
print(f"Code: {test_code}")
print(f"\nFeatures:")
features = classifier.extract_features(test_code)
for k, v in features.items():
    print(f"  {k}: {v}")

print(f"\nPrediction:")
result = classifier.predict(test_code)
print(f"  {result}")

print("\n" + "="*50)

# 测试f-string SQL注入
test_code2 = 'def search(query):\n    return f"SELECT * FROM products WHERE name = \'{query}\'"'
print(f"\nCode: {test_code2}")
features2 = classifier.extract_features(test_code2)
for k, v in features2.items():
    print(f"  {k}: {v}")
result2 = classifier.predict(test_code2)
print(f"  Prediction: {result2}")
