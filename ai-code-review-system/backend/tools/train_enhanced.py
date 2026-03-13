"""
增强版训练脚本 - 生成更多样化的训练数据
"""
import json
import random
import os
import re
from collections import defaultdict

def generate_enhanced_training_data():
    """生成增强的训练数据"""
    
    # 缺陷代码模板
    defect_templates = {
        'null_pointer': [
            # 基本空指针
            ("user = None\nreturn user.name", "null_pointer"),
            ("obj = None\nobj.data", "null_pointer"),
            ("result = None\nprint(result.value)", "null_pointer"),
            
            # 函数返回None后直接使用
            ("def get():\n    return None\n\nget().process()", "null_pointer"),
            ("def find():\n    return None\n\nfind().name", "null_pointer"),
            
            # 列表/字典访问
            ("items = []\nreturn items[0].name", "null_pointer"),
            ("data = {}\nreturn data['key'].value", "null_pointer"),
            
            # 方法链式调用
            ("data = get_data()\nreturn data.result.value", "null_pointer"),
            ("user = query()\nreturn user.profile.name", "null_pointer"),
            
            # 三元表达式中的空指针
            ("x = None if cond else value\nreturn x.name", "null_pointer"),
            
            # 循环后可能为空的变量
            ("for item in items:\n    pass\nreturn item.name", "null_pointer"),
            
            # 参数可能为空
            ("def process(user):\n    return user.name", "null_pointer"),
            
            # 条件判断后直接使用
            ("if flag:\n    user = None\nreturn user.name", "null_pointer"),
            
            # with语句外的变量
            ("f = open('f.txt')\nreturn f.read()", "null_pointer"),
        ],
        
        'sql_injection': [
            # 字符串拼接
            ("sql = 'SELECT * FROM users WHERE id = ' + id", "sql_injection"),
            ("query = \"SELECT * FROM logs WHERE name = '\" + name + \"'\"", "sql_injection"),
            
            # f-string注入
            ('sql = f"SELECT * FROM users WHERE name = \'{name}\'"', "sql_injection"),
            ('query = f"DELETE FROM products WHERE id = {id}"', "sql_injection"),
            
            # %格式化
            ("sql = 'SELECT * FROM t WHERE v = %s' % val", "sql_injection"),
            ("query = \"SELECT * FROM users WHERE id = '%s'\" % user_id", "sql_injection"),
            
            # .format注入
            ("sql = 'SELECT * FROM users WHERE name = {}'.format(name)", "sql_injection"),
            ("query = \"SELECT * FROM logs WHERE id = {}\".format(user_id)", "sql_injection"),
            
            # 多表查询注入
            ("sql = 'SELECT * FROM ' + table + ' WHERE id = ' + id", "sql_injection"),
            
            # 动态列名
            ("cols = 'id,name'\nsql = 'SELECT ' + cols + ' FROM users'", "sql_injection"),
            
            # LIKE注入
            ("sql = \"SELECT * FROM users WHERE name LIKE '%\" + search + \"%'\"", "sql_injection"),
            
            # INSERT/DELETE/UPDATE
            ("sql = 'INSERT INTO users VALUES (\"' + data + '\")'", "sql_injection"),
            ("sql = 'DELETE FROM users WHERE id = ' + id", "sql_injection"),
        ],
        
        'memory_leak': [
            # 文件未关闭
            ("f = open('file.txt')\nreturn f.read()", "memory_leak"),
            ("data = open('data.txt').read()", "memory_leak"),
            ("f = open('log.txt', 'a')\nf.write('msg')", "memory_leak"),
            
            # 数据库连接
            ("conn = db.connect()\nreturn conn", "memory_leak"),
            ("cursor = conn.cursor()\nreturn cursor", "memory_leak"),
            
            # 网络请求
            ("resp = urllib.urlopen(url)\nreturn resp", "memory_leak"),
            ("session = requests.Session()\nreturn session", "memory_leak"),
            
            # 线程未join
            ("t = Thread(target=worker)\nt.start()", "memory_leak"),
            ("thread = threading.Thread(target=task)\nthread.start()", "memory_leak"),
            
            # 缓存无清理
            ("cache = {}\ndef add(k, v):\n    cache[k] = v", "memory_leak"),
            
            # 打开文件句柄
            ("fd = os.open('file.txt', os.O_RDONLY)\nreturn fd", "memory_leak"),
        ],
        
        'race_condition': [
            # 全局变量
            ("counter = 0\ndef inc():\n    global counter\n    counter += 1", "race_condition"),
            ("total = 0\ndef add(n):\n    global total\n    total = total + n", "race_condition"),
            
            # 共享变量
            ("balance = 100\ndef withdraw(amt):\n    balance -= amt", "race_condition"),
            ("cache = {}\ndef update(k, v):\n    cache[k] = v", "race_condition"),
            
            # 异步竞态
            ("async def fetch():\n    await asyncio.sleep(1)\n    return data", "race_condition"),
            
            # 锁未使用
            ("def transfer():\n    balance = get_balance()\n    balance -= amount\n    save(balance)", "race_condition"),
            
            # 类变量竞态
            ("class Counter:\n    count = 0\n    def inc(self):\n        self.count += 1", "race_condition"),
        ],
        
        'security': [
            # eval/exec
            ("eval(code)", "security"),
            ("exec('print(1)')", "security"),
            ("eval(user_input)", "security"),
            
            # 命令注入
            ("os.system('ls ' + dir)", "security"),
            ("os.popen('cat ' + filename)", "security"),
            ("subprocess.call(cmd, shell=True)", "security"),
            
            # 硬编码密码/密钥
            ("password = 'admin123'", "security"),
            ("DB_PASSWORD = 'root123'", "security"),
            ("api_key = 'sk-abcdef123456'", "security"),
            ("secret_key = 'my-secret-key'", "security"),
            ("token = 'Bearer abc123'", "security"),
            
            # 不安全的反序列化
            ("data = pickle.loads(user_data)", "security"),
            ("obj = yaml.load(user_yaml)", "security"),
            
            # 弱随机
            ("key = random.randint(0, 1000000)", "security"),
            
            # 不安全的临时文件
            ("f = tempfile.mktemp()", "security"),
        ],
    }
    
    # 良好代码模板
    good_templates = {
        'no_defect': [
            # 正确的空值检查
            ("if user is not None:\n    return user.name", "no_defect"),
            ("if data:\n    return data.value", "no_defect"),
            ("if result is not None:\n    return result.process()", "no_defect"),
            ("if items:\n    return items[0].name", "no_defect"),
            
            # 三元表达式安全写法
            ("return user.name if user else None", "no_defect"),
            ("return data.get('key') if data else None", "no_defect"),
            
            # try-except保护
            ("try:\n    return user.except:\n    return None", "no_defect"),
            ("try:\n    result = risky()\nexcept:\n    result = None", "no_defect"),
            
            # with语句
            ("with open('file.txt') as f:\n    return f.read()", "no_defect"),
            ("with db.connect() as conn:\n    return conn", "no_defect"),
            
            # 参数化查询
            ("cursor.execute('SELECT * WHERE id = %s', (id,))", "no_defect"),
            ("cursor.execute('INSERT INTO t VALUES (?, ?)', (a, b))", "no_defect"),
            
            # 正确的锁使用
            ("with lock:\n    counter += 1", "no_defect"),
            
            # 类型注解
            ("def greet(name: str) -> str:\n    return f'Hello {name}'", "no_defect"),
            
            # 安全的命令执行
            ("subprocess.run(['ls', dir])", "no_defect"),
            
            # 环境变量
            ("key = os.environ.get('API_KEY')", "no_defect"),
            
            # 安全反序列化
            ("data = pickle.loads(safe_data)", "no_defect"),
            ("obj = yaml.safe_load(user_yaml)", "no_defect"),
        ]
    }
    
    # 生成所有数据
    all_data = []
    
    # 添加缺陷样本
    for label, templates in defect_templates.items():
        for code, lbl in templates:
            all_data.append({'code': code, 'label': lbl})
            # 添加变体
            variants = generate_variants(code, label)
            all_data.extend(variants)
    
    # 添加良好样本
    for label, templates in good_templates.items():
        for code, lbl in templates:
            all_data.append({'code': code, 'label': lbl})
            # 添加变体
            variants = generate_variants(code, label)
            all_data.extend(variants)
    
    return all_data


def generate_variants(code: str, label: str):
    """生成代码变体"""
    variants = []
    
    # 添加函数包装
    if 'def ' not in code:
        variants.append({'code': 'def process():\n    ' + code.replace('\n', '\n    '), 'label': label})
    
    # 添加注释
    variants.append({'code': '# processed\n' + code, 'label': label})
    
    # 改变缩进
    if '\n    ' in code:
        variants.append({'code': code.replace('\n    ', '\n        '), 'label': label})
    
    return variants


def train_enhanced_model():
    """训练增强模型"""
    print("="*60)
    print("生成增强训练数据...")
    print("="*60)
    
    training_data = generate_enhanced_training_data()
    
    # 统计
    label_counts = defaultdict(int)
    for s in training_data:
        label_counts[s['label']] += 1
    
    print(f"总样本数: {len(training_data)}")
    print("标签分布:")
    for label, count in label_counts.items():
        print(f"  {label}: {count}")
    
    # 分割数据
    random.shuffle(training_data)
    split_idx = int(len(training_data) * 0.8)
    train_data = training_data[:split_idx]
    test_data = training_data[split_idx:]
    
    print(f"\n训练集: {len(train_data)} 样本")
    print(f"测试集: {len(test_data)} 样本")
    
    print("\n" + "="*60)
    print("训练模型...")
    print("="*60)
    
    from ml_trainer import SimpleMLClassifier
    
    classifier = SimpleMLClassifier()
    classifier.train(train_data, epochs=20)
    
    print("\n" + "="*60)
    print("评估模型...")
    print("="*60)
    
    results = classifier.evaluate(test_data)
    
    print(f"\n准确率: {results['accuracy']*100:.2f}%")
    print(f"正确预测: {results['correct']}/{results['total']}")
    
    # 保存模型
    from ml_trainer import save_model
    save_model(classifier, 'trained_model_enhanced.json')
    
    print("\n增强模型已保存到 trained_model_enhanced.json")
    
    # 测试一些样本
    print("\n" + "="*60)
    print("样本测试:")
    print("="*60)
    
    test_samples = [
        "user = None\nreturn user.name",
        "sql = 'SELECT * FROM users WHERE id = ' + id",
        "with open('file.txt') as f:\n    return f.read()",
        "cursor.execute('SELECT * WHERE id = %s', (id,))",
        "def greet(name: str) -> str:\n    return f'Hello {name}'",
    ]
    
    for code in test_samples:
        result = classifier.predict(code)
        print(f"\n代码: {code[:40]}...")
        print(f"预测: {result['defect_type']} (置信度: {result['confidence']:.2f})")
    
    return classifier, results


if __name__ == "__main__":
    train_enhanced_model()
