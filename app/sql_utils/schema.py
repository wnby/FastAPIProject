from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os

# 定义基础类
Base = declarative_base()

# 数据库文件名
DB_FILE_NAME = "hotel.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE_NAME}"

# 创建数据库引擎
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 定义数据模型
class RoomInfo(Base):
    __tablename__ = 'room_info'

    room_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String(255))
    client_name = Column(String(255))
    checkin_time = Column(DateTime)
    checkout_time = Column(DateTime)
    state = Column(Integer)
    current_speed = Column(String(255))
    current_tempera = Column(Float)


class OpRecord(Base):
    __tablename__ = 'op_record'

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer)
    op_time = Column(DateTime)
    op_type = Column(Integer)
    old = Column(String(255))
    new = Column(String(255))


class Detail(Base):
    __tablename__ = 'detail'

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer)
    query_time = Column(DateTime)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    serve_time = Column(Float)
    speed = Column(String(255))
    cost = Column(Float)
    rate = Column(Float)


class User(Base):
    __tablename__ = 'user'

    account = Column(String(255), primary_key=True)
    password = Column(String(255))
    identity = Column(String(255))


class SchedulerBoard(Base):
    __tablename__ = 'scheduler_board'

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer)
    duration = Column(Float)
    speed = Column(String(255))
    cost = Column(Float)


# 初始化数据库，检查文件是否存在
def init_db():
    if not os.path.exists(DB_FILE_NAME):
        print(f"Initializing database: {DB_FILE_NAME}")
        # 数据库文件不存在时进行迁移
        Base.metadata.create_all(bind=engine)
        init_default_users()  # 添加默认的用户数据
    else:
        print(f"Database file {DB_FILE_NAME} exists, skipping initialization.")


# 插入默认用户（根据你的 Go 代码）
def init_default_users():
    db = SessionLocal()
    try:
        db.add_all([
            User(account="manager", password="password", identity="0"),
            User(account="reception", password="password", identity="1"),
        ])
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error initializing default users: {e}")
    finally:
        db.close()


# 调用数据库初始化
init_db()
