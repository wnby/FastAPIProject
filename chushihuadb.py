import sqlite3

def create_tables():
    # 连接到 SQLite 数据库
    conn = sqlite3.connect('db/hotel.db')

    # 创建一个游标对象
    cursor = conn.cursor()

    # 创建表格
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS rooms (
        room_id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_number INTEGER NOT NULL UNIQUE,
        room_type TEXT NOT NULL,
        status TEXT NOT NULL,
        temperature REAL DEFAULT 24,
        speed TEXT DEFAULT 'low',
        current_fee REAL DEFAULT 0
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS check_ins (
        check_in_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        room_id INTEGER NOT NULL,
        check_in_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        check_out_time TIMESTAMP,
        deposit REAL,
        total_fee REAL,
        FOREIGN KEY (user_id) REFERENCES users (user_id),
        FOREIGN KEY (room_id) REFERENCES rooms (room_id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS ac_usage (
        usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_id INTEGER NOT NULL,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP,
        temperature REAL,
        speed TEXT,
        total_fee REAL,
        FOREIGN KEY (room_id) REFERENCES rooms (room_id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS ac_admins (
        admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'admin',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS reports (
        report_id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_type TEXT,
        data TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 提交事务
    conn.commit()

    # 关闭游标和连接
    cursor.close()
    conn.close()

# 创建数据库和表
create_tables()
