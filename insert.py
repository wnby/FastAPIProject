import sqlite3

DB_PATH = 'db/hotel.db'

def execute_query(query, params=()):
    """执行一个查询并提交更改"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def insert_user(username, password):
    """向 users 表插入一个新用户（仅用户名和密码）"""
    query = """
    INSERT INTO users (username, password) 
    VALUES (?, ?)
    """
    execute_query(query, (username, password))

def fetch_all_users():
    """获取所有用户"""
    query = "SELECT * FROM users"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query)
    users = cursor.fetchall()
    conn.close()
    return users

# 示例：插入一个新用户
insert_user('123', '123')

# 查看所有用户记录，验证插入是否成功
print(fetch_all_users())
