# 测试用例1: 空指针异常

def null_pointer_test():
    user = None
    return user.name


# 测试用例2: SQL注入
def sql_injection_test(user_input):
    sql = "SELECT * FROM users WHERE username = '" + user_input + "'"
    return sql


# 测试用例3: 内存泄漏
def memory_leak_test():
    cache = []
    while True:
        cache.append('x' * 1024 * 1024)


# 测试用例4: 竞态条件
counter = 0
def race_condition_test():
    global counter
    for i in range(1000):
        counter += 1


# 测试用例5: 安全问题
def security_test():
    password = "secret123"
    print("Password:", password)


# 测试用例6: 数组越界
def array_index_test():
    arr = [1, 2, 3]
    print(arr[5])


# 测试用例7: 未关闭资源
def resource_leak_test():
    f = open('test.txt', 'r')
    data = f.read()
    return data


# 测试用例8: 逻辑错误
def logic_error_test():
    x = 5
    if x = 10:  # 应该是 == 而不是 =
        print("x is 10")
