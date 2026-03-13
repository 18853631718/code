import pymysql
from datetime import datetime, timedelta
import random

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'lirui4689321',
    'database': 'ai_code_review',
    'charset': 'utf8mb4'
}

SAMPLE_CODES = [
    # 空指针/空值相关
    ("def get_user(user_id):\n    user = None\n    return user.name", "python", "null_pointer", 0.92, 3, "high"),
    ("def fetch_data():\n    result = None\n    return result.data", "python", "null_pointer", 0.89, 3, "high"),
    ("def get_item(items):\n    if len(items) > 0:\n        return items[0].name\n    return None\nitem = None\nprint(item.name)", "python", "null_pointer", 0.91, 7, "high"),
    ("class User:\n    def __init__(self, name):\n        self.name = name\n\nuser = User(None)\nprint(user.name.upper())", "python", "null_pointer", 0.85, 6, "high"),
    ("def process(data):\n    return data['key'].value", "python", "null_pointer", 0.88, 2, "high"),
    
    # SQL注入
    ("def query_db(user_input):\n    sql = \"SELECT * FROM users WHERE name = '\" + user_input + \"'\"\n    return sql", "python", "sql_injection", 0.88, 2, "high"),
    ("def search(query):\n    return \"SELECT * FROM products WHERE name LIKE '%\" + query + \"%'\"", "python", "sql_injection", 0.90, 2, "high"),
    ("user_id = request.GET['id']\nsql = \"DELETE FROM users WHERE id = \" + user_id", "python", "sql_injection", 0.93, 2, "high"),
    ("def get_user(name):\n    query = f\"SELECT * FROM users WHERE name = '{name}'\"\n    return query", "python", "sql_injection", 0.91, 2, "high"),
    ("cursor.execute(\"INSERT INTO logs VALUES ('\" + message + \"')\")", "python", "sql_injection", 0.89, 1, "high"),
    
    # 内存泄漏/资源未释放
    ("def read_file():\n    f = open('test.txt', 'r')\n    data = f.read()\n    return data", "python", "memory_leak", 0.85, 2, "medium"),
    ("def get_connection():\n    conn = db.connect()\n    return conn", "python", "memory_leak", 0.87, 2, "medium"),
    ("def process_data():\n    handler = open_handler()\n    data = handler.read()\n    # 忘记关闭", "python", "memory_leak", 0.84, 3, "medium"),
    ("class DataProcessor:\n    def __init__(self):\n        self.cache = {}\n    \n    def add(self, key, value):\n        self.cache[key] = value\n    # 缓存永远不清理", "python", "memory_leak", 0.82, 1, "medium"),
    ("def create_thread():\n    thread = threading.Thread(target=worker)\n    thread.start()\n    # 线程未join", "python", "memory_leak", 0.86, 2, "medium"),
    
    # 缓冲区溢出
    ("char buffer[10];\nstrcpy(buffer, \"This is too long for buffer\");", "c", "buffer_overflow", 0.90, 2, "high"),
    ("int arr[5];\nfor(int i=0; i<10; i++) { arr[i] = i; }", "c", "buffer_overflow", 0.92, 2, "high"),
    ("void copy(char *dest, char *src) {\n    while(*src) *dest++ = *src++;\n}", "c", "buffer_overflow", 0.88, 1, "high"),
    ("char str[20];\nmemset(str, 0, 25);", "c", "buffer_overflow", 0.91, 2, "high"),
    ("int *arr = malloc(10 * sizeof(int));\nfor(int i=0; i<20; i++) arr[i] = i;", "c", "buffer_overflow", 0.89, 2, "high"),
    
    # 竞态条件
    ("def increment():\n    global counter\n    temp = counter\n    temp = temp + 1\n    counter = temp", "python", "race_condition", 0.75, 5, "medium"),
    ("balance = 0\ndef withdraw(amount):\n    if balance >= amount:\n        time.sleep(0.1)\n        balance -= amount\n    return balance", "python", "race_condition", 0.78, 2, "medium"),
    ("shared_data = {}\ndef update(key, value):\n    old = shared_data.get(key, 0)\n    shared_data[key] = old + value", "python", "race_condition", 0.77, 3, "medium"),
    ("class Counter:\n    count = 0\n    def inc(self):\n        self.count += 1\n# 多线程不安全", "python", "race_condition", 0.80, 4, "medium"),
    ("cache = {}\ndef get_or_set(key, factory):\n    if key not in cache:\n        cache[key] = factory()\n    return cache[key]", "python", "race_condition", 0.73, 4, "medium"),
    
    # 安全问题
    ("def execute_command(cmd):\n    os.system(cmd)", "python", "security", 0.92, 2, "high"),
    ("eval(user_input)", "python", "security", 0.95, 1, "high"),
    ("import pickle\ndata = pickle.loads(user_data)", "python", "security", 0.90, 2, "high"),
    ("password = 'admin123'\nif user_input == password:", "python", "security", 0.88, 2, "high"),
    ("secret_key = 'my-secret-key-12345'", "python", "security", 0.85, 1, "high"),
    
    # 逻辑错误
    ("def is_even(n):\n    if n % 2 == 0:\n        return False\n    else:\n        return True", "python", "logic_error", 0.82, 2, "low"),
    ("def find_max(items):\n    max = items[0]\n    for item in items:\n        if item > max:\n            max = item\n    return min", "python", "logic_error", 0.85, 5, "low"),
    ("def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n)", "python", "logic_error", 0.80, 4, "low"),
    
    # 良好代码（无缺陷）
    ("def hello():\n    print('Hello World')\n    return True", "python", "no_defect", 0.98, 1, "none"),
    ("def add(a, b):\n    return a + b", "python", "no_defect", 0.99, 1, "none"),
    ("def is_valid_email(email):\n    import re\n    pattern = r'^[\\w.-]+@[\\w.-]+\\.\\w+$'\n    return re.match(pattern, email) is not None", "python", "no_defect", 0.95, 3, "none"),
    ("class Calculator:\n    @staticmethod\n    def add(a, b):\n        return a + b\n    \n    @staticmethod\n    def subtract(a, b):\n        return a - b", "python", "no_defect", 0.97, 1, "none"),
    ("def process_data(data):\n    with open('output.txt', 'w') as f:\n        f.write(data)\n    return True", "python", "no_defect", 0.96, 2, "none"),
]

SESSIONS_DATA = [
    ("Python Code Review", "admin", "active", "admin,zhangsan,lisi"),
    ("Security Audit", "zhangsan", "active", "zhangsan,lisi"),
    ("Performance Optimization", "lisi", "closed", "lisi,wangwu"),
    ("Bug Fixes Review", "wangwu", "active", "wangwu,admin,zhangsan"),
    ("Code Refactoring", "admin", "active", "admin,lisi"),
]

def insert_sample_data():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Connected to MySQL successfully!")
        
        cursor.execute("DELETE FROM review_comments")
        cursor.execute("DELETE FROM review_sessions")
        cursor.execute("DELETE FROM analysis_results")
        cursor.execute("DELETE FROM code_files")
        conn.commit()
        
        print("Cleared existing data...")
        
        suggestions = {
            'null_pointer': 'Add null check before dereferencing. Use "if variable is not None:"',
            'sql_injection': 'Use parameterized queries instead of string concatenation',
            'memory_leak': 'Ensure proper resource cleanup. Use "with" statement or close files',
            'buffer_overflow': 'Use safer string functions with bounds checking',
            'race_condition': 'Use proper locking mechanisms for concurrent access',
            'security': 'Follow security best practices. Avoid eval, pickle, hardcoded secrets',
            'logic_error': 'Review logic and fix the error'
        }
        
        for i, (code, lang, defect_type, confidence, line, severity) in enumerate(SAMPLE_CODES):
            filename = f"sample_{i+1}.{lang}"
            
            cursor.execute(
                "INSERT INTO code_files (filename, language, content) VALUES (%s, %s, %s)",
                (filename, lang, code)
            )
            file_id = cursor.lastrowid
            
            if defect_type != "no_defect":
                cursor.execute(
                    """INSERT INTO analysis_results 
                       (file_id, defect_type, confidence, line_number, suggestion, severity) 
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (file_id, defect_type, confidence, line, suggestions.get(defect_type, ''), severity)
                )
        
        for name, owner, status, participants in SESSIONS_DATA:
            cursor.execute(
                "INSERT INTO review_sessions (name, owner, status, participants) VALUES (%s, %s, %s, %s)",
                (name, owner, status, participants)
            )
            session_id = cursor.lastrowid
            
            comments_pool = [
                ("Looks good, approved!", "Good implementation"),
                ("Consider adding error handling", "Missing error handling"),
                ("This might cause a security issue", "Security concern found"),
                ("Performance could be improved", "Performance optimization needed"),
                ("Add unit tests for this function", "Testing needed"),
                ("Code style doesn't match our guidelines", "Style issue"),
                ("Nice use of best practices", "Good job!"),
            ]
            
            num_comments = random.randint(2, 5)
            selected_comments = random.sample(comments_pool, min(num_comments, len(comments_pool)))
            
            for author, content in selected_comments:
                cursor.execute(
                    "INSERT INTO review_comments (session_id, author, content, line_number) VALUES (%s, %s, %s, %s)",
                    (session_id, author, content, random.randint(1, 50))
                )
        
        conn.commit()
        
        print(f"Inserted {len(SAMPLE_CODES)} sample codes with analysis results!")
        print(f"Inserted {len(SESSIONS_DATA)} review sessions!")
        
        cursor.execute("SELECT NOW()")
        current_time = cursor.fetchone()[0]
        print(f"\nCurrent database time: {current_time}")
        
        cursor.execute("SELECT COUNT(*) FROM code_files")
        print(f"Total files in database: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM analysis_results")
        print(f"Total analysis results: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT defect_type, COUNT(*) as count FROM analysis_results GROUP BY defect_type")
        print("\nDefect distribution:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")
        
        cursor.close()
        conn.close()
        
    except pymysql.Error as e:
        print(f"MySQL Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    insert_sample_data()
