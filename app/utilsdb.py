import sqlite3

DB_PATH = 'db/hotel.db'

def execute_query(query, params=()):
    """执行 SQL 查询并提交更改"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def fetch_one(query, params=()):
    """获取单条查询结果"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchone()
    conn.close()
    return result
